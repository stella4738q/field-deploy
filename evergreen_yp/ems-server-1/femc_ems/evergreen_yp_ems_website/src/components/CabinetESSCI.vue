<template>
  <div class="row m-0 p-0" v-loading="Loading">
    <div class="  col  m-0 p-0 me-2 ">
      <div ref="ChartESSCI" style="width:100%;height:400px">
      </div>
    </div>
  </div>
  <!-- ========================================================= -->
  <el-dialog title="ESSCI" v-model="outerVisible" :width="dialogWidth" :destroy-on-close="true">
    <div class="row g-3" v-loading="Loading">
    <!-- ========================================================= -->
    <div class="col-12">
      <div class="card shadow border-0">
        <div ref="ChartESSCI2" style="height:250px"></div>
      </div>
    </div>
    <!-- ========================================================= -->
    <div class="col-12 col-md-6">
      <div class="card shadow border-0">
        <div ref="ChartICI" style="height:250px"></div>
      </div>
    </div>
    <!-- ========================================================= -->
    <div class="col-12 col-md-6">
      <div class="card shadow border-0">
       <!-- ================================== -->
       <div v-show="isV" ref="ChartV" style="height:250px;"></div>
        <!-- ======================= -->
        <div v-if="!isV" class="row m-0 p-0" style="font-size: xx-small;">
          <div class="col-6">
            <div v-for="(item, ind) in TData.TDataListB" :key="ind" class="row m-0 p-0 border">
              <div
                class="col-4 p-0 m-0 bg-secondary text-white text-center d-flex align-items-center justify-content-center">
                {{ item.label }}</div>
              <div class="col  p-0 m-0  row">
                <div v-for="(itemData, indData) in item.data" :key="indData" class="text-center col-6 m-0 p-0">
                  <span :class="itemData == getMax ? 'text-danger' : (itemData == getMin ? 'text-primary' : '')">
                    {{ itemData }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div v-for="(item, ind) in TData.TDataListA" :key="ind" class="row m-0 p-0 border">
              <div
                class="col-4 p-0 m-0 bg-secondary text-white text-center d-flex align-items-center justify-content-center">
                {{ item.label }}</div>
              <div class="col  p-0 m-0  row">
                <div v-for="(itemData, indData) in item.data" :key="indData" class="text-center col-6 m-0 p-0">
                  <span :class="itemData == getMax ? 'text-danger' : (itemData == getMin ? 'text-primary' : '')">
                    {{ itemData }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- ========================================================= -->
      </div>
    </div>
    <!-- ========================================================= -->
  </div>
  <!-- ========================================================= -->
  </el-dialog>
  <!-- ========================================================= -->
</template>
<script>
import moment from 'moment';
import { getEMSESSCI, getSystemStorageSetting } from '@/api/Api.js';
import ESSCIDemoData from '@/JSON/ESSCI.json';

import * as echarts from "echarts";
var ChartESSCI = null;
var ChartESSCI2 = null;
var ChartICI = null;
var ChartV = null;

export default {
  name: 'CabinetESSCI',
  setup() { },
  props: {
  },
  components: {
  },
  data() {
    return {
      moment,
      Loading: false,
      ESSCIDemoData,
      ESSCIClickObj: {
        index: -1,
        name: '',
        obj: null,
      },
      ICIClickObj: {
        index: -1,
        name: '',
        obj: null,
      },
      outerVisible: false,
      isV: true,
      threshold: 70,
      ApiResult: {
        postCabinetESSCI: null,
      },
      dialogWidth: '1100px',
    };
  },
  methods: {
    getConfig() {
      const vm = this;
      getSystemStorageSetting({ equipment_type: 1 }).then((response) => {
        if (response.data.message == "Success") {
          var find = response.data.data.find(x => x.key == "eci_warning_std");
          if (find) {
            vm.threshold = find.value * 100;
          }
        }
      }).finally(() => {
        vm.getEMSESSCI();
      })
    },
    getEMSESSCI() {
      const vm = this;
      var p = process.env.VUE_APP_DemoData;
      if (p == 1) {
        vm.ApiResult.postCabinetESSCI = vm.ESSCIDemoData.data;
        vm.ESSCI();
      } else {
        vm.Loading = true;
        getEMSESSCI()
          .then((response) => {
            if (response.data.message.toLowerCase() == "success") {
              vm.ApiResult.postCabinetESSCI = response.data.data;
              vm.ESSCI();
            } else {
              vm.$message({ type: 'error', message: response.data.message });
            }
          })
          .catch((response) => {
            vm.$message({ type: 'error', message: response.message });
          })
          .finally(() => {
            vm.Loading = false;
          });
      }

    },
    ESSCI() {
      const vm = this;
      vm.ChartESSCI = echarts.init(vm.$refs.ChartESSCI);
      vm.ChartESSCI.setOption({
        title: {
          text: 'ESSCI',
          left: 'center',
        },
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            return `<div>${params[0].data[0]}</div><div> ${params[0].data[2]}: ${params[0].data[1]}</div>`;
          },
        },
        xAxis: {
          type: 'category',
        },
        yAxis: {
          type: 'value'
        },
        series: {
          data: vm.ApiResult.postCabinetESSCI.map(x => { return [vm.moment(x.data_time).format("HH:mm"), (x.essci.ECI[0].value * 100).toFixed(2), x.essci.ECI[0].rack_key] }),
          type: 'line',
          symbol: 'circle', // 將點的形狀設定為實心圓
          symbolSize: 8, // 設定點的大小
          markLine: {
            symbol: ['none', 'none'],//去掉箭头
            itemStyle: {
              normal: {
                lineStyle: { type: 'dashed', color: 'green', width: 2 }
                , label: { show: false, position: 'left' }
              }
            },
            data: [{ yAxis: vm.threshold }]
          }
        },

      });
      vm.ChartESSCI.on('click', function (params) {
        if (params.componentType === 'series') {
          vm.ESSCIClickObj.index = params.dataIndex;
          vm.ESSCIClickObj.name = params.data[2];
          vm.ESSCIClickObj.obj = params;
          vm.ICIClickObj.index = -1;
          vm.ICIClickObj.name = '';
          vm.ESSCIClick();
        }
      });
    },
    ESSCIClick() {
      const vm = this;
      vm.outerVisible = true;
      vm.$nextTick(() => {
        vm.ChartESSCI2 = echarts.init(vm.$refs.ChartESSCI2);
        vm.ChartESSCI2.setOption({
          title: {
            text: 'ESSCI',
            left: 'center',
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params) {
              return `<div>${params[0].data[0]}</div><div> ${params[0].data[2]}: ${params[0].data[1]}</div>`;
            },
          },
          xAxis: {
            type: 'category',
          },
          yAxis: {
            type: 'value'
          },
          series: {
            data: vm.ApiResult.postCabinetESSCI.map(x => { return [vm.moment(x.data_time).format("HH:mm"), (x.essci.ECI[0].value * 100).toFixed(2), x.essci.ECI[0].rack_key] }),
            type: 'line',
            symbol: 'circle', // 將點的形狀設定為實心圓
            symbolSize: 8, // 設定點的大小
            markLine: {
              symbol: ['none', 'none'],//去掉箭头
              itemStyle: {
                normal: {
                  lineStyle: { type: 'dashed', color: 'green', width: 2 }
                  , label: { show: false, position: 'left' }
                }
              },
              data: [{ yAxis: vm.threshold },]
            }
          }
        });
        vm.ChartESSCI2.on('click', function (params) {
          if (params.componentType === 'series') {
            vm.ESSCIClickObj.index = params.dataIndex;
            vm.ESSCIClickObj.name =  params.data[2];
            vm.ESSCIClickObj.obj = params;
            vm.ICIClickObj.index = -1;
            vm.ICIClickObj.name = '';
            vm.ICIChart();
          }
        });
        // vm.ICIChart();
        // 剛生成直接進最後一點資料
        setTimeout(() => {
            let allData = vm.ApiResult.postCabinetESSCI.map(x => { return [vm.moment(x.data_time).format("HH:mm"), (x.essci.ECI[0].value * 100).toFixed(2), x.essci.ECI[0].rack_key] });
            vm.ESSCIClickObj.index = allData.length - 1;
            vm.ESSCIClickObj.name = allData[allData.length - 1][2];
            vm.ESSCIClickObj.obj = null;
            vm.ICIClickObj.index = -1;
            vm.ICIClickObj.name = '';
            vm.ICIChart();
          }, 1000);

      })
    },
    ICIChart() {
      const vm = this;
      vm.$nextTick(() => {
        if (vm.ChartICI == null) vm.ChartICI = echarts.init(vm.$refs.ChartICI);
        vm.ChartICI.setOption({
          title: {
            text: `${vm.ESSCIClickObj.name} ICI`,
            left: 'center',
          },
          tooltip: {
            trigger: 'axis',
          },
          xAxis: {
            type: 'value',
            max: 100,
            min: -100
          },
          yAxis: {
            type: 'category',
            axisTick: {
              show: false
            },
          },
          series: {
            type: 'bar',
            data: vm.ESSCIClickObj.index == -1 ? [] : vm.ApiResult.postCabinetESSCI[vm.ESSCIClickObj.index].essci.ICI[0].value.map(x => { return [(x.value * 100).toFixed(2), x.key] }).reverse()
          },
        });

        vm.ChartICI.on('click', function (params) {
          console.log(params.dataIndex);
          if (params.componentType === 'series') {
            vm.ICIClickObj.index = params.dataIndex;
            vm.ICIClickObj.name = params.data[1];
            vm.ICIClickObj.obj = params;
            vm.ICIChart_Click();
          }
        });

        // vm.ICIChart_Click();
        // 剛生成直接進最後一點資料
        setTimeout(() => {
            let allData = vm.ESSCIClickObj.index == -1 ? [] : vm.ApiResult.postCabinetESSCI[vm.ESSCIClickObj.index].essci.ICI[0].value.map(x => { return [(x.value * 100).toFixed(2), x.key] }).reverse();
            vm.ICIClickObj.index = allData.length - 1;
            vm.ICIClickObj.name = allData[allData.length - 1][1];
            vm.ICIClickObj.obj = null;
            vm.ICIChart_Click();
          }, 1000);

      });
    },
    ICIChart_Click() {
      const vm = this;
      vm.$nextTick(() => {
        if (vm.ChartV == null) vm.ChartV = echarts.init(vm.$refs.ChartV);
        vm.ChartV.setOption({
          title: {
            text: vm.ESSCIClickObj.name + '-' + vm.ICIClickObj.name,
            left: 'center',
          },
          tooltip: { trigger: 'axis', },
          xAxis: { type: 'category' },
          yAxis:
          {
            type: 'value',
            // max: vm.ICIClickObj.name == 'T' ? 50 : 3.6,
            // min: vm.ICIClickObj.name == 'T' ? 20 : 3.2,
          },
          series: {
            type: 'bar',
            data: vm.ESSCIClickObj.index == -1 ? [] : vm.ApiResult.postCabinetESSCI[vm.ESSCIClickObj.index].essci.RAW[0].find(x => {
              return x.key2 == vm.ICIClickObj.name && x.rack_key == vm.ESSCIClickObj.name
            })?.data.map((x, ind) => { return [ind + 1, x.toFixed(2)] })
          },
        });
      });
    },
    setDialogWidth() {
      let windowSize = document.body.clientWidth;
      if (windowSize < 1110) {
        this.dialogWidth = '85%';
      } else {
        this.dialogWidth = '1100px';
      }    
    },
    ChartResize(){
      setTimeout(() => {
        if (this.ChartESSCI2) {
          this.ChartESSCI2.resize();
        }
        if (this.ChartICI) {
          this.ChartICI.resize();
        }
        if (this.ChartV) {
          this.ChartV.resize();
        }
      }, 100);
    },
  },
  watch: {
  },
  mounted() {
    this.getConfig();
    window.onresize = () => {
        return (() => {
          this.setDialogWidth();
          this.ChartResize();
      })();
    };
  },
  beforeUnmount() {
    ChartESSCI = null;
    ChartICI = null;
    ChartV = null;
  },
  computed: {
  },
  created() {
  },
};
</script>