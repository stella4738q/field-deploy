<template>

  <div class="row">
    <div class="col-12 mb-3">
      <!-- <p>最高溫度：{{ option.maxVal?.toFixed(2) }} ℃</p>
      <p>最高溫度電芯位址： {{ option.maxPostion }}</p>
      <p>最低溫度：{{ option.minVal?.toFixed(2) }} ℃</p>
      <p>最低電芯位址：{{ option.minPostion }}</p>
      <p>溫度差：{{ (option.maxVal - option.minVal).toFixed(2) }} ℃</p> -->
      <ul class="chartT_list">
        <li>最高溫度：{{ option.maxVal?.toFixed(0) }} ℃</li>
        <li>最高極柱溫度位址： {{ option.maxPostion }}</li>
        <li>最低溫度：{{ option.minVal?.toFixed(0) }} ℃</li>
        <li>最低極柱溫度位址：{{ option.minPostion }}</li>
        <li>溫度差：{{ (option.maxVal - option.minVal).toFixed(0) }} ℃</li>
      </ul>
    </div>
    <div class="col-12">
      <div style="overflow-x:auto;">
      <div :id="chartId" style="height: 500px; min-width: 900px;"></div>
    </div>
      <div class="mt-3 p-3">
        <p class="m-0"> {{ RangeMin }} </p>
        <el-slider class="" v-model="TempValue" range :min="RangeMin" :max="RangeMax" @change="initChart" />
        <p> {{ RangeMax }} </p>
      </div>
    </div>
  </div>


  <!-- <div class="row ">

    <div class="col col align-self-center mb-5">
      <div class="">
        <p>最高溫度：{{ option.maxVal?.toFixed(2) }} ℃</p>
        <p>最高溫度電芯位址： {{ option.maxPostion }}</p>
        <p>最低溫度：{{ option.minVal?.toFixed(2) }} ℃</p>
        <p>最低電芯位址：{{ option.minPostion }}</p>
        <p>溫度差：{{ (option.maxVal - option.minVal).toFixed(2) }} ℃</p>
      </div>
    </div>
  </div> -->
</template>

<script>
import * as echarts from "echarts";
import UUID from "@/lib/UUID.js";
import { mapState } from "vuex";
import { computed } from 'vue';

let ChartT = null;
export default {
  props: {
    RackData: {
      type: Object,
      default: null,
    },
  },
  components: {
    echarts,
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    option: function () {
      const vm = this;
      var model_y_title = [];
      var data = [];
      var maxVal = 0;
      var minVal = 1000;
      var minPostion = "";
      var maxPostion = "";
      var xLength = 0;
      let option = {};
      var packObj = this.RackData?.pack_list ?? this.RackData?.packs;
      if (packObj) {
        packObj?.forEach((x, ind) => {
          model_y_title.push("Pack " + x.pack_no);
          let tempObj = x.cell_terminal_temp;

          tempObj.forEach((x2, ind2) => {
            data.push([ind2, ind, x2]);
            if (maxVal < x2) {
              maxVal = x2;
              maxPostion = `Pack ${ind + 1} - Point ${ind2 + 1} `;
            }
            if (minVal > x2) {
              minVal = x2;
              minPostion = `Pack ${ind + 1} - Point ${ind2 + 1} `;
            }
          });
        });

        option = {
          tooltip: {
            position: "top",
            formatter: function (params) {
              const pack = params.data[1];
              const serial = params.data[0];
              const temperature = params.data[2];
              return `Pack: ${pack + 1}<br/>Point: ${serial + 1
                }<br/>temperature: ${temperature.toFixed(0)}℃`;
            },
          },
          grid: {
            height: "100%",
            top: "5px",
          },
          xAxis: {
            type: "category",
            data: Array.from({ length: xLength }, (_, index) => index + 1),
          },
          yAxis: {
            type: "category",
            data: model_y_title,
          },
          visualMap: {
            min: this.TempValue[0], //28
            max: this.TempValue[1], //35,
            show: false,
            realtime: true,
            orient: "horizontal",
            left: "center",
            bottom: "0%",
            inRange: {
              color: ["#FFD700", "#FA8072"],
            },
            formatter: "{value}℃",
          },
          series: [
            {
              type: "heatmap",
              data: data,
              label: {
                show: true,
                formatter: function (params) {
                  const value = params.value[2];
                  let color = "black";
                  if (value >= maxVal || value >= vm.TempValue[1]) {
                    color = "darkred";
                  }
                  else if (value <= minVal || value <= vm.TempValue[0]) {
                    color = "blue";
                  }

                  return `{${color}|${value.toFixed(0)}}`;
                },
                rich: {
                  darkred: {
                    color: "darkred",
                    fontSize: 12,
                  },
                  blue: {
                    color: "blue",
                    fontSize: 12,
                  },
                },
              },
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowColor: "rgba(0, 0, 0, 0.5)",
                },
              },
            },
          ],
        };
      }
      return { option, minVal, maxVal, minPostion, maxPostion };
    },
  },
  data() {
    return {
      chartId: "",
      TempValue: [
        20,
        45
      ],
      RangeMax: 50,
      RangeMin: 0,
      // screenWidth: window.innerWidth,
    };
  },
  mounted() {
    this.initChart();
    // this.$nextTick(() => {
    //   window.addEventListener('resize', this.onResize);
    // });
  },
  beforeUnmount() {
    ChartT = null;
  },
  created() {
    this.chartId = UUID();
  },
  watch: {
    SocketDataALL: {
      handler: function () {
        this.initChart();
        this.getTemp();
      },
      deep: true,
      immediate: false,
    },
  },
  methods: {
    initChart() {
      this.$nextTick(function () {
        if (!ChartT) {
          ChartT = echarts.init(document.getElementById(this.chartId));
          window.allCharts.push(ChartT)
        }
        ChartT.setOption(this.option.option);
        ChartT.resize();
      });
    },
    getTemp() {
      var packObj = this.RackData?.pack_list ?? this.RackData?.packs;
      var maxValData = 0;
      var minValData = 1000;
      if (packObj) {
        packObj?.forEach((x, ind) => {
          let tempObj = x.cell_terminal_temp;
          tempObj.forEach((x2, ind2) => {
            if (maxValData < x2) {
              maxValData = x2;
            }
            if (minValData > x2) {
              minValData = x2;
            }
          });
        });
      }
      return [maxValData - 4, maxValData];
    },
  },
};
</script>
<style>
.el-slider__bar {
  background-image: linear-gradient(to right, gold, orangered);

}

.el-slider .el-slider__button-wrapper:nth-child(2) .el-slider__button {
  background-color: gold !important;
  border: unset !important;
}

.el-slider .el-slider__button-wrapper:nth-child(3) .el-slider__button {
  background-color: orangered !important;
  border: unset !important;
}
.chartT_list li{
 display: inline-block;
 margin-right: 10px;
}
</style>
