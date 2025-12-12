<template>
  <div class="p-3">
    <h3>規則設定</h3>
    <div class="d-flex align-items-center mt-3">
      <el-form :model="FormSearch" ref="FormSearch" :inline="true" label-width="60px">
        <el-form-item label="名稱" prop="name">
          <el-input v-model="FormSearch.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="代碼" prop="code">
          <el-input v-model="FormSearch.code" autocomplete="off"></el-input>
        </el-form-item>

        <el-form-item label="">
          <el-button type="primary" @click="Add">
            <font-awesome-icon icon="plus" />
          </el-button>
        </el-form-item>
        <el-form-item label="">
          <el-button type="primary" @click="SearchClick">
            <font-awesome-icon icon="search" />
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- table -->

    <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle">
      <el-table-column label="代碼" prop="code" align="center" width="80px">
        <template #default="scope">
          <el-button type="text" @click="Edit(scope.row)">
            {{ scope.row.code }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="名稱" prop="name"></el-table-column>
      <el-table-column label="訊息類型" prop="type" align="center" width="80px">
        <template #default="scope">
          {{ scope.row.type == 1 ? "通知" : "告警" }}
        </template>
      </el-table-column>
      <!-- <el-table-column label="調頻備轉" prop="afc" align="center">
        <template #default="scope">
          <font-awesome-icon v-show="scope.row.afc" class="text-success" icon="circle-check" />
        </template>
      </el-table-column>
      <el-table-column label="增強型調頻備轉" prop="edreg" align="center">
        <template #default="scope">
          <font-awesome-icon v-show="scope.row.edreg" class="text-success" icon="circle-check" />
        </template>
      </el-table-column>
      <el-table-column label="即時與補充備轉" prop="dip_sup" align="center">
        <template #default="scope">
          <font-awesome-icon v-show="scope.row.dip_sup" class="text-success" icon="circle-check" />
        </template>
      </el-table-column>
      <el-table-column label="太陽能" prop="solar" align="center">
        <template #default="scope">
          <font-awesome-icon v-show="scope.row.solar" class="text-success" icon="circle-check" />
        </template>
      </el-table-column>
      <el-table-column label="廠內用電優化" prop="optimization" align="center">
        <template #default="scope">
          <font-awesome-icon v-show="scope.row.optimization" class="text-success" icon="circle-check" />
        </template>
      </el-table-column>

      <el-table-column label="執行周期" prop="cycle_type" align="center" width="80px">
        <template #default="scope">
          {{ scope.row.cycle_unit }}
          {{
            EnumList.cycle_type.find((x) => {
              return x.key == scope.row?.cycle_type;
            })?.val
          }}
        </template>
      </el-table-column> -->
      <el-table-column label="刪除" prop="token" align="center" width="80px">
        <template #default="scope">
          <el-button type="text" @click="Delete(scope.row)">
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
        <el-form-item label="代碼" prop="code">
          <el-input v-model="Form.code" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="名稱" prop="name">
          <el-input v-model="Form.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="詳細說明" prop="description">
          <el-input v-model="Form.description" autocomplete="off"></el-input>
        </el-form-item>
        <!-- <el-form-item label="啟用類型">
          <el-checkbox v-model="Form.afc" label="調頻備轉"></el-checkbox>
          <el-checkbox v-model="Form.edreg" label="增強型調頻備轉"></el-checkbox>
          <el-checkbox v-model="Form.dip_sup" label="即時/補充備轉"></el-checkbox>
          <el-checkbox v-model="Form.solar" label="太陽能"></el-checkbox>
          <el-checkbox v-model="Form.optimization" label="廠內用電優化"></el-checkbox>
        </el-form-item>
        <el-form-item label="訊息類型" prop="type">
          <el-select v-model="Form.type" placeholder=" " class="me-2">
            <el-option label="通知" :value="1"></el-option>
            <el-option label="告警" :value="2"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="執行的周期單位" prop="cycle_type">
          <el-select
            v-model="Form.cycle_type"
            placeholder=" "
            class="me-2"
            @change="
              () => {
                Form.cycle_unit = null;
              }
            "
          >
            <el-option v-for="item in EnumList.cycle_type" :label="item.val" :value="item.key" :key="item.key"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="執行的周期單位值" prop="cycle_unit">
          <el-input v-if="Form.cycle_type != 't'" type="number" v-model.number="Form.cycle_unit"></el-input>
          <el-input v-if="Form.cycle_type == 't'" v-model="Form.cycle_unit" placeholder="hhmmss" />
        </el-form-item> -->
      </el-form>
      <div class="dialog-footer" align="end">
        <el-button @click="Dialog = false">取消</el-button>
        <el-button type="primary" @click="Submit">確定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getFemcNotifyRule, postFemcNotifyRule, delFemcNotifyRule } from "@/api/Api.js";
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
        name: "",
        code: ""
      },
      FormSearch: {
        name: "",
        code: ""
      },
      Form: {
        _id: null,
        name: "",
        code: "",
        description: "",
        // afc: false,
        // dip_sup: false,
        // edreg: false,
        // solar: false,
        // optimization: false,
        // type: 1,
        // cycle_type: "m",
        // cycle_unmit: 1
      },
      FormTemplate: {
        _id: null,
        name: "",
        code: "",
        description: "",
        // afc: false,
        // dip_sup: false,
        // edreg: false,
        // solar: false,
        // optimization: false,
        // type: 1,
        // cycle_type: "m",
        // cycle_unmit: 1
      },

      PageController: {
        pageInd: 1,
        countPerPage: 30,
        total: 0,
        CurrentData: [],
        DataSource: []
      }
    };
  },
  computed: {
    FormRule: function () {
      return {
        name: [{ required: true, message: " ", trigger: "blur" }],
        code: [{ required: true, message: " ", trigger: "blur" }],
        // type: [{ required: true, message: " ", trigger: "blur" }],
        // cycle_type: [{ required: true, message: " ", trigger: "blur" }],
        // cycle_unit: [{ type: this.Form.cycle_type == "t" ? "string" : "number", required: true, message: " ", trigger: "blur" }]
      };
    }
  },
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
          delFemcNotifyRule({ _id: item._id })
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
          postFemcNotifyRule(vm.Form)
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
      getFemcNotifyRule(vm.FormQuery)
        .then((resopnse) => {
          if (resopnse.data.message == "Success") {
            vm.PageController.DataSource = resopnse.data.data.sort((a, b) => {
              return a.code?.localeCompare(b.code);
            });
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
    }
  }
};
</script>
