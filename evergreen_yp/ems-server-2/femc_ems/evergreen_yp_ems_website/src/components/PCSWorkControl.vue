<template>
  <div class=" m-0 p-0">
    <div class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：{{ SocketDataALL.pcs[0]?.working_mode ?? "N/A" }}
    </div>

    <div class="mt-5 text-center">
      <el-button type="primary" @click="ConnectClick" :disabled="allDisable || disabledConnect">
        並網模式
      </el-button>
      <el-button type="primary" @click="DisconnectClick" :disabled="allDisable || disabledDisonnect">
        離網模式
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
    allDisable: function () {//'並網模式''離網模式'
      return [undefined, null, '並網恆流', '並網恆壓', '並網恆功率（AC）/並網模式', '並網恆功率（DC）/並網模式', '保留', 'VSG模式']
        .includes(this.SocketDataALL.pcs[0]?.working_mode);
    },
    disabledConnect: function () {//'離網模式'
      return ['並網恆流', '並網恆壓', '並網恆功率（AC）/並網模式', '並網恆功率（DC）/並網模式', '保留', '並網模式', 'VSG模式']
        .includes(this.SocketDataALL.pcs[0]?.working_mode);
    },
    disabledDisonnect: function () {
      return ['並網恆流', '並網恆壓', '並網恆功率（AC）/並網模式', '並網恆功率（DC）/並網模式', '保留', 'VSG模式', '離網模式']
        .includes(this.SocketDataALL.pcs[0]?.working_mode);
    },
  },
  methods: {

    ConnectClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "PCS",
          action: "PCS_SET_MODE",
          equipment_id: null,
          value: 'on-grid',
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
    DisconnectClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        // vm.$message({ type: 'success', message: "指令已下達(NO api)" });
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "PCS",
          action: "PCS_SET_MODE",
          equipment_id: null,
          value: 'off-grid',
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
  