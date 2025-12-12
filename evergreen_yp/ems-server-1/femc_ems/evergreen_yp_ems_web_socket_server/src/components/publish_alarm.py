import json
from datetime import datetime

import pandas as pd

from src.constants.config_const import DestinationConfigConst
from src.utility.utils import MyEncoder


class Alarm:
    def __init__(self):
        self.time = None
        self.field_id = None
        self.equipment_type = None
        self.equipment_id = None
        self.code = None
        self.message = None
        self.abnormal = True

    def to_json(self):
        return json.dumps(self.__dict__, cls=MyEncoder)


def publish_alarm(dest_conn_list: list):
    publish_list = []
    for source in dest_conn_list:
        client = None
        try:
            client = source.dao.get_connect()
            db = client[source.config[DestinationConfigConst.DATABASE_NAME.value]]
            cursor = db.alarm.find({'done_time': None})
            alarm_data = pd.DataFrame(list(cursor))
            for data in alarm_data.to_dict(orient='records'):
                alarm = Alarm()
                alarm.time = datetime.strftime(data['time'], '%Y-%m-%d %H:%M:%S')
                alarm.field_id = data['field_id']
                alarm.equipment_id = data['equipment_id']
                alarm.equipment_type = parser_equipment_code(data['equipment_id'])
                alarm.code = data['code']
                alarm.message = data['message']
                publish_list.append(alarm.to_json())
        except KeyError as e:
            source.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            source.logger.exception(repr(e))
            raise Exception
        finally:
            # source.logger.info('close mongodb client')
            if client is not None:
                client.close()
    return json.dumps(publish_list, cls=MyEncoder)


def parser_equipment_code(equipment_id):
    rtn_code = 0
    if 'AIR' in equipment_id:
        rtn_code = 0
    elif 'FIRE' in equipment_id:
        rtn_code = 1
    elif 'DOOR' in equipment_id:
        rtn_code = 2
    elif 'INVERTER' in equipment_id:
        rtn_code = 3
    elif 'PCS' in equipment_id:
        rtn_code = 4
    elif 'BMS' in equipment_id:
        rtn_code = 5
    elif 'RACK' in equipment_id:
        rtn_code = 6
    elif 'METER' in equipment_id:
        rtn_code = 7
    elif 'UPS' in equipment_id:
        rtn_code = 8
    return rtn_code
