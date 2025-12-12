<template>
  <div :id="ChartId" ref="myChart" style="width: 100%; height:100%;"></div>
</template>

<script >
import * as echarts from "echarts";
import { getChartHistorySunDB } from '@/api/Api.js';
import { mapState } from "vuex";
import moment from 'moment';

var ChartObj = null;

export default {
  props: {
  },
  components: {
    echarts
  },
  data() {
    return {
      ChartId: 'AdvancedTek_ChartSunPower',
      moment,
      chartData: {
        'inverter_1':[],
        'inverter_2':[],
        'inverter_3':[],
        'inverter_4':[],
        'inverter_5':[],
        'solar_exposure': []
      },
      dataZoomStart: 50, //預設顯示一半
      dataZoomEnd: 100,
    };
  },
  mounted() {
    this.initChart();
  },
  created() {
    this.ChartId = this.getUUID();
    this.initHistory()
  },
  watch: {
    LineChartDataPowerSun: {
      handler() {
        this.updateChart();
      },
      deep: true,
    },
    LineChartDataSolar: {
      handler() {
        this.updateChart();
      },
      deep: true,
    }
  },
  computed: {
    ...mapState(["LineChartDataPowerSun"]),
    ...mapState(["LineChartDataSolar"]),
    setOption: function () {
      var option = {
        legend: {
          data: ['逆變器1', '逆變器2', '逆變器3', '逆變器4', '逆變器5', '日照量'],
          orient: 'horizontal',
          left: 'center',
          bottom: '0%',
          textStyle: {
            color: '#333',
          }
        },
        grid: {
          top: '10%',
          bottom: '20%',
          left: '10%',
          right: '10%',
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            let tooltipContent = `<div>${params[0].name}</div>`;
            params.forEach(item => {
              tooltipContent += `
                <div>
                  <span style="color:${item.color}">●</span> ${item.seriesName}: ${this.formatNumber(item.data[1])}
                </div>
              `;
            });
            return tooltipContent;
          }
        },
        xAxis: {
          type: 'category',
          axisLine: {
            show: false
          },
          axisTick: {
            interval: 'auto',
            maxInterval: 5,
          },
          axisLabel: {
            interval: 'auto',
            maxInterval: 5,
            formatter: (function (value) {
              if (value) {
                return moment(value).format("HH:mm:ss")
              } else return null;
            })
          }
        },
        yAxis: [
          {
            type: 'value',
            max: function(value) {
                return (value.max + 10).toFixed(0);
            },
            min: 0,
            scale: true,
            position: 'left',
            name: '功率 (kW)',
          },
          {
            type: 'value',
            min: 0,
            scale: true,
            position: 'right',
            name: '日照量 (W/m2)',
          }
        ],
        series: [
          {
            name: '逆變器1',
            yAxisIndex: 0,
            data: this.chartData['inverter_1'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
          },
          {
            name: '逆變器2',
            yAxisIndex: 0,
            data: this.chartData['inverter_2'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
          },
          {
            name: '逆變器3',
            yAxisIndex: 0,
            data: this.chartData['inverter_3'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
          },
          {
            name: '逆變器4',
            yAxisIndex: 0,
            data: this.chartData['inverter_4'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
          },
          {
            name: '逆變器5',
            yAxisIndex: 0,
            data: this.chartData['inverter_5'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
          },
          {
            name: '日照量',
            yAxisIndex: 1,
            data: this.chartData['solar_exposure'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
            color: ['#c6e5d4d4'],
            areaStyle: {},
          },
        ],
        dataZoom: [
          {
            type: "inside",
            start: this.dataZoomStart,
            end: this.dataZoomEnd,
            throttle: 0 
          }
        ]
      };
      
      return option;
    },
  },
  methods: {
    getCurrentDateFormatted() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}${month}${day}`;
    },
    getUUID() {
      var d = Date.now();
      if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
        d += performance.now(); //use high-precision timer if available
      }
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
      });
    },
    initChart() {
      const vm = this;
      vm.$nextTick(function () {

        let el = this.$refs.myChart
        if (echarts.getInstanceByDom(el)) echarts.getInstanceByDom(el).setOption(vm.setOption);
        else echarts.init(el).setOption(vm.setOption)
      });
    },
    updateChart() {
      Object.values(this.chartData).forEach(value => {
        if(value.length > 43200){
          value.shift();
        }
      });
      var up = false;
      this.LineChartDataPowerSun.forEach(item => {
        const eq_id = item.equipment_id.substr(item.equipment_id.length - 1);
        const newDataTime = item.data_time.split('.')[0];
        const lastData = this.chartData[`inverter_${eq_id}`].slice(-1)[0];
        if (!lastData || lastData[0] !== newDataTime) {
          //
          this.chartData[`inverter_${eq_id}`].push([
            newDataTime,
            parseFloat(this.formatNumber(item.total_active_power)).toFixed(3)
          ]);
          //
          if(!up) {
            this.chartData['solar_exposure'].push([
              newDataTime,
              parseFloat(this.formatNumber(this.LineChartDataSolar[0]['solar_exposure'])).toFixed(3)
            ]);
            up = true;
          }
        }
      });

      // this.LineChartDataSolar.forEach(item => {
      //   const newDataTime = item.data_time.split('.')[0];
      //   const lastData = this.chartData['solar_exposure'].slice(-1)[0];
      //   if (!lastData || lastData[0] !== newDataTime) {
      //     this.chartData['solar_exposure'].push([
      //       newDataTime,
      //       parseFloat(this.formatNumber(item.solar_exposure)).toFixed(3)
      //     ]);
      //   }
      // });

      let el = this.$refs.myChart
      const chart = echarts.getInstanceByDom(el);
      if (chart) {
        this.dataZoomStart = chart.getOption().dataZoom[0].start
        this.dataZoomEnd = chart.getOption().dataZoom[0].end;
      }
      
      if (echarts.getInstanceByDom(el)) echarts.getInstanceByDom(el).setOption(this.setOption);
      else echarts.init(el).setOption(this.setOption)
    },
    async initHistory() {
      let vm = this;
      try {
        vm.$loading();
        const parame = {
          'start_date': vm.getCurrentDateFormatted()
        }
        const response = await getChartHistorySunDB(parame);
        if (response.data.Success) {
          const hisData = response.data.Data;
          if (hisData) {
            ['inverter_1', 'inverter_2', 'inverter_3', 'inverter_4', 'inverter_5', 'solar_exposure'].forEach(inverter => {
              if (hisData[inverter]) {
                vm.chartData[inverter].splice(0, 0, ...hisData[inverter]);
              }
            });
          }
        } else {
          vm.$message({ type: 'error', message: response.data.Msg });
        }
      } catch (error) {
        vm.$message({ type: 'error', message: "error" });
      } finally {
        vm.$loading().close();
      }
    },
    formatNumber(value) {
      if(value === 'NaN' || Number.isNaN(value) || value === null || value === undefined){
        return 0;
      }
      return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
  }
};
</script>
<style>
.tipsText{
  font-size:14px;
  color:#666;
  font-weight:400;
  line-height:1;
  display: block;
}
.tipBlock {
  display:block;
  margin-top: 2px;
}
.tipBlockT {
  font-size:14px;
  color:#666;
  font-weight:400;
  margin-left:4px;
}
.tipBlockV {
  font-size:14px;
  color:#666;
  font-weight:900;
  float:right;
  margin-left:20px;
}
.PCSsymbol {
  display:inline-block;
  /* margin-right:4px; */
  border-radius:10px;
  width:10px;
  height:10px;
  background-color:#5470c6;
}
.SOCsymbol {
  display:inline-block;
  /* margin-right:4px; */
  width:10px;
  height:10px;
  background-color:#91cc75;
}
.TMPsymbol {
  display:inline-block;
  /* margin-right:4px; */
  /* background-color:purple; */
  width:0;
  height:0;
  border-width:0 5px 10px ;
  border-style:solid;
  border-color:transparent transparent purple;
}
</style>