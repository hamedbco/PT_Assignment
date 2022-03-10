import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://postgres:123456@postgres:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ViewsConfig:
    #
    UPLOAD_FOLDER = f"{os.getcwd()}/static/uploads"
    #
    ALLOWED_EXTENTIONS = set(
        ['doc', 'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


class MailConfig:
    #
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = "Your Mail"
    MAIL_PASSWORD = "Your Password"
    MAIL_SSL = True
    SENDER = 'ParsTasmim@Company.com'
