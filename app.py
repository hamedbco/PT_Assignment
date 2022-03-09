


import os
import datetime as dt
from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import ForeignKey, Column, Integer, VARCHAR, DateTime, Boolean
from sqlalchemy import func, and_
from config import Configuration, ViewsConfig, MailConfig
from werkzeug.utils import secure_filename
from func import allowedFile, zipFile, getAllFile
from send_mail import sendMail
from seed_db import seeder

app = Flask(__name__)
# app.config.from_object(Configuration)
app.config['SQLALCHEMY_DATABASE_URI'] = Configuration.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Configuration.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session = sessionmaker(bind=db)
session = Session()


###################################################
##################### Model #######################
###################################################
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
        self.file_extention = extention
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


#############################################################
##################### Create Tabels #########################
#############################################################
# db.init_app(app)s
db.drop_all()
db.create_all()
db.session.commit()


#############################################################
##################### HardCode Data #########################
#############################################################



seeder = seeder()


#############################################################
##################### Views #########################
#############################################################

@app.route('/')
def get_root():
    return render_template('index.html')


@app.route('/api/docs/')
def get_docs():
    return render_template('index.html')


# Get and Show List Of Automobile Parts
@app.route('/listofparts')
def get_api():

    automobileName = request.args.get('automobile_name')
    query = db.session.query(Manufacturer.id).filter(func.lower(
        Manufacturer.manufacturer_name) == automobileName.lower()).first()
    if query:
        print(query)
        # print(query)
        listOfParts = db.session.query(Part.part_name).filter(
            Part.manufacturer_id == int(query[0])).all()
        listDict = {}
        listDict.update({str(idx+1): str(lop[0])
                        for idx, lop in enumerate(listOfParts)})
        return jsonify(listDict)

    else:
        resp = jsonify({'Message': 'AutoMobile Not Found!'})
        resp.status_code = 400
        return resp


# Upload File
@app.route('/uploads', methods=["GET", "POST"])
def uploads_file():
    partName = request.args.get('partname')

    query = db.session.query(Part.id).filter(
        func.lower(Part.part_name) == partName.lower()).first()
    if not query:
        resp = jsonify({'Error': 'Part Not Found!'})
        resp.status_code = 404
        return resp

    partId = query[0]

    if 'file' not in request.files:
        resp = jsonify({'Message': 'No Part File in the REQUEST'})
        resp.status_code = 400
        return resp

    getFilesList = request.files.getlist('file')

    errors = {}
    success = False

    # Get all Files In UPLOAD_FOLDER
    allFiles = next(os.walk(ViewsConfig.UPLOAD_FOLDER))[2]

    for file in getFilesList:
        fileEXT = allowedFile(file)

        if f"{partId}-{file.filename}" in allFiles:
            resp = jsonify({'Message': 'File Exist!'})
            resp.status_code = 400
            return resp
        else:
            if file and allowedFile(file.filename) and allowedFile(fileEXT.filename) in ViewsConfig.ALLOWED_EXTENTIONS:
                secureFileName = secure_filename(file.filename)
                file.save(os.path.join(
                    f"{ViewsConfig.UPLOAD_FOLDER}/"f"{partId}-{secureFileName}"))
                success = True
            else:
                errors[file.filename] = 'File Type is NOT Allowed'

            if success and errors:
                errors['message'] = 'Error File or File Type '
                resp = jsonify(errors)
                resp.status_code = 500
                return resp

            if success:
                resp = jsonify({'Message': 'File(s) successfully Upload.'})
                resp.status_code = 201

                # Get AutoMobile  Model , Part Name and File Link to Send to Users With Email
                typeNameQuery = db.session.query(Model.model_name).filter(
                    and_(Part.id == partId, Model.id == Part.type_id)).first()
                partNameQuery = db.session.query(
                    Part.part_name).filter(Part.id == partId).first()
                partLink = f"http://localhost:5000/static/uploads/{partId}-{secureFileName}"
                #
                getUserEmailQuery = db.session.query(
                    User.user_email).filter(User.is_active == 'true').all()

                sendMail(getUserEmailQuery, typeNameQuery,
                         partNameQuery, partLink)

                # insert
                try:
                    #
                    db.session.add(File(
                        name=f'{partId}-{secureFileName}', extention=f'{allowedFile(file.filename)}', partID=partId))
                    # db.session.add(
                    #     File(extention=f'{allowedFile(file.filename)}'))
                    # db.session.add(File(partID=partId))
                    db.session.commit()

                    getFileId = db.session.query(File.id).filter(
                        File.part_id == Part.id).first()
                    # for fileID in getFileId:
                    Part.file_id = getFileId
                    db.session.commit()

                except Exception as e:
                    db.session.rollback()
                    print(e)
                #
                return resp

            else:  # Not success
                resp = jsonify(errors)
                resp.status_code = 500
                return resp


# Download Files View
@app.route('/download-single', methods=['GET'])
def download_single():
    #
    partName = request.args.get('partname')
    query = db.session.query(Part.id).filter(func.lower(
        Part.part_name) == partName.lower()).first()
    #
    if not query:
        resp = jsonify({'Error': 'Part Not Found!'})
        resp.status_code = 404
        return resp

    #
    partId = query[0]

    #
    listFiles = []

    #
    allFiles = next(os.walk(ViewsConfig.UPLOAD_FOLDER))[2]
    #
    for file in allFiles:
        #
        if int(file.split('-')[0]) == partId:
            listFiles.append(f"http://localhost:5000/static/uploads/{file}")
    #
    if listFiles:
        resp = jsonify(listFiles)
        resp.status_code = 201
        return resp
    #
    else:
        resp = jsonify({'Message': 'No File(s) Exists!'})
        resp.status_code = 400
        return resp


# Download All File of Part View
@app.route('/download-all', methods=['GET'])
def download_all():
    #
    partName = request.args.get('partname')
    # namePart = db.session.query(Part.part_name).first()[0]
    query = db.session.query(Part.id).filter(func.lower(
        Part.part_name) == partName.lower()).first()

    if not query:
        resp = jsonify({'Error': 'Part Name Not Found!'})
        resp.status_code = 404
        return resp

    partId = query[0]

    #
    listPartFiles = []
    # success = False

    # path = f"{UPLOAD_FOLDER}"
    allFiles = next(os.walk(ViewsConfig.UPLOAD_FOLDER))[2]
    #
    for file in allFiles:
        if int(file.split('-')[0]) == int(partId) and allowedFile(file) in (ViewsConfig.ALLOWED_EXTENTIONS):
            listPartFiles.append(file)
    #
    if listPartFiles:
        #

        zipPartFileName = zipFile(partName, listPartFiles)
        #
        res = [
            f"http://localhost:5000/static/uploads/PartFiles/{zipPartFileName}"]
        resp = jsonify(res)
        resp.status_code = 201
        return resp

    else:
        #
        resp = jsonify({'Message': 'No Exists File(s)!'})
        resp.status_code = 400
        return resp


# Download All File of AutoMobile
@app.route('/download-all-automobiles', methods=['GET'])
def download_all_automobile():
    #
    modelName = request.args.get('modelname')
    query = db.session.query(Model.id).filter(func.lower(
        Model.model_name) == modelName.lower()).first()

    #
    if not query:
        resp = jsonify({'Error': 'AutoMobile Model Not Found!'})
        resp.status_code = 404
        return resp
    #
    modelId = int(query[0])
    #
    modelName = modelName.replace(' ', '')

    #
    allPartIdQuery = db.session.query(Part.id).filter(
        Part.model_id == modelId).all()
    #
    if not allPartIdQuery:
        resp = jsonify({'Error': 'AutoMobile Model Has Not Any File!'})
        resp.status_code = 404
        return resp

    listModelFiles = []

    allFiles = getAllFile()

    for PIQ in allPartIdQuery:
        #
        for file in allFiles:
            #
            if int(file.split('-')[0]) == int(PIQ[0]) and allowedFile(file) in (ViewsConfig.ALLOWED_EXTENTIONS):
                listModelFiles.append(file)

    if listModelFiles:
        #

        #
        zipFileName = zipFile(modelName, listModelFiles)

        res = [
            f"http://localhost:5000/static/uploads/AutoMobileFiles/{zipFileName}"]
        resp = jsonify(res)
        resp.status_code = 201
        return resp

    else:
        resp = jsonify({'Message': 'No Exists File(s)!'})
        resp.status_code = 400
        return resp


if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", debug=True)
    # app.run(debug=True)
