import csv
import os

def csv_reader(name):
    """
    :param name: имя исходного файла
    :return: возвращает, заголовки и данные
    """
    csv_list = csv.reader(open(name, encoding='utf-8-sig'))
    data = [x for x in csv_list]
    return data[0], data[1::]

def make_chunks(vac, header):
    """
    :param vac: список вакансий
    :param header: заголовок
    :return: список с годами
    """
    if not os.path.exists("../files"):
        os.makedirs("../files")
    chunks = []
    dict_naming = 0
    for i in range(len(header)):
        if header[i] == "published_at":
            dict_naming = i
    for row in vac:
        year = row[dict_naming].split('-')[0]
        file = open(f'../files/{year}.csv', 'a', encoding='utf-8-sig', newline='')
        writer = csv.writer(file)
        if year not in chunks:
            writer.writerow(header)
            chunks.append(year)
        writer.writerow(row)
    return chunks

header,vac = csv_reader("vacancies_by_year.csv")
make_chunks(vac,header)