import datetime
from enum import Enum

import pandas as pd


class SRStatus(Enum):
    NoBids = 0
    StandardBy = 1
    Abandon = 2
    Processing = 3
    Recover = 4


class SRProcess:
    def __init__(self, database_dao):
        self.dao = database_dao
        self.case_list = list()
        self.__init_case__()

    def __init_case__(self):
        case_df: pd.DataFrame = self.dao.get_case()
        if not case_df.empty:
            case_list = case_df['_id'].to_list()
            self.case_list = [{
                'case_id': case_id,
                'capacity': 0,
                'status': SRStatus.NoBids.value,
                'cbl': 0
            } for case_id in case_list]

            self.get_sr_data()

    def get_sr_data(self):
        for case in self.case_list:
            current_state = SRStatus.NoBids
            won_bids = self.dao.get_won_bids(case['case_id'])
            if won_bids is not None and won_bids['capacity'] is not None and won_bids['capacity'] > 0:
                case['capacity'] = won_bids['capacity'] * 1000
                current_state = SRStatus.StandardBy

                abandon = self.dao.get_bid_abandon(case['case_id'])
                if abandon is not None:
                    case['capacity'] = abandon['capacity'] * 1000
                    if case['capacity'] == 0:
                        # 全部中止
                        current_state = SRStatus.Abandon

            target: dict = self.dao.get_case_dispatching(case['case_id'])
            if target['recovering'] is not None:
                # 調度恢復中
                current_state = SRStatus.Recover
            elif target['dispatching'] is not None:
                # 執行調度中
                current_state = SRStatus.Processing

            cbl_df = self.dao.get_cbl(case['case_id'])
            if not cbl_df.empty:
                case['cbl'] = abs(cbl_df.iloc[0]['cbl'])
            else:
                case['cbl'] = 0
            case['status'] = current_state.value
