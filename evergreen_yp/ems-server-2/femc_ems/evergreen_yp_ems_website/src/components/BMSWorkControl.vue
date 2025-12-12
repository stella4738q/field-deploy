<template>
  <div class=" m-0 p-0">
    <div class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：{{ SocketDataALL.bms[0]?.working_status ?? "N/A" }}
    </div>

    <div class="mt-5 text-center">
      <el-button type="primary" @click="ConnectClick" :disabled="disabledConnect">
        開機
      </el-button>
      <el-button type="primary" @click="DisconnectClick" :disabled="disabledDisonnect">
        關機
      </el-button>
      <el-button type="primary" @click="OfflineDisconnectClick" :disabled="disabledOfflineDisconnectClick">
        離網開機
      </el-button>
    </div>
  </div>
</template>
<script>




import { postModbusControl } from '@/api/Api.js';
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

    }
  },
  watch: {

  },

  mounted() {
  },
  computed: {
    ...mapState(["SocketDataALL"]),

    disabledConnect: function () {//開機
      return ["運行狀態", "ECO狀態", "維護狀態", "故障狀態", "自檢狀態", "空閒狀態", "待機狀態"]
        .includes(this.SocketDataALL.bms[0]?.working_status);
    },
    disabledDisonnect: function () {//關機
      return ["運行狀態", "ECO狀態", "維護狀態", "故障狀態", "自檢狀態", "空閒狀態", "待機狀態"]
        .includes(this.SocketDataALL.pcs[0]?.working_status);
    },
    disabledOfflineDisconnectClick: function () {//離網開機
      let gridVal = ['併網'].includes(this.SocketDataALL.pcs[0]?.grid_status);
      let bmsStatus = ["運行狀態", "ECO狀態", "維護狀態", "故障狀態", "自檢狀態", "空閒狀態", "待機狀態"].includes(this.SocketDataALL.bms[0]?.working_status);
      return gridVal || bmsStatus;
    },
  },
  methods: {

    ConnectClick() {//開機
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "BMS",
          action: "BMS_ON_OFF",
          equipment_id: null,
          value: true,
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
    DisconnectClick() {//關機
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "BMS",
          action: "BMS_ON_OFF",
          equipment_id: null,
          value: false,
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
    OfflineDisconnectClick() {//離網開機
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "BMS",
          action: "BMS_ON_OFF",
          equipment_id: null,
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
  