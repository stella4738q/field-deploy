from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class JobConst(ExtendedEnum):
    TascoBatchECI = 'tasco_batch_eci'
    TascoBatchSynchronize = 'tasco_batch_synchronize'
    TascoChargeDischargeSchedule = 'tasco_job_charge_discharge_schedule'
    TascoStatusControl = 'tasco_job_status_control'
    TascoNeededControl = 'tasco_job_needed_power'
    TascoBatchChargeReport = 'tasco_batch_charge_report'

