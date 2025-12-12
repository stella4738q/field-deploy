import numpy as np
import statistics
import pandas as pd
from logging_utils.logger import Logger
from apps.dashboard import log_path, logging_level


class Detection:
    def __init__(self, pd_data, vol_count=20, logging_level=logging_level, log_path=log_path):
        self.logger = Logger().create('Anomaly Detection Lib', level=logging_level, log_path=log_path)
        self.pd_data = pd_data
        self.vol_count = vol_count

    def get_voltage_data(self):
        self.logger.info('Get Voltage Raw Data')
        tot_column_list = self.pd_data.columns.values.tolist()
        group_column = []

        temp_group = []
        vol_pack_idx = 1
        for idx, column_name in enumerate(tot_column_list):
            if column_name.startswith('BMSnV'):
                if idx != 0 and idx % self.vol_count == 0:
                    if len(temp_group) > 0:
                        group_column.append(temp_group)
                        vol_pack_idx = vol_pack_idx + 1
                    temp_group = []
                temp_group.append(column_name)

        group_column.append(temp_group)

        dataframe_list = []
        for idx, item in enumerate(group_column):
            vol_data = self.pd_data[item].values.tolist()

            temp_raw_data = {
                'key': f'P{idx + 1}_V',
                'data': vol_data
            }

            vol_data = self.pd_data[item]
            dataframe_list.append(vol_data)
        return dataframe_list

    def normcdf(self, array, w=0.5):
        self.logger.info('Normal CDF Index')
        # is_out_spec = out_spec(array)
        # if is_out_spec:
        #     return 0
        sigma = statistics.stdev(array)
        mu = statistics.mean(array)
        n = len(array)
        if sigma == 0:
            return None

        x = [z for z in array if z <= mu]
        semi_sigma = np.sqrt(np.var(x) / n)
        if semi_sigma == 0:
            x = [z for z in array if z >= mu]
            semi_sigma = np.sqrt(np.var(x) / n)
            if semi_sigma == 0:
                semi_sigma = sigma

        z_scores_1 = list(map(lambda x: (x - mu) / np.sqrt(sigma), array))
        z_scores_2 = list(map(lambda x: (x - mu) / sigma, array))
        p0 = []
        p1 = []
        p2 = []
        for x, z1, z2 in zip(array, z_scores_1, z_scores_2):
            if z1 <= 0:
                _p0 = statistics.NormalDist(mu=mu, sigma=sigma).cdf(x)
                _p1 = statistics.NormalDist(mu=0, sigma=1).cdf(z1)
                _p2 = statistics.NormalDist(mu=0, sigma=1).cdf(z2)
            else:
                _p0 = 1 - statistics.NormalDist(mu=mu, sigma=sigma).cdf(x)
                _p1 = 1 - statistics.NormalDist(mu=0, sigma=1).cdf(z1)
                _p2 = 1 - statistics.NormalDist(mu=0, sigma=1).cdf(z2)
            p0.append(_p0)
            p1.append(_p1)
            p2.append(_p2)
        p = p0
        p = w * np.array(p1) + (1 - w) * np.array(p2)
        return min(p)

    def polygon_area(self, x, y):
        self.logger.info('Calculate Polygon Area')
        correction = x[-1] * y[0] - y[-1] * x[0]
        main_area = np.dot(x[:-1], y[1:]) - np.dot(y[:-1], x[1:])
        return 0.5 * np.abs(main_area + correction)

    def polygon_area_index(self, array):
        self.logger.info('Polygon Area Index')
        max_array = [np.mean(array)] * self.vol_count

        def array_to_coord(array):
            self.logger.info('Calculate X Y Coordinate')
            angle = (360/self.vol_count) * np.arange(0, self.vol_count)

            x_list = []
            y_list = []
            for index, item in enumerate(angle):
                x = array[index] * np.cos(np.radians(item))
                y = array[index] * np.sin(np.radians(item))
                x_list.append(x)
                y_list.append(y)
            return x_list, y_list

        x0, y0 = array_to_coord(max_array)
        x1, y1 = array_to_coord(array)

        base = self.polygon_area(x0, y0)
        comp = self.polygon_area(x1, y1)
        return comp / base

    def variance_index(self, array):
        self.logger.info('Variance Index')
        mu = statistics.mean(array)
        variance = list(map(lambda x: np.abs(x - mu) / np.sqrt(2), array))
        return np.sum(variance)

    def get_first_result(self):
        dataframe_list = self.get_voltage_data()
        rnt_dataframe = pd.DataFrame()
        for i in range(len(dataframe_list)):
            area_ratio = list()
            variance = list()
            for ind, row in dataframe_list[i].iterrows():
                area_ratio.append(self.polygon_area_index(row.to_list()))
                variance.append(self.variance_index(row.to_list()))

            rnt_dataframe[f'P{i + 1}_mixed'] = (np.array(area_ratio) + np.array(variance)) / 2
        return rnt_dataframe

    def get_result(self):
        dataframe = self.pd_data
        rnt_dataframe = pd.DataFrame()
        area_ratio = list()
        variance = list()
        for ind, row in dataframe.iterrows():
            area_ratio.append(self.polygon_area_index(row.to_list()))
            variance.append(self.variance_index(row.to_list()))

        rnt_dataframe['mixed'] = (np.array(area_ratio) + np.array(variance)) / 2
        return rnt_dataframe
