import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_migrate import Migrate
from apps.models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:123456@localhost:5432/testy"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session = sessionmaker(bind=db)
session = Session()
