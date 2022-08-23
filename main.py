from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import datetime
import math
import json

app = Flask(__name__, template_folder='templates')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'lcp_practical'

mysql = MySQL(app)



def database_information():
    db_cursor = mysql.connection.cursor()
    db_cursor.execute('''SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "lcp_practical"''')
    result = db_cursor.fetchall()
    columns = db_cursor.description
    result = converter(result, columns)
    tables = set()
    for row in result:
        tables.add(row['Table name'])
    return tables, result


def graph_and_chart():
    db_cursor = mysql.connection.cursor()
    db_cursor.execute(
        'SELECT COUNT(pupils.id) AS pupils, schools.school_name AS school_name FROM pupils INNER JOIN schools ON pupils.school_id=schools.school_code GROUP BY school_name')
    pupils_school = db_cursor.fetchall()
    pupils_school_columns = db_cursor.description
    pupils_school_results = converter(pupils_school, pupils_school_columns)

    seasons = []
    db_cursor.execute('SELECT COUNT(*) FROM pupils WHERE MONTH(date_of_birth) <= 3')
    spring = db_cursor.fetchall()[0][0]

    db_cursor.execute('SELECT COUNT(*) FROM pupils WHERE MONTH(date_of_birth) >= 4 AND MONTH(date_of_birth) <= 8')
    autumn = db_cursor.fetchall()[0][0]

    db_cursor.execute('SELECT COUNT(*) FROM pupils WHERE MONTH(date_of_birth) >= 9 AND MONTH(date_of_birth) <= 12')
    summer = db_cursor.fetchall()[0][0]
    seasons.append({'Season': 'Spring', 'Pupils': spring})
    seasons.append({'Season': 'Summer', 'Pupils': summer})
    seasons.append({'Season': 'Autumn', 'Pupils': autumn})
    return pupils_school_results, seasons


def converter(arr, columns):
    final_results = []
    for row in arr:
        obj = {}
        for i in range(len(row)):
            if isinstance(row[i], datetime.date):
                obj[columns[i][0].replace('_', ' ').capitalize()] = row[i].strftime('%Y-%m-%d')
            else:
                obj[columns[i][0].replace('_', ' ').capitalize()] = row[i]
        final_results.append(obj)
    return final_results

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
    per_page = 20
    start = (page * per_page) - per_page
    db_cursor = mysql.connection.cursor()
    db_cursor.execute("SELECT pupils.id, pupils.first_name, pupils.surname, pupils.gender, pupils.date_of_birth, pupils.ethnicity, schools.school_name FROM pupils INNER JOIN schools ON pupils.school_id = schools.school_code LIMIT %s, %s", (start , per_page))
    result = db_cursor.fetchall()
    columns = db_cursor.description
    result = converter(result, columns)
    columns = result[0].keys()

    db_cursor.execute('SELECT COUNT(*) FROM pupils')
    count = db_cursor.fetchall()

    pupils_school_results, seasons = graph_and_chart()

    tables, table_columns = database_information()

    return render_template('home.html', data=json.dumps(pupils_school_results), tables=tables, table_columns=table_columns, seasons=json.dumps(seasons), result=result, columns=columns, total_pages=math.ceil((list(count)[0][0])/per_page), pupil_count=count[0][0], current_page=page)


@app.route('/filter', defaults={'page': 1})
@app.route('/filter/<int:page>')
def filter(page):
    per_page = 20
    start = (page * per_page) - per_page
    filters = request.args
    db_cursor = mysql.connection.cursor()
    query = '''SELECT pupils.id, pupils.first_name, pupils.surname, pupils.gender, pupils.date_of_birth, pupils.ethnicity, schools.school_name FROM pupils INNER JOIN schools ON pupils.school_id = schools.school_code '''
    if filters['filter'] == 'match':
        query += ''' WHERE ''' + filters['column'].replace(' ', '_').lower() + '''="''' + filters['value'] + '''"'''
    if filters['filter'] != 'match':
        query += ''' WHERE ''' + filters['column'].replace(' ', '_').lower() + '''!="''' + filters['value'] + '''"'''
    db_cursor.execute(query)
    extra = list(db_cursor.fetchall())
    total_pages = math.ceil(len(extra) / per_page)
    query += '''LIMIT %s, %s'''
    db_cursor.execute(query, (start, per_page))
    result = db_cursor.fetchall()
    columns = db_cursor.description
    result = converter(result, columns)
    columns = result[0].keys()
    db_cursor.execute('SELECT COUNT(*) FROM pupils')
    count = db_cursor.fetchall()
    pupils_school_results, seasons = graph_and_chart()
    return render_template('home.html', seasons=json.dumps(seasons), data=json.dumps(pupils_school_results), result=result, columns=columns,
                           total_pages=total_pages, filters=filters, pupil_count=count[0][0], current_page=page, filter=True)


@app.route('/search', defaults={'page': 1})
@app.route('/search/<search_input>/<int:page>')
def search(page):
    per_page = 50
    start = (page*per_page) - per_page
    result = []
    columns = []
    if request.method == 'GET':
        search_sentence = request.args.get('search_input')
        print(request.args)
        if search_sentence != '' or search_sentence is not None:
            db_cursor = mysql.connection.cursor()

            query = "SELECT pupils.first_name, pupils.surname, statements.statement FROM pupils INNER JOIN data ON data.pupil_id = pupils.id INNER JOIN statements ON statements.statement_id = data.statement_id WHERE pupils.first_name LIKE '%"+ search_sentence +"%' OR pupils.surname LIKE '%"+ search_sentence +"%' OR pupils.ethnicity LIKE '%"+ search_sentence +"%' OR statements.statement LIKE '%"+ search_sentence +"%'"
            search_query = query
            db_cursor.execute(search_query)
            result = db_cursor.fetchall()
            columns = db_cursor.description
            result = converter(result, columns)
            columns = result[0].keys()
            total_rows = query + " LIMIT 10000"
            db_cursor.execute(total_rows)
            print(search_query)
            print(total_rows)
            total_rows_result = list(db_cursor.fetchall())
            total_pages = math.ceil(len(total_rows_result)/per_page)
    return render_template('search.html', result=result, columns=columns, search_sentence=search_sentence, total_pages=total_pages, current_page=page)


@app.route('/pupil/<id>', defaults={'page': 1})
@app.route('/pupil/<id>/<int:page>')
def details(id, page):
    per_page = 20
    start = (page*per_page) - 20
    db_cursor = mysql.connection.cursor()
    db_cursor.execute('''SELECT pupils.id, pupils.first_name, pupils.surname, pupils.gender, pupils.date_of_birth, 
    pupils.ethnicity, pupils.yearreal, pupils.looked_after_child, pupils.military_family, schools.school_name FROM pupils INNER JOIN schools 
    ON pupils.school_id = schools.school_code WHERE id="''' + id + '''"''')
    pupil_result = db_cursor.fetchall()
    pupil_columns = db_cursor.description
    result = converter(pupil_result, pupil_columns)
    db_cursor.execute('''SELECT data.assessment_term, data.assessment_year, data.score_id, data.subject_id, data.category_id, data.component_id, data.is_target, data.id, data.date_created, data.date_observed, statements.statement FROM data 
        INNER JOIN statements ON data.statement_id=statements.statement_id 
        WHERE pupil_id="''' + id + '''"''')
    extra = list(db_cursor.fetchall())
    total_pages = math.ceil(len(extra)/per_page)
    db_cursor.execute('''SELECT data.assessment_term, data.assessment_year, data.score_id, data.subject_id, data.category_id, data.component_id, data.is_target, data.id, data.date_created, data.date_observed, statements.statement FROM data 
    INNER JOIN statements ON data.statement_id=statements.statement_id 
    WHERE pupil_id="''' + id + '''" LIMIT %s, %s''', (start, per_page))
    extra_result = db_cursor.fetchall()
    extra_columns = db_cursor.description
    extra = converter(extra_result, extra_columns)
    columns = extra[0].keys()
    return render_template('details.html', result=result[0], extra_info=extra, columns=columns, total_pages=total_pages, current_page=page)


if __name__ == '__main__':
    app.run(debug=True)


