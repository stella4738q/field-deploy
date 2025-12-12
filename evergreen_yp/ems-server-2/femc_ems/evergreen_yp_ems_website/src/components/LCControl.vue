<template>
  <div class=" m-0 p-0">
    <div class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：{{ SocketDataALL?.lc[0]?.system_working_status ?? "N/A" }}
    </div>

    <div class="rounded p-1 text-white text-center  bg-secondary alert alert-success">
      絕緣阻抗：
      [正極：{{ SocketDataALL?.pcs[0]?.positive_insulation_impedance  }}]
      [負極：{{ SocketDataALL?.pcs[0]?.negative_insulation_impedance  }}]
    </div>

    

    <div class="rounded p-1 text-white text-center  bg-info alert alert-success">
      {{ openStatus == '' ? "無" : openStatus }}
    </div>
    <div class="mt-5 text-center">
      <el-button type="primary" @click="ConnectClick" :disabled="allDisable || disabledConnect || !DoOpen">
        開機
      </el-button>
      <el-button type="primary" @click="DisconnectClick" :disabled="allDisable || disabledDisonnect">
        關機
      </el-button>
      <!-- <el-button type="primary" @click="DisconnectClick" :disabled="allDisable || disabledECO">
        ECO模式
      </el-button> -->
    </div>
    <div class="mt-5 text-center">
      <el-button type="primary" @click="ResetClick" v-show="showAction">
        重置錯誤
      </el-button>
    </div>
  </div>
</template>
<script>




import { postModbusControl, getModbusControlCheck } from '@/api/Api.js';
import moment from "moment";
import { mapState } from "vuex";

export default {
  name: 'PCSWorkControl',
  props: {
    PCSIndex: {
      type: Number,
      default: 0
    }

  },
  components: {
  },
  data() {
    return {
      showAction: !this.$store.getters.DiasbledAction,
      openStatus: '',
      DoOpen: false,
      moment,
    }
  },
  watch: {

  },

  mounted() {
    this.TimmerCheck();
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    allDisable: function () {
      return [null, undefined, '保留', '自檢', '啟動中', '運行', '故障停機中', '停機中', '自檢失敗', '啟動失敗', '停機失敗', '低電量補償']
        .includes(this.SocketDataALL?.lc[0]?.system_working_status);
    },
    disabledECO: function () {//'ECO模式'

      return ['保留', '停機', '自檢', '啟動中', '運行', '故障停機中', '故障', '停機中', '自檢失敗', '啟動失敗', '停機失敗', '待機', '低電量補償']
        .includes(this.SocketDataALL?.lc[0]?.system_working_status);
    },
    disabledConnect: function () {//'停機'
      return ['保留', '自檢', '啟動中', '運行', '故障停機中', '故障', '停機中', '自檢失敗', '啟動失敗', '停機失敗', '待機', '低電量補償', 'ECO模式']
        .includes(this.SocketDataALL?.lc[0]?.system_working_status);
    },
    disabledDisonnect: function () {//'待機'
      return ['保留', '停機', '自檢', '啟動中', '運行', '故障停機中', '故障', '停機中', '自檢失敗', '啟動失敗', '停機失敗', '低電量補償', 'ECO模式']
        .includes(this.SocketDataALL?.lc[0]?.system_working_status);
    },
    disabledReset: function () {//'故障'
      var result = !['保留', '停機', '自檢', '啟動中', '運行', '故障停機中', '停機中', '自檢失敗', '啟動失敗', '停機失敗', '待機', '低電量補償', 'ECO模式']
        .includes(this.SocketDataALL?.lc[0]?.system_working_status);
      return result;
    },
  },
  methods: {
    TimmerCheck() {
      const vm = this;
      setTimeout(() => {
        vm.getModbusControlCheck().then(chkResult => {
          if (!chkResult) {
            vm.TimmerCheck();
          }
        })
      }, 1000);
    },
    getModbusControlCheckForce() {
      getModbusControlCheck({ force_reset: 1 }).then(response => {
        var msg = JSON.stringify(response.data);
        vm.$message({ type: 'success', message: "指令已下達：" + msg });
      }).catch((e) => {
        vm.$message({ type: 'error', message: response.data });
      });
    },
    getModbusControlCheck() {//只有status null 跟 error可以開機, 其他就顯示message
      const vm = this;
      return new Promise((resolve, reject) => {
        getModbusControlCheck().then(response => {
          if (response.data.Success) {
            if (response.data.Data == null || response.data.Data.status == null || response.data.Data.status.toUpperCase() == "ERROR") {
              vm.openStatus = response.data.Data == null ? "" : ('開機' + (response.data.Data.status.toUpperCase() == "ERROR" ? "失敗：" + response.data.Data.message : "完成"));

              vm.DoOpen = true;
              resolve(true);
            } else {
              vm.openStatus = vm.moment().format("HH:mm:ss")
                + '開機中：'
                + response.data.Data.message;
              vm.DoOpen = false;
              resolve(false);
            }
          } else {
            vm.$message({ type: 'error', message: (response.data.Data?.status ?? JSON.stringify(response.data)) });
            resolve(false);
          }
        }).catch(response => {
          vm.$message({ type: 'error', message: response.data });
          resolve(false);
        })
      });
    },
    ResetClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "LC",
          action: "LC_FAULT_RESET",
          equipment_id: null,
          value: null,
        };
        postModbusControl(postData).then(response => {
          if (response.data.Success) {
            vm.$message({ type: 'success', message: "指令已下達" });
          } else {
            vm.$message({ type: 'error', message: response.data.Msg });
          }
        }).catch(response => {
          vm.$message({ type: 'error', message: "api error" });
        }).finally(() => {
          vm.$loading().close();
        });

      }).catch(() => {
      });
    },
    ConnectClick() {
      const vm = this;
      vm.openStatus = '';
      vm.getModbusControlCheck().then((chkLCStatus) => {
        if (chkLCStatus) {
          vm.$confirm('確定送出指令?', '提示', {
            confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
          }).then(() => {
            vm.$loading();
            var postData = { customer: "tasco", code: "LC", action: "LC_ON_OFF", equipment_id: null, value: true, };
            postModbusControl(postData).then(response => {
              if (response.data.Success) {
                vm.$message({ type: 'success', message: "指令已下達" });
                vm.TimmerCheck();
              } else {
                vm.$message({ type: 'error', message: response.data.Msg });
              }
            }).catch(response => {
              vm.$message({ type: 'error', message: "api error" });
            }).finally(() => {
              vm.$loading().close();
            });
          });
        }
      }).catch((exx) => {
        vm.$message({ type: 'error', message: (exx.message ? exx.message : JSON.stringify(exx)) });
      });
    },
    DisconnectClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "LC",
          action: "LC_ON_OFF",
          equipment_id: null,
          value: false,
        };
        postModbusControl(postData).then(response => {
          if (response.data.Success) {
            vm.$message({ type: 'success', message: "指令已下達" });
          } else {
            vm.$message({ type: 'error', message: response.data });
          }
        }).catch(response => {
          vm.$message({ type: 'error', message: "api error" });
        }).finally(() => {
          vm.$loading().close();
        });

      }).catch(() => {
      });

    },
  },
  created() {


  },
}
</script>
  