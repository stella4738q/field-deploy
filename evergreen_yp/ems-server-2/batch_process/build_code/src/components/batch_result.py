from datetime import datetime


class BatchResult:
    def __init__(self, execute_time, batch_code, batch_name, finish_time=None, success=True, msg=''):
        self.execute_time: datetime = execute_time
        self.batch_no = batch_code
        self.batch_name = batch_name
        self.finish_time: datetime = finish_time
        self.spend_time = 0
        self.success = success
        self.msg = msg

    def get_spend_time(self):
        self.spend_time = (self.finish_time - self.execute_time).total_seconds()