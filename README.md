# Artemis

Artemis empowers unit testing for SQL Server databases.


## Setup
Instructions are provided for Windows CMD. Commands should be run from the base directory of the repository.

Set up the virtual environment:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run the application:
```
venv\Scripts\activate
set FLASK_APP=artemis
set FLASK_ENV=development
flask init-db
flask run
```

To run on a specific port:
```
flask run -h localhost -p 3000
```


## Database
Artemis uses a SQLite database to store pivots which are used to generate the dashboard. The database is instantiated by the command `flask init-db`. SQLite files are stored in the folder `instance`.

To access the database using the command line, use the SQLite command line tool. Download the [Windows command-line tools](https://www.sqlite.org/2020/sqlite-tools-win32-x86-3320300.zip) from the [official SQLite webpage](https://www.sqlite.org/download.html). 
1. Create a new folder named `C:\sqlite`.
2. Extract the ZIP folder, and move the `.exe` files to the folder `C:\sqlite`.
3. Add `C:\sqlite` to your Windows PATH. The PATH variables are set in the `Environment Variables` window.
4. Open the database file using the command `sqlite3 artemis.sqlite`.

## Contributing
After installing new packages to the venv, save the requirements to `requirements.txt` so that your dependencies are added to the repository.
```
python -m pip freeze > requirements.txt
```

To delete the sqlite database, delete the folder `instance`. To reinstantiate a new database:
```
flask init-db
```


## Common Issues
`Access is denied` can indicate the virtual environment is not activated.
