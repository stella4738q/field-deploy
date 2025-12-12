<template>
  <div class="inverter-info">
    <div class="inverter-details">
      <el-row :gutter="20" align="middle">
        <el-col :span="18">
          <h3>逆變器{{ this.inverter?.equipment_id?.substr(this.inverter?.equipment_id?.length - 1 ?? 0) ?? "" }}</h3>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="8">
          <TextBlock 
            :icon="''" 
            :num="this.maxPower && this.maxPower != 0 ? ((this.inverter?.total_active_power ?? 0) / this.maxPower * 100).toFixed(2) : '0.00'" 
            :unit="'%'" 
            :hint="'輸出百分比'"></TextBlock>
        </el-col>

        <el-col :xs="12" :sm="12" :md="8">
          <TextBlock 
            :icon="''" 
            :num="(this.inverter?.energy_today_kwh ?? 0).toFixed(2) ?? '0.00'" 
            :unit="'KWH'" 
            :hint="'日發電量'"></TextBlock>
        </el-col>

        <el-col :xs="12" :sm="12" :md="8">
          <TextBlock 
            :icon="''" 
            :num="this.totalDCPower.toFixed(2) ?? '0.00'" 
            :unit="'kW'" 
            :hint="'DC功率'"></TextBlock>
        </el-col>
      </el-row>

      <el-button type="text" @click="toggleDCInfo">{{ showDCInfo ? '隱藏' : '顯示' }}其他資訊</el-button>

      <div v-if="showDCInfo">
        <el-row :gutter="20">
            <el-col :xs="12" :sm="12" :md="8">
              <TextBlock 
                :icon="''" 
                :num="this.inverter?.operation_mode_name ?? '-'"
                :unit="''" 
                :hint="'模式'"></TextBlock>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8">
              <TextBlock 
                :icon="''" 
                :num="this.inverter?.internal_temperature ?? 0" 
                :unit="'°C'" 
                :hint="'溫度'"></TextBlock>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8">
              <TextBlock 
                :icon="''" 
                :num="(this.inverter?.energy_total_kwh ?? 0).toFixed(2) ?? '0.00'" 
                :unit="'kWH'" 
                :hint="'總發電量'"></TextBlock>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8">
              <TextBlock 
                :icon="''" 
                :num="(((this.inverter?.ac_l1_phase_voltage ?? 0) + (this.inverter?.ac_l2_phase_voltage ?? 0) + (this.inverter?.ac_l3_phase_voltage ?? 0)) / 3).toFixed(2)" 
                :unit="'V'" 
                :hint="'AC電壓'"></TextBlock>
            </el-col>
            <el-col :xs="12" :sm="12" :md="8">
              <TextBlock 
                :icon="''" 
                :num="(((this.inverter?.ac_l1_phase_current ?? 0) + (this.inverter?.ac_l2_phase_current ?? 0) + (this.inverter?.ac_l3_phase_current ?? 0)) / 3).toFixed(2)" 
                :unit="'A'" 
                :hint="'AC電流'"></TextBlock>
            </el-col>
            <el-col :xs="12" :sm="12" :md="8">
              <TextBlock 
                :icon="''" 
                :num="this.inverter?.total_active_power?.toFixed(3) ?? 0" 
                :unit="'kW'" 
                :hint="'AC功率'"></TextBlock>
            </el-col>
        </el-row>
        <h4>DC資訊</h4>
        <el-table :data="pvData" style="width: 100%">
          <el-table-column prop="name" label="串列" :min-width="100"></el-table-column>
          <el-table-column prop="voltage" label="電壓 (V)" :min-width="100"></el-table-column>
          <el-table-column prop="current" label="電流 (A)" :min-width="100"></el-table-column>
          <el-table-column prop="power" label="功率 (W)" :min-width="100"></el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { getEquipments, postModbusControl } from '@/api/Api.js';
import TextBlock from '@/components/TextBlock.vue';

export default {
  name: 'InverterInfo',
  props: {
    inverter: {
      type: Object,
      required: true,
    },
    pvCount: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      maxPower: 0,
      showDCInfo: false,
    };
  },
  computed: {
    ControlPriviage : function () { return this.$store.getters.userPriviagePage('P01-03'); },
    pvData() {
      const rtnData = [];
      for (let i = 0; i < this.pvCount; i++) {
        const pvId = i + 1;
        let name = `PV${pvId}`;
        let voltage = 0;
        let current = 0;
        let power = 0;

        if (pvId === 1) {
          voltage = this.formatNumber(this.inverter?.dc_1st_input_voltage?.toFixed(2)) ?? '0';
          current = this.formatNumber(this.inverter?.dc_1st_input_current?.toFixed(3)) ?? '0';
          power = this.formatNumber(this.inverter?.dc_1st_input_power?.toFixed(3)) ?? '0';
        } else if (pvId === 2) {
          voltage = this.formatNumber(this.inverter?.dc_2nd_input_voltage?.toFixed(2)) ?? '0';
          current = this.formatNumber(this.inverter?.dc_2nd_input_current?.toFixed(3)) ?? '0';
          power = this.formatNumber(this.inverter?.dc_2nd_input_power?.toFixed(3)) ?? '0';
        } else if (pvId === 3) {
          voltage = this.formatNumber(this.inverter?.dc_3rd_input_voltage?.toFixed(2)) ?? '0';
          current = this.formatNumber(this.inverter?.dc_3rd_input_current?.toFixed(3)) ?? '0';
          power = this.formatNumber(this.inverter?.dc_3rd_input_power?.toFixed(3)) ?? '0';
        } else {
          voltage = this.formatNumber(this.inverter ? (this.inverter[`dc_${pvId}th_input_voltage`]?.toFixed(2) ?? 0) : 0) ?? '0';
          current = this.formatNumber(this.inverter ? (this.inverter[`dc_${pvId}th_input_current`]?.toFixed(3) ?? 0) : 0) ?? '0';
          power = this.formatNumber(this.inverter ? (this.inverter[`dc_${pvId}th_input_power`]?.toFixed(3) ?? 0) : 0) ?? '0';
        }
        rtnData.push({ name, voltage, current, power });
      }
      return rtnData;
    },
    totalDCPower() {
      const total = this.pvData.reduce((sum, item) => {
        return sum + (parseFloat(item.power.toString().replace(/,/g, '')) || 0);
      }, 0);
      return total/1000; //轉kwh
    }
  },
  components: {
    TextBlock,
  },
  mounted() {
    this.getEquipment();
  },
  methods: {
    getEquipment() {
      const vm = this;
      var parameter = {
        equipment_type: 3,
        name: vm.inverter.equipment_id
      }

      getEquipments(parameter)
        .then((response) => {
          vm.maxPower = response.data?.data[0]?.capacity ?? 0;
        })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        });
    },
    formatNumber(value) {
      if(value === 'NaN' || Number.isNaN(value) || value === null || value === undefined){
        return 0;
      }
      return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    SUN_ON_OFF(id, value) {
      const vm = this;

      vm.$confirm(`確定【${value ? '開啟' : '關閉'}】【${id}】?`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        if (id.indexOf(3) > -1) {
          vm.$loading();
          let AllP = vm.postRackList(value);
          Promise.all(AllP).then(response => { }).finally(x => {
            vm.$loading().close();
            vm.$message({ type: 'success', message: "指令已下達" });
          })

        } else {
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
        }


      }).catch(() => {
      });
    },
    SUN_PERCENT(id, value) {
      const vm = this;

      vm.$confirm(`確定設置【${id}】輸出百分比為【${value}】?`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        if (id.indexOf(3) > -1) {
          vm.$loading();
          let AllP = vm.postRackList(value);
          Promise.all(AllP).then(response => { }).finally(x => {
            vm.$loading().close();
            vm.$message({ type: 'success', message: "指令已下達" });
          })

        } else {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "INVERTER",
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
        }


      }).catch(() => {
      });
    },
    toggleDCInfo() {
      this.showDCInfo = !this.showDCInfo;
    },
  }
};
</script>

<style scoped>
.inverter-info {
  padding: 20px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  max-width: 1200px; 
  margin: 0 auto; 
}

.inverter-details h3 {
  color: #333;
  margin-bottom: 15px;
}

.el-col {
  margin-bottom: 10px;
}

.pv-details {
  padding: 15px;
  margin-top: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.1);
}

.pv-details h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #444;
}

.el-table th {
  background-color: #f5f5f5;
  color: #444;
  font-weight: bold; 
}

.el-table td {
  text-align: center;
  line-height: 1.8; 
}

.el-table-column {
  padding: 12px;
}

.text-block {
  background-color: #fafafa; 
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.05);
}
</style>
