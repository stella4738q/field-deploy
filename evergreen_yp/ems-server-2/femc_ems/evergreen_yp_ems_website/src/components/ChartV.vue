<template>
  <div class="row">
    <div class="col-12 col-md-8">
      <div :id="chartId" style="height:500px"></div>
    </div>
    <div class="col-12 col-md-4">
      <div class="mt-3">
        <p>最高電壓：{{ (option?.maxVal / this.dif)?.toFixed(3) }} V</p>
        <p>最高電壓電芯位址： {{ option?.maxPostion }}</p>
        <p>最低電壓：{{ (option?.minVal / this.dif)?.toFixed(3) }} V</p>
        <p>最低電壓電芯位址：{{ option?.minPostion }}</p>
        <p>電壓差：{{ ((option?.maxVal - option?.minVal) / this.dif).toFixed(3) }} V</p>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import UUID from '@/lib/UUID.js';
import { mapState } from "vuex";
let ChartV = null;
export default {
  props: {
    RackData: {
      type: Object,
      default: null,
    },
    dif: {
      type: Number,
      default: 1,
    }
  },
  components: {
    echarts
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    option: function () {
      let maxVal = 0;
      let minVal = 100000;
      let minRange = 0;
      let maxRange = 100000;
      let minPostion = '';
      let maxPostion = '';
      let option = {};
      let Series = [];
      var packObj = this.RackData?.packs ?? this.RackData?.pack_list;
      packObj.forEach((x, ind) => {
        let voltObject = x.cell_volt ?? x.cell_voltage;
        voltObject.forEach((x2, ind2) => {
          let mySeries = Series[ind2];
          if (!mySeries) {
            mySeries = { name: ind2 + 1, type: 'bar', data: [] }
            Series.push(mySeries);
          }
          mySeries.data.push({
            value: x2,
            pack: x.pack_no,
            series: (ind2 + 1),
            itemStyle: {
              color: '#5470C6'
            }
          },)
          if (maxVal < x2) { maxVal = x2; maxPostion = `Pack ${ind + 1} - Cell ${ind2 + 1} ` }
          if (minVal > x2) { minVal = x2; minPostion = `Pack ${ind + 1} - Cell ${ind2 + 1} ` }
        })

      });

      Series.forEach(a => {
        a.data.forEach(b => {
          if (b.value == maxVal || b.value == minVal) {
            b.itemStyle.color = '#EE6666';
          }
          b.value = b.value / this.dif;
        })
      });


      minRange = parseFloat((minVal / this.dif - 0.001).toFixed(3));
      maxRange = parseFloat((maxVal / this.dif + 0.001).toFixed(3));

      option = {
        tooltip: {
          formatter: function (params) {

            return `Pack: ${params.data.pack}<br/>Cell: ${params.data.series}<br/>Voltage: ${params.data.value.toFixed(3)}V`;
          }
        },

        xAxis: { type: 'category', data: Series[0].data.map((x, ind) => { return ind + 1 }) },
        yAxis: { min: minRange, max: maxRange },
        series: Series
      }

      let result = { option, minVal, maxVal, minPostion, maxPostion };
      return result;
    },
  },
  data() {
    return {
      chartId: '',
    };
  },
  mounted() {
    this.initChart();
  },
  beforeUnmount() {
    ChartV = null;
  },
  created() {
    this.chartId = UUID();
  },
  watch: {
    "SocketDataALL": {
      handler: function () {
        this.initChart();
      },
      deep: true,
      immediate: false,
    }
  },
  methods: {

    initChart() {
      const vm = this;
      vm.$nextTick(function () {
        if (!ChartV) {
          ChartV = echarts.init(document.getElementById(vm.chartId));
          window.allCharts.push(ChartV)
        }
        ChartV.setOption(vm.option.option);
        ChartV.resize();
      });
    },
  }
};
</script>
<style>

</style>