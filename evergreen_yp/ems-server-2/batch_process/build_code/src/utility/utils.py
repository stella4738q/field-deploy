import os
from datetime import timedelta, datetime

from ..constants.foler_and_file_const import FolderAndFileConst as FileConst


class ApiResponse:
    def __init__(self, success=True, msg='Success', rtn_data=None):
        self.Success = success
        self.Msg = msg
        self.Data = rtn_data

    @property
    def serialized(self):
        return self.__dict__


class WarningMessage:
    def __init__(self):
        self.datetime = datetime.now()
        self.category = None
        self.table = None
        self.target_id = None
        self.target_name = None
        self.subject = None
        self.content = None
        self.business_unit = None
        self.warning_user = list()


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


def creator(now):
    creator_dict = {
        "created_on": now,
        "created_by": None,
        "created_name": 'batch'
    }
    return creator_dict


def modifier(now):
    modifier_dict = {
        "modified_on": now,
        "modified_by": None,
        "modified_name": 'batch'
    }
    return modifier_dict
