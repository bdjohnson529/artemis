# Artemis

Artemis empowers unit testing for data engineering teams.


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
