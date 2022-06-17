import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/data/willy/NLP/audios"

__all__ = ['Upload_Files']

class Upload_Files():
    def __init__(self, file):
        self.file = file
        self.filename = secure_filename(self.file.filename) + '.wav'

        
    def save_file(self):
        self.file.save(os.path.join(UPLOAD_FOLDER, self.filename))
        # self.file.save(os.path.join(UPLOAD_FOLDER,'temp.wav'))