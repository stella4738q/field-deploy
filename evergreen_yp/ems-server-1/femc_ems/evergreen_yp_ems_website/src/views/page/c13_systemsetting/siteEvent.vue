<template>
  <div class="p-3">
    <h3>平台事件記錄</h3>
    <div class="d-flex align-items-center mt-3">
      <el-form :model="FormSearch" ref="FormSearch" :inline="true" label-width="60px">
        <el-form-item label="時間" prop="date">
          <el-date-picker v-model="FormSearch.date" type="daterange" value-format="YYYYMMDD" class="me-2" style="width: 250px"/>
        </el-form-item>
        <el-form-item label="關鍵字" prop="key_word">
          <el-input v-model="FormSearch.key_word" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="">
          <el-button type="primary" @click="Add">
            <font-awesome-icon icon="plus" />
          </el-button>
          <el-button type="primary" @click="SearchClick">
            <font-awesome-icon icon="search" />
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- table -->

    <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle">
      <el-table-column label="記錄時間" prop="datetime" width="90px">
        <template #default="scope">
          {{ moment(scope.row.datetime).format("YYYY-MM-DD HH:mm:ss") }}
        </template>
      </el-table-column>
      <el-table-column label="主旨" prop="subject" width="300px"></el-table-column>
      <el-table-column label="內容" prop="description">
        <template #default="scope">
          <el-popover  :content="scope.row.description" placement="bottom" trigger="click">
            <template #reference>
              {{ scope.row.description.substring(0, 40) }}
              {{ scope.row.description.length > 40 ? '...' : '' }}
            </template>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="影響範圍" prop="scope" width="120px"></el-table-column>

      <el-table-column label="刪除" width="60px">
        <template #default="scope">
          <el-button type="primary" @click="Delete(scope.row)">
            <font-awesome-icon icon="trash" />
          </el-button>
        </template>
      </el-table-column>
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

    <el-dialog :title="Form._id ? '編輯' : '新增'" center v-model="Dialog" :close-on-click-modal="false" :show-close="false" width="800px">
      <el-form :model="Form" ref="Form" :rules="FormRule" label-width="140px">
        <el-form-item label="主旨" prop="subject">
          <el-input v-model="Form.subject" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="內容" prop="description">
          <el-input v-model="Form.description" type="textarea" :autosize="{ minRows: 2, maxRows: 20 }" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="影響範圍" prop="scope">
          <el-input v-model="Form.scope" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div class="dialog-footer" align="end">
        <el-button @click="Dialog = false">取消</el-button>
        <el-button type="primary" @click="Submit">確定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getSiteEvent, postSiteEvent, delSiteEvent } from "@/api/Api.js";
import moment from "moment";
export default {
  components: {},
  data() {
    return {
      Dialog: false,
      moment,
      FormQuery: {
        start_date: "", // moment().add(1, "months").format("YYYYMMDD"),
        end_date: "", //moment().format("YYYYMMDD"),
        key_word: ""
      },
      FormSearch: {
        key_word: "",
        date: ""
      },
      Form: {
        _id: null,
        subject: "",
        description: "",
        scope: ""
      },
      FormTemplate: {
        _id: null,
        subject: "",
        description: "",
        scope: ""
      },
      FormRule: {
        subject: [{ required: true, message: " ", trigger: "blur" }],
        description: [{ required: true, message: " ", trigger: "blur" }],
        scope: [{ required: true, message: " ", trigger: "blur" }]
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
  computed: {},
  mounted() {},
  created() {
    this.getData();
  },
  watch: {},
  methods: {
    Delete(item) {
      const vm = this;
      vm.$confirm("確定刪除", "確認", {
        confirmButtonText: "確定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          delSiteEvent({ _id: item._id })
            .then((resopnse) => {
              if (resopnse.data.message == "Success") {
                vm.getData();
              } else {
                vm.$message({ type: "error", message: resopnse.data.message });
              }
            })
            .catch((response) => {
              if (response) vm.$message({ type: "error", message: response.message });
            })
            .finally(() => {
              vm.$loading().close();
            });
        })
        .catch(() => {});
    },
    Add() {
      this.Form = Object.assign({}, this.FormTemplate);
      this.Dialog = true;
    },
    Edit(item) {
      this.Form = Object.assign({}, this.FormTemplate, item);
      this.Dialog = true;
    },
    Submit() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          postSiteEvent(vm.Form)
            .then((resopnse) => {
              if (resopnse.data.message == "Success") {
                vm.getData();
                vm.Dialog = false;
              } else {
                vm.$message({ type: "error", message: resopnse.data.message });
              }
            })
            .catch((response) => {
              if (response) vm.$message({ type: "error", message: response.message });
            })
            .finally(() => {
              vm.$loading().close();
            });
        }
      });
    },
    getData() {
      const vm = this;
      vm.$loading();
      getSiteEvent(vm.FormQuery)
        .then((resopnse) => {
          if (resopnse.data.message == "Success") {
            vm.PageController.DataSource = resopnse.data.data;
            vm.PageChanged(1, vm.PageController);
          } else {
            vm.$message({ type: "error", message: resopnse.data.message });
          }
        })
        .catch((response) => {
          if (response) vm.$message({ type: "error", message: response.message });
        })
        .finally(() => {
          vm.$loading().close();
        });
    },
    SearchClick() {
      const vm = this;
      vm.$refs.FormSearch.validate((valid) => {
        if (valid) {
          vm.FormQuery.start_date = vm.FormSearch.date[0];
          vm.FormQuery.end_date = vm.FormSearch.date[1];
          vm.FormQuery.key_word = vm.FormSearch.key_word;
          vm.getData();
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
