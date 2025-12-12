<template>
  <div class="row text-start g-3">
    <div class="col-12 col-md-4">
    <div class="card border-success p-2">
      <p class="fs-12 m-0 border-bottom border-success">DCP狀態</p>
      <div class="fs-5 p-0 text-end row m-0 text-white" v-if="myDCP">
        <div class="col p-0 m-0 text-center border border-white mt-1" v-for="(dcp) in [
            {key:'dcp_a_on', label: 'DCP 1'}, 
            {key:'dcp_b_on', label: 'DCP 2'}
          ]">
          <div :class="getDCPClass(dcp.key)"> {{ dcp.label }} </div>
        </div>
      </div>
    </div>
  </div>


    <div class="col-12 col-md-4">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success">電池電壓</p>
        <div class="fs-5 p-0 text-end row m-0 text-white" v-if="SocketDataALL?.bms">
          <div class="col p-0 m-0 text-center border border-white mt-1" v-for="(bms, ind) in sortedBMS" :key="bms.equipment_id">
            <div class="text-dark"> {{ ind + 1 }}: {{ bms.voltage }} </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="col-12 col-md-4">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success">壓差(最大)</p>
        <div class="fs-4 text-dark text-center mt-1">
          {{ bmsVoltageDiff }} V
        </div>
      </div>
    </div>

  </div>

  <table class="table w-100 table-bordered text-start align-middle mt-2">
    <tbody>
      <tr>
        <td style="width:100px">DCP 1</td>
        <td colspan="3">
          <el-button-group>
            <el-button type="primary" :disabled="!(myDCP?.DCP1CanOn == true) || !ControlPriviage"
              @click="DCP_ON_OFF(myDCP.equipment_id, true, 1)">開</el-button>
            <el-button type="danger" :disabled="!(myDCP?.DCP1CanOff == true) || !ControlPriviage"
              @click="DCP_ON_OFF(myDCP.equipment_id, false, 1)">關</el-button>
          </el-button-group>
        </td>
      </tr>
      <tr>
        <td style="width:100px">DCP 2</td>
        <td colspan="3">
          <el-button-group>
            <el-button type="primary" :disabled="!(myDCP?.DCP2CanOn == true) || !ControlPriviage"
              @click="DCP_ON_OFF(myDCP.equipment_id, true, 0)">開</el-button>
            <el-button type="danger" :disabled="!(myDCP?.DCP2CanOff == true) || !ControlPriviage"
              @click="DCP_ON_OFF(myDCP.equipment_id, false, 0)">關</el-button>
          </el-button-group>
        </td>
      </tr>
      <tr>
        <td>狀態</td>
        <td colspan="3">
          <div class="json-display" style="max-height: 500px; overflow-y: auto ;">
            {{ myDCP.content }}
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script>
import { mapState } from "vuex";
import { postModbusControl } from '@/api/Api.js';

export default {
  props: {
    DCPStoreID: null,
  },
  components: {
  },
  data() {
    return {
      power1: 0,
      power2: 0,
      current: 0,
      voltage: 0,
      input2: '',
    };
  },
  computed: {
    ControlPriviage: function () { return this.$store.getters.userPriviagePage('P01-02') && this.OPERATE_MODE !== 1;},
    ...mapState(["SocketDataALL", "DCP", "OPERATE_MODE"]),
    myDCP: function () {
      return this[this.DCPStoreID];
    },
    bmsVoltageDiff() {
      const list = this.SocketDataALL?.bms || []
      const voltages = list.map(b => b.voltage).filter(v => typeof v === 'number')
      if (voltages.length < 2) return 'N/A'
      return (Math.max(...voltages) - Math.min(...voltages)).toFixed(2)
    },
    sortedBMS() {
    return (this.SocketDataALL?.bms || []).slice().sort((a, b) => {
      return a.equipment_id > b.equipment_id ? 1 : -1;
    });
  }
  },
  mounted() {
  },
  created() {
  },
  watch: {
  },
  methods: {
    getDCPClass(attr) {
      var find = this.myDCP
      if (find) {
        var state_color = find[attr] ? ' bg-success' : ' bg-dark';
        if (find.abnormal){
          var level_list = []
          find.warning.forEach(x => {
            level_list.add(x.level)
          });
          var max_level = Math.max(...level_list);
          var state_color = max_level >= 2 ? ' bg-danger' :   max_level >= 1 ? " bg-warning": state_color;
        }
        return find.abnormal ? ' bg-danger' : ' ' + state_color;
      }
      return ' bg-dark';
    },
    DCP_ON_OFF(id, value, unit) {
      let dcp_name = unit === 1 ? "1": unit === 0 ? "2" : "NA"
      const vm = this;
      vm.$confirm(`${this.DCPStoreID}_${dcp_name} 確定執行【${ value ? '開機': '關機' }】指令？`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
        var postData = {
          customer: "advanced",
          code: "DCP",
          action: "BMS_DCP_ON_OFF",
          parameter: unit,
          equipment_id: id,
          value: value,
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
  }
};
</script>
<style>
.table {
  display: table;
  width: 100%;
}

.table-row {
  display: table-row;
}

.table-cell {
  display: table-cell;
  border: 1px solid #ccc;
  padding: 5px 0;
}

.table-cell:first-child {
  min-width: 100px;
}
</style>