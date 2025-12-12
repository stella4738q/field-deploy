<template>
  <p class="chartName text-center">{{ chartObj.name }}</p>
  <!-- <p class="chartName text-center">Meter-{{ chartObj.equipment_id }}</p> -->
  <p class="chartName text-center">{{ Object.keys(name).indexOf(chartObj.equipment_id) === -1 ? chartObj.equipment_id : name[chartObj.equipment_id] }}</p>
  <div :id="ChartId" style="height:200px"></div>
</template>

<script >
import * as echarts from "echarts";
import echartsGL from 'echarts-gl';

    export default {
      props: {
         chartObj: {
          type:Object,
          default:{  }
         }
      },
      components: {
         echarts
      },
        data() {
            return {
              ChartId: '',
              Chart: null,
              max_A:1587,
              max_V:11800,
              max_K:1575,
              max_Q:100,
              max_S:100,
              name: {
                METER_MAIN: '高壓總錶',
                METER_SUN1: '太陽能電錶1',
                METER_SUN2: '太陽能電錶2',
                METER_VCB: 'VCB電錶',
                METER_MP1: 'BESS-MPA',
                METER_MP2: 'BESS-MPB',
              },
            };
        },
        mounted(){
           this.initChart();
        },
        created() {
          this.ChartId = this.getUUID();
        },
        watch: {
           "chartObj" :  {
            handler: function () {
              this.reSetData();
            },
            deep:true,
            immediate:false,
          }
        },
        computed:{ 
          setOption:function () { 
            
            var _data = []
            if (this.chartObj.equipment_id == 'METER_SUN'){
              _data = [
                        {
                          //電流小數1位
                          value: this.chartObj.ampere ? (this.chartObj.ampere / this.max_A) * 100 : 0,
                          name: (this.chartObj.ampere ? this.chartObj.ampere.toFixed(1).toLocaleString() : 0) +' A',
                          title: { fontSize: 18, offsetCenter: ['0%', '0%'],color:"blueviolet" },
                          itemStyle: { color: 'blueviolet'  },
                        },
                        {
                          //電壓小數1位
                          value: this.chartObj.voltage ? (this.chartObj.voltage / this.max_V) * 100 : 0,
                          name: (this.chartObj.voltage ? this.chartObj.voltage.toFixed(1).toLocaleString() : 0) +' V',
                          title: { fontSize: 18, offsetCenter: ['0%', '-20%'],color:"darkorange" },
                          itemStyle: { color: 'darkorange'  },
                        },
                        {
                          value: this.chartObj.kW ? (this.chartObj.kW / this.max_K) * 100 : 0,
                          name: (this.chartObj.kW ? this.chartObj.kW.toFixed(2).toLocaleString() : 0) +' kW',
                          title: { fontSize: 18, offsetCenter: ['0%', '-40%'] ,color:"#00a8ff" },
                          itemStyle: { color: '#00a8ff'  },
                        },
                        {
                          //功率因數以 PF 0.XX 顯示
                          value: this.chartObj.pf_total ? this.chartObj.pf_total  : 0,
                          name: 'PF ' + (this.chartObj.pf_total ? (this.chartObj.pf_total).toFixed(2) : 0),
                          title: { fontSize: 18, offsetCenter: ['0%', '20%'],color:"green" },
                          itemStyle: { color: 'green'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.imp_kwh ? this.chartObj.imp_kwh > 999999 ? (this.chartObj.imp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-imp' : (this.chartObj.imp_kwh.toFixed(0).toLocaleString() + ' KWh-imp') : '0 KWh-imp',
                          title: { fontSize: 18, offsetCenter: ['0%', '40%'],color:"teal" },
                          itemStyle: { color: 'teal'  },
                        }
                      ]
            }
            else if(this.chartObj.equipment_id == 'METER_MAIN'){
              _data = [
                        {
                          //電流小數1位
                          value: this.chartObj.ampere ? (this.chartObj.ampere / this.max_A) * 100 : 0,
                          name: (this.chartObj.ampere ? this.chartObj.ampere.toFixed(1).toLocaleString() : 0) +' A',
                          title: { fontSize: 18, offsetCenter: ['0%', '-10%'],color:"blueviolet" },
                          itemStyle: { color: 'blueviolet'  },
                        },
                        {
                          //電壓顯示KV且不需小數位
                          value: this.chartObj.voltage ? (this.chartObj.voltage / this.max_V) * 100 : 0,
                          name: (this.chartObj.voltage ? (this.chartObj.voltage / 1000).toFixed(1).toLocaleString() : 0) +' kV',
                          title: { fontSize: 18, offsetCenter: ['0%', '-30%'],color:"darkorange" },
                          itemStyle: { color: 'darkorange'  },
                        },
                        {
                          //KW不用小數位
                          value: this.chartObj.kW ? (this.chartObj.kW / this.max_K) * 100 : 0,
                          name: (this.chartObj.kW ? this.chartObj.kW.toFixed(0).toLocaleString() : 0) +' kW',
                          title: { fontSize: 18, offsetCenter: ['0%', '-50%'] ,color:"#00a8ff" },
                          itemStyle: { color: '#00a8ff'  },
                        },
                        {
                          //功率因數以PF 0.XX顯示
                          value: this.chartObj.pf_total ? this.chartObj.pf_total  : 0,
                          name: 'PF ' + (this.chartObj.pf_total ? (this.chartObj.pf_total).toFixed(2) : 0),
                          title: { fontSize: 18, offsetCenter: ['0%', '10%'],color:"green" },
                          itemStyle: { color: 'green'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.imp_kwh ? this.chartObj.imp_kwh > 999999 ? (this.chartObj.imp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-imp' : (this.chartObj.imp_kwh.toFixed(0).toLocaleString() + ' KWh-imp') : '0 KWh-imp',
                          title: { fontSize: 18, offsetCenter: ['0%', '30%'],color:"teal" },
                          itemStyle: { color: 'teal'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.exp_kwh ? this.chartObj.exp_kwh > 999999 ? (this.chartObj.exp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-exp' : (this.chartObj.exp_kwh.toFixed(0).toLocaleString() + ' KWh-exp') : '0 KWh-exp',
                          title: { fontSize: 18, offsetCenter: ['0%', '50%'],color:"gray" },
                          itemStyle: { color: 'gray'  },
                        }
                      ]
            }
            else if(this.chartObj.equipment_id == 'METER_FACTORY'){
              _data = [
                        {
                          //電流小數1位
                          value: this.chartObj.ampere ? (this.chartObj.ampere / this.max_A) * 100 : 0,
                          name: (this.chartObj.ampere ? this.chartObj.ampere.toFixed(1).toLocaleString() : 0) +' A',
                          title: { fontSize: 18, offsetCenter: ['0%', '-10%'],color:"blueviolet" },
                          itemStyle: { color: 'blueviolet'  },
                        },
                        {
                          //電壓小數1位
                          value: this.chartObj.voltage ? (this.chartObj.voltage / this.max_V) * 100 : 0,
                          name: (this.chartObj.voltage ? this.chartObj.voltage.toFixed(1).toLocaleString() : 0) +' V',
                          title: { fontSize: 18, offsetCenter: ['0%', '-30%'],color:"darkorange" },
                          itemStyle: { color: 'darkorange'  },
                        },
                        {
                          value: this.chartObj.kW ? (this.chartObj.kW / this.max_K) * 100 : 0,
                          name: (this.chartObj.kW ? this.chartObj.kW.toFixed(2).toLocaleString() : 0) +' kW',
                          title: { fontSize: 18, offsetCenter: ['0%', '-50%'] ,color:"#00a8ff" },
                          itemStyle: { color: '#00a8ff'  },
                        },
                        {
                          //功率因數以 PF 0.XX顯示
                          value: this.chartObj.pf_total ? this.chartObj.pf_total  : 0,
                          name: 'PF ' + (this.chartObj.pf_total ? (this.chartObj.pf_total).toFixed(2) : 0),
                          title: { fontSize: 18, offsetCenter: ['0%', '10%'],color:"green" },
                          itemStyle: { color: 'green'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.imp_kwh ? this.chartObj.imp_kwh > 999999 ? (this.chartObj.imp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-imp' : (this.chartObj.imp_kwh.toFixed(0).toLocaleString() + ' KWh-imp') : '0 KWh-imp',
                          title: { fontSize: 18, offsetCenter: ['0%', '30%'],color:"teal" },
                          itemStyle: { color: 'teal'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.exp_kwh ? this.chartObj.exp_kwh > 999999 ? (this.chartObj.exp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-exp' : (this.chartObj.exp_kwh.toFixed(0).toLocaleString() + ' KWh-exp') : '0 KWh-exp',
                          title: { fontSize: 18, offsetCenter: ['0%', '50%'],color:"gray" },
                          itemStyle: { color: 'gray'  },
                        }
                      ]
            }
            else if(this.chartObj.equipment_id == 'METER_CABINET'){
              _data = [
                        {
                          //電流小數1位
                          value: this.chartObj.ampere ? (this.chartObj.ampere / this.max_A) * 100 : 0,
                          name: (this.chartObj.ampere ? this.chartObj.ampere.toFixed(1).toLocaleString() : 0) +' A',
                          title: { fontSize: 18, offsetCenter: ['0%', '-10%'],color:"blueviolet" },
                          itemStyle: { color: 'blueviolet'  },
                        },
                        {
                          //電壓小數1位
                          value: this.chartObj.voltage ? (this.chartObj.voltage / this.max_V) * 100 : 0,
                          name: (this.chartObj.voltage ? this.chartObj.voltage.toFixed(1).toLocaleString() : 0) +' V',
                          title: { fontSize: 18, offsetCenter: ['0%', '-30%'],color:"darkorange" },
                          itemStyle: { color: 'darkorange'  },
                        },
                        {
                          value: this.chartObj.kW ? (this.chartObj.kW / this.max_K) * 100 : 0,
                          name: (this.chartObj.kW ? this.chartObj.kW.toFixed(2).toLocaleString() : 0) +' kW',
                          title: { fontSize: 18, offsetCenter: ['0%', '-50%'] ,color:"#00a8ff" },
                          itemStyle: { color: '#00a8ff'  },
                        },
                        {
                          //功率因數以 PF 0.XX 顯示
                          value: this.chartObj.pf_total ? this.chartObj.pf_total  : 0,
                          name: 'PF ' + (this.chartObj.pf_total ? (this.chartObj.pf_total).toFixed(2) : 0),
                          title: { fontSize: 18, offsetCenter: ['0%', '10%'],color:"green" },
                          itemStyle: { color: 'green'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.imp_kwh ? this.chartObj.imp_kwh > 999999 ? (this.chartObj.imp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-imp' : (this.chartObj.imp_kwh.toFixed(0).toLocaleString() + ' KWh-imp') : '0 KWh-imp',
                          title: { fontSize: 18, offsetCenter: ['0%', '30%'],color:"teal" },
                          itemStyle: { color: 'teal'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.exp_kwh ? this.chartObj.exp_kwh > 999999 ? (this.chartObj.exp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-exp' : (this.chartObj.exp_kwh.toFixed(0).toLocaleString() + ' KWh-exp') : '0 KWh-exp',
                          title: { fontSize: 18, offsetCenter: ['0%', '50%'],color:"gray" },
                          itemStyle: { color: 'gray'  },
                        }
                      ]
            }
            else if(this.chartObj.equipment_id == 'METER_VCB'){
               _data = [
                        {
                          //電流小數1位
                          value: this.chartObj.ampere ? (this.chartObj.ampere / this.max_A) * 100 : 0,
                          name: (this.chartObj.ampere ? this.chartObj.ampere.toFixed(1).toLocaleString() : 0) +' A',
                          title: { fontSize: 18, offsetCenter: ['0%', '-10%'],color:"blueviolet" },
                          itemStyle: { color: 'blueviolet'  },
                        },
                        {
                          //電壓顯示KV且不需小數位
                          value: this.chartObj.voltage ? (this.chartObj.voltage / this.max_V) * 100 : 0,
                          name: (this.chartObj.voltage ? (this.chartObj.voltage / 1000).toFixed(1).toLocaleString() : 0) +' kV',
                          title: { fontSize: 18, offsetCenter: ['0%', '-30%'],color:"darkorange" },
                          itemStyle: { color: 'darkorange'  },
                        },
                        {
                          //KW不用小數位
                          value: this.chartObj.kW ? (this.chartObj.kW / this.max_K) * 100 : 0,
                          name: (this.chartObj.kW ? this.chartObj.kW.toFixed(0).toLocaleString() : 0) +' kW',
                          title: { fontSize: 18, offsetCenter: ['0%', '-50%'] ,color:"#00a8ff" },
                          itemStyle: { color: '#00a8ff'  },
                        },
                        {
                          //功率因數以PF 0.XX顯示
                          value: this.chartObj.pf_total ? this.chartObj.pf_total  : 0,
                          name: 'PF ' + (this.chartObj.pf_total ? (this.chartObj.pf_total).toFixed(2) : 0),
                          title: { fontSize: 18, offsetCenter: ['0%', '10%'],color:"green" },
                          itemStyle: { color: 'green'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.imp_kwh ? this.chartObj.imp_kwh > 999999 ? (this.chartObj.imp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-imp' : (this.chartObj.imp_kwh.toFixed(0).toLocaleString() + ' KWh-imp') : '0 KWh-imp',
                          title: { fontSize: 18, offsetCenter: ['0%', '30%'],color:"teal" },
                          itemStyle: { color: 'teal'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.exp_kwh ? this.chartObj.exp_kwh > 999999 ? (this.chartObj.exp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-exp' : (this.chartObj.exp_kwh.toFixed(0).toLocaleString() + ' KWh-exp') : '0 KWh-exp',
                          title: { fontSize: 18, offsetCenter: ['0%', '50%'],color:"gray" },
                          itemStyle: { color: 'gray'  },
                        }
                      ]
            }
            else {
              _data = [
                        {
                          value: this.chartObj.ampere ? (this.chartObj.ampere / this.max_A) * 100 : 0,
                          name: (this.chartObj.ampere ? this.chartObj.ampere.toFixed(2).toLocaleString() : 0) +' A',
                          title: { fontSize: 18, offsetCenter: ['0%', '-10%'],color:"blueviolet" },
                          itemStyle: { color: 'blueviolet'  },
                        },
                        {
                          value: this.chartObj.voltage ? (this.chartObj.voltage / this.max_V) * 100 : 0,
                          name: (this.chartObj.voltage ? this.chartObj.voltage.toFixed(2).toLocaleString() : 0) +' V',
                          title: { fontSize: 18, offsetCenter: ['0%', '-30%'],color:"darkorange" },
                          itemStyle: { color: 'darkorange'  },
                        },
                        {
                          value: this.chartObj.kW ? (this.chartObj.kW / this.max_K) * 100 : 0,
                          name: (this.chartObj.kW ? this.chartObj.kW.toFixed(2).toLocaleString() : 0) +' kW',
                          title: { fontSize: 18, offsetCenter: ['0%', '-50%'] ,color:"#00a8ff" },
                          itemStyle: { color: '#00a8ff'  },
                        },
                        {
                          value: this.chartObj.pf_total ? this.chartObj.pf_total  : 0,
                          name: 'PF ' + (this.chartObj.pf_total ? (this.chartObj.pf_total).toFixed(2) : 0),
                          title: { fontSize: 18, offsetCenter: ['0%', '10%'],color:"green" },
                          itemStyle: { color: 'green'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.imp_kwh ? this.chartObj.imp_kwh > 999999 ? (this.chartObj.imp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-imp' : (this.chartObj.imp_kwh.toFixed(0).toLocaleString() + ' KWh-imp') : '0 KWh-imp',
                          title: { fontSize: 18, offsetCenter: ['0%', '30%'],color:"teal" },
                          itemStyle: { color: 'teal'  },
                        },
                        {
                          value: 0,
                          name: this.chartObj.exp_kwh ? this.chartObj.exp_kwh > 999999 ? (this.chartObj.exp_kwh / 1000).toFixed(0).toLocaleString() + ' MWH-exp' : (this.chartObj.exp_kwh.toFixed(0).toLocaleString() + ' KWh-exp') : '0 KWh-exp',
                          title: { fontSize: 18, offsetCenter: ['0%', '50%'],color:"gray" },
                          itemStyle: { color: 'gray'  },
                        }
                      ]
            }

            return {
                      series: [  
                        {
                          radius: '100%',
                          data: _data,
                          type: 'gauge',
                          startAngle: 90,
                          endAngle: -270,
                          pointer: {
                            show: false
                          },
                          progress: {
                            show: true,
                            overlap: false,
                            roundCap: true,
                            clip: false,
                            itemStyle: {
                              borderWidth: 0, 
                            }
                          },
                          axisLine: {
                            lineStyle: {
                              width: 10, 
                            }
                          },
                          splitLine: {
                            show: false,
                            distance: 0,
                            length: 10
                          },
                          axisTick: {
                            show: false
                          },
                          axisLabel: {
                            show: false,
                            distance: 50
                          },
                          
                          title: {
                            fontSize: 12
                          },
                          detail: {
                            show:false,
                          }
                        }
                      ]
                    }
          }
        },
        methods: {
          getUUID() {
            var d = Date.now();
            if (typeof performance !== 'undefined' && typeof performance.now === 'function'){
              d += performance.now(); //use high-precision timer if available
            }
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
              var r = (d + Math.random() * 16) % 16 | 0;
              d = Math.floor(d / 16);
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
          },
          initChart(){
            this.$nextTick(function () {
              this.Chart = echarts.init(document.getElementById(this.ChartId));
              this.Chart.setOption( this.setOption ); 
              this.Chart.resize();
            });
          },
          reSetData() {
              this.Chart.setOption( this.setOption ); 
              this.Chart.resize();
          }
        }
    };
</script>
<style>
</style>