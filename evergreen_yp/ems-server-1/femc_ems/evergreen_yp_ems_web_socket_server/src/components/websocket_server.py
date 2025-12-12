from urllib.parse import parse_qs, urlparse

import asyncio
import copy
import json
import os
import pandas as pd
import ssl
import sys
import time
import websockets
from bson import ObjectId
from distutils.util import strtobool
from typing import List

from src.components.alarm_controller import AlarmController
from src.components.publish_data import publish_socket_data
from src.constants.config_const import ConfigSession, SettingConfigConst, SocketServerConst
from src.constants.foler_and_file_const import FolderAndFileConst
from src.constants.source_type_const import SourceTypeConfigConst
from src.dao.file_system_dao import FileSystemDao, FilesystemSettings, FolderType
from src.dao.mongodb_dao import MongoDBDao
from src.utility.edutil import EDUtility
from src.utility.logger import MyLogger
from src.utility.utils import EventMessage

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))

current_data = {}


async def subscribe_websocket(socket_obj):
    retries = 0
    global current_data
    url = socket_obj.get('url')
    formatter = socket_obj.get('map_layout')
    token = socket_obj.get('token', '')

    while True:
        try:
            async with websockets.connect(url) as ws:
                # 訂閱先驗證
                send_msg = {'action': 'auth', 'token': token}
                await ws.send(json.dumps(send_msg))

                while True:
                    pub_data = await ws.recv()
                    obj = json.loads(pub_data)
                    parallel_update(obj, formatter, is_socket=True)
                    retries = 0
        except Exception as ex:
            print(f"Error handling websocket {url} ({retries}): {ex}")
            retries += 1
            if retries <= 10:
                retry_interval = 3
            elif 10 < retries < 20:
                retry_interval = 10
            elif 21 < retries < 30:
                retry_interval = 30
            else:
                retry_interval = 60
        await asyncio.sleep(retry_interval)


def parallel_update(_update_data, formatter=None, is_socket=False):
    for key in _update_data.keys():
        if is_socket:
            if key in formatter:
                transfer_key = key
                update_data(_update_data, key, transfer_key)
        else:
            if formatter is not None:
                transfer_key = formatter[key]
            else:
                transfer_key = key
            update_data(_update_data, key, transfer_key)


def update_data(_update_data, key, transfer_key):
    base_target = current_data.get(transfer_key, [])
    upsert = _update_data.get(key, [])
    if type(upsert) is dict:
        if not base_target:
            current_data[key] = dict()
            base_target = current_data[key]
        for key, value in upsert.items():
            base_target[key] = value
    elif type(upsert) is list:
        if key in ['alarm', 'ems_schedule']:
            current_data[transfer_key] = upsert
        else:
            for _d in upsert:
                target_id = _d["equipment_id"] if 'equipment_id' in _d else None
                matching_items = [_t for _t in base_target if _t["equipment_id"] == target_id]
                if matching_items:
                    index = base_target.index(matching_items[0])
                    base_target[index] = _d
                else:
                    current_data[transfer_key].append(_d)


class WebSocketServer:
    def __init__(self, config):
        self.config = config
        self.ed_util = EDUtility(config)
        self.pri_data = None

        # init logger
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        config_setting = config[ConfigSession.SETTINGS.value]
        logging_level = str(config_setting[SettingConfigConst.LOGGING_LEVEL.value])
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()

        # init alarm controller
        self.logger.info('create alarm controller instance list')
        self.alarm_handler = AlarmController(config)

        # load web socket source config
        config_path = "config/socket_source.json"
        with open(config_path, 'r') as file:
            source_config = json.load(file)

        self.layout_format = source_config['layout_format']
        global current_data
        current_data = copy.deepcopy(self.layout_format)

        self.mvcb_meter_base_path = None
        self.mvcb_map_key = None
        self.append_accu_data = False
        self.meter_accu_dao = None
        self.meter_accu_settings = None

        mvcv_settings = source_config['mvcb_settings']
        self.use_meter_ms = mvcv_settings.get('from_meter_ms', False)
        if self.use_meter_ms:
            self.mvcb_meter_base_path = mvcv_settings.get('base_path', None)
            self.mvcb_map_key = mvcv_settings.get('map_layout', None)
            if not (self.mvcb_meter_base_path and self.mvcb_map_key):
                self.use_meter_ms = False
            else:
                self.append_accu_data = mvcv_settings.get('append_accu_data', False)
                if self.append_accu_data:
                    accu_settings = mvcv_settings.get('accu_setting', None)
                    if accu_settings is not None:
                        accu_base_path = accu_settings.get('base_path', None)
                        target_name_list = accu_settings.get('target_name_list', None)
                        self.meter_accu_dao = FileSystemDao(accu_base_path)
                        self.meter_accu_settings = FilesystemSettings(
                            target_name_list=target_name_list, target_data=FolderType.Current, base_path=accu_base_path)
                    else:
                        self.append_accu_data = False

        self.source_list = list()
        self.source_socket_list = list()

        # init fs source handlers
        self.logger.info('create filesystem source instance list')
        fs_source_list: List[dict] = source_config.get('filesystem', None)
        if fs_source_list is not None:
            for item in fs_source_list:
                base_path = item.get('base_path', None)
                map_layout = item.get('map_layout', None)
                target_name_list = item.get('target_name_list', None)
                if not (base_path and map_layout and target_name_list):
                    continue

                dao = FileSystemDao(base_path)
                settings = FilesystemSettings(
                    target_name_list=target_name_list, target_data=FolderType.Current, base_path=base_path)
                self.source_list.append({
                    'type': SourceTypeConfigConst.FILE_SYSTEM.value,
                    'dao': dao,
                    'settings': settings,
                    'map_key': map_layout
                })

        # init ws handlers
        self.logger.info('create web socket source instance list')
        ws_source_list: List[dict] = source_config.get('websocket', None)
        if ws_source_list is not None:
            for item in ws_source_list:
                map_layout = item.get('map_layout', None)
                url = item.get('url', None)
                token = item.get('token', None)
                if not (url and map_layout):
                    continue

                self.source_socket_list.append({
                    'url': url,
                    'token': token,
                    'map_layout': map_layout
                })

        # init api handlers
        self.logger.info('create api source instance list')
        api_source_list: List[dict] = source_config.get('webapi', None)
        if api_source_list is not None:
            for item in api_source_list:
                url = item.get('url', None)
                method = item.get('method', None)
                auth_header = item.get('auth_header', None)
                auth_token = item.get('auth_token', None)
                map_layout = item.get('map_layout', None)
                if not (url and method and auth_header and auth_token and map_layout):
                    continue
                self.source_list.append({
                    'type': SourceTypeConfigConst.WEB_API.value,
                    'url': url,
                    'method': method,
                    'auth_header': auth_header,
                    'auth_token': auth_token,
                    'map_key': map_layout
                })

        # use sim data
        use_sim_data = config_setting.get(SettingConfigConst.USE_SIM_DATA.value, None)
        if use_sim_data is None:
            self.use_sim_data = False
        else:
            self.use_sim_data = strtobool(use_sim_data)

        # load_fixed_attr
        load_fixed_attr = config_setting.get(SettingConfigConst.LOAD_FIXED_ATTR.value, None)
        if load_fixed_attr is None:
            self.load_fixed_attr = True
        else:
            self.load_fixed_attr = strtobool(load_fixed_attr)

        # database conn
        db_config = source_config.get('database')
        db_host = db_config.get('host')
        db_user_name = db_config.get('username')
        db_password = db_config.get('password')
        db_database_name = db_config.get('database_name')
        dao = MongoDBDao(db_host, db_user_name, db_password, db_database_name)
        self.db_dao = dao

        # init websocket server handler
        websocket_settings = config[ConfigSession.WEB_SOCKET_SERVER.value]
        self.host = websocket_settings[SocketServerConst.SERVER_HOST.value]
        self.port = int(websocket_settings[SocketServerConst.SERVER_PORT.value])
        self.ssl = int(websocket_settings[SocketServerConst.SSL.value])
        if self.ssl:
            cert_path = websocket_settings[SocketServerConst.CERT_PATH.value]
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            crt_path = os.path.join(cert_path, 'fullchain.crt')
            key_path = os.path.join(cert_path, 'privkey.key')
            self.ssl_context.load_cert_chain(certfile=crt_path, keyfile=key_path)

        # Client
        self.CLIENTS = set()

    async def start_server(self):
        self.logger.info(f"Server listing on port: {self.port}")
        await self.main()

    async def main(self):
        if self.ssl:
            async with websockets.serve(self.handler, self.host, self.port, ssl=self.ssl_context):
                asyncio.create_task(self.broadcast_data())
                # 判斷是否為使用模擬資料，不是的話如果有WebSocket訂閱，跑背景
                if not self.use_sim_data:
                    for url in self.source_socket_list:
                        asyncio.create_task(subscribe_websocket(url))
                await asyncio.Future()
        else:
            async with websockets.serve(self.handler, self.host, self.port):
                asyncio.create_task(self.broadcast_data())
                # 判斷是否為使用模擬資料，不是的話如果有WebSocket訂閱，跑背景
                if not self.use_sim_data:
                    for url in self.source_socket_list:
                        asyncio.create_task(subscribe_websocket(url))
                await asyncio.Future()

    async def handler(self, websocket: websockets, path):
        """
            Handle a connection and dispatch it according to who is connecting.
        """

        # url 呼叫
        query_params = parse_qs(urlparse(path).query)
        token = query_params.get('token', [None])[0]  # noqa

        # request head 呼叫
        if not token:
            headers = websocket.request_headers
            token = headers.get('Femc-Access-Token', None)

        sso_first = True if token is not None else False

        while True:
            try:
                # 有SSO，直接做驗證
                if sso_first:
                    sso_first = False
                    if token == 'hIIaMFemcSclIeNtNOaUthplZHAHA':
                        # 寫死不用驗證，給廠內Client使用
                        if websocket not in self.CLIENTS:
                            self.CLIENTS.add(websocket)
                    else:
                        result = self.auth(token)
                        if not result.Success:
                            await websocket.close(1011, "authentication failed")
                        else:
                            user_info = UserInfo(result.Data, self.db_dao)
                            if user_info.Error:
                                await websocket.close(1011, "authentication failed")
                            else:
                                if websocket not in self.CLIENTS:
                                    self.CLIENTS.add(websocket)
                else:
                    message = await websocket.recv()
                    if not message:
                        continue
                    message = json.loads(message.replace('\r\n', '').replace(' ', ''))
                    action = message.get('action', None)

                    if action == 'auth':
                        token = message.get('token', None)
                        if token == 'hIIaMFemcSclIeNtNOaUthplZHAHA':
                            # 寫死不用驗證，給廠內Client使用
                            if websocket not in self.CLIENTS:
                                self.CLIENTS.add(websocket)
                        else:
                            result = self.auth(token)
                            if not result.Success:
                                await websocket.close(1011, "authentication failed")
                            else:
                                user_info = UserInfo(result.Data, self.db_dao)
                                if user_info.Error:
                                    await websocket.close(1011, "authentication failed")
                                else:
                                    if websocket not in self.CLIENTS:
                                        self.CLIENTS.add(websocket)

            except websockets.ConnectionClosedOK as close_event:
                await self.remove_websocket_all_topic(websocket)
                break
            except websockets.ConnectionClosedError as conn_error:
                self.logger.error(str(conn_error))
                await self.remove_websocket_all_topic(websocket)
                await websocket.close(conn_error.code, str(conn_error.rcvd))
                break
            except Exception as e:
                self.logger.error(f'Socket error: {str(e)}')
                # await self.on_process_error(websocket, str(e))

    async def on_process_error(self, websocket, message):
        """
        Send an error message.

        """
        event = EventMessage(False, message)
        await websocket.send(event.to_json())

    async def remove_websocket_all_topic(self, websocket):
        try:
            if self.CLIENTS:
                self.CLIENTS.remove(websocket)
        except Exception as e:
            self.logger.error(f'Socket error: {str(e)}')

    async def broadcast_data(self):
        while True:
            try:
                self.wait_until_next_second()
                main_data, jso_data = publish_socket_data(
                    self.layout_format, self.use_meter_ms, self.mvcb_meter_base_path, self.mvcb_map_key,
                    self.append_accu_data, self.meter_accu_dao, self.meter_accu_settings,
                    self.source_list, self.use_sim_data, self.load_fixed_attr, self.db_dao, current_data
                )

                # if 'other' in main_data:
                #     current_data['other'] = main_data['other']
                #     main_data.pop('other')
                #
                # if 'alarm' in main_data:
                #     current_data['alarm'] = main_data['alarm']
                #     main_data.pop('alarm')
                #
                # if 'sbspm' in main_data:
                #     current_data['sbspm'] = main_data['sbspm']
                #     main_data.pop('sbspm')

                parallel_update(main_data)
                if self.CLIENTS:
                    websockets.broadcast(self.CLIENTS, json.dumps(current_data))
            except Exception as ex:
                print(f"Error in broadcast_data loop: {ex}")

            await asyncio.sleep(0.5)

    @staticmethod
    def wait_until_next_second():
        current_time = time.time()
        current_second = int(current_time)
        time_to_next_second = current_second + 1.0 - current_time - 0.2
        if time_to_next_second > 0:
            time.sleep(time_to_next_second)

    def auth(self, token):
        return self.ed_util.data_decrypt(token)


class UserInfo:
    def __init__(self, token_data, db_conn):
        self.UserId = token_data['id']
        self.Name = token_data['name']
        self.Company = token_data.get('company', None)
        self.IsAdmin = False
        self.Fields = list()
        self.__init_data__(db_conn)
        self.Error = False

    def __init_data__(self, db_dao):
        client = None
        try:
            client = db_dao.get_connect()
            db = client[db_dao.database_name]
            user = db.users.find_one({'_id': ObjectId(self.UserId), 'enable': 1})
            if user is None:
                self.Error = True
            else:
                self.IsAdmin = True if user['is_admin'] == 1 else False

                cursor = db.user_fields.find({'user_id': self.UserId})
                pd_data = pd.DataFrame(list(cursor))
                if not pd_data.empty:
                    self.Fields = pd_data['field_id'].tolist()
        except KeyError as e:
            print(str(e))
            self.Error = True
            raise KeyError
        except Exception as e:
            print(str(e))
            self.Error = True
            raise Exception
        finally:
            if client is not None:
                client.close()

