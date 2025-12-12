<template>
  <div class=" m-0 p-0">
    <div class="rounded p-1 text-white text-center  bg-success alert alert-success"
      v-if="myACB?.remote">
      遠端控制：是
    </div>
    <div class="rounded p-1 text-white text-center  bg-danger alert alert-success"
      v-if="myACB?.local">
      遠端控制：否
    </div>
    <div v-if="myACB?.cb_closed"
      class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：CLOSE(閉合)
    </div>
    <div v-if="myACB?.cb_open" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-danger alert alert-success">
      狀態：OPEN(斷開)
    </div>
    <div v-if="myACB?.cb_serve"
      class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：Serve
    </div>
    <div v-if="myACB?.cb_test" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-danger alert alert-success">
      狀態：Test
    </div>
    <div v-if="myACB?.cb_trip" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-danger alert alert-success">
      狀態：TRIP
    </div>
    <div class="mt-5 text-center">

      <el-button type="primary" @click="OpenClick" :disabled="[undefined, null, true].includes(myACB?.cb_closed) || myACB?.local || myACB?.cb_test">
        閉合
        <!--  -->
      </el-button>
      <el-button type="primary" @click="CloseClick" :disabled="[undefined, null, true].includes(myACB?.cb_open) || myACB?.local || myACB?.cb_test">
        斷開
        <!--  -->
      </el-button>
<!-- 
      <el-button type="primary" @click="testClick" >
        test
      </el-button> -->

    </div>
  </div>
</template>
<script>

import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";

import moment from 'moment';
export default {
  name: 'ACBControl',
  props: {
    StoreID: null,
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
    ...mapState(["SocketDataALL", "ACB_MP1", "ACB_MP2"]),
    myACB: function () {
      return this[this.StoreID];
    },
  },
  methods: {
    OpenClick() {
      const vm = this;
      vm.$confirm(`${this.myACB.equipment_id}確定執行【閉合】指令?`, 
        '提示', {confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        var postData = {
          customer: "evergreen-yp",
          code: "IO",
          action: "ACB_ON_OFF",
          equipment_id: this.myACB?.equipment_id,
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
    CloseClick() {
      const vm = this;

      vm.$confirm(`${this.myACB.equipment_id}確定執行【斷開】指令?`, 
        '提示', {confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {


        vm.$loading();
        var postData = {
          customer: "evergreen-yp",
          code: "IO",
          action: "ACB_ON_OFF",
          equipment_id: this.myACB?.equipment_id,
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
  },
  created() {


  },
}
</script>
  