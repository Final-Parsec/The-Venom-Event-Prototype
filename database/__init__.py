from flask.ext.sqlalchemy import SQLAlchemy

db = None
current_app = None
g = None


def init_database(app_name, global_var):
    global db, current_app, g
    g = global_var
    current_app = app_name
    db = SQLAlchemy(app_name)