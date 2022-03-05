


import os
from config import ViewsConfig
import zipfile
import datetime as dt


def allowedFile(filename):
    #
    if '.' in filename:
        #
        return filename.rsplit('.', 1)[1].lower()
    #
    return filename

def getAllFile():
    return next(os.walk(ViewsConfig.UPLOAD_FOLDER))[2]


def zipFile(Name, listFiles):
    generateTime = int(dt.datetime.timestamp(dt.datetime.now()))
    with zipfile.ZipFile(f"{ViewsConfig.UPLOAD_FOLDER}/PartFiles/{Name}-{generateTime}.zip", "w") as myzip:
        for file in listFiles:
            myzip.write(f"{ViewsConfig.UPLOAD_FOLDER}/" + file, arcname=file)
    #
    return f'{Name}-{generateTime}.zip'