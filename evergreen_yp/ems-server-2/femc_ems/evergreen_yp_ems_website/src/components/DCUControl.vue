<template>
  <div class="card border-primary p-2">
    <div class="table">
      <!-- 標題列 -->
      <div class="table-row table-header">
        <div class="table-cell">項目</div>
        <div 
          v-for="meter in meters" 
          :key="meter.equipment_id" 
          class="table-cell text-center"
        >
          {{ meter.equipment_id == "METER_SUN1" ?  "PV第一機組升壓站(MVCB1)": "F1變電站(MVCB2)" }}
        </div>
      </div>

      <!-- 功率列 -->
      <div class="table-row">
        <div class="table-cell">功率 (kW)</div>
        <div 
          v-for="meter in meters" 
          :key="meter.equipment_id" 
          class="table-cell text-center"
        >
          {{ meter.total_active_power }}
        </div>
      </div>

      <!-- 三相電壓列 -->
      <div class="table-row">
        <div class="table-cell">三相電壓 (V)</div>
        <div 
          v-for="meter in meters" 
          :key="meter.equipment_id" 
          class="table-cell text-center"
        >
          A: {{ meter.voltage_a }} / B: {{ meter.voltage_b }} / C: {{ meter.voltage_c }}
        </div>
      </div>

      <!-- 三相電流列 -->
      <div class="table-row">
        <div class="table-cell">三相電流 (A)</div>
        <div 
          v-for="meter in meters" 
          :key="meter.equipment_id" 
          class="table-cell text-center"
        >
          A: {{ meter.current_a }} / B: {{ meter.current_b }} / C: {{ meter.current_c }}
        </div>
      </div>

      <!-- 功率因素列 -->
      <div class="table-row">
        <div class="table-cell">功率因素</div>
        <div 
          v-for="meter in meters" 
          :key="meter.equipment_id" 
          class="table-cell text-center"
        >
          A: {{ meter.pfa }} / B: {{ meter.pfb }} / C: {{ meter.pfc }} / 總: {{ meter.total_power_factor }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";
import EC from '@/JSON/EquipmentColor.json';

export default {
  props: {},
  components: {
  },
  data() {
    return {
      EC
    };
  },
  computed: {
    ...mapState(["SocketDataALL", "METER_SUN1", "METER_SUN2", "OPERATE_MODE"]),
    ControlPriviage : function () { return this.$store.getters.userPriviagePage('P01-03'); },
    meters: function () {
      return [this["METER_SUN1"], this["METER_SUN2"]];
    },
  },
  mounted() {

  },
  created() {
  },
  watch: {
  },
  methods: {
    getDCUClass(attr) {
      const device = this.SocketDataALL?.dcu.find(x => x.equipment_id === attr);
      if (!device) return ' bg-dark';

      const stop = [1, 2, 3, 6];
      const fault = [7, 8];

      if (device.abnormal) return ' bg-danger';

      if (stop.includes(device.operation_mode)) return ' bg-dark';
      if (fault.includes(device.operation_mode)) return ' bg-danger';

      return ' bg-success'; 
    },

    SUN_ON_OFF(id, value) {
      const vm = this;

      vm.$confirm(`確定【${value ? '開啟' : '關閉'}】【${id}】?`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
          var postData = {
            customer: "advanced",
            code: "INVERTER",
            action: "SUNCTL_ON_OFF",
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

    SUN_PERCENT(id, value) {
      const vm = this;

      vm.$confirm(`確定設置【${id}】輸出百分比為【${value}】?`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
          var postData = {
            customer: "advanced",
            code: "DCU",
            action: "SUNCTL_SET_POWER",
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
<style scoped>
.table {
  display: table;
  width: 100%;
  border-collapse: collapse;
}

.table-row {
  display: table-row;
}

.table-cell {
  display: table-cell;
  border: 1px solid #ccc;
  padding: 6px 10px;
  vertical-align: middle;
}

.table-cell:first-child {
  font-weight: bold;
  background-color: #f8f9fa;
  min-width: 120px;
}

.table-header .table-cell {
  font-weight: bold;
  background-color: #e9ecef;
}
</style>