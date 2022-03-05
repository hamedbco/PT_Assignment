
import os
import datetime as dt
from . import app, db, session
from models import Manufacturer, Type, Model, Part, File, User
from flask import Flask, jsonify, render_template, request
from sqlalchemy import func, and_
from werkzeug.utils import secure_filename
from ..config import ViewsConfig
from func import allowedFile, zipFile, getAllFile
from send_mail import sendMail
import zipfile



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
    print(request.method)
    print(request.args.get('partname'))
    print(request.values.get('partname'))
    partName = request.args.get('partname')

    query = session.query(Part.id).filter(
        func.lower(Part.part_name) == partName.lower()).first()
    print(query)
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
        if (f"{partId}-{str(file.filename)}") in allFiles:
            resp = jsonify({'Message': 'File Exist!'})
            resp.status_code = 400
            return resp
        else:
            if file and allowedFile(file.filename):
                secureFileName = secure_filename(file.filename)
                file.save(os.path.join(ViewsConfig.UPLOAD_FOLDER, '/',
                                       f"{partId}-{secureFileName}"))
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
                typeNameQuery = db.session.query(Model.type_name).filter(
                    and_(Part.id == partId, Model.id == Part.type_id)).first()
                partNameQuery = db.session.query(
                    Part.part_name).filter(Part.id == partId).first()
                partLink = f"http://localhost:5000/static/uploads/{partId}-{secureFileName}"
                #
                getUserEmailQuery = db.session.query(
                    User.email).filter(User.is_active == 'true').all()
                sendMail(getUserEmailQuery, typeNameQuery,
                         partNameQuery, partLink)

                # insert
                try:
                    #
                    db.session.add(
                        File(file_name=f'{partId}-{secureFileName}'))
                    db.session.add(
                        File(file_extention=f'{allowedFile(file.filename)}'))
                    db.session.add(File(part_id=partId))
                    db.session.commit()

                    getFileId = db.session.query(File.id).filter(
                        File.part_id == Part.id).first()
                    # for fileID in getFileId:
                    db.session.add(Part(file_id=getFileId[0]))
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

    # app.secret_key = "parstasmim-company"
    # UPLOAD_FOLDER = f"{os.getcwd()}/static/uploads"
    # print(UPLOAD_FOLDER)
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #
    listFiles = []
    # success = False

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
        if int(file.split('-')[0]) == int(partId) and allowedFile(file) in ViewsConfig.AllOWED_EXTENTIONS:
            listPartFiles.append(file)
    #
    if listPartFiles:
        #
        # generateTime = int(dt.datetime.timestamp(dt.datetime.now()))
        #
        # os.makedirs(f"{ViewsConfig.UPLOAD_FOLDER}/PartFiles", exist_ok=True)
        #
        zipPartFileName = zipFile(listPartFiles)
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
            if int(file.split('-')[0]) == int(PIQ[0]) and allowedFile(file) in ViewsConfig.AllOWED_EXTENTIONS:
                listModelFiles.append(file)

    if listModelFiles:
        #
        # generateTime = int(dt.datetime.timestamp(dt.datetime.now()))
        #
        # os.makedirs(f"{ViewsConfig.UPLOAD_FOLDER}/PartFiles", exist_ok=True)
        #
        zipFileName = zipFile(listModelFiles)

        res = [
            f"http://localhost:5000/static/uploads/AutoMobileFiles/{zipFileName}"]
        resp = jsonify(res)
        resp.status_code = 201
        return resp

    else:
        resp = jsonify({'Message': 'No Exists File(s)!'})
        resp.status_code = 400
        return resp
