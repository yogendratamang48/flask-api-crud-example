## Flask CRUD App
- flask cli for db scripts
- implements `jwt token` for securing APIS.
- implements `marshmallow` for Object serializing.
- `Flask-mail` for forgot password feature. [Using https://mailtrap.io]
- `flask-sqlalchemy` as ORM.

### Install requirements

> `pip install -r requirements.txt`

### Update environment file

- create `.envfile` inside `src` folder.

### Run application

- cd into `src` and run
- `python app.py`

## Database Scripts

- cd into `src` and run following commands

### Create Database

> `flask create_db`

### Seed Database

> `flask db_seed`

### Drop Database

> `flask drop_db`
