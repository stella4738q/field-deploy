<template>
  <div class="row g-3">
    <div class="col-12">
      <div class="card shadow border-0">
        <div ref="ChartESSCI" style="height:250px"></div>
      </div>
    </div>

    <div class="col-12 col-md-6">
      <div class="card shadow border-0">
        <div ref="ChartICI" style="height:250px"></div>
      </div>
    </div>

    <div class="col-12 col-md-6">
      <div class="card shadow border-0">
        <div v-show="isV" ref="ChartV" style="height:250px;"></div>
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
      </div>
    </div>


  </div>


</template>
<script>
import moment from 'moment';
import { getEMSESSCI, getSystemStorageSetting } from '@/api/Api.js';
import ESSCIDemoData from '@/JSON/ESSCI.json';

import * as echarts from "echarts";
var ChartESSCI = null;
var ChartICI = null;
var ChartV = null;

export default {
  name: 'CabinetESSCI',
  setup() { },
  props: {
    RackName: {
      type: String,
      default: 'Rack'
    },
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
      if (process.env.VUE_APP_DemoData == 1) {
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
      // console.log(window.allCharts);
      // debugger;
      vm.$nextTick(() => {
        if (vm.$refs.ChartESSCI) {
          this.ChartESSCI = echarts.init(vm.$refs.ChartESSCI);
          // window.allCharts.push(ChartESSCI);
          this.ChartESSCI.setOption({
            title: {
              text: 'ECI',
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
              data: vm.RackECIData.filter(x => { return x != null && x != undefined }).map((x) => {
                return [vm.moment(x.data_time).format("HH:mm"), (x.eci_list[0].value * 100).toFixed(2), x.rack_id]
              }),
              type: 'line',
              symbol: 'circle', // 將點的形狀設定為實心圓
              symbolSize: 5, // 設定點的大小
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

          this.ChartESSCI.on('click', function (params) {
            // console.log(params);
            if (params.componentType === 'series') {
              vm.ESSCIClickObj.index = params.dataIndex;
              vm.ESSCIClickObj.name = params.data[2];
              vm.ESSCIClickObj.obj = params;
              vm.ICIClickObj.index = -1;
              vm.ICIClickObj.name = '';
              vm.ICIChart();
            }
          });
          // ChartESSCI.resize();
          // 剛生成直接進最後一點資料
          setTimeout(() => {
            let allData = vm.RackECIData.filter(x => { return x != null && x != undefined }).map((x) => {
              return [vm.moment(x.data_time).format("HH:mm"), (x.eci_list[0].value * 100).toFixed(2), x.rack_id]
            });
            vm.ESSCIClickObj.index = allData.length - 1;
            vm.ESSCIClickObj.name = allData[allData.length - 1][2];
            vm.ESSCIClickObj.obj = null;
            vm.ICIClickObj.index = -1;
            vm.ICIClickObj.name = '';
            vm.ICIChart();
          }, 1000);
        }

      });
    },
    ICIChart() {
      const vm = this;
      vm.$nextTick(() => {
        if (this.ChartICI == null) this.ChartICI = echarts.init(vm.$refs.ChartICI);
        this.ChartICI.setOption({
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
            data: vm.ESSCIClickObj.index == -1 ? [] : vm.RackECIData[vm.ESSCIClickObj.index].ici_list[0].value.slice(0, 10).reverse().map(x => { return [(x.value * 100).toFixed(2), x.key] })
          },
        });

        this.ChartICI.on('click', function (params) {
          // console.log(params.dataIndex);
          if (params.componentType === 'series') {
            vm.ICIClickObj.index = params.dataIndex;
            vm.ICIClickObj.name = params.data[1];
            vm.ICIClickObj.obj = params;
            vm.ICIChart_Click();
          }
        });
        // vm.ICIChart_Click();
        // ChartICI.resize();
        // 剛生成直接進最後一點資料
        setTimeout(() => {
              let allData = vm.ESSCIClickObj.index == -1 ? [] : vm.RackECIData[vm.ESSCIClickObj.index].ici_list[0].value.slice(0, 10).reverse().map(x => { return [(x.value * 100).toFixed(2), x.key] });
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
        if (this.ChartV == null) this.ChartV = echarts.init(vm.$refs.ChartV);
        // window.allCharts.push(ChartV);
        this.ChartV.setOption({
          title: {
            text: vm.ESSCIClickObj.name + '-' + vm.ICIClickObj.name,
            left: 'center',
          },
          tooltip: { trigger: 'axis', },
          xAxis: { type: 'category' },
          yAxis:
          {
            type: 'value',
            max: ["T", "T2"].includes(vm.ICIClickObj.name) ? 50 : 3.6,
            min: ["T", "T2"].includes(vm.ICIClickObj.name) ? 20 : 3.2,
          },
          series: {
            type: 'bar',
            data: vm.ESSCIClickObj.index == -1
              ? []
              : vm.RackECIData[vm.ESSCIClickObj.index].raw_list.find(x => {
                return x.key2 == vm.ICIClickObj.name && x.rack_key == vm.ESSCIClickObj.name
              })?.data.map((x, ind) => { return [ind + 1, x.toFixed(2)] })
          },
        });
        this.ChartV.resize();
      });
    },
    ChartResize(){
      setTimeout(() => {
        if (this.ChartESSCI) {
          this.ChartESSCI.resize();
        } else {
          this.getConfig();
        }
        if (this.ChartICI) {
          this.ChartICI.resize();
        }
        if (this.ChartV) {
          this.ChartV.resize();
        }
      }, 100);
    }
  },
  watch: {
  },
  mounted() {
    this.getConfig();
    window.onresize = () => {
        return (() => {
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
    RackECIData: function () {
      const vm = this;
      return vm.ApiResult.postCabinetESSCI
        .map(x => {
          var find = x.eci_list.find((xx) => { return xx.rack_id == vm.RackName });
          if (find) find.data_time = x.data_time;
          return find;
        });
    },
  },
  created() {
  },
};
</script>