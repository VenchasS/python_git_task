import os.path

from jinja2 import Environment, FileSystemLoader
import pdfkit
from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment


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

class Table:
    """
    Класс который формирует html таблицу
    """
    def __init__(self, width):
        """

        :param width: ширина таблицы
        """
        self.width = width
        self.rows = []
        pass

    def add_row(self):
        """
        добавляет новую строку в таблицу
        :return:
        """
        self.rows.append([" "] * self.width)

    def set_value(self, row, column, value):
        """
        устанавливает значение в ячейку
        :param row: номер строки
        :param column: номер столбца
        :param value: значение
        :return:
        """
        if row > len(self.rows):
            self.add_row()
        self.rows[row - 1][column - 1] = value

    def to_string(self):
        """
        формирует html таблицу
        :return: таблица в формате html
        """
        result = ""
        result += "<table>\n"

        for row in self.rows:
            result += "<tr>"
            for value in row:
                result += f"<th>{value}</th>"
            result += "</tr>"

        result += "</table>"
        return result


thin = Side(border_style="thin", color="000000")
ws1 = Table(5)
ws2 = Table(5)



def set_cities(salaries, vacancies):
    """
        Устанавливает в таблицу все списки городов
        :param salaries: список зарплат
        :param vacancies: список вакансий
        :return: ничего
        """
    setCell(row=1, column=1, value="Город",bold=True, ws=ws2)
    setCell(row=1, column=2, value="Уровень зарплаты", ws=ws2,bold=True)
    setCell(row=1, column=4, value="Город", ws=ws2, bold=True)
    setCell(row=1, column=5, value="Доля вакансий", ws=ws2,bold=True)
    index = 2
    for key in salaries:
        setCell(row=index, column=1, ws=ws2, value=key)
        setCell(row=index, column=2, ws=ws2, value=salaries[key])
        index+=1
    index = 2
    for key in vacancies:
        setCell(row=index, column=4, value=key , ws=ws2)
        setCell(row=index, column=5, value=f'{round(vacancies[key] * 100,2)}%', ws=ws2)
        index+=1

def setCell(row,column,value,ws, bold=False):
    """
    Устанавливает значение в таблицу применяя параметры
    :param row: номер строки
    :param column   номер столбца
    :param value: значение ячейки
    :param ws: ссылка на таблицу
    :param bold: жирность текста
    :return: ничего
    """
    ws.set_value(row=row,column=column,value=value)


def set_years(salary_dynamic, count_dynamic, salary_prof_dynamic , prof_count):
    """
    Устанавливает значение в таблицу применяя параметры
    :param salary_dynamic: список зарплат
    :param count_dynamic: список кол-ва
    :param salary_prof_dynamic: список зарплат по професии
    :param prof_count: список кол-ва по профессии
    :return: ничего
    """
    setCell(row=1,column=1,value="год",ws=ws1,bold=True)
    setCell(row=1,column=2,value="Средняя зарплата" ,ws=ws1,bold=True)
    setCell(row=1,column=3,value="Средняя зарплата " + prof ,ws=ws1,bold=True)
    setCell(row=1,column=4,value="Количество вакансий",ws=ws1,bold=True)
    setCell(row=1,column=5,value="Количество вакансий " + prof,ws=ws1,bold=True)
    index = 2
    for key in prof_count:
        setCell(row=index, column=1, value=key, ws=ws1)
        setCell(row=index, column=2, value=salary_dynamic[key], ws=ws1)
        setCell(row=index, column=3, value=salary_prof_dynamic[key], ws=ws1)
        setCell(row=index, column=4, value=count_dynamic[key], ws=ws1)
        setCell(row=index, column=5, value=prof_count[key], ws=ws1)
        index+=1


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

def generate_pdf(img_path: str, prof: str, ws1 ,ws2 ):
    """
    генерирует пдф файл
    :param img_path: имя файла
    :param prof: профессия
    :param ws1: таблица 1
    :param ws2: иаблица 2
    :return:
    """
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("pdf_template.html")
    pdf_template = template.render({'prof': prof, 'img_path': img_path, 'ws1': ws1 , 'ws2':ws2})
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={"enable-local-file-access": ""})

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

set_years(salary_dynamic,count_dynamic,salary_prof_dynamic,prof_count)
set_cities(dict(Counter(salary_city).most_common(10)), most)

plt.savefig("graph.png")
#plt.show()

file_path = os.path.abspath('graph.png')
print(file_path)
generate_pdf(file_path, prof, ws1.to_string(), ws2.to_string())
