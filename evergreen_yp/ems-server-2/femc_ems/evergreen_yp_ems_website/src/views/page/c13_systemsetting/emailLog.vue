<template>
  <div class="p-3">
    <h3>郵件發送記錄-待實作</h3>
    <div class="d-flex align-items-center mt-3" >
      <el-form :model="Form" ref="Form" :rules="FormRule" :inline="true" label-width="90px">
        <!-- <el-form-item label="報價代碼" prop="case_code" >
          <el-select v-model="Form.case_code" placeholder="請選擇" clearable filterable multiple class="me-2" style="width: 150px">
            <el-option v-for="item in CaseList" :key="item.code" :label="item.label" :value="item.code"> {{ item.code }} - {{ item.service }} </el-option>
          </el-select>
        </el-form-item> -->
        <el-form-item label="時間" prop="date"  >
          <el-date-picker v-model="Form.date" type="daterange" range-separator="To" style="width: 250px" />
        </el-form-item>
        <el-form-item label="">
          <el-button type="primary" @click="SearchClick">
            <font-awesome-icon icon="search" />
          </el-button>
        </el-form-item>
        <el-form-item label="">
          <el-button type="primary" @click="Download" :disabled="PageController.DataSource == 0">
            <font-awesome-icon icon="download" />
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- table -->
    
    <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle">
      <el-table-column label="報價代碼" prop="case_code" align="center"></el-table-column>
      <el-table-column label="服務類型" prop="case_service" align="center"></el-table-column>
      <el-table-column label="調度起始時間" prop="start" align="center"></el-table-column>
      <el-table-column label="調度結束時間" prop="end" align="center"></el-table-column>
      <el-table-column label="調度執行量(MW)" prop="exec_capacity" align="center">
        <template #default="scope">
          {{ scope.row.exec_capacity ? scope.row.exec_capacity.toFixed(1) : '0' }}
        </template>
      </el-table-column>
      <el-table-column label="用電基準量(KW)" prop="cbl" align="center"></el-table-column>
      <el-table-column label="台電通知時間" prop="notify_time" align="center"></el-table-column>
      <el-table-column label="收到指令時間" prop="notify_rcv_time" align="center"></el-table-column>
      <el-table-column label="轉發開始指令時間" prop="mqtt_start_time" align="center"></el-table-column>
      <el-table-column label="轉發開始指令回覆時間" prop="mqtt_start_resp_time" align="center"></el-table-column>
      <el-table-column label="轉發結束指令時間" prop="mqtt_end_time" align="center"></el-table-column>
      <el-table-column label="轉發結束指令回覆時間" prop="mqtt_end_resp_time" align="center"></el-table-column>
    </el-table>
    <!-- pagger  -->
    <div class="d-flex justify-content-end">
      <el-pagination
        layout="prev, pager, next"
        v-model:currentPage="PageController.pageInd"
        :page-size="PageController.countPerPage"
        :total="PageController.DataSource.length"
        @current-change="
          (ind) => {
            PageChanged(ind, PageController);
          }
        "
      />
    </div>
  </div>
</template>

<script>
import { postOperationDispatchingHistory, getCaseOption } from "@/api/Api.js";
import moment from "moment";
import libJsonToCSV from "@/lib/libJsonToCSV.js";

export default {
  components: {},
  data() {
    return {
      moment,
      formLabelWidth: "100px",
      CaseList: [],
      Form: {
        date: [],
        case_code: []
      },
      FormRule: {
        date: [{ required: true, message: " ", trigger: "blur" }]
      },
      PageController: {
        pageInd: 1,
        countPerPage: 10,
        total: 0,
        CurrentData: [],
        DataSource: []
      }
    };
  },
  computed: {
    ApiRequest: function () {
      return {
        postOperationDispatchingHistory: {
          date_start: moment(this.Form.date[0]).format("YYYYMMDD"),
          date_end: moment(this.Form.date[1]).format("YYYYMMDD"),
          case_code: this.Form.case_code.length
            ? this.Form.case_code
            : this.CaseList.map((item) => {
                return item.case_code;
              })
        }
      };
    }
  },
  mounted() {},
  created() {
    // this.getCase();
  },
  watch: {},
  methods: {
    Download() {
      const vm = this;
      let data = [];
      const headerMapping = [
        { key: "case_code", label: "報價代碼" },
        { key: "case_service", label: "服務類型" },
        { key: "start", label: "調度起始時間" },
        { key: "end", label: "調度結束時間" },
        { key: "exec_capacity", label: "調度執行量(MW)" },
        { key: "cbl", label: "用電基準量(kW)" },
        { key: "notify_time", label: "台電通知時間" },
        { key: "notify_rcv_time", label: "收到指令時間" },
        { key: "mqtt_start_time", label: "轉發開始指令時間" },
        { key: "mqtt_start_resp_time", label: "轉發開始指令回覆時間" },
        { key: "mqtt_end_time", label: "轉發結束指令時間" },
        { key: "mqtt_end_resp_time", label: "轉發結束指令回覆時間" }
      ];
      libJsonToCSV(vm.PageController.DataSource, headerMapping, "調度記錄.csv");
    },
    getCase() {
      const vm = this;
      vm.CaseList = [];
      getCaseOption()
        .then((resopnse) => {
          if (resopnse.data.message == "Success") {
            vm.CaseList = resopnse.data.data.filter(x=> { return ['即時備轉容量','補充備轉容量'].includes(x.service)});
          } else {
            vm.$message({ type: "error", message: resopnse.data.message });
          }
        })
        .catch((response) => {
          if (response) vm.$message({ type: "error", message: response.message });
        })
        .finally(() => {});
    },
    getData() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          vm.$loading();
          postOperationDispatchingHistory(vm.ApiRequest.postOperationDispatchingHistory)
            .then((resopnse) => {
              if (resopnse.data.message == "Success") {
                vm.PageController.DataSource = resopnse.data.data;
                vm.PageChanged(1, vm.PageController);
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

    SearchClick() {
      const vm = this;
      vm.getData();
    },
    PageChanged(ind, Controller) {
      Controller.pageInd = ind;
      var sliceBegin = (Controller.pageInd - 1) * Controller.countPerPage;
      var sliceEnd = Controller.pageInd * Controller.countPerPage;
      Controller.CurrentData = Controller.DataSource.slice(sliceBegin, sliceEnd);
    }
  }
};
</script>
