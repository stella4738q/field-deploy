<template>
  <div class=" m-0 p-0">
    <div v-if="SocketDataALL.io[0]?.solenoid_on == true"
      class="rounded p-1 text-white text-center  bg-danger alert alert-success">
      狀態：ON
    </div>
    <div v-if="SocketDataALL.io[0]?.solenoid_on == false" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-success alert alert-success">
      狀態：OFF
    </div>
    <div class="mt-5 text-center">
      <el-button type="primary" @click="OpenFireClick"
        :disabled="[true, undefined, null].includes(SocketDataALL.io[0]?.solenoid_on)">
        ON
      </el-button>
      <el-button type="primary" @click="CloseFireClick"
        :disabled="[false, undefined, null].includes(SocketDataALL.io[0]?.solenoid_on)">
        OFF
      </el-button>
    </div>
  </div>
</template>
<script>

import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";

import moment from 'moment';
export default {
  name: 'Schedule',
  props: {
    SOC: {
      type: Number,
      default: 0
    }

  },
  components: {
  },
  data() {
    return {
      moment,
      ManualDischarging: false,
      FormManualDischarge: {
        min: 15,
        power: 1000,
      },
      FormManualDischargeTemplate: {
        min: 15,
        power: 1000,
      },
    }
  },
  watch: {

  },

  mounted() {
  },
  computed: {
    ...mapState(["SocketDataALL"])

  },
  methods: {
    OpenFireClick() {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {


        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "FIRE",
          equipment_id: null,
          action: "FIRE_ON_OFF",
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
    CloseFireClick() {
      const vm = this;


      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {


        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "FIRE",
          equipment_id: null,
          action: "FIRE_ON_OFF",
          value: false
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
  