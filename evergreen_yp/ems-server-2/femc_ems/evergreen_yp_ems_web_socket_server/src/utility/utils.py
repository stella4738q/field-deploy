import json
import os
import numpy as np

from ..constants.foler_and_file_const import FolderAndFileConst as FileConst


def check_file_exist(logger, filepath):
    if not os.path.isfile(filepath):
        logger.error(f'{filepath} is not found')
        raise FileNotFoundError


class SystemFolders:

    @staticmethod
    def get_project_root():
        current_cwd = os.getcwd()
        cwd = current_cwd
        while '.root' not in os.listdir():
            os.chdir('..')
            cwd = os.getcwd()
            if cwd == '/':
                break
        project_root = cwd
        os.chdir(current_cwd)
        return project_root

    @staticmethod
    def get_log_folder(cwd):
        log_dir_path = os.path.join(cwd, FileConst.LOG_DIR.value)
        return log_dir_path


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class EventMessage:
    def __init__(self, success: bool = True, message: str = "", data=None):
        self.Success = success
        self.Message = message
        self.Data = data

    def to_json(self):
        return json.dumps(self.__dict__, cls=MyEncoder)

    def to_dict(self):
        return {'Success': self.Success, 'Message': self.Message, 'Data': self.Data}


class User:
    def __init__(self, user_id, field_id, user_name=None, auth=None):
        self.user_id = user_id
        self.field_id = field_id
        self.user_name = user_name
        self.auth = auth
        self.user_field_list = list()
        self.permission_list = list()

    def to_json(self):
        return json.dumps(self.__dict__)


class Permission:
    def __init__(self):
        self.api_key = str
        self.create = False
        self.update = False
        self.delete = False
