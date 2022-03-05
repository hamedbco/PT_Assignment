from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_migrate import Migrate
from sqlalchemy import  ForeignKey, Column, Integer, VARCHAR, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime as dt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:123456@localhost:5432/testy"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session = sessionmaker(bind=db)
session = Session()


class Manufacturer(db.Model):
    __tablename__ = "manufacturers"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    manufacturer_name = Column(VARCHAR(150), nullable=False, unique=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    # modified_at
    updated_at = Column(DateTime, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.manufacturer_name = name


class Type(db.Model):
    __tablename__ = "types"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    type_name = Column(VARCHAR(150), nullable=False, unique=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.type_name = name


class Model(db.Model):
    __tablename__ = "models"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    model_name = Column(VARCHAR(150), nullable=False, unique=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.model_name = name


class Part(db.Model):
    __tablename__ = "parts"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    part_name = Column(VARCHAR(150), nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)
    # RelationShip --> manufacturers Table
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    manufacturer = relationship("Manufacturer", backref="parts")
    # RelationShip To--> types Table
    type_id = Column(Integer, ForeignKey("types.id"))
    types = relationship("Type", backref="parts")
    # RelationShip To--> models Table
    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship("Model", backref="parts")
    # RelationShip To--> files Table
    file_id = Column(Integer, nullable=True, default=None)
    # file_id = Column(Integer, ForeignKey("files.id"))
    # file = relationship("File", backref="parts")

    def __init__(self, name, manufID, typeID, modelID, fileID=None):
        self.part_name = name
        self.manufacturer_id = manufID
        self.type_id = typeID
        self.model_id = modelID
        self.file_id = fileID


class File(db.Model):
    __tablename__ = "files"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    file_name = Column(VARCHAR(200), nullable=False)
    file_extention = Column(VARCHAR(10), nullable=False)
    part_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)


    def __init__(self, name, extention, partID):
        self.file_name = name
        self.file_extension = extention
        self.part_id = partID


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    user_name = Column(VARCHAR(100), nullable=False, unique=True)
    user_email = Column(VARCHAR(120), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)

    def __init__(self, name, email, is_active):
        self.user_name = name
        self.user_email = email
        self.is_active = is_active