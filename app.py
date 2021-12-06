from flask import Flask
from controller import *
from config.config import get_yaml_config

app = Flask(__name__)

# set app config
# app_config = get_yaml_config('app_config')
# app.config.from_mapping(app_config)

api2prefix = [
    # (xxx_api, '/xxxApp'),
]
for api, prefix in api2prefix:
    app.register_blueprint(api, url_prefix=prefix)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)