import datetime
import os
import glob
from enum import Enum
from abc import ABC
from distutils.util import strtobool
from zipfile import ZipFile

import pandas as pd

from .mongodb_dao import MongoDBDao
from ..constants.foler_and_file_const import FolderAndFileConst
from ..utility.logger import MyLogger


class CallType(Enum):
    NonDef = 0
    OnOrAfter = 1
    OnOrBefore = 2
    Between = 3


class FileExtension(Enum):
    csv = 'csv'
    xlsx = 'xlsx'
    json = 'json'
    txt = 'txt'


class FolderType(Enum):
    History = 0
    Current = 1


class DirDefinition:
    def __init__(self, dir_type: FolderType, path: str, is_zip: bool = False, zip_file: str = None,
                 zip_path: str = None):
        self.Type = dir_type
        self.Path = path
        self.IsZip = is_zip
        self.ZipFile = zip_file
        self.ZipPath = zip_path
        self.Key = None
        self.__set_key__()

    def __set_key__(self):
        if self.Type == FolderType.History:
            p_list = []
            b_path = self.Path
            for i in range(4):
                temp_path = os.path.split(b_path)
                p_list.append(temp_path[1])
                b_path = temp_path[0]
            self.Key = datetime.datetime(int(p_list[3]), int(p_list[2]), int(p_list[1]), int(p_list[0]), 0, 0)


class FilesystemSettings:
    def __init__(self, base_path: str, target_name_list=None,
                 target_data: FolderType = None, current_data_folder_name: str = 'current_data',
                 filter_date_star: datetime.datetime = None, filter_date_end: datetime.datetime = None,
                 file_extension: FileExtension = FileExtension.csv):
        self._base_path = base_path
        self._target_name_list = [] if target_name_list is None else \
            [target_name_list] if isinstance(target_name_list, str) else target_name_list
        self._target_data = target_data
        self._current_data_folder_name = current_data_folder_name
        self._file_extension = file_extension
        self._filter_date_star = filter_date_star
        self._filter_date_end = filter_date_end
        self.cal_type = CallType.NonDef
        self.__process__()

    def __process__(self):
        """
        cal_type 0: sdate X , edate X
        cal_type 1: sdate O , edate X
        cal_type 2: sdate X , edate O
        cal_type 3: sdate O , edate O
        """
        if self._filter_date_star is not None and self._filter_date_end is None:
            self.cal_type = CallType.OnOrAfter
        elif self._filter_date_star is None and self._filter_date_end is not None:
            self.cal_type = CallType.OnOrBefore
        elif self._filter_date_star is not None and self._filter_date_end is not None:
            self.cal_type = CallType.Between

    @property
    def target_name_list(self):
        return self._target_name_list

    @target_name_list.setter
    def target_name_list(self, value):
        if isinstance(value, str):
            self._target_name_list = [value]
        else:
            self._target_name_list = value

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = value

    @property
    def file_extension(self):
        return self._file_extension

    @file_extension.setter
    def file_extension(self, value):
        self._file_extension = value

    @property
    def filter_date_star(self):
        return self._filter_date_star

    @filter_date_star.setter
    def filter_date_star(self, value):
        self._filter_date_star = value
        self.__process__()

    @property
    def filter_date_end(self):
        return self._filter_date_end

    @filter_date_end.setter
    def filter_date_end(self, value):
        self._filter_date_end = value
        self.__process__()

    @property
    def current_data_folder_name(self):
        return self._current_data_folder_name

    @current_data_folder_name.setter
    def current_data_folder_name(self, value):
        self._current_data_folder_name = value

    @property
    def target_data(self):
        return self._target_data

    @target_data.setter
    def target_data(self, value):
        self._target_data = value


class FileSystemDao(ABC):

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def __init__(self, config):
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        my_logger = MyLogger(self.__class__.__name__)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()
        self.config = config
        self.db_dao = MongoDBDao(config)
        self.__init_base_path()

    def __init_base_path(self):
        base_path = self.config[FolderAndFileConst.BASE_PATH.value]
        self.check_folder_exist(base_path)
        self.base_path = base_path

    @staticmethod
    def check_folder_exist(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def create(self, data, **kwargs):
        raise NotImplementedError

    def read(self, criteria: FilesystemSettings, **kwargs):
        rtn_data = pd.DataFrame()
        if criteria.base_path is None:
            return rtn_data

        # get all accept folder
        folders = self.scan_folder(criteria, criteria.base_path)
        topic_list = dict()
        for folder in folders:
            if criteria.target_name_list is None:
                criteria.target_name_list = ['*']

            if folder.IsZip:
                with ZipFile(folder.ZipFile, 'r') as archive:
                    names = [name for name in archive.namelist() if name.startswith(folder.ZipPath)]
                    for file_name in criteria.target_name_list:
                        files = [name for name in names if match(file_name, name.split('/')[1])]
                        for file in files:
                            if criteria.file_extension.value == 'csv':
                                df = pd.read_csv(archive.open(file), on_bad_lines='skip', encoding='utf-8')
                            elif criteria.file_extension.value == 'json':
                                df = pd.read_json(archive.open(file))
                            elif criteria.file_extension.value == 'xlsx':
                                df = pd.read_excel(archive.open(file))
                            elif criteria.file_extension.value == 'txt':
                                df = pd.read_fwf(archive.open(file))
                            else:
                                df = pd.DataFrame()
                            arr_topic = os.path.basename(file).split('_')
                            topic = arr_topic[0]
                            if topic in topic_list.keys():
                                topic_list[topic].append(df)
                            else:
                                topic_list[topic] = [df]
            else:
                for file_name in criteria.target_name_list:
                    files = glob.glob(os.path.join(folder.Path, f"{file_name}.{criteria.file_extension.value}"))
                    for file in files:
                        if criteria.file_extension.value == 'csv':
                            df = pd.read_csv(file, on_bad_lines='skip', encoding='utf-8')
                        elif criteria.file_extension.value == 'json':
                            df = pd.read_json(file)
                        elif criteria.file_extension.value == 'xlsx':
                            df = pd.read_excel(file)
                        elif criteria.file_extension.value == 'txt':
                            df = pd.read_fwf(file)
                        else:
                            df = pd.DataFrame()
                        arr_topic = os.path.basename(file).split('_')
                        topic = arr_topic[0]
                        if topic in topic_list.keys():
                            topic_list[topic].append(df)
                        else:
                            topic_list[topic] = [df]

        keys = topic_list.keys()
        if len(keys) == 1:
            key = list(topic_list.keys())[0]
            rtn_data = pd.concat(topic_list[key], axis=0, ignore_index=True)
        elif len(keys) > 1:
            for key in topic_list.keys():
                li = topic_list[key]
                topic_list[key] = pd.concat(li, axis=0, ignore_index=True)
            rtn_data = topic_list
        return rtn_data

    # @slack_message(title='MongoDB DAO update method')
    def update(self, **kwargs):
        raise NotImplementedError

    # @slack_message(title='MongoDB DAO delete method')
    def delete(self, **kwargs):
        raise NotImplementedError

    def scan_folder(self, settings: FilesystemSettings, base_path, level=0, result=None):
        if result is None:
            result = []
        for f in os.scandir(base_path):
            if f.is_dir():
                if f.name == settings.current_data_folder_name:
                    if settings.target_data == FolderType.Current or settings.target_data is None:
                        f_def = DirDefinition(FolderType.Current, f.path)
                        result.append(f_def)
                elif settings.target_data == FolderType.History or settings.target_data is None:
                    self.scan_folder(settings, f.path, level + 1, result)
                    if level == 3:
                        f_def = DirDefinition(FolderType.History, f.path)
                        if settings.cal_type == CallType.NonDef:
                            result.append(f_def)
                        elif settings.cal_type == CallType.OnOrAfter:
                            if f_def.Key >= settings.filter_date_star:
                                result.append(f_def)
                        elif settings.cal_type == CallType.OnOrBefore:
                            if f_def.Key <= settings.filter_date_end:
                                result.append(f_def)
                        elif settings.cal_type == CallType.Between:
                            if settings.filter_date_star <= f_def.Key <= settings.filter_date_end:
                                result.append(f_def)
            elif f.is_file():
                if level == 2:
                    fp = os.path.splitext(f)
                    # 每日壓縮檔
                    if fp[1] == '.zip':
                        with ZipFile(f, 'r') as archive:
                            names = [info.filename for info in archive.infolist() if info.is_dir()]
                        for item in names:
                            temp_name = item.split('/')
                            path = os.path.join(fp[0], temp_name[0])
                            zip_path = item
                            f_def = DirDefinition(FolderType.History, path,
                                                  is_zip=True, zip_path=zip_path, zip_file=f.path)
                            if settings.cal_type == CallType.NonDef:
                                result.append(f_def)
                            elif settings.cal_type == CallType.OnOrAfter:
                                if f_def.Key >= settings.filter_date_star:
                                    result.append(f_def)
                            elif settings.cal_type == CallType.OnOrBefore:
                                if f_def.Key <= settings.filter_date_end:
                                    result.append(f_def)
                            elif settings.cal_type == CallType.Between:
                                if settings.filter_date_star <= f_def.Key <= settings.filter_date_end:
                                    result.append(f_def)
        return result


def match(first, second):
    if len(first) == 0 and len(second) == 0:
        return True
    if len(first) > 1 and first[0] == '*':
        i = 0
        while i + 1 < len(first) and first[i + 1] == '*':
            i = i + 1
        first = first[i:]
    if len(first) > 1 and first[0] == '*' and len(second) == 0:
        return False
    if (len(first) > 1 and first[0] == '?') or (len(first) != 0 and len(second) != 0 and first[0] == second[0]):
        return match(first[1:], second[1:])
    if len(first) != 0 and first[0] == '*':
        return match(first[1:], second) or match(first, second[1:])
    return False
