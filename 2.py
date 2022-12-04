import csv
import re
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np

currency_to_rub = {
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
def csv_reader(name):
    """

    :param name: имя исходного файла
    :return: возвращает, заголовки и данные
    """
    csv_list = csv.reader(open(name, encoding='utf-8-sig'))
    data = [x for x in csv_list]
    return data[0], data[1::]

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

name = input('Введите название файла: ')
if name == "":
    name = "vacancies_by_year.csv"
prof = input('Введите название профессии: ')
if prof == "":
    prof = "Аналитик"
header, vac = csv_reader(name)
vac = csv_filer(vac)
dict_naming = {}
for i in range(len(header)):
    dict_naming[header[i]] = i

salary_dynamic = {}
count_dynamic = {}
salary_prof_dynamic = {}
city_count = {}
salary_city = {}
prof_count = {}
for item in vac:
    year = int(item[dict_naming['published_at']].split('-')[0])
    if year not in count_dynamic:
        count_dynamic[year] = 0
    count_dynamic[year] += 1
    for i in range(len(item)):
        if header[i] == 'salary_from':
            salary = (float(item[i]) + float(item[i+1])) / 2
            if item[dict_naming['salary_currency']] != 'RUR':
                salary *= currency_to_rub[item[dict_naming['salary_currency']]]
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

for item in vac:
    for i in range(len(item)):
        if header[i] == 'salary_from':
            salary = (float(item[i]) + float(item[i+1])) / 2
            city = item[dict_naming['area_name']]
            if item[dict_naming['salary_currency']] != 'RUR':
                salary *= currency_to_rub[item[dict_naming['salary_currency']]]
            if city_count[city] >= int(sum(city_count.values()) * 0.01):
                if city not in salary_city:
                    salary_city[city] = []
                salary_city[city].append(int(salary))
for key in salary_dynamic:
    salary_dynamic[key] = sum(salary_dynamic[key]) // len(salary_dynamic[key])
for key in salary_prof_dynamic:
    salary_prof_dynamic[key] = sum(salary_prof_dynamic[key]) // max(len(salary_prof_dynamic[key]), 1)
for key in salary_city:
    salary_city[key] = sum(salary_city[key]) // len(salary_city[key])

fig, axs = plt.subplots(nrows= 2 , ncols= 2 , figsize=(10,10), dpi=100)

ax1 = axs[0,0]
ax2 = axs[0,1]
ax3 = axs[1,0]
ax4 = axs[1,1]

def set_ax4(most, total):
    """
    заполняет 4 график данными
    :param most: значения по 10 городам
    :param total: остальные города
    :return:
    """
    arr = []
    labels = []
    for key in most:
        arr.append(most[key])
        labels.append(key)

    ax4.pie(arr, labels=labels)
    ax4.set_title("Доля вакансий по городам")

def set_ax3(salaries):
    """

    :param salaries: список зарплат
    :return:
    """
    arr = []
    labels = []
    for key in salaries:
        arr.append(salaries[key])
        labels.append(key)
    ax3.barh(labels,arr)
    ax3.set_title("Уровень зарплат по городам")
    ax3.invert_yaxis()  # labels read top-to-bottom

def set_ax1(salaries, prof_salaries, prof):
    """

    :param salaries: список зарплат
    :param prof_salaries: список зарплат по профессии
    :param prof: профессия
    :return:
    """
    x_axis = np.arange(len(salaries))
    years = []
    arr = []
    prof_arr = []
    for key in salaries:
        years.append(key)
        arr.append(salaries[key])
        prof_arr.append(prof_salaries[key])
    ax1.bar(x_axis - 0.2, arr, width=0.4, label='средняя з/п')
    ax1.bar(x_axis + 0.2, prof_arr, width=0.4, label='з/п ' + prof)
    ax1.set_xticks(x_axis, years, rotation='vertical')

    ax1.legend()
    ax1.set_title("Уровень заплат по годам")

def set_ax2(vacancies, prof_vacancies, prof):
    """

    :param vacancies: кол-во вакансий
    :param prof_vacancies: кол-во вакансий по профессии
    :param prof: профессия
    :return:
    """
    x_axis = np.arange(len(vacancies))
    years = []
    arr = []
    prof_arr = []
    for key in vacancies:
        years.append(key)
        arr.append(vacancies[key])
        prof_arr.append(prof_vacancies[key])
    ax2.bar(x_axis - 0.2, arr, width=0.4, label='количество вакансий')
    ax2.bar(x_axis + 0.2, prof_arr, width=0.4, label='количество вакансий ' + prof)
    ax2.set_xticks(x_axis, years,rotation='vertical')
    ax2.legend()
    ax2.set_title("Количество вакансий по годам")



print('Динамика уровня зарплат по годам:', salary_dynamic)
print('Динамика количества вакансий по годам:', count_dynamic)
print('Динамика уровня зарплат по годам для выбранной профессии:', salary_prof_dynamic)
print('Динамика количества вакансий по годам для выбранной профессии:', prof_count)




print('Уровень зарплат по городам (в порядке убывания):', dict(Counter(salary_city).most_common(10)))
most = dict(Counter({k: float('{:.4f}'.format(v/sum(city_count.values()))) for k,v in city_count.items()}).most_common(10))
most = {k: v for k, v in most.items() if v >= 0.01}
print('Доля вакансий по городам (в порядке убывания):', most)

set_ax1(salaries=salary_dynamic,prof_salaries=salary_prof_dynamic, prof=prof)
set_ax2(vacancies=count_dynamic, prof_vacancies=prof_count, prof=prof)
set_ax3(salaries=dict(Counter(salary_city).most_common(10)))
set_ax4(most=most, total= sum(city_count.values()))

plt.savefig("graph.png")
plt.show()
