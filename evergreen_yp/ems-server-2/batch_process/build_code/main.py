import distutils.util
import importlib
import sys
import time

from apscheduler.schedulers.background import BackgroundScheduler

from src.components.alarm_controller import AlarmController
from src.constants.config_const import ConfigSession, SystemSettingConfigConst, ScheduleType
from src.constants.schedule_job_const import JobConst
from src.dao.dao_factory import StorageFactory
from src.utility.config_parser import ConfigParser


def split_char(val, symbol=','):
    val_list = val.split(symbol)
    val_list = [s.strip() for s in val_list]
    return val_list


if __name__ == '__main__':
    try:
        start_date = None
        end_date = None

        # 如果使用者手動輸入起訖時間，則執行一次 (補資料用)
        # 否則使用現在時間作為起訖
        # 輸入時間格式: 20230326 / 20230326000000
        args = sys.argv[1:]
        if len(args) > 0:
            start_date = args[0]
            end_date = args[1]

        config_parser = ConfigParser()
        config = config_parser.parse('./config.ini', expend_vars=False)
        settings_config = config[ConfigSession.SETTINGS.value]

        # Get Source
        source_value = settings_config[SystemSettingConfigConst.SOURCE.value]
        source_config = config[source_value]
        source_dao = StorageFactory(source_config).get_dao()

        # Get Desc
        destination_value = settings_config[SystemSettingConfigConst.DESTINATION.value]
        destination_config = config[destination_value]
        destination_dao = StorageFactory(destination_config).get_dao()

        # Get Logger
        logger_config = config[ConfigSession.LOGGER.value]

        # Get Schedule
        use_schedule = distutils.util.strtobool(settings_config[SystemSettingConfigConst.USE_SCHEDULE.value])
        schedule_type = settings_config[SystemSettingConfigConst.SCHEDULE_TYPE.value]
        cron_day_of_week = settings_config[SystemSettingConfigConst.CRON_DAY_OF_WEEK.value]
        cron_hour = settings_config[SystemSettingConfigConst.CRON_HOUR.value]
        cron_minute = settings_config[SystemSettingConfigConst.CRON_MINUTE.value]
        cron_second = settings_config[SystemSettingConfigConst.CRON_SECOND.value]
        interval_unit = settings_config[SystemSettingConfigConst.INTERVAL_UNIT.value]
        interval_value = settings_config[SystemSettingConfigConst.INTERVAL_VALUE.value]

        # Slack info
        slack_config = config[ConfigSession.SLACK_MESSAGE.value]
        slack_controller = AlarmController(slack_config)

        schedule_job = BackgroundScheduler(timezone="UTC", daemon=True, coalesce=True)

        # Get Job
        run_schedule = False
        job_list_data = settings_config[SystemSettingConfigConst.JOB_ID.value]
        job_list_data = split_char(job_list_data)
        job_list = list()
        for job in job_list_data:
            if job in JobConst.list():
                class_name = JobConst(job).name
                _class = getattr(importlib.import_module(f"src.components.{job}"), class_name)
                instance = _class(source_dao, destination_dao, slack_controller, logger_config,
                                  settings_config, start_date, end_date)
                job_list.append(instance)
            else:
                continue

            if use_schedule and start_date is None and end_date is None:
                if schedule_type == ScheduleType.CRON.value:
                    schedule_job.add_job(instance.execute, 'cron', day_of_week=cron_day_of_week,
                                         hour=cron_hour, minute=cron_minute, second=cron_second)
                    run_schedule = True
                elif schedule_type == ScheduleType.INTERVAL.value:
                    interval_value = int(interval_value)
                    if interval_unit == 'seconds':
                        schedule_job.add_job(instance.execute, 'interval', seconds=interval_value)
                    elif interval_unit == 'minutes':
                        schedule_job.add_job(instance.execute, 'interval', minutes=interval_value)
                    elif interval_unit == 'hours':
                        schedule_job.add_job(instance.execute, 'interval', hours=interval_value)
                    elif interval_unit == 'days':
                        schedule_job.add_job(instance.execute, 'interval', days=interval_value)
                    else:
                        schedule_job.add_job(instance.execute, 'interval', weeks=interval_value)
                    run_schedule = True

        if run_schedule:
            schedule_job.start()
            while True:
                time.sleep(1)
        else:
            for job in job_list:
                job.execute()
    except Exception as e:
        print(e)



