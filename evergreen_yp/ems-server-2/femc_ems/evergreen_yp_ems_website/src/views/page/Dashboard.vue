<template>
  <div class="row gx-3 gy-3">
    <div class="col-12 col-md-6 col-lg-4">
      <div class="card shadow-sm border-0">
        <div class="card-body text-center">
          <h5 class="card-title">設備狀態</h5>
          <div class="mb-3">
            <font-awesome-icon icon="square" class="text-success" />正常
            <font-awesome-icon icon="square" class="text-warning" />告警
            <font-awesome-icon icon="square" class="text-danger" />異常
            <font-awesome-icon icon="square" class="text-dark" />關閉
          </div>
          <!-- ======================================================= -->
          <DashboardEquipment></DashboardEquipment>
          <!-- ======================儲能櫃================================= -->
          <div class="row mb-2 text-white">
            <!-- BMU1 -->
            <div class="col-6 p-1 border cursor-pointer" @click="toCabinetList('BMU_1')">
              <div class="row p-0 m-0 flex-column align-items-stretch">
                <div :class="'border mb-1 small-status-block text-dark'">BMS_1</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_1', 'rack_6')">R6</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_1', 'rack_5')">R5</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_1', 'rack_4')">R4</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_1', 'rack_3')">R3</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_1', 'rack_2')">R2</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_1', 'rack_1')">R1</div>
                <div :class="'border mb-1 small-status-block ' + getBmuFireClass('bmu_1')">消防</div>
                <div :class="'border mb-1 small-status-block ' + getTMSStatus('bmu_1')">液冷</div>
              </div>
            </div>

            <!-- BMU2 -->
            <div class="col-6 p-1 border cursor-pointer" @click="toCabinetList('BMU_2')">
              <div class="row p-0 m-0 flex-column align-items-stretch">
                <div :class="'border mb-1 small-status-block text-dark'">BMS_2</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_2', 'rack_6')">R6</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_2', 'rack_5')">R5</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_2', 'rack_4')">R4</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_2', 'rack_3')">R3</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_2', 'rack_2')">R2</div>
                <div :class="'border mb-1 small-status-block ' + getRackClass('bmu_2', 'rack_1')">R1</div>
                <div :class="'border mb-1 small-status-block ' + getBmuFireClass('bmu_2')">消防</div>
                <div :class="'border mb-1 small-status-block ' + getTMSStatus('bmu_2')">液冷</div>
              </div>
            </div>
          </div>
          <!-- ======================================================= -->
          <div class="row">
            <div class="col-12 col-md-12 col-lg-6" v-for="meter in orderedMeters" :key="meter.equipment_id">
              <ChartAVWTASTO :chartObj="{
                name: meter.parent_id,
                equipment_id: meter.equipment_id,
                ampere: meter.current_avg,
                voltage: meter.voltage_avg,
                kW: meter.total_active_power,
                q_total: meter.total_reactive_power,
                s_total: meter.total_apparent_power,
                pf_total: meter.total_power_factor,
                exp_kwh: meter.ac_energy_exp,
                imp_kwh:  meter.ac_energy_imp
              }">
              </ChartAVWTASTO>
            </div>
          </div>
          <!-- ======================================================= -->
        </div>
      </div>
    </div>
    <!----------------------------------------------------------->
    <div class="col-12 col-md-6 col-lg-8">
      <!-- ======================================================= -->
      <!-- 控制模式 -->
      <div style="font-size: large;" class="row shadow justify-content-center align-items-center pt-3 pb-3 alert alert-warning ">
        <!-- <div class="col-4 col-sm-6 col-md-3"><b>控制模式：</b>{{ myOperationMode }} </div>
        <span class="col-4 col-sm-3 col-md-3" v-if="$store.getters.userPriviagePage('P01-07')">
          <el-button :type="this.OPERATE_MODE === 0 ? 'success' : this.OPERATE_MODE === 1 ? 'primary' : 'dark'" 
            @click="ChangeModeClick">
            切換模式 <font-awesome-icon icon="bars" class="ps-2 pb-1" />
        </el-button>
        </span> -->
                <div class="col-6 col-sm-6 col-md-3">  
          <span class="col-4 col-sm-3 col-md-3" v-if="$store.getters.userPriviagePage('P01-06')">
            <el-dropdown>
              <el-button type="danger" class="border-0">
                緊急控制 <font-awesome-icon icon="bars" class="ms-2" />
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="CloseClick">
                    系統急停
                  </el-dropdown-item>
                  <el-dropdown-item @click="VCBClick">
                    VCB開關
                  </el-dropdown-item>
                  <el-dropdown-item @click="MPBESSClick">
                    MPBESS控制
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </span>
        </div>
      </div>

      <!-- 契約容量 -->
      <div style="font-size: large;" class="row shadow justify-content-center align-items-center pt-3 pb-3 alert alert-success ">
        <!-- <div class="col"><b>系統可充電量：</b>{{ SocketDataALL?.lc[0]?.system_available_charge_energy ?? 0 }} kWh</div>
          <div class="col"><b>系統可放電量：</b>{{ SocketDataALL?.lc[0]?.system_available_discharge_energy ?? 0 }} kWh</div> -->
        <div class="col-6 col-sm-6 col-md-3"><b>EMS狀態：</b>{{ myEMSStatus }} </div>
        <div class="col-6 col-sm-6 col-md-3"> <b>15分鐘平均：{{ METER_MAIN?.accu_demand_kw?.toLocaleString() }}</b>kW</div>
        <div class="col-6 col-sm-6 col-md-3"> <b>契約容量：{{ SystemConfig.contract_capacity?.toLocaleString() }}</b>kW</div>
      </div>

      <!-- 契約容量 -->
      <!-- ======================================================= -->
      <div class="card shadow-sm border-0 mb-3">
        <div class="card-body row">
          <!-- 各櫃soh -->
          <div class="col-12 col-md-12 col-lg-6 col-xl-6 m-0 p-0">
            <div class="m-1">
              <ChartPower></ChartPower>
            </div>
          </div>
          <!-- 各櫃soc -->
          <div class="col-12 col-md-12 col-lg-6 col-xl-3 m-0 p-0">
            <div class="m-1">
              <ChartGaugeSOC :socketData="this.BMS1"></ChartGaugeSOC>
              <b>BMS_1</b>
              <div v-if="this.BMS1" class="mt-1" style="font-size: smaller">
                <div class="">
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(103, 194, 58, 0.2)">
                    <span><font-awesome-icon icon="battery" />日充電量</span>
                    <span class="text-end"> {{ this.BMS1?.daily_charging_capacity?.toLocaleString() }} kWh</span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(255, 127, 14, 0.3)">
                    <span><font-awesome-icon icon="bolt" />日放電量</span>
                    <span> {{ this.BMS1?.daily_discharging_capacity?.toLocaleString() }} kWh </span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(103, 194, 58, 0.2)">
                    <span><font-awesome-icon icon="battery" />總充電量</span>
                    <span class="text-end"> {{ this.BMS1?.total_charge_capacity?.toLocaleString() }} kWh</span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(255, 127, 14, 0.3)">
                    <span><font-awesome-icon icon="bolt" />總放電量</span>
                    <span> {{ this.BMS1?.total_discharge_capacity?.toLocaleString() }} kWh </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-12 col-md-12 col-lg-6 col-xl-3 m-0 p-0">
            <div class="m-1">
              <ChartGaugeSOC :socketData="this.BMS2"></ChartGaugeSOC>
              <b>BMS_2</b>
              <div v-if="this.BMS2" class="mt-1" style="font-size: smaller">
                <div class="">
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(103, 194, 58, 0.2)">
                    <span><font-awesome-icon icon="battery" />日充電量</span>
                    <span class="text-end"> {{ this.BMS2?.daily_charging_capacity?.toLocaleString() }} kWh</span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(255, 127, 14, 0.3)">
                    <span><font-awesome-icon icon="bolt" />日放電量</span>
                    <span> {{ this.BMS2?.daily_discharging_capacity?.toLocaleString() }} kWh </span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(103, 194, 58, 0.2)">
                    <span><font-awesome-icon icon="battery" />總充電量</span>
                    <span class="text-end"> {{ this.BMS2?.total_charge_capacity?.toLocaleString() }} kWh</span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(255, 127, 14, 0.3)">
                    <span><font-awesome-icon icon="bolt" />總放電量</span>
                    <span> {{ this.BMS2?.total_discharge_capacity?.toLocaleString() }} kWh </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- ======================================================= -->
      <div class="card shadow-sm border-0 mb-3">
        <div class="card-body row">
          <div class="col-12" style="overflow-x: auto;">
            <Schedule :Editable="false" :SOC="SocketDataALL?.bms[0]?.soc" :chargeType="this.SystemConfig.chargeType" :operationMode="this.OPERATE_MODE"></Schedule>
          </div>
        </div>
      </div>
      <!-- ======================================================= -->
    </div>
    <!-- ======================================================= -->
  </div>

  <el-dialog title="VCB開關" v-model="VCBControlDialog" top="10px" class="dialog-width" :destroy-on-close="true">
      <VCBControl :StoreID="'VCB'"></VCBControl>
  </el-dialog>

  <el-dialog v-model="CabinetControlDialog" top="10px" class="dialog-width" :destroy-on-close="true">
    <el-tabs v-model="activeCabinetTab" type="card">
        <el-tab-pane
            v-for="index in 2"
            :key="'MP-BESS' + index"
            :label="'MP-BESS-' + index"
            :name="'MP-BESS' + index"
        >
         <CabinetControl :CabinetNo="index"></CabinetControl>
        </el-tab-pane>
    </el-tabs>  
  </el-dialog>
</template>
<script>
import Schedule from '@/components/Schedule.vue';
import ChartGaugeSOC from '@/components/ChartGaugeSOC.vue';
import ChartGaugeSOH from '@/components/ChartGaugeSOH.vue';
import ChartAVWTASTO from '@/components/ChartAVWTASTO.vue';
import ChartPower from '@/components/ChartPower.vue';
import { getSystemStorageSetting, postModbusControlEmergency, postOperateModeChange, getSystemDemand } from '@/api/Api.js';
import ManualDischarge from '@/components/ManualDischarge.vue';
import VCBControl from '@/components/VCBControl.vue';
import moment from "moment";
import EnumList from '@/JSON/EnumList.json';
import FireAlarmCodeList from '@/JSON/FireAlarmCodeList.json';
import EquipmentStatusColor from '@/JSON/EquipmentStatusColor.json';
import { mapState } from "vuex";
import PCSControl from '@/components/PCSControl.vue';
import BMSControl from '@/components/BMSControl.vue';
import CabinetControl from '@/components/CabinetControl.vue';
import DashboardEquipment from '@/components/DashboardEquipment.vue';
import {
  getSystemElectricSetting,
} from '@/api/Api.js';

window.allCharts = [];

export default {
  components: {
    Schedule,
    ChartGaugeSOC,
    ChartGaugeSOH,
    ChartAVWTASTO,
    ManualDischarge,
    CabinetControl,
    ChartPower,
    PCSControl,
    BMSControl,
    VCBControl,
    DashboardEquipment
  },
  data() {
    return {
      moment,
      EnumList,
      FireDialog: false,
      ManualDischargeDialog: false,
      ACBDialog: false,
      VCBDialog: false,
      FireAlarmCodeList,
      EquipmentStatusColor,
      PCSControlDialog: false,
      PCSWorkDialog: false,
      LCControlDialog: false,
      BMSControlDialog: false,
      SystemConfig: {},
      SolarControlDialog: false,
      myPCS: null,
      myBMS: null,
      myDCP: null,
      intervalId: null,
      VCBControlDialog: false,
      CabinetControlDialog: false,
      activeCabinetTab: 'MP-BESS1'
    };
  },
  computed: {
    ...mapState(["SocketDataALL", "METER_SUN", "METER_FACTORY", "METER_MAIN", "METER_CABINET", "OPERATE_MODE", "BMS1", "BMS2"]),
    myEMSStatus: function () {
      let result = '無訊號';
      if (this.SocketDataALL?.other?.ems_status != null) {
        var find = this.EnumList.ems_status.find(x => {
          return x.key == this.SocketDataALL?.other?.ems_status
        });

        if (find) {
          result = find.val.replace('{0}', this.SocketDataALL?.pcs[0]?.active_power > 0 ? "放" : "充");
        }
      }


      return result;
    },
    myOperationMode: function () {
      let result = '無訊號';
      if (this.OPERATE_MODE != null) {
        var find = this.EnumList.operation_mode.find(x => {
          return x.key == this.OPERATE_MODE
        });

        if (find) {
          result = find.val;
        }
      }


      return result;
    },
    mySRStatus: function () {
      let result = '';
      if (this.SystemConfig.sr_status != null) {
        var find = this.EnumList.sr_status.find(x => {
          return x.key == this.SystemConfig.sr_status
        });

        if (find) {
          result = find.val;
        }
      }
      return result;
    },
    getClassFire: function () {
      //SocketDataALL.io[0]?.solenoid_on
      //第三版開始
      var findErrorCode = false;
      this.SocketDataALL?.alarm?.forEach((item) => {
        findErrorCode = FireAlarmCodeList.includes(item.code);
        if (findErrorCode) return;
      });

      return findErrorCode ? ' bg-danger' : ' bg-success';


      //第三版結束

      //第二版開始
      // var fireState = this.SocketDataALL?.io[0]?.solenoid_on;
      // if (fireState == null || fireState == undefined) return ' bg-dark';
      // return fireState ? ' bg-danger' : ' bg-success';
      //第二版結束
      //第一版開始
      // var find = false;
      // this.SocketDataALL?.alarm.forEach(x=> {
      //    var mapCode = this.FireAlarmCodeList.includes(x.code);
      //    if (mapCode) {
      //     find = true;
      //     return;
      //    } 
      // });
      // 第一版結束
      return find ? ' bg-danger' : ' bg-success';

      return ' bg-dark';
    },
    getPCSClass: function () {
      var find = this.SocketDataALL?.pcs[0];
      if (find) {
        if (find.working_status.indexOf('關機') > -1) {
          return ' bg-dark';
        }
        return find.abnormal ? ' bg-danger' : ' bg-success';
      }
      return ' bg-dark';
    },
    orderedMeters() {
      const order = ["METER_MAIN", "METER_VCB", "METER_MP1", "METER_MP2", "METER_SUN1", "METER_SUN2"];
      const big = 9999; // 未命中時丟到最後

      const idx = (pid) => {
        if (!pid) return big;
        const i = order.indexOf(String(pid).toUpperCase());
        return i === -1 ? big : i;
      };

      const list = this.SocketDataALL?.meter || [];
      return [...list].sort((a, b) => {
        const ai = idx(a.equipment_id);
        const bi = idx(b.equipment_id);
        if (ai !== bi) return ai - bi;
        return String(a.equipment_id || "").localeCompare(String(b.equipment_id || ""));
      });
    }
  },
  mounted() {
    this.getSystemElectricSetting();
    // this.LoadSetting();
    this.fetchDemand();
    let vm = this;
    if (vm.intervalId === null) {
      vm.intervalId = window.setInterval(vm.fetchDemand, 10000);
    }
  },
  beforeUnmount() {
    // console.log('Dashboard beforeUnmount');
    let vm = this;
    window.clearInterval(this.intervalId);
    vm.intervalId = null;
  },
  created() {},
  methods: {
    LoadSetting() {
      const vm = this;
      vm.$loading();
      getSystemStorageSetting({ equipment_type: 1 })
        .then(response => {
          if (response.data.message == "Success") {
            var responseData = response.data.data;
            vm.SystemConfig.contract_capacity = responseData.find(x => { return x.key == "contract_capacity" })?.value;
            if (vm.SystemConfig.contract_capacity) {
              vm.SystemConfig.contract_capacity = vm.SystemConfig.contract_capacity * 1000;
            }

            //2024.11.28 新增 SystemConfig.chargeType
            var chargeType = responseData.find(x => { return x.key == "charge_type" })?.value;
            if (chargeType == 0) {
              vm.SystemConfig.chargeType = '手動排程';
            }
            else if(chargeType == 1){
              vm.SystemConfig.chargeType = '自動離峰儲電';
            }
            else{
              vm.SystemConfig.chargeType = '';
            }

          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .finally(() => {
          vm.$loading().close();
        })
    },
    async fetchDemand() {
      const vm = this;
      getSystemDemand().then(response => {
          if (response.data.message == "Success") {
            vm.SystemConfig.contract_capacity = (response.data?.data || 0).toLocaleString();
            vm.SystemConfig.chargeType = response.data?.charge_type;
            vm.SystemConfig.sr_status = response.data?.sr_status;
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
    },
    getSystemElectricSetting() {
      const vm = this;
      getSystemElectricSetting({
        is_set: 1
      }).then(response => {
          if (response.data.message == "Success") {
            vm.Setting.summer_time_start = response.data.data.summer_date_start.replace('-', '')
            vm.Setting.summer_time_end = response.data.data.summer_date_end.replace('-', '')
            var find = response.data.data.data.find(x => { return x.is_set == 1 });
            if (find) {
              vm.Setting.ElectSetting = find;
            }
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => { })
        .finally(() => { })
    },
    getClass(BMSName, attr) {
      var find = this.SocketDataPCS.find(x => { return x.parent_id == BMSName });
      if (find) {
        if (find.hasOwnProperty(attr)) {
          return find[attr] ? ' bg-danger' : ' bg-success';
        }
      }
      return ' bg-dark';
    },
    getClassBSC() {
      const stateALL = ['運行狀態', 'ECO狀態', '維護狀態', '故障狀態', '自檢狀態', '空閒狀態', '待機狀態'];
      const stateGood = ['運行狀態', 'ECO狀態', '維護狀態', '自檢狀態', '空閒狀態', '待機狀態'];

      var find = this.SocketDataALL?.bms[0];
      if (find) {
        if (stateGood.includes(find.working_status)) return ' bg-success';
        if (find.abnormal == '運行') return ' bg-danger';
      }
      return ' bg-dark';

      // var find = this.SocketDataALL?.bms[0];
      // if (find) {
      //   return find.abnormal ? ' bg-danger' : ' bg-success';
      // }
      // return ' bg-dark';
    },
    getRackClass(equipment_id, attr) {
      var findBms = this.SocketDataALL?.bms?.find(x => { return x.equipment_id?.toLowerCase() == equipment_id?.toLowerCase() });
      if (findBms) {
        var findRack = findBms?.rack?.find(x => { return x.equipment_id?.toLowerCase() == attr?.toLowerCase() });
        if (findRack){
          // 取得設備的狀態顏色
          const state_color = this.EquipmentStatusColor.RACK.find(x => x.name === findRack?.rack_state)?.color || '';
          // 檢查是否有 2 級或以上的告警
          const lv_2_alarm = findRack.warning?.find(ala => ala.level >= 2);

          // 判斷顏色邏輯
          if (lv_2_alarm || state_color.includes('danger')) {
              return ' bg-danger';
          }
          
          // 根據是否異常設定背景顏色
          return findRack.abnormal ? ' bg-warning' : ` ${state_color}`;
        }
      }
      return ' bg-dark';
    },
    getBmuFireClass(equipment_id){
      var find = this.SocketDataALL?.bms?.find((x)=>{ return x.equipment_id?.toLowerCase() == equipment_id.toLowerCase()});
      if (find == null || find === undefined) {
        return ' bg-dark';
      }
      if (find.fire)
        return ' bg-danger'
      return ' bg-success'
    },
    toCabinetList(par) {
      this.$router.push({ name: 'CabinetList', query: { tabname: par } });
    },
    PCSClick(item, item2) {
      this.myPCS = item;
      this.myBMS = item2;
      this.PCSControlDialog = true;
    },
    BMSClick(item) {
      this.myBMS = item;
      this.BMSControlDialog = true;
    },
    CloseClick() {
      const vm = this;
      vm.$confirm('確定送出【系統急停】指令？', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        var postData = {
          customer: "advanced",
          // code: "PCS",
          action: "EMERGENCY_ON_OFF",
          // equipment_id: this.SocketDataALL.pcs[0].equipment_id,
          // value: false,
        };
        postModbusControlEmergency(postData).then(response => {
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
    VCBClick() {
      this.VCBControlDialog = true;
    },
    MPBESSClick() {
      this.CabinetControlDialog = true;
    },
    ChangeModeClick() {
      const vm = this;
      var mode = vm.SocketDataALL?.other?.operation_mode;

      vm.$confirm(`確定修改控制模式為【${mode == 0 ? "遠端控制" : "EMS控制"}】？`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        var postData = {
          operation_mode: this.SocketDataALL?.other?.operation_mode == 0 ? 1 : 0,
        };
        postOperateModeChange(postData).then(response => {
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
    getFanStatus(equipment_id) {
      var find = this.SocketDataALL?.bms?.find((x)=>{ return x.equipment_id?.toLowerCase() == equipment_id.toLowerCase()});
      if (find == null || find === undefined) {
        return " bg-dark text-white";
      }

      if (find.fan_error) {
        return " bg-danger text-white";
      }

      if (find.fan_status) {
        return " bg-success text-white";
      } else {
        return " bg-dark text-white";
      }
    },
    getTMSStatus(equipment_id) {
      var find = this.SocketDataALL?.bms?.find((x)=>{ return x.equipment_id?.toLowerCase() == equipment_id.toLowerCase()});
      if (find == null || find === undefined) {
        return " bg-dark text-white";
      }
      else if (find.tms_fault_code) {
        return " bg-danger text-white";
      }
      else if (find.tms_status_code !== 0) {
        return " bg-success text-white";
      } else {
        return " bg-dark text-white";
      }
    },
    getSRColor() {
      switch (this.SystemConfig.sr_status) {
        case 0:
          //未得標
          return 'green';
        case 1:
          //待命中
          return 'blue';
        case 2:
          //中止服務
          return '#B36F05';
        case 3:
          //執行調度中
          return 'red'
        default:
          //調度恢復
          return '#5C05B3';
      }
    },
  },
};
</script>

<style scoped>
.small-status-block {
  height: 26px;
  line-height: 26px;
  font-size: 13px;
  padding: 0;
  text-align: center;
}

.arrow-charge {
  animation: arrowcharge 2s linear infinite;
}

.arrow-discharge {
  animation: arrowdischarge 2s linear infinite;
}

.arrow-charge-from-TAI {
  animation: arrowChargefromT 2s linear infinite;
}

.arrow-discharge-to-TAI {
  animation: arrowDischargeToT 2s linear infinite;
}

@keyframes arrowcharge {

  0% {

    transform: translateX(0%);
  }

  100% {
    transform: translateX(100%);
  }
}

@keyframes arrowdischarge {
  0% {

    transform: translateX(0%);
  }

  100% {
    transform: translateX(-100%);
  }
}

@keyframes arrowChargefromT {
  0% {

    transform: translateY(0%);
  }

  100% {
    transform: translateY(100%);
  }
}

@keyframes arrowDischargeToT {
  0% {

    transform: translateY(100%);
  }

  100% {
    transform: translateY(0%);
  }
}

.dialog-width {
  width: 100% !important;
}


@media(min-width: 800px) {
  .dialog-width {
    width: 800px !important;
  }
}
</style>