<template>
  <div class="p-3 card border-0 shadow-sm">
    <div class="card-body">
      <h1 class="mb-2">BMS歷史記錄</h1>
      <div class="d-flex justify-content-between align-items-center mt-3">
      <el-form :model="Form" ref="Form" :rules="FormRule" label-width="auto" inline>
        <el-form-item label="時間區間" prop="daterange">
          <el-date-picker v-model="Form.daterange" type="datetimerange" placeholder="請選擇日期時間" value-format="YYYYMMDDHHmmss"></el-date-picker>
        </el-form-item>
        <el-form-item label="數據類型" prop="type">
          <el-select v-model="Form.type" placeholder="請選擇" @change="TypeOnChange">
            <el-option v-for="(item, index) in typeData" :key="index" :label="item.name" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Rack" prop="rack" v-if="Form.type != 'current'">
          <el-select v-model="Form.rack" placeholder="請選擇" clearable>
            <el-option v-for="(item, index) in SocketDataALL?.bms[0]?.rack" :key="index" :label="item.equipment_id" :value="index + 1"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Pack" prop="pack" v-if="Form.type != 'current'">
          <el-select v-model="Form.pack" placeholder="請選擇" clearable>
            <el-option v-for="(item, index) in packs" :key="index" :label="item.name" :value="index + 1"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <div class="text-center">
            <el-button class="btn btn-primary btn-sm" :disabled="sendCheck" @click="SearchClick">
              <font-awesome-icon icon="search" />
            </el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <div class="text-center">
            <el-button class="btn btn-primary btn-sm" :disabled="sendCheck" @click="DownloadCSV">
              <font-awesome-icon icon="download" />
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
     <!---------------------------------------------------------------------->
    <div id="RunChart" ref="RunChart" style="height: 300px"></div>
    </div>
    <!---------------------------------------------------------------------->
    <!-- <pre>{{ apiTableData }}</pre> -->
    <el-table id="bmsHistoryTable" :data="apiTableData" size="small" height="350" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle2">
      <el-table-column v-for="(col, index) in tableHeader" :key="index" :min-width="index === 0 ? 140 : 90" :prop="col" :label="col" :fixed="index === 0" show-overflow-tooltip sortable></el-table-column>
    </el-table>
  </div>
</template>
<script>
import moment, { duration } from "moment";
import * as echarts from "echarts";
import { getBMUGetData, getBMUGetDataDownload } from "@/api/Api.js";
import libDownload from "@/lib/libDownload.js";
import { mapState } from "vuex";
var RunChart = null;

export default {
  components: {},
  data() {
    return {
      moment,
      today: moment().startOf("day"),
      typeData: [
        { name: "溫度", value: "temp" },
        { name: "電壓", value: "voltage" },
        { name: "電流", value: "current" }
      ],
      packs: [
        { name: "pack1", value: "1" },
        { name: "pack2", value: "2" },
        { name: "pack3", value: "3" },
        { name: "pack4", value: "4" },
        { name: "pack5", value: "5" },
        { name: "pack6", value: "6" },
        { name: "pack7", value: "7" },
        { name: "pack8", value: "8" },
        { name: "pack9", value: "9" },
        { name: "pack10", value: "10" },
        { name: "pack11", value: "11" },
        { name: "pack12", value: "12" },
        { name: "pack13", value: "13" },
        { name: "pack14", value: "14" },
        { name: "pack15", value: "15" },
        { name: "pack16", value: "16" },
        { name: "pack17", value: "17" },
        { name: "pack18", value: "18" },
        { name: "pack19", value: "19" },
        { name: "pack20", value: "20" }
      ],
      ApiResult: {
        datetime: []
        // "rack": [],
        // "pack": [],
      },
      Form: {
        daterange: [moment().add(-1, "day").startOf("day").format("YYYYMMDDHHmmss"), moment().add(-1, "day").endOf("day").format("YYYYMMDDHHmmss")],
        // daterange: ['20240605070000', '20240605080000'],
        type: "",
        rack: "",
        pack: ""
      },
      PostData: {
        type: "",
        rack: "",
        pack: "",
        dateBegin: "",
        level: "",
        bmsFileName: "",
        dateEnd: ""
      },
      FormRule: {
        type: [{ type: "string", required: true, message: " ", trigger: "blur" }],
        daterange: [{ type: "array", required: true, message: " ", trigger: "blur" }]
      },
      tableHeader: [],
      apiTableData: [],
    };
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    sendCheck() {
      const vm = this;
      let dis = true;
      let nullVal = 0;
      let req = ['daterange', 'type'];
      req.forEach((kkk) => {
        if (kkk === 'daterange') {
          if(!vm.Form[kkk][0]) {
            nullVal += 1;
          }
          if(!vm.Form[kkk][1]) {
            nullVal += 1;
          }
        } else {
          if(!vm.Form[kkk]) {
            nullVal += 1;
          }
        }
      });
      if(nullVal === 0) {
        dis = false;
      }
      return dis;
    },
  },
  mounted() {
    RunChart = echarts.init(this.$refs.RunChart);
  },
  beforeUnmount() {
    RunChart = null;
  },
  created() {},
  watch: {},
  methods: {
    TypeOnChange() {
      if (this.Form.type == "current") {
        this.Form.rack = "";
        this.Form.pack = "";
      }
    },
    setChart() {
      const vm = this;
      // 提取日期和數值
      const datetime = vm.ApiResult.data.find((item) => item.name === "datetime").data;
      const seriesData = vm.ApiResult.data
        .filter((item) => item.name !== "datetime")
        .map((item) => {
          let dataSource = [];
          if (vm.PostData.level != "rack" && vm.PostData.type == "voltage") {
            dataSource = item.data.map((x) => {
              return x.toFixed(3);
            });
          } else {
            dataSource = item.data.map((x) => {
              return x.toFixed(3);
            });
          }

          return {
            data: dataSource,
            type: "line",
            showSymbol: false,
            name: item.name
          };
        });

        let maxVal = -99999999;
        let minVal = 999999;
        seriesData.forEach(element => {
          element.data.forEach(x=> {
            if (x > maxVal ) maxVal = x;
            if (x < minVal ) minVal = x;
          })
        });

      const legend = seriesData.map((x) => x.name);
      RunChart.clear();
      RunChart.resize();
      RunChart.setOption({
        dataZoom: [
          {
            type: "inside",
            start: 0,
            end: 100
          }
        ],
        legend: {
          x: "center",
          y: "bottom",
          data: legend
        },
        grid: {
          top: "10%",
          bottom: "20%"
        },
        tooltip: {
          trigger: "axis"
        },
        toolbox: {
          left: "center",
          feature: {
            saveAsImage: { title: "另存圖片", show: true },
            dataView: { title: "數據表", show: true, lang: ["數據表", "關閉", "重新載入"] }
          }
        },
        xAxis: {
          type: "category",
          data: datetime,
        },
        yAxis: {
          type: "value",
          // max:maxVal,
          min:minVal,
        },
        series: seriesData
      });
    },
    tableData() {
      const vm = this;
      vm.apiTableData = [];
      const headerName = vm.ApiResult.data.map((item) => item.name);
      const datetime = vm.ApiResult.data.find((item) => item.name === "datetime").data;
      //
      datetime.forEach((oneDate, index) => {
        let obj = {
          datetime: oneDate,
        };
        headerName.forEach((key) => {
          if (key !== 'datetime') {
            let cellData = vm.ApiResult.data.find((item) => item.name === key).data;
            obj[key] = cellData[index];
          }
        });
        this.apiTableData.push(obj);
      });
    },
    SearchClick() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          vm.$loading();
          let setLevel = "rack"; //rack/pack/cell
          if (vm.Form.rack !== "") setLevel = "pack";
          if (vm.Form.pack !== "") setLevel = "cell";
          vm.PostData = {
            type: vm.Form.type,
            rack: vm.Form.rack,
            pack: vm.Form.pack,
            dateBegin: vm.Form.daterange[0],
            level: setLevel,
            bmsFileName: `bmu_${vm.SocketDataALL.bms[0].equipment_id}`,
            dateEnd: vm.Form.daterange[1]
          };
          getBMUGetData(vm.PostData)
            .then((resopnse) => {
              if (resopnse.data.message == "Success") {
                vm.ApiResult = resopnse.data;
                vm.tableHeader = resopnse.data.data.map((item) => item.name);
                vm.setChart();
                vm.tableData();
              } else {
                vm.$message({ type: "error", message: resopnse.data.message });
              }
            })
            .catch((resopnse) => {
              vm.$message({ type: "error", message: resopnse.message });
            })
            .finally(() => {
              vm.$loading().close();
            });
        }
      });
    },
    // ExportClick() {

    // },
    DownloadCSV() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          vm.$loading();
          let setLevel = "rack"; //rack/pack/cell
          if (vm.Form.rack !== "") setLevel = "pack";
          if (vm.Form.pack !== "") setLevel = "cell";
          vm.PostData = {
            type: vm.Form.type,
            rack: vm.Form.rack,
            pack: vm.Form.pack,
            dateBegin: vm.Form.daterange[0],
            level: setLevel,
            bmsFileName: `bmu_${vm.SocketDataALL.bms[0].equipment_id}`,
            dateEnd: vm.Form.daterange[1]
          };
          getBMUGetDataDownload(vm.PostData)
            .then((resopnse) => {
              // if (resopnse.data.message == "Success") {
              //   let fileName = `BMS紀錄_${vm.moment(vm.Form.daterange[0]).format("YYYYMMDD")}-${vm.moment(vm.Form.daterange[1]).format("YYYYMMDD")}`;
              //   libDownloadTxtCSV(resopnse.data.data, fileName);
              // } else {
              //   vm.$message({ type: "error", message: resopnse.data.message });
              // }
              let fileName = `BMS紀錄_${vm.moment(vm.Form.daterange[0], 'YYYYMMDDHHmmss').format("YYYYMMDD")}-${vm.moment(vm.Form.daterange[1], 'YYYYMMDDHHmmss').format("YYYYMMDD")}.csv`;
              libDownload(resopnse, fileName);
            })
            .catch((resopnse) => {
              vm.$message({ type: "error", message: resopnse.message });
            })
            .finally(() => {
              vm.$loading().close();
            });
        }
      });
    },
  }
};
</script>
<style></style>
