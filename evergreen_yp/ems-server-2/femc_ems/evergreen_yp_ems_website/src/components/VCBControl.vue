<template>
  <div class=" m-0 p-0">
    <div class="rounded p-1 text-white text-center  bg-success alert alert-success"
      v-if="myVCB?.remote">
      遠端控制：是
    </div>
    <div class="rounded p-1 text-white text-center  bg-danger alert alert-success"
      v-if="myVCB?.local">
      遠端控制：否
    </div>
    <div v-if="myVCB?.cb_closed"
      class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：CLOSE(閉合)
    </div>
    <div v-if="myVCB?.cb_open" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-danger alert alert-success">
      狀態：OPEN(斷開)
    </div>
    <div v-if="myVCB?.cb_serve"
      class="rounded p-1 text-white text-center  bg-success alert alert-success">
      狀態：Serve
    </div>
    <div v-if="myVCB?.cb_test" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-danger alert alert-success">
      狀態：Test
    </div>
    <div v-if="myVCB?.cb_trip" style="font-size: small;"
      class="rounded p-1 text-white  text-center  bg-danger alert alert-success">
      狀態：TRIP
    </div>
    <div class="mt-5 text-center">

      <el-button type="primary" @click="OpenClick" :disabled="[undefined, null, true].includes(myVCB?.cb_closed) || myVCB?.local || myVCB?.cb_test">
        閉合
        <!--  -->
      </el-button>
      <el-button type="primary" @click="CloseClick" :disabled="[undefined, null, true].includes(myVCB?.cb_open) || myVCB?.local || myVCB?.cb_test">
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

import { iecVCBControl } from '@/api/Api.js';
import { mapState } from "vuex";

import moment from 'moment';
export default {
  name: 'VCBControl',
  props: {
    StoreID: null,
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
    ...mapState(["SocketDataALL", "VCB"]),
    myVCB: function () {
      return this[this.StoreID];
    },
  },
  methods: {
    OpenClick() {
      const vm = this;
      vm.$confirm(
        '確定執行【VCB閉合】指令?', 
        '提示', {confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'})
      .then(() => {
        vm.$loading();
        iecVCBControl({customer: "evergreen-yp", code: "VCB", equipment_id: this.myVCB?.equipment_id, action: "VCB_ON_OFF", value: true }).then(response => {
          if (response.data.success) {
            vm.$message({ type: 'success', message: "指令已下達" });
          } else {
            vm.$message({ type: 'error', message: response.data.message });
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
      vm.$confirm(
        '確定執行【VCB斷開】指令?', 
      '提示', {confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        iecVCBControl({customer: "evergreen-yp", code: "VCB", equipment_id: this.myVCB?.equipment_id, action: "VCB_ON_OFF", value: false }).then(response => {
          if (response.data.success) {
            vm.$message({ type: 'success', message: "指令已下達" });
          } else {
            vm.$message({ type: 'error', message: response.data.message });
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
  