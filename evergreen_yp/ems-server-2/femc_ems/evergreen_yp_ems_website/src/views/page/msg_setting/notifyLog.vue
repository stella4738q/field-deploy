<template>
  <div class="p-2">
    <h3>發送記錄</h3>
    <div class="d-flex align-items-center mt-3">
      <el-form :model="Form" ref="Form" inline>
        <el-form-item label="時間" prop="date" :rules="[{ required: true, message: '請選擇時間範圍', trigger: 'change' }]">
          <el-date-picker v-model="Form.date" type="daterange" range-separator="To" style="width: 280px" />
        </el-form-item>
        <el-form-item label="規則" prop="rule_id">
          <el-select v-model="Form.rule_id" placeholder="請選擇" clearable filterable class="me-2" style="width: 100%">
            <el-option v-for="item in RuleList" :key="item._id" :label="item.code + '  ' + item.name" :value="item._id"> </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="通知群組" prop="token_id">
          <el-select v-model="Form.token_id" placeholder="請選擇" clearable filterable class="me-2" style="width: 100%">
            <el-option v-for="item in TokenList" :key="item._id" :label="item.name" :value="item._id"> </el-option>
          </el-select>
        </el-form-item>
        <!-- <el-form-item label="報價代碼" prop="case_id">
          <el-select v-model="Form.case_id" placeholder="請選擇" clearable filterable class="me-2" style="width: 140px">
            <el-option v-for="item in CaseList" :key="item.case_id" :label="item.case_name" :value="item.case_id"> {{ item.case_name }} </el-option>
          </el-select>
        </el-form-item> -->
        <el-form-item label="">
          <el-button type="primary" @click="SearchClick">
            <font-awesome-icon icon="search" />
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- table -->

    <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle">
      <el-table-column label="發送時間" width="140" prop="datetime" align="center">
        <template #default="scope">
          {{ scope.row.datetime ? moment(scope.row.datetime).format("YYYY-MM-DD HH:mm:ss") : scope.row.datetime }}
        </template>
      </el-table-column>
      <!-- <el-table-column label="報價代碼" prop="case_name" align="center"></el-table-column> -->
      <!-- <el-table-column label="案場名稱" prop="field_name" align="center"></el-table-column> -->
      <el-table-column label="規則" width="180" prop="rule_name" align="center"></el-table-column>
      <el-table-column label="群組" width="250" prop="token_name" align="center"></el-table-column>
      <el-table-column label="是否發送成功" width="100" prop="success" align="center">
        <template #default="scope">
          {{ scope.row.success ? '是' : '否' }}
        </template>
      </el-table-column>
      <el-table-column label="訊息內容" min-width="100" prop="message" align="center"></el-table-column>
      <el-table-column label="發送失敗原因" prop="fail_message" align="center"></el-table-column>
      <!-- <el-table-column label="調度執行量(MW)" prop="exec_capacity" align="center">
        <template #default="scope">
          {{ scope.row.exec_capacity ? scope.row.exec_capacity.toFixed(1) : "0" }}
        </template>
      </el-table-column> -->
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
import { getCaseOption, getFemcNotifyRule, getFemcNotifyToken, getFemcNotifyLog } from "@/api/Api.js";

import moment from "moment";

export default {
  components: {},
  data() {
    let now = new Date();
    let yesterday = new Date();
    yesterday.setDate(now.getDate() - 1);
    yesterday.setHours(0, 0, 0, 0);

    return {
      moment,
      // CaseList: [],
      TokenList: [],
      RuleList: [],
      Form: {
        date: [
          yesterday,
          now
        ],
        // case_id: null,
        token_id: null,
        rule_id: null
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
        getNotifyLog: {
          start_date: this.Form.date[0] ? moment(this.Form.date[0]).format("YYYYMMDD") : null,
          end_date: this.Form.date[1] ? moment(this.Form.date[1]).format("YYYYMMDD") : null,
          // case_id: this.Form.case_id,
          rule_id: this.Form.rule_id,
          token_id: this.Form.token_id
        }
      };
    }
  },
  mounted() {},
  created() {
    // this.getCaseOption(); //getCaseOption, getNotifyRule, getNotifyToken, getNotifyLog
    this.getNotifyRule();
    this.getNotifyToken();
  },
  watch: {},
  methods: {
    getNotifyToken() {
      const vm = this;
      vm.TokenList = [];
      getFemcNotifyToken()
        .then((resopnse) => {
          if (resopnse.data.message == "Success") {
            vm.TokenList = resopnse.data.data;
          } else {
            vm.$message({ type: "error", message: resopnse.data.message });
          }
        })
        .catch((response) => {
          if (response) vm.$message({ type: "error", message: response.message });
        })
        .finally(() => {});
    },
    getNotifyRule() {
      const vm = this;
      getFemcNotifyRule()
        .then((resopnse) => {
          if (resopnse.data.message == "Success") {
            vm.RuleList = resopnse.data.data;
          } else {
            vm.$message({ type: "error", message: resopnse.data.message });
          }
        })
        .catch((response) => {
          if (response) vm.$message({ type: "error", message: response.message });
        })
        .finally(() => {});
    },
    getCaseOption() {
      const vm = this;
      vm.CaseList = [];
      getCaseOption()
        .then((resopnse) => {
          if (resopnse.data.message == "Success") {
            vm.CaseList = resopnse.data.data;
          } else {
            vm.$message({ type: "error", message: resopnse.data.message });
          }
        })
        .catch((response) => {
          if (response) vm.$message({ type: "error", message: response.message });
        })
        .finally(() => {});
    },
    SearchClick() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          vm.$loading();
          getFemcNotifyLog(vm.ApiRequest.getNotifyLog)
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

    PageChanged(ind, Controller) {
      Controller.pageInd = ind;
      var sliceBegin = (Controller.pageInd - 1) * Controller.countPerPage;
      var sliceEnd = Controller.pageInd * Controller.countPerPage;
      Controller.CurrentData = Controller.DataSource.slice(sliceBegin, sliceEnd);
    }
  }
};
</script>
