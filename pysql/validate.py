"""
validate.py
====================================
Validations on a SQL query
"""

import numpy as np
import pandas as pd
import pysql.io as io



def expectNoNullEntries(server, database, table, column):
    """
    Expect no null entries in a table.
    """

    query = f"""SELECT  TOP 100 [{column}]
                FROM    [{table}]
                WHERE   [{column}] IS NULL
    """

    df = io.executeQuery(server, database, query)

    if(df.shape[0] == 0):
        return 'PASS'
    else:
        return 'FAIL'


def expectGreaterThanZero(df, mask):
    """
    Expect each value in a matrix to be greater than zero
    """

    srs_list = []

    # vectorize this
    for key, val in mask.items():
        srs = pd.Series(val).rename('Masked Column').to_frame().set_index('Masked Column')
        srs[key] = True
        srs_list.append(srs)


    masked_df = pd.concat(srs_list, axis=1).fillna(False).T


    # window the pivot to the columns, indices in mask_df
    col_list = masked_df.columns.tolist()
    ix_list = masked_df.index

    windowed_df = df.loc[ix_list][col_list]
    failed_df = ~(windowed_df > 0)


    # failed_df AND masked_df yields the cells which failed testing
    test_df = np.logical_and(failed_df, masked_df)
    test = test_df.sum().sum()


    # select only rows, columns with failed value
    cols = test_df.sum()
    rows = test_df.sum(axis=1)

    failed_cols = cols[cols > 0].index.tolist()
    failed_rows = rows[rows > 0].index.tolist()


    failed_df = test_df.loc[failed_rows][failed_cols].replace({True: 'FAIL', False: 'PASS'})



    if(test == 0):
        print("Tests passed")
        return False, failed_df
    else:
        print("Tests failed")
        return True, failed_df