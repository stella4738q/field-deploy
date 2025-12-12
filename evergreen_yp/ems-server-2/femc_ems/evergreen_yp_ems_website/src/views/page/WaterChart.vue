<template>
  <div class="p-5">
    <h1>水冷記錄</h1>
    <div class="d-flex align-items-center mb-3">
      <el-form :model="Form" ref="Form" :rules="FormRule" :inline="true">
        <el-form-item label="開始時間" prop="start_time">
          <el-date-picker v-model="Form.start_time" type="datetime" value-format="YYYYMMDDHHmmss" />
        </el-form-item>
        <el-form-item label="結束時間" prop="end_time">
          <el-date-picker v-model="Form.end_time" type="datetime" value-format="YYYYMMDDHHmmss" />
        </el-form-item>
        <el-form-item label="聚合類型" prop="date_type">
          <el-select v-model="Form.date_type" placeholder="請選擇">
            <el-option label="分" value="minute" />
            <el-option label="秒" value="second" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-form-item>
        <button class="btn btn-primary btn-sm" @click="getData">
          <font-awesome-icon icon="search" /></button>
      </el-form-item>
    </div>

    <div id="WaterChart" ref="WaterChart" style="height:300px"></div>

  </div>
</template>
<script>

import moment from 'moment';
import * as echarts from "echarts";
import { getBMUGetData } from '@/api/Api.js';
import WaterChartData from '@/JSON/WaterChart.json'
var WaterChart = null;




export default {
  components: {
  },
  data() {
    var lessTwoDays = (rule, value, callback) => {
      if (!this.Form.start_time || !this.Form.end_time) {
        return callback();
      } else {
        let a = this.moment(this.Form.start_time, "YYYYMMDDHHmmss");
        let b = this.moment(this.Form.end_time, "YYYYMMDDHHmmss");
        if (b.diff(a, 'seconds') <= 172800) {
          return callback();
        } else {
          return callback(new Error('查詢時間範圍不可大於兩天'));
        }
      }
    };

    return {
      moment,
      Form: {
        brand: "Sungrow",
        equipment_id: 'BMS',
        start_time: '',
        end_time: '',
        date_type: 'minute',
      },
      FormRule: {
        start_time: [{ required: true, message: ' ', trigger: 'blur' }],
        end_time: [
          { required: true, message: ' ', trigger: 'blur' },
          { validator: lessTwoDays, trigger: 'blur' }
        ],
        date_type: [{ required: true, message: ' ', trigger: 'blur' }],
      },
      ApiResult: {
        outlet_water_temperature: [],
        inlet_water_temperature: [],
      },
    }
  },
  computed: {


  },
  mounted() {
    WaterChart = echarts.init(this.$refs.WaterChart);
  },
  beforeUnmount() {
    WaterChart = null;
  },
  created() {
    this.Form.start_time = this.moment().startOf('day').format("YYYYMMDDHHmmss");
    this.Form.end_time = this.moment().endOf('day').format("YYYYMMDDHHmmss");
  },
  watch: {
  },
  methods: {
    setChart() {
      const vm = this;
      WaterChart.setOption({
          grid: {
            top: '10%',
            bottom: '10%',
          },
          tooltip: {
            trigger: 'axis',
          },
          xAxis: {
            type: 'category',
            axisLabel: {
              formatter: function (value, index) {
                return vm.moment(value).format("YYYY-MM-DD HH:mm:ss");
              }
            }
          },
          yAxis: {
            type: 'value',
          },
          series: [
            {
              data: vm.ApiResult.inlet_water_temperature,
              type: 'line',
              showSymbol: false,
              name: '回水溫度'
            },
            {
              data: vm.ApiResult.outlet_water_temperature,
              type: 'line',
              showSymbol: false,
              name: '出水溫度'
            }

          ]
        });
    },
    getData() {
      const vm = this;
      if (process.env.VUE_APP_DemoData == 1) {
        vm.ApiResult = WaterChartData.data;
        vm.setChart();
      } else {
        vm.$refs.Form.validate((valid) => {
          if (valid) {
            vm.$loading();

            getBMUGetData(vm.Form)
              .then(resopnse => {
                if (resopnse.data.message == "Success") {
                  vm.ApiResult = resopnse.data.data;
                  vm.setChart();
                } else {
                  vm.$message({ type: 'error', message: resopnse.data.message });
                }
              }).catch(resopnse => {
                vm.$message({ type: 'error', message: resopnse.message });
              }).finally(() => {
                vm.$loading().close();
              });

          }
        });
      }
    },

  },
};
</script>