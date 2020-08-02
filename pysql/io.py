"""
io.py
====================================
SQL IO module
"""

import time
import pandas as pd
import numpy as np
import pyodbc
import sqlalchemy


def getTableSchema(server, database, table):
    query = f"""
                SELECT      COLUMN_NAME,
                            IS_NULLABLE,
                            DATA_TYPE,
                            CHARACTER_MAXIMUM_LENGTH
                FROM        INFORMATION_SCHEMA.COLUMNS
                WHERE       TABLE_NAME = N'{table}'
            """

    df = executeQuery(server, database, query)

    return df



def executeQuery(server, database, query, print_feedback=False):
    """
    Read table from SQL query, using Pyodbc.

    :param server: Server name
    :type server: str
    :param database: Database name
    :type database: str
    :param query: SQL query
    :type query: str
    """
    if(print_feedback):
        print(query)

    # Create the connection
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';Trusted_Connection=yes')

    # Read in query
    start = time.time()
    input_df = pd.io.sql.read_sql(query, conn)
    end = time.time()


    # Print descriptive statistics
    print("Read time :\t", int(end-start), "s")

    # Close connection
    conn.close()

    return input_df



def executeQueryFromFile(server, database, file_name):
    """
    Excutes a query from a file.

    :param server: Server name
    :type server: str
    :param database: Database name
    :type database: str
    :param file_name: SQL file
    :type query: str
    """

    # Create the connection
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';Trusted_Connection=yes')

    # read query into string
    with open(file_name) as file:
        query = file.read()

    # Read in query
    start = time.time()
    df = pd.io.sql.read_sql(query, conn)
    end = time.time()

    # Close connection
    conn.close()

    # Print descriptive statistics
    print("\nRead time :\t", int(end-start), "s")
    rows = df.shape[0]
    cols = df.shape[1]

    print(f"Rows : \t\t {rows:,d}")
    print(f"Columns : \t {cols:,d}")

    return df


def writeDfToSQL(df, server, database, table, driver='SQL+Server', chunksize=200):
    """
    Wrapper for pd.to_sql()

    :param df: table
    :type df: pd.DataFrame
    :param server: Server name
    :type server: str
    :param database: Database name
    :type database: str
    :param table_name: Database name
    :type table_name: str
    """

    # initialize SQL engine
    if(True):
        connection_str = 'mssql+pyodbc://' + server + '/' + database + '?driver=' + driver
        engine = sqlalchemy.create_engine(connection_str)
    else:
        params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + db)
        engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    start = time.time()

    # table name needs to be lower case
    table_name = table_name.lower()

    df.to_sql(table_name, con=engine,
                      if_exists='replace', index=False,
                      method='multi', chunksize=chunksize)


    end = time.time()

    # diagnostic timing
    print("Write time :\t", int(end - start), " s")