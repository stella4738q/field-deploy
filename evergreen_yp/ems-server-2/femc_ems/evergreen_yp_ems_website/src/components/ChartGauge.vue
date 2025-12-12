<template>
  <div :id="ChartId" style="height:130px;width:130px"></div>
</template>

<script >
import resize from 'vue-resize-directive'
import * as echarts from "echarts";
 
    export default {
      props: {
        title: {
          type : String,
          default: '',
        },
        unit: {
          type:String ,
          default:'',
        },
        val: {
          type:Number,
          default: 0,
        },
        color: {
          type: Array,
          default:[[0.3, '#00a8ff'],
                    [0.7, '#44bd32'],
                    [1, '#e84118']],
        },
        height: {
          type:String,
          default:'130px'
        },
        min: {
          type:Number,
          default:0
        },
        max: {
          type:Number,
          default:100
        },
      },
      components: {
         echarts,resize
      },
        data() {
            return {
              ChartObj:null,
              ChartId: '',
            };
        },
        mounted(){
           this.initChart();
        },
        created() {
          this.ChartId = this.getUUID();
        },
        watch: {
          "val" : function (newVal,oldVal) {
            this.initChart();
          }
        },
        computed:{
          setOption:function () {
            return {
              title: {
                    show: true,
                    text: this.title,
                    x: 'center',
                    y: 'bottom',
                    textStyle: {
                        fontSize: 14,
                        fontWeight: "normal",
                    },
                    padding: [0, 0, 10, 0],
                },
                series: [{
                    min: this.min,
                    max: this.max,
                    center: ['50%', '45%'],
                    type: 'gauge',
                    axisLine: {
                        lineStyle: {
                            width: 10,
                            color: this.color
                        }
                    },
                    pointer: {
                        itemStyle: {
                            color: 'auto',
                        }
                    },
                    axisTick: {
                        distance: -10,
                        length: 4,
                        lineStyle: {
                            color: '#fff',
                            width: 1
                        }
                    },
                    splitLine: {
                        distance: -20,
                        length: 20,
                        lineStyle: {
                            color: '#fff',
                            width: 2
                        }
                    },
                    axisLabel: {
                        color: 'auto',
                        distance: 12,
                        fontSize: 7
                    },
                    detail: {
                        valueAnimation: true,
                        formatter: '{value} ' + this.unit,
                        lineHeight: 14,
                        color: 'auto',
                        fontSize: 12,
                        offsetCenter: [0, '70%'],
                    },
                    data: [{
                        value: this.val,
                    }]
                }]
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
            const vm = this;
            this.$nextTick(function () {
              if (!vm.ChartObj){
                vm.ChartObj = echarts.init(document.getElementById(this.ChartId));
              }
              vm.ChartObj.setOption( this.setOption ); 
              vm.ChartObj.resize();
            });
          },
        }
    };
</script>
<style>
</style>