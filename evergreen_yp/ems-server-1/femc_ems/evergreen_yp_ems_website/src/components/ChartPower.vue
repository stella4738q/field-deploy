<template>
  <div :id="ChartId" ref="myChart" style="height:450px;"></div>
</template>

<script >
import * as echarts from "echarts";
import { getChartHistory } from '@/api/Api.js';
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
      ChartId: 'AdvancedTek_ChartGaugePower',
      moment,
      chartData: {
        'pcs1_power':[],
        'pcs2_power':[],
        'soc':[],
        'temp':[]
      },
      dataZoomStart: 99, //預設往前抓24小時共1440筆，抓1%，顯示最後15筆
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
    LineChartDataPower: {
      handler() {
        this.updateChart();
      },
      deep: true,
    }
  },
  computed: {
    ...mapState(["LineChartDataPower"]),
    setOption: function () {
      var option = {
        // legend: {
        //     data: ['PCS功率', 'SOC', '液冷櫃內溫度']
        // },
        grid: {
          top: '10%',
          bottom: '20%',
          left: '15%',
        },
        tooltip: {
          trigger: 'axis',
          formatter: (function (value) {
            // console.log(value);
            let timeStr = `<div class="tipsText">${value[0].name}</div>`;
            let divStr = '';
            value.forEach((item)=> {
              if(item.seriesName === 'PCS1功率') {
                divStr += `<div class="tipBlock"><span class="PCS1symbol"></span><span class="tipBlockT">${item.seriesName}</span><span class="tipBlockV">${item.data[1]}</span></div>`;
              }
              if(item.seriesName === 'PCS2功率') {
                divStr += `<div class="tipBlock"><span class="PCS2symbol"></span><span class="tipBlockT">${item.seriesName}</span><span class="tipBlockV">${item.data[1]}</span></div>`;
              }
              if(item.seriesName === 'SOC') {
                divStr += `<div class="tipBlock"><span class="SOCsymbol"></span><span class="tipBlockT">${item.seriesName}</span><span class="tipBlockV">${item.data[1]}</span></div>`;
              }
              if(item.seriesName === '液冷櫃內溫度') {
                divStr += `<div class="tipBlock"><span class="TMPsymbol"></span><span class="tipBlockT">${item.seriesName}</span><span class="tipBlockV">${item.data[1]}</span></div>`;
              }
            });
            return `${timeStr}${divStr}`;
          }),
        },
        xAxis: {
          type: 'category',
          // data: this.LineChartDataPower.map(x => { return x.time }),
          axisLine: {
            show: false  // 隱藏 x 軸零線
          },
          axisTick: {
            interval: 'auto',  // 自動計算間隔
            maxInterval: 5,  // 強制顯示所有刻度標籤
          },
          axisLabel: {
            interval: 'auto',  // 自動計算間隔
            maxInterval: 5,  // 強制顯示所有刻度標籤
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
                return value.max + 50;
            },
            min: function(value) {
                return value.min - 50;
            },
            scale: true,
            position: 'left'
          },
          {
            type: 'value',
            max: 100,
            min: 0,
            position: 'right',
          }
        ],
        series: [
          {
            name: 'PCS1功率',
            yAxisIndex: 0,
            data: this.chartData['pcs1_power'],
            type: 'line',
            symbol: 'circle',
            color: '#5470c6',
            symbolSize: 10,
            showSymbol: false
          },
          {
            name: 'PCS2功率',
            yAxisIndex: 0,
            data: this.chartData['pcs2_power'],
            type: 'line',
            symbol: 'circle',
            color: '#cc7307',
            symbolSize: 10,
            showSymbol: false
          },
          {
            name: 'SOC',
            data: this.chartData['soc'],
            type: 'bar',
            symbol: 'square',
            color: '#91cc75',
            symbolSize: 10,
            showSymbol: false,
            yAxisIndex: 1
          },
          {
            name: '液冷櫃內溫度',
            data: this.chartData['temp'],
            yAxisIndex: 1,
            type: 'line',
            color: 'purple',
            symbol: 'triangle',
            symbolSize: 10,
            showSymbol: false
          }
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

        // if (ChartObj) {
        //   ChartObj = echarts.init(document.getElementById(vm.ChartId));
        // }
        // vm.ChartObj.setOption(vm.setOption);
      });
    },
    updateChart() {
      // ChartObj.setOption(this.setOption);

      Object.values(this.chartData).forEach(value => {
        if(value.length > 43200){
          value.shift();
        }
      });
      
      this.chartData['pcs1_power'].push([this.LineChartDataPower[0], this.LineChartDataPower[1]]);
      this.chartData['pcs2_power'].push([this.LineChartDataPower[0], this.LineChartDataPower[2]]);
      this.chartData['soc'].push([this.LineChartDataPower[0], this.LineChartDataPower[3]]);
      this.chartData['temp'].push([this.LineChartDataPower[0], this.LineChartDataPower[4]]);

      let el = this.$refs.myChart
      const chart = echarts.getInstanceByDom(el);
      if (chart) {
        this.dataZoomStart = chart.getOption().dataZoom[0].start
        this.dataZoomEnd = chart.getOption().dataZoom[0].end;
      }
      
      if (echarts.getInstanceByDom(el)) echarts.getInstanceByDom(el).setOption(this.setOption);
      else echarts.init(el).setOption(this.setOption)
    },
    initHistory(){
      let vm = this;
      getChartHistory().then(response => {
        if (response.data.Success) {
          var hisData = response.data.Data;
          if(hisData.pcs_power.length > 0){
            vm.chartData.pcs1_power.splice(0, 0, ...hisData.pcs1_power);
            vm.chartData.pcs2_power.splice(0, 0, ...hisData.pcs2_power);
            vm.chartData.soc.splice(0, 0, ...hisData.soc);
            vm.chartData.temp.splice(0, 0, ...hisData.temp);
          }
        } else {
          vm.$message({ type: 'error', message: response.data.Msg });
        }
      }).catch(response => {
        vm.$message({ type: 'error', message: "error" });
      }).finally(() => {
        vm.$loading().close();
      });
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
.PCS1symbol {
  display:inline-block;
  /* margin-right:4px; */
  border-radius:10px;
  width:10px;
  height:10px;
  background-color:#5470c6;
}
.PCS2symbol {
  display:inline-block;
  /* margin-right:4px; */
  border-radius:10px;
  width:10px;
  height:10px;
  background-color:#cc7307;
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