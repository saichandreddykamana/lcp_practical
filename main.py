from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import datetime
import math

app = Flask(__name__, template_folder='templates')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'lcp_practical'

mysql = MySQL(app)


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
    per_page = 10
    start = (page * per_page) - 10
    db_cursor = mysql.connection.cursor()
    db_cursor.execute("SELECT pupils.id, pupils.first_name, pupils.surname, pupils.gender, pupils.date_of_birth, pupils.ethnicity, schools.school_name FROM pupils INNER JOIN schools ON pupils.school_id = schools.school_code LIMIT %s, %s", (start , per_page))
    result = db_cursor.fetchall()
    columns = db_cursor.description
    result = converter(result, columns)
    columns = result[0].keys()
    db_cursor.execute('SELECT COUNT(*) FROM pupils')
    count = db_cursor.fetchall()
    db_cursor.execute('SELECT COUNT(*) FROM schools')
    school_count = db_cursor.fetchall()
    db_cursor.execute('SELECT COUNT(*) FROM statements')
    statement_count = db_cursor.fetchall()
    return render_template('home.html', result=result, columns=columns, total_pages=math.ceil((list(count)[0][0])/per_page), pupil_count=count[0][0], school_count=school_count[0][0], statement_count=statement_count[0][0])


@app.route('/filter', defaults={'page': 1})
@app.route('/filter/<int:page>')
def filter(page):
    per_page = 10
    start = (page * per_page) - 10
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
    db_cursor.execute('SELECT COUNT(*) FROM schools')
    school_count = db_cursor.fetchall()
    db_cursor.execute('SELECT COUNT(*) FROM statements')
    statement_count = db_cursor.fetchall()
    return render_template('home.html', result=result, columns=columns,
                           total_pages=total_pages, filters=filters, pupil_count=count[0][0], school_count=school_count[0][0], statement_count=statement_count[0][0])


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


@app.route('/search')
def search():
    return render_template('search.html')


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
    return render_template('details.html', result=result[0], extra_info=extra, columns=columns, total_pages=total_pages)


if __name__ == '__main__':
    app.run(debug=True)


