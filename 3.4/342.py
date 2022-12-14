import math
import os
import shutil
import pandas as pd
import report_class
from multiprocessing import Process, Queue
pd.options.mode.chained_assignment = None

def main(file_name, folder_name):
    new_path = fr'./{folder_name}'
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    df = pd.read_csv(file_name)
    df['year'] = df['published_at'].apply(lambda x: x[0:4])
    df_group = df.groupby('year')

    for year, data in df_group:
        data.loc[:, data.columns != 'year'].to_csv(rf'{folder_name}\part_{year}.csv', index=False)


class Statistics:
    def __init__(self):
        self.year_by_vac_num = {}
        self.year_by_salary = {}
        self.year_by_vac_num_job = {}
        self.year_by_salary_job = {}
        self.vac_num_by_area = {}
        self.salary_by_area = {}

class UserInput:
    def __init__(self):
        self.file_name = 'vacancies_dif_currencies.csv'
        self.job_name = 'Аналитик'


def fill_df(df, currencies):
    df['salary'] = df.apply(lambda x: get_salary(x, currencies), axis=1)
    df.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)
    df = df.reindex(columns=['name', 'salary', 'area_name', 'published_at'], copy=True)
    return df


def get_salary(x, currencies):
    salary_from, salary_to, salary_currency, published_at = x.loc['salary_from'], x.loc['salary_to'], x.loc['salary_currency'], x.loc['published_at']
    currencies_to_work = list(currencies.loc[:, ~currencies.columns.isin(['date'])].columns.values)
    date = published_at[:7]
    if math.isnan(salary_to) or math.isnan(salary_from):
        salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        salary = math.floor((salary_from + salary_to) / 2)
    if salary_currency == 'RUR' or salary_currency not in currencies_to_work:
        return salary
    return math.floor(salary * currencies.loc[currencies['date'] == date][salary_currency].values[0])


def calc_year_stat_mp(file_name, job_name, q, currencies):
    df = pd.read_csv(file_name)
    df = fill_df(df, currencies)
    data_job = df[df['name'].str.contains(job_name, case=False)]

    q.put([int(df['published_at'].values[0][:4]), df.shape[0], math.floor(df['salary'].mean()), data_job.shape[0], math.floor(data_job['salary'].mean()), df])


def calc_year_stats_mp():
    global st, df_res
    process = []
    q = Queue()
    currencies = pd.read_csv('currencies.csv')
    for file_name in os.listdir(temp_folder):
        p = Process(target=calc_year_stat_mp, args=(temp_folder + '/' + file_name, user_input.job_name, q, currencies.copy()))
        process.append(p)
        p.start()

    for p in process:
        p.join(1)
        data = q.get()
        st.year_by_vac_num[data[0]] = data[1]
        st.year_by_salary[data[0]] = data[2]
        st.year_by_vac_num_job[data[0]] = data[3]
        st.year_by_salary_job[data[0]] = data[4]
        df_res.append(data[5])

    st.year_by_vac_num = dict(sorted(st.year_by_vac_num.items(), key=lambda i: i[0]))
    st.year_by_salary = dict(sorted(st.year_by_salary.items(), key=lambda i: i[0]))
    st.year_by_vac_num_job = dict(sorted(st.year_by_vac_num_job.items(), key=lambda i: i[0]))
    st.year_by_salary_job = dict(sorted(st.year_by_salary_job.items(), key=lambda i: i[0]))


def calc_area_stats():
    global st
    df = pd.concat(df_res, ignore_index=True)
    all_vac_num = df.shape[0]
    vac_percent = int(all_vac_num * 0.01)

    data = df.groupby('area_name')['name'] \
        .count() \
        .apply(lambda x: round(x / all_vac_num, 4)) \
        .sort_values(ascending=False) \
        .head(10) \
        .to_dict()
    st.vac_num_by_area = data

    area_vac_num = df.groupby('area_name')['name']\
        .count()\
        .loc[lambda x: x > vac_percent]\
        .to_dict()

    data = df.loc[df['area_name'].isin(area_vac_num.keys())]\
        .groupby('area_name')['salary']\
        .mean()\
        .apply(lambda x: math.floor(x))\
        .sort_values(ascending=False)\
        .head(10)\
        .to_dict()
    st.salary_by_area = data


def print_stats():
    print(f'Динамика уровня зарплат по годам: {st.year_by_salary}')
    print(f'Динамика количества вакансий по годам: {st.year_by_vac_num}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {st.year_by_salary_job}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {st.year_by_vac_num_job}')
    print(f'Уровень зарплат по городам (в порядке убывания): {st.salary_by_area}')
    print(f'Доля вакансий по городам (в порядке убывания): {st.vac_num_by_area}')


if __name__ == '__main__':
    st = Statistics()
    df_res = []
    temp_folder = 'csv_files_dif_currencies_temp'

    user_input = UserInput()
    main(user_input.file_name, temp_folder)
    calc_year_stats_mp()
    calc_area_stats()

    report_class.main(user_input, st)
    print_stats()
    shutil.rmtree(rf'./{temp_folder}')