<template>
  <div class="p-2">
    <h3>Token 管理</h3>
    <div class="d-flex align-items-center mt-3">
      <el-form :model="FormSearch" ref="FormSearch" inline>
        <el-form-item label="名稱" prop="name">
          <el-input v-model="FormSearch.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item>
        <el-button @click="SearchClick" class="ms-2">
          <font-awesome-icon icon="search" />
        </el-button>
        <el-button type="primary" @click="Add">
            <font-awesome-icon icon="plus" />
          </el-button>
      </el-form-item>
      </el-form>
    </div>
    <!-- table -->

    <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle">
      <el-table-column label="名稱" min-width="150" prop="name" align="center">
        <template #default="scope">
          <el-button type="text" @click="Edit(scope.row)">
            {{ scope.row.name }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="token" min-width="350" prop="token" align="center"></el-table-column>
      <el-table-column label="刪除" width="120" prop="token" align="center" fixed="right">
        <template #default="scope">
          <el-button type="danger" @click="Delete(scope.row)">
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
        <el-form-item label="名稱" prop="name">
          <el-input v-model="Form.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="token" prop="token">
          <el-input v-model="Form.token" autocomplete="off"></el-input>
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
import { getNotifyToken, delNotifyToken, postNotifyToken } from "@/api/Api.js";
import EnumList from "@/JSON/EnumList.json";
import moment from "moment";

export default {
  components: {},
  data() {
    return {
      EnumList,
      Dialog: false,
      moment,

      FormQuery: {
        name: ""
      },
      FormSearch: {
        name: ""
      },
      Form: {
        _id: null,
        name: "",
        token: ""
      },
      FormTemplate: {
        _id: null,
        name: "",
        token: ""
      },
      FormRule: {
        name: [{ required: true, message: " ", trigger: "blur" }],
        token: [{ required: true, message: " ", trigger: "blur" }]
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
          delNotifyToken({ _id: item._id })
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
          postNotifyToken(vm.Form)
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
      getNotifyToken(vm.FormQuery)
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
          vm.FormQuery = JSON.parse(JSON.stringify(vm.FormSearch));
          vm.getData();
        }
      });
    },

    PageChanged(ind, Controller) {
      Controller.pageInd = ind;
      var sliceBegin = (Controller.pageInd - 1) * Controller.countPerPage;
      var sliceEnd = Controller.pageInd * Controller.countPerPage;
      Controller.CurrentData = Controller.DataSource.slice(sliceBegin, sliceEnd);
      this.$emit('update-setting');
    }
  }
};
</script>
