<template>
  <div :id="ChartId" style="height:250px;"></div>
</template>

<script >
import * as echarts from "echarts";
import { mapState } from "vuex";

export default {
  props: { 
    socketData: {
      type: Object,
      required: false
    }
  },
  components: {
    echarts
  },
  data() {
    return {
      ChartObj: null,
      ChartId: 'TASCO_ChartGaugeSOC',
    };
  },
  mounted() {
    this.initChart();
  },
  created() {
    this.ChartId = this.getUUID();
  },
  watch: {
    socketData: {
      handler() {
        this.initChart();
      },
      deep: true
    }
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    setOption: function () {
      return {
        title: {
          text: 'SOC',
          textStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          top: '0',
          left: 'center'
        },
        grid: {
          top: '10%',
          bottom: '10%',
        },
        series: [
          {
            type: 'gauge',
            axisLine: {
              lineStyle: {
                width: 10,
                color: [
                  [0.1, '#fd666d'],
                  [0.47, 'gold'],
                  [0.9, 'limegreen'],
                  [1, 'silver'],
                ]
              }
            },
            pointer: {
              itemStyle: {
                color: 'auto'
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
              distance: -30,
              length: 30,
              lineStyle: {
                color: '#fff',
                width: 2
              }
            },
            axisLabel: {
              color: 'auto',
              distance: 15,
              fontSize: 10
            },
            detail: {
              valueAnimation: true,
              formatter: '{value}%',
              color: 'auto',
              fontSize: 20,
              offsetCenter: [0, '50%'],
            },
            data: [
              {
                value: Number(this.socketData?.soc ?? 0).toFixed(2),
                name: 'SOH: ' + (this.socketData?.soh ?? '--') + '%',
                title: {
                  offsetCenter: ['0%', '100%']
                },
              },
            ]
          }
        ]
      }
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
        if (!vm.ChartObj) {
          vm.ChartObj = echarts.init(document.getElementById(vm.ChartId));
        }
        vm.ChartObj.setOption(vm.setOption);
      });
    },
  }
};
</script>
<style></style>