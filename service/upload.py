import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/data/willy/NLP/audios"

class Upload_Files():
    def __init__(self, file):
        self.file = file
        
    def save_file(self):
        audio_filename = secure_filename(self.file.filename) + '.wav' #.mp3?
        self.file.save(os.path.join(UPLOAD_FOLDER, audio_filename))
        # self.file.save(os.path.join(UPLOAD_FOLDER,'temp.wav'))