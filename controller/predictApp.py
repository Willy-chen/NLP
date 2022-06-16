import os
from flask import Blueprint, request
from service.predict import Predict
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
        return HTTPError(f'Failed!', 402)
    return HTTPResponse(f'success!')

@predictApp_api.route('/debug', methods=['POST'])
def debug():
    print("debug received!")
    return HTTPResponse(f'success!')