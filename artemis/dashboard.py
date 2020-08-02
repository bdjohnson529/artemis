from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

import pandas as pd
import numpy as np

import sys
sys.path.append('..')
import pysql.io
import pysql.alert
import pysql.pivot
import pysql.validate
import pysql.render


bp = Blueprint('dashboard', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():

    html = "Select a table."
    server = ""
    database = ""
    table = ""

    if request.method == 'POST':
        if not server:
            error = 'Server is required.'
        elif not database:
            error = 'Database is required.'
        elif not table:
            error = 'Table is required.'
    
        session['server'] = request.form['server']
        session['database'] = request.form['database']
        session['table'] = request.form['table']

        server = request.form['server']
        database = request.form['database']
        table = request.form['table']



        try:
            # find faster way to verify table exists
            df= pysql.io.getTableSchema(server, database, table)
            html = df.to_html()

            f = open('test_again_again.html', 'w')
            f.write(html)

            return redirect(url_for('dashboard.schema'))
        except:
            error = "Could not retrieve"


    return render_template('dashboard/select.html')



@bp.route('/schema', methods=('GET', 'POST'))
def schema():
    html = ""

    server = session['server']
    database = session['database']
    table = session['table']


    try:
        df= pysql.io.getTableSchema(server, database, table)
        df['schema'] = df.apply(lambda x: "<a href=\"/pivot?server=" + server + "&database=" + database + "&table=" + table + "&column=" + x['COLUMN_NAME'] + "\">Pivot</a>", axis=1)

        html = df.to_html(escape=False)

        f = open('test_again_again.html', 'w')
        f.write(html)

        return render_template('dashboard/schema.html', server=server, database=database, table=table, html=html)

    except:
        html = "Could not retrieve"


    return render_template('dashboard/schema.html', server=server, database=database, table=table, html=html)



@bp.route('/pivot', methods=('GET', 'POST'))
def pivot():
    server = request.args.get('server')
    database = request.args.get('database')
    table = request.args.get('table')
    column = request.args.get('column')


    df = pysql.pivot.SumValues(server, database, table, column)

    html = df.T.style.format('<button name="df">{}</button>').render()

    f = open('test.html', 'w')
    f.write(html)

    html_fmt = pysql.render.formatTable(html, "yellow")
    body_html = "<h2>Sum Greater than Zero</h2>" + html_fmt




    return render_template('dashboard/pivot.html', html=body_html)