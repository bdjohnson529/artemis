from flask import Blueprint, request
from .db import get_db


api = Blueprint('api', __name__)


@api.route('/retrieveData', methods=('GET', 'POST'))
def get():
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


@api.route('/sendData', methods=('GET', 'POST'))
def update():
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