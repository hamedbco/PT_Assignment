import os
from dotenv import load_dotenv 

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Configuration:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:123456@localhost:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ViewsConfig:
    #
    # UPLOAD_FOLDER = f"{os.getcwd()}/static/uploads"
    UPLOAD_FOLDER = f"{os.getcwd()}/static/uploads"
    #
    AllOWED_EXTENTIONS = set(
        ['doc', 'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])