<template>
  <div class=" m-0 p-0">
    <div class="rounded p-1 text-center  alert alert-success">
      設備狀態： {{ SocketDataALL.pcs[PCSIndex]?.working_status ?? "N/A" }}
    </div>
    <div class="mt-5 text-center">
      <el-button type="primary" @click="OpenClick" :disabled="allDisable || disabledOpen">
        開機
      </el-button>
      <el-button type="primary" @click="CloseClick" :disabled="allDisable || disabledClose">
        關機
      </el-button>
      <el-button type="primary" @click="StandbyClick" :disabled="allDisable || disabledStandby">
        待機
      </el-button>
    </div>
  </div>
</template>
<script>




import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";

export default {
  name: 'PCSStatusControl',
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
    }
  },
  watch: {

  },

  mounted() {
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    allDisable: function () {
      return [undefined, null, '保留', '啟動中', '關機中', '故障停機', '告警運行', '降額運行', '通信異常']
        .includes(this.SocketDataALL.pcs[0]?.working_status);
    },
    disabledOpen: function () {
      return ['運行', '保留', '待機', '啟動中', '關機中', '故障停機', '告警運行', '降額運行', '通信異常']
        .includes(this.SocketDataALL.pcs[0]?.working_status);
    },
    disabledClose: function () {
      return ['保留', '按鍵關機', '待機', '啟動中', '關機中', '故障停機', '告警運行', '降額運行', '通信異常']
        .includes(this.SocketDataALL.pcs[0]?.working_status);
    },
    disabledStandby: function () {
      return ['保留', '按鍵關機', '待機', '啟動中', '關機中', '故障停機', '告警運行', '降額運行', '通信異常']
        .includes(this.SocketDataALL.pcs[0]?.working_status);
    },
  },
  methods: {
    OpenClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          key:'TOPOEVENT',
          customer: "tasco",
          code: "PCS",
          action: "PCS_ON_OFF",
          equipment_id: null,
          value: 1,
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
    CloseClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "PCS",
          action: "PCS_ON_OFF",
          equipment_id: null,
          value: 0,
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
    StandbyClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });

        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "PCS",
          action: "PCS_ON_OFF",
          value: -99,
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
  },
  created() {


  },
}
</script>
  