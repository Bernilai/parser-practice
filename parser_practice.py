import random
import time

import psycopg2
import requests

db_config = {
    'database': "vacancies",
    'user': "postgres",
    'password': "83276320",
    'host': "localhost",
    'port': "6320"
}


def get_vacancies(keyword, page):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": None,
        "page": page,
        "per_page": 20,
    }
    headers = {
        "User-Agent": "Your User Agent",
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()


def create_table(conn):
    cur = conn.cursor()

    create_table_query = ("CREATE TABLE IF NOT EXISTS vacancies ("
                          "id SERIAL PRIMARY KEY,"
                          "title VARCHAR(255),"
                          "salary VARCHAR(50),"
                          "schedule VARCHAR(50),"
                          "experience VARCHAR(50),"
                          "city VARCHAR(50),"
                          "employer VARCHAR(255),"
                          "url VARCHAR(255))")
    cur.execute(create_table_query)

    conn.commit()
    cur.close()


def drop_table(conn):
    cur = conn.cursor()

    drop_table_query = "DROP TABLE IF EXISTS vacancies"
    cur.execute(drop_table_query)

    conn.commit()
    cur.close()


def parse_vacancies(keyword):
    with psycopg2.connect(**db_config) as conn:
        drop_table(conn)
        create_table(conn)

        page = 0
        while True:
            data = get_vacancies(keyword, page)

            if not data.get('items'):
                break

            with conn.cursor() as cur:
                for item in data['items']:
                    title = item['name']
                    city = item['area']['name']
                    employer = item['employer']['name']
                    experience = item['experience']['name']
                    schedule = item['schedule']['name']
                    salary = item['salary']
                    url = item['alternate_url']
                    if salary is None:
                        salary = "не указана"
                    else:
                        salary = f"от {salary.get('from')} до {salary.get('to')}"

                    insert_query = ("INSERT INTO vacancies "
                                    "(title, salary, city, schedule, employer, experience, url)"
                                    "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                    cur.execute(insert_query, (title, salary, city, schedule, employer, experience, url))
                if page >= data['pages'] - 1:
                    break

                page += 1

                time.sleep(random.uniform(1, 3))

        conn.commit()
