from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

import re
import json
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
            # convert to native flask
            df['schema'] = df.apply(lambda x: "<a href=\"/dashboard/create?server=" + server + "&database=" + database + "&table=" + table + "&column=" + x['COLUMN_NAME'] + "\">Pivot</a>", axis=1)
            html = df.to_html(escape=False)

            return render_template('dashboard/index.html', html=html)
        except:
            error = "Could not retrieve"


    return render_template('dashboard/index.html', html=html)



@bp.route('/dashboard/create', methods=('GET', 'POST'))
def create():

    server = request.args.get('server')
    database = request.args.get('database')
    table = request.args.get('table')
    column = request.args.get('column')

    print(server)
    print(database)
    print(table)
    print(column)

    error = None

    try:
        df = pysql.pivot.SumValues(server, database, table, column).T

        tform_df = pysql.pivot.StackDataFrame(df)
        tform_df = tform_df.rename(columns={'Value': 'SumGreaterThanZero'})
        tform_df['Mask'] = 0
        tform_df = tform_df[['Indices', 'Row_Name', 'Column_Name', 'Mask', 'SumGreaterThanZero']]
        

        # convert dataframe to list of tuples
        records = list(tform_df.to_records(index=False))
        str_records = [str(x) for x in records]
        insert_vals = ",".join(str_records)

        f = open('temp/insert.txt', 'w')
        f.write(insert_vals)
    except:
        error = 'Could not pivot table.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            f"""INSERT INTO pivot (Indices, 
                                Row_Name, 
                                Column_Name, 
                                Mask, 
                                SumGreaterThanZero)
                VALUES {insert_vals}
            """
        )
        db.commit()

        return redirect(url_for('dashboard.display'))


    return render_template('dashboard/index.html')



@bp.route('/display', methods=('GET', 'POST'))
def display():
    db = get_db()
    rows = db.execute(
        """SELECT   Row_Name,
                    Column_Name,
                    Mask,
                    SumGreaterThanZero
        FROM pivot"""
    ).fetchall()

    # create df from sqlite data
    vals = [tuple(r) for r in rows]
    transposed_df = pd.DataFrame(vals, columns=['Row_Name', 'Column_Name', 'Mask', 'SumGreaterThanZero'])

    value_df = transposed_df.pivot(index='Row_Name', columns='Column_Name', values='SumGreaterThanZero')
    value_df.index.name = None

    mask_df = transposed_df.pivot(index='Row_Name', columns='Column_Name', values='Mask')
    mask_df.index.name = None


    # apply mask
    compare_df = value_df - 2 * mask_df
    compare_df[compare_df < 0] = -1
    compare_df = compare_df.replace({1: True, 0: False, -1: 'Masked'})


    # render values
    html = compare_df.style.format('<button class="button-clickable">{}</button>').render()
    html_fmt = pysql.render.styleButton(html)
    body_html = "<h2>Sum Greater than Zero</h2>" + html_fmt


    f = open("temp/test.html", 'w')
    f.write(html_fmt)

    return render_template('dashboard/display.html', html=body_html)


@bp.route('/display/toggle_mask', methods=('GET', 'POST'))
def toggle_mask():
    if request.method == 'POST':
        pid = request.form['pid']

        print(pid)

        match = re.search(r"row\d+_col\d+", pid)
        val = match.group()
        arr = val.split('_')
        row = arr[0][3:]
        col = arr[1][3:]
        indices = f"({row}, {col})"

        print(indices)


        db = get_db()
        db.execute(
            f"""UPDATE pivot
                SET     mask = 1 - mask
                WHERE   indices = \"{indices}\"
            """
        )
        db.commit()

    return "success"


@bp.route('/display/retrieveData', methods=('GET', 'POST'))
def retrieveData():
    """
    Retrieves data from pivot table.
    """
    if request.method == 'POST':
        pid = request.form['pid']

        match = re.search(r"row\d+_col\d+", pid)
        val = match.group()
        arr = val.split('_')
        row = arr[0][3:]
        col = arr[1][3:]
        indices = f"({row}, {col})"



        db = get_db()
        rows = db.execute(
            f"""SELECT  Row_Name,
                        Column_Name,
                        Mask,
                        Notes
                FROM    pivot
                WHERE   indices = \"{indices}\"
            """
        ).fetchall()

        vals = [tuple(r) for r in rows]

        if(len(vals) > 1):
            return "Invalid API call."

        row_name = vals[0][0]
        column_name = vals[0][1]
        mask = vals[0][2]

        notes = ""
        if vals[0][3] is not "None":
            notes = vals[0][3]


        resp = {'Indices': indices,
                'Client': column_name,
                'Column': row_name,
                'Mask': mask,
                'Notes': notes}

    return json.dumps(resp)


@bp.route('/display/sendData', methods=('GET', 'POST'))
def sendData():
    """
    Sends data to pivot table.
    """
    if request.method == 'POST':
        indices = request.form['indices']
        notes = request.form['notes']
        mask = request.form['mask']


        db = get_db()
        rows = db.execute(
            f"""UPDATE  pivot
                SET     Mask = \"{mask}\",
                        Notes = \"{notes}\"
                WHERE   indices = \"{indices}\"
            """
        )
        db.commit()


    return "success"