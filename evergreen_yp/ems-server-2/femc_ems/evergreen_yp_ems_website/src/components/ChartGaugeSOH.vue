<template>
  <div :id="ChartId" style="height:200px;"></div>
</template>

<script >
import * as echarts from "echarts";

export default {
  props: {
    socketData: {
      type: Number,
      default: null,
    }
  },
  components: {
    echarts
  },
  data() {
    return {
      ChartObj: null,
      ChartId: 'TASCO_ChartGaugeSOH',
    };
  },
  computed: {
    setOption: function () {
      return {
        series: [
          {
            type: 'gauge',
            axisLine: {
              lineStyle: {
                width: 10,
                color: [

                  [1, 'limegreen']
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
              offsetCenter: [0, '70%'],
            },
            data: [
              {
                value: [null, undefined].includes(this.socketData) ? null : this.socketData.toFixed(2),
                name:'SOH',
                 title: {
                  offsetCenter: ['0%', '100%']
                },
              }
            ]
          }
        ]
      }
    }

  },
  mounted() {
    this.initChart();
  },
  created() {
    this.ChartId = this.getUUID();
  },
  watch: {
    "socketData": {
      handler: function () {
        this.initChart();
      },
      deep: true,
      immediate: false,
    }
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