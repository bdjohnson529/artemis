from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import pandas as pd
import numpy as np

import sys
sys.path.append('..')
import pysql.io as io
import pysql.alert as alert
import pysql.pivot as pivot
import pysql.validate as validate


bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    df = pd.util.testing.makeDataFrame()
    html = df.to_html()


    return render_template('dashboard/index.html', table=html)



@bp.route('/pivot', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':

        server = request.form['server']
        database = request.form['database']
        table = request.form['table']

        if not server:
            error = 'Server is required.'
        elif not database:
            error = 'Database is required.'
        elif not table:
            error = 'Table is required.'

        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')
