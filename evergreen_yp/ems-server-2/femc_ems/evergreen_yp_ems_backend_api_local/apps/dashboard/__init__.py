from __future__ import absolute_import

import logging
import os
import sys

from flask_cors import CORS

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))

from apps.dashboard.constant import ConfigConstant
from utility.config_parser import convenient_parser
from utility.token_module import TokenModule
from distutils.util import strtobool

from flask import Flask
from flask_session import Session
from apps.dashboard.constant import PROJECT_ROOT


config = convenient_parser(project_root=PROJECT_ROOT,
                           config_file_path='configs/api_config.yml')

log_path = config[ConfigConstant.APP.value][ConfigConstant.LOG_PATH.value]
logging_level = logging.INFO
single_login = strtobool(config[ConfigConstant.APP.value].get(ConfigConstant.SINGLE_LOGIN.value, 'False'))

token_module = TokenModule(config)

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)
if not os.path.exists(log_path):
    os.mkdir(log_path)

version = os.getenv('VERSION', 'v1')
if version == 'v1':
    import api_v1 as api_version
else:
    raise NotImplementedError('API version is not v1')


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(
        api_version.bp, url_prefix="/api/{version}".format(version=version)
    )
    return app


if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = os.getenv('PORT', 5000)

    use_ssl = int(config[ConfigConstant.APP.value][ConfigConstant.USE_SSL.value])
    if use_ssl:
        ssl_path = config[ConfigConstant.APP.value][ConfigConstant.SSL_PATH.value]
        create_app().run(
            debug=False,
            host=host,
            port=port,
            use_reloader=False,
            ssl_context=(os.path.join(ssl_path, 'fullchain.crt'), os.path.join(ssl_path, 'privkey.key'))
        )
    else:
        create_app().run(
            debug=False,
            host=host,
            port=port,
            use_reloader=False,
        )
