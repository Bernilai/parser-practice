import psycopg2
from flask import Flask, render_template, request
import parser_practice

app = Flask(__name__)


@app.route('/')
def vacancies():
    return render_template('home.html')


@app.route('/search', methods=['POST'])
def search():
    conn = psycopg2.connect(**parser_practice.db_config)
    cur = conn.cursor()

    keyword = request.form['query']

    parser_practice.parse_vacancies(keyword)

    cur.execute('SELECT title, salary, schedule, experience, city, employer, url FROM vacancies')
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('all_vac.html', data=rows, keyword=keyword)


if __name__ == '__main__':
    app.run(debug=True)
