from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

import pandas as pd
import numpy as np

from artemis.db import get_db

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
            df['schema'] = df.apply(lambda x: "<a href=\"/pivot?server=" + server + "&database=" + database + "&table=" + table + "&column=" + x['COLUMN_NAME'] + "\">Pivot</a>", axis=1)
            html = df.to_html(escape=False)

            return render_template('dashboard/select.html', html=html)
        except:
            error = "Could not retrieve"


    return render_template('dashboard/select.html', html=html)



@bp.route('/pivot', methods=('GET', 'POST'))
def pivot():
    server = request.args.get('server')
    database = request.args.get('database')
    table = request.args.get('table')
    column = request.args.get('column')

    error = None

    try:
        df = pysql.pivot.SumValues(server, database, table, column)
        transposed_df = df.stack().reset_index().rename(columns={'Client':'pivot_column','level_1': 'value_column', 0: 'sumGreaterThanZero'})
        transposed_df['mask'] = 0
        transposed_df = transposed_df[['pivot_column', 'value_column', 'mask', 'sumGreaterThanZero']]

        records = list(transposed_df.to_records(index=False))
        str_records = [str(x) for x in records]
        insert_vals = ",".join(str_records)
        print(insert_vals)
    except:
        error = 'Could not pivot table.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            "INSERT INTO pivot (pivot_column, value_column, mask, sumGreaterThanZero) VALUES " + insert_vals
        )
        db.commit()

        return redirect(url_for('dashboard.display'))



    return render_template('dashboard/select.html', html=html)



@bp.route('/display', methods=('GET', 'POST'))
def display():
    db = get_db()
    rows = db.execute(
        """SELECT   pivot_column,
                    value_column,
                    mask,
                    sumGreaterThanZero
        FROM pivot"""
    ).fetchall()

    vals = [tuple(r) for r in rows]

    transposed_df = pd.DataFrame(vals, columns=['pivot_column', 'value_column', 'mask', 'sumGreaterThanZero'])

    transposed_df.to_csv('transposed.csv')

    value_df = transposed_df.pivot(index='pivot_column', columns='value_column', values='sumGreaterThanZero')
    value_df.index.name = None

    mask_df = transposed_df.pivot(index='pivot_column', columns='value_column', values='mask')
    mask_df.index.name = None
    mask_df['ApplicationID'] = 1


    compare_df = value_df - 2 * mask_df
    compare_df[compare_df < 0] = -1
    compare_df = compare_df.replace({1: True, 0: False, -1: 'Masked'})


    mask_df.to_csv("mask.csv")
    compare_df.to_csv("compare.csv")


    # render values
    html = compare_df.T.style.format('<button name="df">{}</button>').render()
    html_fmt = pysql.render.styleButton(html)
    body_html = "<h2>Sum Greater than Zero</h2>" + html_fmt


    f = open('test.html', 'w')
    f.write(html_fmt)

    return render_template('dashboard/display.html', html=body_html)


@bp.route('/display/edit_mask', methods=('GET', 'POST'))
def edit_mask():
    if request.method == 'POST':
        pid = request.form['pid']

        print(pid)

    return "hello world"