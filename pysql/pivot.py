"""
pivot.py
====================================
Pivots a SQL table into a numeric matrix
"""

import numpy as np
import pandas as pd
import os
import pysql.io as io
import pysql.validate as validate



def NullEntries(server, database, table, pivot_column):
    """
    Pivots a table and verifies that each segment has no null entries.


    Template query:
    ----------------------------------
    SELECT      {pivot_column},
                CASE
                    WHEN SUM({column}) > 0 THEN 'FAIL'
                    ELSE 'PASS'
                END AS {column}
    FROM
    (
                SELECT      {pivot-column},
                            CASE
                                WHEN {column} IS NULL THEN 1
                                ELSE 0
                            END AS {column}
                FROM        {table}
    )
    GROUP BY    {pivot_column}
    ----------------------------------
    """

    
    schema_df = io.getTableSchema(server, database, table)
    column_list = schema_df['COLUMN_NAME']


    query = f"SELECT      [{pivot_column}],\n"

    for i, column in enumerate(column_list):
        if(column == pivot_column):
            continue

        query += f"""
                    CASE
                        WHEN SUM([{column}]) > 0 THEN 'TRUE'
                        ELSE 'FALSE'
                    END AS [{column}]"""

        if(i+1 < len(column_list)):
            query += ",\n"


    query += f"""FROM
                    (
                        SELECT      [{pivot_column}],
                """

    for i, column in enumerate(column_list):
        if(column == pivot_column):
            continue

        query += f"""
                    CASE
                        WHEN [{column}] IS NULL THEN 1
                        ELSE 0
                    END AS [{column}]"""

        if(i+1 < len(column_list)):
            query += ",\n"


    query += f"""
                        FROM        {table}
                    ) AS A
                    GROUP BY    [{pivot_column}]
                """


    df = io.executeQuery(server, database, query)
    
    return df



def SumValues(server, database, table, pivot_column):
    """
    Pivots a table and verifies that each segment has no null entries.


    Template query:
    ----------------------------------
    SELECT      {pivot_column},
                SUM({column})
    FROM        {table}
    GROUP BY    {pivot_column}
    ----------------------------------
    """

    schema_df = io.getTableSchema(server, database, table)

    column_df = schema_df.loc[schema_df['DATA_TYPE'].isin(['int', 'float', 'decimal'])]
    column_list = column_df['COLUMN_NAME']


    query = f"SELECT      [{pivot_column}],\n"

    for i, column in enumerate(column_list):
        if(column == pivot_column):
            continue

        query += f"SUM(CAST([{column}] AS FLOAT)) AS [{column}]"

        if(i+1 < len(column_list)):
            query += ",\n"
        else:
            query += "\n"

    query += f"""FROM {table}
            GROUP BY [{pivot_column}]
            """


    df = io.executeQuery(server, database, query)
    df = df.set_index(pivot_column)

    return (df > 0)