from flask import Blueprint
from .utils.response import HTTPResponse, HTTPError
from .utils.request import Request

__all__ = ['predictApp_api']

predictApp_api = Blueprint('predictApp_api', __name__)

@predict_api.route('/predict', methods=['POST'])
@Request.files('files')
def upload_files(files):
    ''' save file '''
    try:
        pass
    except:
        pass
        return HTTPError(f'Failed!')
    return HTTPResponse(f'success!')