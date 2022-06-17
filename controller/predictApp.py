import os
from flask import Blueprint
from service.predict import Predict
from service.STT import STT
from service.upload import Upload_Files
from .utils.response import HTTPResponse, HTTPError
from .utils.request import Request

__all__ = ['predictApp_api']

predictApp_api = Blueprint('predictApp_api', __name__)

@predictApp_api.route('/upload', methods=['POST'])
@Request.files("audio")
def upload_files(audio):
    ''' save file '''
    try:
        upload = Upload_Files(audio)
        upload.save_file()
    except:
        return HTTPError(f'Failed to save audio files!', 403)
    
    try:
        rec = STT("eng", upload.filename)
        text = rec.recognize()
    except:
        return HTTPError(f'Failed to transcript!', 403)        
    return HTTPResponse(f'success!', data={"text":text})

@predictApp_api.route('/predict', methods=['POST'])
@Request.form('transcript')
def predict(transcript):
    ''' save file '''
    try:
        # generate response
        text = "Bot response"
        pass
    except:
        return HTTPError(f'Failed to generate response!', 403)
    return HTTPResponse(f'success!', data={"text":text})

@predictApp_api.route('/debug', methods=['POST'])
def debug():
    print("debug received!")
    return HTTPResponse(f'success!')