<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
    <h1 class="mb-2">PCS歷史記錄下載</h1>
    <div class="d-flex align-items-center mb-3">
      <el-form :model="Form" ref="Form" :rules="FormRule" :inline="true" label-position="top" class="align-items-end">
        <el-form-item label="設備" prop="equipment_id">
          <el-select v-model="Form.equipment_id" placeholder="請選擇">
            <!-- <el-option v-for="option in enumlist.MeterOption" :label="option.label" :value="option.val" /> -->
            <el-option value="PCS_1" label="PCS"> </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="開始時間" prop="start_date">
          <el-date-picker v-model="Form.start_date" type="datetime" value-format="YYYYMMDDHHmmss" />
        </el-form-item>
        <el-form-item label="結束時間" prop="end_date">
          <el-date-picker v-model="Form.end_date" type="datetime" value-format="YYYYMMDDHHmmss" />
        </el-form-item>
        <el-form-item label="聚合類型" prop="date_type">
          <el-select v-model="Form.date_type" placeholder="請選擇">
            <el-option label="分" value="minute" />
            <el-option label="秒" value="second" />
          </el-select>
        </el-form-item>
        <el-form-item>
        <el-button type="primary" :disabled="sendCheck" @click="SearchClick">
          <font-awesome-icon icon="search" /></el-button>
          <el-button type="primary" class="ms-2" :disabled="sendCheck" @click="DownloadClick">
          <font-awesome-icon icon="download" />
        </el-button>
      </el-form-item>
      </el-form>
    </div>
    <!------------------------------------------------------------------------------------------->
    <el-tabs type="border-card" v-model="activeName">
    <!------------------------------------------------------------------------------------------->
    <el-tab-pane label="搜尋結果" name="tab1">
      <div>
      <el-form-item class="mb-0" label="數據類型1" prop="type">
        <el-select v-model="OptionValue.Chart1" placeholder="請選擇" @change="setMeterChart1" clearable>
          <el-option v-for="option in enumlist.PCSAttrOption" :label="option.label" :value="option.val" />
        </el-select>
      </el-form-item>
      <div id="MeterChart1" ref="MeterChart1" style="height:190px" class="mb-3"></div>

      <el-form-item class="mb-0" label="數據類型2" prop="type">
        <el-select v-model="OptionValue.Chart2" placeholder="請選擇" @change="setMeterChart2">
          <el-option v-for="option in enumlist.PCSAttrOption" :label="option.label" :value="option.val" />
        </el-select>
      </el-form-item>
      <div id="MeterChart2" ref="MeterChart2" style="height:190px" class="mb-3"></div>

      <el-form-item class="mb-0" label="數據類型3" prop="type">
        <el-select v-model="OptionValue.Chart3" placeholder="請選擇" @change="setMeterChart3">
          <el-option v-for="option in enumlist.PCSAttrOption" :label="option.label" :value="option.val" />
        </el-select>
      </el-form-item>
      <div id="MeterChart3" ref="MeterChart3" style="height:190px"></div>
    </div>
    </el-tab-pane>
    <!------------------------------------------------------------------------------------------->
    <el-tab-pane label="下載結果" name="tab2">
      <DataExportQuery class="mt-2 mb-2" ref="dataExportQuery" equipment_id="PCS_1"></DataExportQuery>
    </el-tab-pane>
  </el-tabs>
    <!------------------------------------------------------------------------------------------->
  </div>
</div>
</template>
<script>

import moment from 'moment';
import * as echarts from "echarts";
import { postExportAsyncData, getPCSHistoryData, getExportAsyncData } from '@/api/Api.js';
import DataExportQuery from '@/components/DataExportQuery.vue'
import enumlist from '@/JSON/EnumList.json';
import libDownload from "@/lib/libDownload.js";

var MeterChart1 = null;
var MeterChart2 = null;
var MeterChart3 = null;


export default {
  components: {
    DataExportQuery,
  },
  data() {
    var lessTwoDays = (rule, value, callback) => {
      if (!this.Form.start_date || !this.Form.end_date) {
        return callback();
      } else {
        let a = this.moment(this.Form.start_date, "YYYYMMDDHHmmss");
        let b = this.moment(this.Form.end_date, "YYYYMMDDHHmmss");
        if (b.diff(a, 'seconds') <= 172800) {
          return callback();
        } else {
          return callback(new Error('查詢時間範圍不可大於兩天'));
        }
      }
    };

    return {
      moment,
      enumlist,
      activeName: 'tab1',
      Form: {
        equipment_id: 'PCS_1',
        start_date: null,
        end_date: null,
        date_type: 'minute',
      },
      OptionValue: {
        Chart1: '',
        Chart2: '',
        Chart3: '',
      },
      FormRule: {
        equipment_id: [{ required: true, message: ' ', trigger: 'blur' }],
        start_date: [{ required: true, message: ' ', trigger: 'blur' }],
        end_date: [
          { required: true, message: ' ', trigger: 'blur' },
          { validator: lessTwoDays, trigger: 'blur' }
        ],
        date_type: [{ required: true, message: ' ', trigger: 'blur' }],
      },
      ApiResult: {
        frequency: [],
        volt_rs: [],
        volt_st: [],
        volt_tr: [],
        volt_avg: [],
        current_r: [],
        current_s: [],
        current_t: [],
        apparent_power: [],
        active_power: [],
        dc_active_power: [],
        battery_voltage: [],
      },
      downloadListEq: [],
    }
  },
  computed: {
    sendCheck() {
      const vm = this;
      let dis = true;
      let nullVal = 0;
      let durCheck = false;
      Object.keys(vm.Form).forEach((kkk) => {
        if(!vm.Form[kkk]) {
          nullVal += 1;
        }
      });
      if(nullVal === 0) {
        let a = this.moment(this.Form.start_date, "YYYYMMDDHHmmss");
        let b = this.moment(this.Form.end_date, "YYYYMMDDHHmmss");
        if (b.diff(a, 'seconds') <= 172800) {
          durCheck = true;
          dis = false;
        } else {
          durCheck = false;
        }
      }
      return dis;
    },
  },
  mounted() {
    MeterChart1 = echarts.init(this.$refs.MeterChart1);
    MeterChart1.group = 'group1';
    MeterChart2 = echarts.init(this.$refs.MeterChart2);
    MeterChart2.group = 'group1';
    MeterChart3 = echarts.init(this.$refs.MeterChart3);
    MeterChart3.group = 'group1';
    echarts.connect('group1');
  },
  beforeUnmount() {
    MeterChart1 = null;
    MeterChart2 = null;
    MeterChart3 = null;
  },
  created() {
    this.Form.start_date = this.moment().startOf('day').format("YYYYMMDDHHmmss");
    this.Form.end_date = this.moment().endOf('day').format("YYYYMMDDHHmmss");
  },
  watch: {
  },
  methods: {
    getData() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
          if (valid) {
            vm.$loading();
            getPCSHistoryData(vm.Form)
              .then(resopnse => {
                if (resopnse.data.message == "Success") {
                  vm.ApiResult = resopnse.data.data;
                  vm.setMeterChart1();
                  vm.setMeterChart2();
                  vm.setMeterChart3();
                } else {
                  if (resopnse.data.data === null) {
                    this.apiResultDefualt();
                  }
                  vm.$message({ type: 'error', message: resopnse.data.message });
                }
              }).catch(resopnse => {
                vm.$message({ type: 'error', message: resopnse.message });
              }).finally(() => {
                vm.$loading().close();
              });

          }
        });
    },
    SearchClick() {
      const vm = this;
      vm.activeName = 'tab1';
      vm.getData();
    },
    DownloadClick() {
      var vm = this;
      getExportAsyncData({ equipment_id: 'PCS_1' })
        .then(response => {
          if (response.data.success) {
            // vm.DataExportData = response.data.data;
            vm.downloadListEq = []; // 清空
            if (response.data.data.length) {
              response.data.data.forEach((item) => {
                vm.downloadListEq.push(item.equipment_id);
              });
            }
          } else {
            vm.$message({ type: 'error', message: response.data.Msg });
          }
        })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        })
        .finally(() => {
          if (vm.downloadListEq.indexOf(vm.Form.equipment_id) !== -1) {
            vm.activeName = 'tab2';
            vm.$refs.dataExportQuery.refreshData();
            vm.$message({ type: 'warning', message: `${vm.Form.equipment_id} 已有檔案，請至下方下載結果。`});
          } else if (vm.downloadListEq.indexOf(vm.Form.equipment_id) === -1) {
            this.DownloadSend();
          }
        });
    },
    DownloadSend() {
      const vm = this;
      const postData = {
        equipment_id: vm.Form.equipment_id,
        start_date: vm.Form.start_date,
        end_date: vm.Form.end_date,
        time_type: vm.Form.date_type
      };
      this.activeName = 'tab2';
      vm.$loading();
          postExportAsyncData(postData).then(response => {
            if(response.headers['content-type'] !== 'application/json'){
                var sdate = vm.Form.start_date;
                var edate = vm.Form.end_date;
                
                let fileName = `${vm.Form.equipment_id}紀錄_${vm.moment(sdate, 'YYYYMMDDHHmmss').format('YYYYMMDDHH')}-${vm.moment(edate, 'YYYYMMDDHHmmss').format('YYYYMMDDHH')}.csv`;
                libDownload(response, fileName);
                vm.$refs.dataExportQuery.refreshData();
            }
            else{
              const text = new TextDecoder('utf-8').decode(new Uint8Array(response.data));
              const _response = JSON.parse(text);
              if(_response.success){
                vm.$message({ type: 'success', message: _response.msg });
                vm.$refs.dataExportQuery.refreshData();
              }
              else{
                vm.$message({ type: 'error', message: _response.msg });
              }
            }
          }).catch(response => {
            vm.$message({ type: 'error', message: response.message });
          }).finally(() => {
            vm.$loading().close();
          });
    },
    setMeterChart3() {
      const vm = this;
      if (vm.OptionValue.Chart3) {
        MeterChart3.setOption({
          grid: {
            top: '10%',
            bottom: '10%',
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params) {
              let param = params[0];
              return `${vm.moment(param.value[0]).format("YYYY-MM-DD HH:mm:ss")} <br/> ${param.value[1].toFixed(2)}`;
            },
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
            max: vm.OptionValue.Chart3 == 'frequency' ? vm.getMax(vm.ApiResult[vm.OptionValue.Chart3]) : null,
            min: vm.OptionValue.Chart3 == 'frequency' ? vm.getMin(vm.ApiResult[vm.OptionValue.Chart3]) : null,
          },
          series: {
            data: vm.ApiResult[vm.OptionValue.Chart3],
            type: 'line',
            showSymbol: false,
          },
          dataZoom: [
              {
                  type: 'inside', 
                  start: 0,
                  end: 100
              },
              {
                  type: 'inside',
                  start: 0,
                  end: 100
              }
          ]
        });
      }
    },
    setMeterChart2() {
      const vm = this;
      if (vm.OptionValue.Chart2) {
        MeterChart2.setOption({
          grid: {
            top: '10%',
            bottom: '10%',
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params) {
              let param = params[0];
              return `${vm.moment(param.value[0]).format("YYYY-MM-DD HH:mm:ss")} <br/> ${param.value[1].toFixed(2)}`;
            },
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
            max: vm.OptionValue.Chart2 == 'frequency' ? vm.getMax(vm.ApiResult[vm.OptionValue.Chart2]) : null,
            min: vm.OptionValue.Chart2 == 'frequency' ? vm.getMin(vm.ApiResult[vm.OptionValue.Chart2]) : null,
          },
          series: {
            data: vm.ApiResult[vm.OptionValue.Chart2],
            type: 'line',
            showSymbol: false,
          },
          dataZoom: [
              {
                  type: 'inside', 
                  start: 0,
                  end: 100
              },
              {
                  type: 'inside',
                  start: 0,
                  end: 100
              }
          ]
        });
      }
    },
    setMeterChart1() {
      const vm = this;
      if (vm.OptionValue.Chart1) {
        MeterChart1.setOption({
          grid: {
            top: '10%',
            bottom: '10%',
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params) {
              let param = params[0];
              return `${vm.moment(param.value[0]).format("YYYY-MM-DD HH:mm:ss")} <br/> ${param.value[1].toFixed(2)}`;
            },
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
            max: vm.OptionValue.Chart1 == 'frequency' ? vm.getMax(vm.ApiResult[vm.OptionValue.Chart1]) : null,
            min: vm.OptionValue.Chart1 == 'frequency' ? vm.getMin(vm.ApiResult[vm.OptionValue.Chart1]) : null,
          },
          series: {
            data: vm.ApiResult[vm.OptionValue.Chart1],
            type: 'line',
            showSymbol: false,
          },
          dataZoom: [
              {
                  type: 'inside', 
                  start: 0,
                  end: 100
              },
              {
                  type: 'inside',
                  start: 0,
                  end: 100
              }
          ]
        });
      }
    },
    getMax(data) {
      let maxTemp = 0;
      for (const subArray of data) {
        if (subArray[1] > maxTemp) {
          maxTemp = subArray[1];
        }
      }
      return parseFloat( maxTemp.toFixed(2));
    },
    getMin(data) { 

      let minTemp = 100;
      for (const subArray of data) {
        if (subArray[1] < minTemp) {
          minTemp = subArray[1];
        }
      }
      return parseFloat(minTemp.toFixed(2));
    },
    apiResultDefualt() {
      this.ApiResult = {
        frequency: [],
        volt_rs: [],
        volt_st: [],
        volt_tr: [],
        volt_avg: [],
        current_r: [],
        current_s: [],
        current_t: [],
        apparent_power: [],
        active_power: [],
        dc_active_power: [],
        battery_voltage: [],
      };
      this.setMeterChart1();
      this.setMeterChart2();
      this.setMeterChart3();
    }
  },
};
</script>