<template>
  <div class="p-2">
    <h3>發送設定</h3>
    <div>
      <el-button type="primary" @click="Submit">
        <font-awesome-icon icon="save" />
      </el-button>
      <el-form :model="Form" :rules="FormRule" ref="form">
        <el-row class="ps-2 pt-2" :gutter="25">
          <el-col :sm="24">
            <el-form-item label="報警(低)-發送間隔時間(秒)" prop="warning_0_alarm_time"  label-position="top">
              <el-input-number v-model.number="Form.warning_0_alarm_time" :step="1" :min="60" />
            </el-form-item>
          </el-col>
          <el-col :sm="24">
            <el-form-item label="報警(中)-發送間隔時間(秒)" prop="warning_1_alarm_time" label-position="top">
              <el-input-number v-model.number="Form.warning_1_alarm_time" :step="1" :min="60" />
            </el-form-item>
          </el-col>
          <el-col :sm="24">
            <el-form-item label="報警(高)-發送間隔時間(秒)" prop="warning_2_alarm_time" label-position="top">
              <el-input-number v-model.number="Form.warning_2_alarm_time" :step="1" :min="60" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <br />
    <h3>訂閱設定</h3>
    <el-table :data="RuleList" size="small" stripe border class="rounded-3 mt-2" header-cell-class-name="tableHeaderStyle">
      <el-table-column label="規則" width="180" prop="name" align="center"></el-table-column>
      <el-table-column label="描述" width="180" prop="description" align="center"></el-table-column>
      <el-table-column label="通知設定" min-width="180" prop="_id" align="center" fixed="right" >
        <template #default="scope">
          <!-- {{ scope.row['_id'] }} -->
          <el-select v-model="ResultList[scope.row['_id']]" multiple placeholder="請選擇">
              <el-option v-for="item in TokenList" :key="item._id" :label="item.name" :value="item._id"> </el-option>
          </el-select>
        </template>
      </el-table-column>
    </el-table>
    <!-- ===================================================================== -->
    <!-- <table class="table mt-4 table-bordered table-sm w-100 text-center">
      <thead class="tableHeaderStyle">
        <tr>
          <th>規則</th>
          <th v-for="caseItem in CaseList">
            {{ caseItem.case_name }}
          </th>
          <th>
            描述
          </th>
          <th>
            通知設定
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ruleItem in RuleList">
          <td>{{ ruleItem.name }}</td>
          <td>{{ ruleItem.description }}</td>
          <td>
            <el-select v-model="ResultList[ruleItem._id]" multiple placeholder="請選擇">
              <el-option v-for="item in TokenList" :key="item._id" :label="item.name" :value="item._id"> </el-option>
            </el-select>
          </td>
          <th v-for="caseItem in CaseList">
            <el-select v-model="ResultList[ruleItem._id + '|' + caseItem.case_id]" multiple placeholder="請選擇">
              <el-option v-for="item in TokenList" :key="item._id" :label="item.name" :value="item._id"> </el-option>
            </el-select>
          </th>
        </tr>
      </tbody>
    </table> -->
  </div>
</template>

<script>
import { getNotifyRule, getNotifyToken, getNotifySetting, postNotifySetting, getCaseOption, getSystemStorageSetting, postSystemStorageSetting } from "@/api/Api.js";

export default {
  components: {},
  data() {
    return {
      RuleList: [],
      TokenList: [],
      CaseList: [],
      SettingList: [],
      ResultList: {},
      Form: {
        warning_0_alarm_time: 600,
        warning_1_alarm_time: 300,
        warning_2_alarm_time: 60,
      },
      FormRule: {
        warning_0_alarm_time: [{ type: "number", required: true, message: '此欄位不能為空', trigger: 'blur' }],
        warning_1_alarm_time: [{ type: "number", required: true, message: '此欄位不能為空', trigger: 'blur' }],
        warning_2_alarm_time: [{ type: "number", required: true, message: '此欄位不能為空', trigger: 'blur' }]
      },
      FormOldData: {},
    };
  },
  computed: {},
  mounted() {},
  created() {
    this.ini();
  },
  watch: {},
  watch: {
    'Form.warning_0_alarm_time'(newVal) {
      newVal = newVal ? parseInt(newVal) : null;
      this.Form.warning_0_alarm_time = newVal;
    },
    'Form.warning_1_alarm_time'(newVal){
      newVal = newVal ? parseInt(newVal) : null;
      this.Form.warning_1_alarm_time = newVal;
    },
    'Form.warning_2_alarm_time'(newVal){
      newVal = newVal ? parseInt(newVal) : null;
      this.Form.warning_2_alarm_time = newVal;
    }
  },
  methods: {
    ini() {
      const vm = this;
      // 取發送設定
      vm.getSystemStorageSetting();

      // let p = [this.getNotifyRule(), this.getNotifyToken(), this.getNotifySetting(), this.getCaseOption()];
      let p = [this.getNotifyRule(), this.getNotifyToken(), this.getNotifySetting(), ];
      Promise.all(p).then((response) => {
        vm.getResultList();
      });
    },
    getNotifyRule() {
      const vm = this;
      return new Promise((resolve) => {
        getNotifyRule()
          .then((resopnse) => {
            if (resopnse.data.message == "Success") {
              vm.RuleList = resopnse.data.data.sort((a, b) => {
                return a.code?.localeCompare(b.code);
              });
              resolve(true);
            } else {
              vm.$message({ type: "error", message: resopnse.data.message });
              resolve(false);
            }
          })
          .catch((response) => {
            if (response) vm.$message({ type: "error", message: response.message });
            resolve(false);
          })
          .finally(() => {});
      });
    },
    getNotifySetting() {
      const vm = this;
      return new Promise((resolve) => {
        getNotifySetting()
          .then((resopnse) => {
            if (resopnse.data.message == "Success") {
              vm.SettingList = resopnse.data.data;
              resolve(true);
            } else {
              vm.$message({ type: "error", message: resopnse.data.message });
              resolve(false);
            }
          })
          .catch((response) => {
            if (response) vm.$message({ type: "error", message: response.message });
            resolve(false);
          })
          .finally(() => {});
      });
    },
    getCaseOption() {
      const vm = this;
      return new Promise((resolve) => {
        getCaseOption()
          .then((resopnse) => {
            if (resopnse.data.message == "Success") {
              vm.CaseList = resopnse.data.data;
              resolve(true);
            } else {
              vm.$message({ type: "error", message: resopnse.data.message });
              resolve(false);
            }
          })
          .catch((response) => {
            if (response) vm.$message({ type: "error", message: response.message });
            resolve(false);
          })
          .finally(() => {});
      });
    },
    getNotifyToken() {
      const vm = this;
      return new Promise((resolve) => {
        getNotifyToken()
          .then((resopnse) => {
            if (resopnse.data.message == "Success") {
              vm.TokenList = resopnse.data.data;
              resolve(true);
            } else {
              vm.$message({ type: "error", message: resopnse.data.message });
              resolve(false);
            }
          })
          .catch((response) => {
            if (response) vm.$message({ type: "error", message: response.message });
            resolve(false);
          })
          .finally(() => {});
      });
    },
    getResultList() {
      const vm = this;
      vm.ResultList = [];
      vm.RuleList.forEach((ruleItem) => {
        const find = vm.SettingList.filter((x) => {
            return x.notify_rule == ruleItem._id;
          }).map((x) => {
            return x.notify_token;
          });
          vm.ResultList[ruleItem._id] = find || [];
      });
      // console.log(vm.ResultList);
      // vm.RuleList.forEach((ruleItem) => {
      //   vm.CaseList.forEach((caseItem) => {
      //     const find = vm.SettingList.filter((x) => {
      //       return x.case_id == caseItem.case_id && x.notify_rule == ruleItem._id;
      //     }).map((x) => {
      //       return x.notify_token;
      //     });
      //     vm.ResultList[ruleItem._id + "|" + caseItem.case_id] = find || [];
      //   });
      // });
    },
    getPostData() {
      const vm = this;
      const PostData = [];
      Object.keys(vm.ResultList).forEach((key) => {
        if (vm.ResultList[key].length) {
          // var keydata = key.split("|");
          // const ruleId = keydata[0];
          // const caseId = keydata[1];
          vm.ResultList[key].forEach((xx) => {
            PostData.push({
              notify_rule: key,
              // case_id: caseId,
              notify_token: xx
            });
          });
        }
      });

      return PostData;
    },
    getSystemStorageSetting() {
      const vm = this;
      getSystemStorageSetting()
        .then(response => {
          if (response.data.message == "Success") {
            var responseData = response.data.data;
            Object.entries(vm.Form).forEach(([key, value]) => {
              var filter_item = responseData.find(x => { return x.key == key });
              if(filter_item){
                vm.Form[key] = filter_item.value;
                vm.FormOldData[key] = filter_item;
              }
            });
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          if (response) vm.$message({ type: "error", message: response.message });
        })
        .finally(() => {})
    },
    Submit() {
      const vm = this;
      //驗證
      vm.$refs.form.validate((valid) => {
        if (!valid) {
          return false;
        }
        else{
          const postData = vm.getPostData();
          // console.log({ data_list: postData });
          vm.$loading();
          postNotifySetting({ data_list: postData })
            .then((resopnse) => {
              if (resopnse.data.message == "Success") {
                vm.$message({ type: "success", message: "儲存完成" });
              } else {
                vm.$message({ type: "error", message: resopnse.data.message });
              }
            })
            .catch((response) => {
              if (response) vm.$message({ type: "error", message: response.message });
            })
            .finally(() => {
              //update time settings
              var PostData = { type: 'notify_time_settings', data: [] };
              Object.entries(vm.Form).forEach(([key, value]) => {
                var find = vm.FormOldData?.hasOwnProperty(key) ? vm.FormOldData[key] : null;
                if(find && find?.value != value){
                  PostData.data.push({
                    "_id": find?._id,
                    "value": value,
                  });
                }
              });
              
              if(PostData.data){
                postSystemStorageSetting(PostData)
                .then(response => {
                  if (response.data.message == "Success") {
                    // vm.$message({ type: 'success', message: "完成" });
                  } else {
                    vm.$message({ type: 'error', message: response.data.message });
                  }
                })
                .catch(response => {
                  vm.$message({ type: 'error', message: response.message });
                })
                .finally(() => {
                  vm.getSystemStorageSetting();
                })
              }
              vm.$loading().close();
            });
        }
      });
    }
  }
};
</script>