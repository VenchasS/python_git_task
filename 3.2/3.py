import csv
import re
from collections import Counter
from datetime import datetime
import concurrent.futures


CURRENCY_TO_RUB = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }


def clean(text):
    """
    очищает строку
    :param text: исходная строка
    :return: очищенная строка
    """
    example = re.compile(r'<[^>]+>')
    s = example.sub('', text).replace(' ', ' ').replace('\xa0', ' ').strip()
    return re.sub(" +", " ", s)

def csv_filer(reader):
    """
    Проверяет данные
    :param reader: ридер csv файла
    :return: возвращает структурированные данные
    """
    all_vac = [x for x in reader if '' not in x and len(x) == len(reader[0])]
    vac = [[clean(y) for y in x] for x in all_vac]
    return vac

class DataSet:

    def __init__(self, name, prof):
        self.file_name = name
        self.prof = prof

    def start(self):
        header, vac = self.csv_reader(self.file_name)
        vac = csv_filer(vac)
        self.dict_naming, self.salary_dynamic, self.count_dynamic, self.salary_prof_dynamic, self.city_count, self.prof_count = DataSet.count(vac, header, self.prof)
        self.salary_city = DataSet.calculate_city(vac, header, self.dict_naming, self.city_count)
        self.salary_dynamic, self.count_dynamic, self.salary_prof_dynamic, self.prof_count, self.salary_city, self.most = DataSet.last_summ(
            self.salary_dynamic, self.salary_prof_dynamic, self.salary_city, self.city_count, self.count_dynamic,
            self.prof_count)

    def start_multi(self, q_salary_dynamic, q_count_dynamic, q_salary_prof_dynamic, q_prof_count):
        self.start()
        q_salary_dynamic.put(self.salary_dynamic)
        q_count_dynamic.put(self.count_dynamic)
        q_salary_prof_dynamic.put(self.salary_prof_dynamic)
        q_prof_count.put(self.prof_count)

    def csv_reader(self,name):
        """
        :param name: имя исходного файла
        :return: возвращает, заголовки и данные
        """
        csv_list = csv.reader(open(name, encoding='utf-8-sig'))
        data = [x for x in csv_list]
        return data[0], data[1::]

    @staticmethod
    def count(vac, header, prof):
        """Выполняет счёт по вакансиям
        """
        dict_naming = {}
        for i in range(len(header)):
            dict_naming[header[i]] = i
        salary_dynamic = {}
        count_dynamic = {}
        salary_prof_dynamic = {}
        city_count = {}
        prof_count = {}
        years = {}
        for item in vac:
            year = int(item[dict_naming['published_at']].split('-')[0])
            if year not in years:
                years[year] = year
            for i in range(len(item)):
                if header[i] == 'salary_from':
                    salary = (float(item[i]) + float(item[i + 1])) / 2
                    if item[dict_naming['salary_currency']] != 'RUR':
                        salary *= DataSet.CURRENCY_TO_RUB[item[dict_naming['salary_currency']]]
                    if year not in salary_dynamic:
                        salary_dynamic[year] = []
                    salary_dynamic[year].append(int(salary))
                    if year not in salary_prof_dynamic:
                        salary_prof_dynamic[year] = []
                    if prof in item[0]: salary_prof_dynamic[year].append(int(salary))
                    if year not in prof_count:
                        prof_count[year] = 0
                    if prof in item[0]: prof_count[year] += 1
                city = item[dict_naming['area_name']]
                if city not in city_count:
                    city_count[city] = 0
                city_count[city] += 1
            if year not in count_dynamic:
                count_dynamic[year] = 0
            count_dynamic[year] += 1
        return dict_naming, salary_dynamic, count_dynamic, salary_prof_dynamic, city_count, prof_count

    @staticmethod
    def calculate_city(vac, header, dict_naming, city_count):
        """Выполняет счет по городам
        """
        salary_city = {}
        for item in vac:
            for i in range(len(item)):
                if header[i] == 'salary_from':
                    salary = (float(item[i]) + float(item[i + 1])) / 2
                    city = item[dict_naming['area_name']]
                    if item[dict_naming['salary_currency']] != 'RUR':
                        salary *= DataSet.CURRENCY_TO_RUB[item[dict_naming['salary_currency']]]
                    if city_count[city] >= int(sum(city_count.values()) * 0.01):
                        if city not in salary_city:
                            salary_city[city] = []
                        salary_city[city].append(int(salary))
        return salary_city

    @staticmethod
    def last_summ(salary_dynamic, salary_prof_dynamic, salary_city, city_count, count_dynamic, prof_count):
        for key in salary_dynamic:
            salary_dynamic[key] = sum(salary_dynamic[key]) // len(salary_dynamic[key])
        for key in salary_prof_dynamic:
            salary_prof_dynamic[key] = sum(salary_prof_dynamic[key]) // max(len(
                salary_prof_dynamic[key]), 1)
        for key in salary_city:
            salary_city[key] = sum(salary_city[key]) // len(salary_city[key])

        salary_city = dict(Counter(salary_city).most_common(10))
        most = {k: float('{:.4f}'.format(v / sum(city_count.values()))) for k, v in city_count.items()}
        most = dict(Counter(most).most_common(10))
        most = {k: v for k, v in most.items() if v >= 0.01}
        return salary_dynamic, count_dynamic, salary_prof_dynamic, prof_count, salary_city, most

    def start_futures(self):
        self.start()
        return self.salary_dynamic, self.count_dynamic, self.salary_prof_dynamic, self.prof_count



if __name__ == '__main__':
    start_time = datetime.now()
    count_dynamic = {}
    salary_dynamic = {}
    salary_prof_dynamic = {}
    prof_count = {}
    futures = []
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)

    for year in range(2007, 2022 + 1):
        data = DataSet(f"files/{year}.csv", "Аналитик")
        future = executor.submit(data.start_futures)
        futures.append(future)
    for future in futures:
        r = future.result()
        salary_dynamic = {**salary_dynamic, **r[0]}
        count_dynamic = {**count_dynamic, **r[1]}
        salary_prof_dynamic = {**salary_prof_dynamic, **r[2]}
        prof_count = {**prof_count, **r[3]}

    print(f"Динамика уровня зарплат по годам: {dict(sorted(salary_dynamic.items(), key=lambda x: x[0]))}")
    print(f"Динамика количества вакансий по годам: {dict(sorted(count_dynamic.items(), key=lambda x: x[0]))}")
    print(f"Динамика уровня зарплат по годам для выбранной профессии: {dict(sorted(salary_prof_dynamic.items(), key=lambda x: x[0]))}")
    print(f"Динамика количества вакансий по годам для выбранной профессии: {dict(sorted(prof_count.items(), key=lambda x: x[0]))}")

    print(f"Время: {datetime.now() - start_time}")