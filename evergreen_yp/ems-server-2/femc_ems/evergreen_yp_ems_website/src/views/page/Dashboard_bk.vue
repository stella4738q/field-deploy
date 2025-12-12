<template>
  <div class="row m-3" style="">
    <div class=" col-4 border-end border-2 d-flex justify-content-center align-items-end p-3 row " style="height: 85vh">
      <div class="row">
        <div class="col">
          <div class="row text-center mb-3">
            <h3>設備狀態</h3>
            <div class="mb-3">
              <font-awesome-icon icon="square" class="text-success" />正常
              <font-awesome-icon icon="square" class="text-warning" />系統程序
              <font-awesome-icon icon="square" class="text-danger" />異常
              <font-awesome-icon icon="square" class="text-dark" />關閉
            </div>
            <!-- ======================================================= -->
            <div class="row p-0 m-0 mb-2 align-items-center ms-5">
              <div class="col-4 p-0 text-start">
                <img src="@/assets/TAIPOWER.png" style="height: 5rem; width: auto;" alt="" />
                <div class="d-flex align-items-center pt-3">
                  <div class="arrow-discharge-to-TAI text-start text-danger" style="padding-left: 8%;" v-if="METER_MAIN.total_active_power > 0">
                    <font-awesome-icon icon="arrow-up-long" />
                  </div>
                  <div class="arrow-charge-from-TAI text-start" style="padding-left: 4%;" v-if="METER_MAIN.total_active_power < 0">
                    <font-awesome-icon icon="arrow-down-long" />
                  </div>
                  <div class="ps-3 pt-2">
                    {{ METER_MAIN.total_active_power }} kW
                  </div>
                </div>
              </div>
              <!-- -------------------太陽能------------------- -->
              <div class="col-8 p-0 text-start">
                <!-- 文字+按鈕 -->
                <div class="row p-0 m-0 ms-5">
                  <div class="col-3 p-0"></div>
                  <div class="col-4 p-0">
                    <div class="text-start" v-if="$store.getters.userPriviagePage('P01-03')">
                      <el-dropdown>
                        <button type="button" class="btn btn-outline-secondary border-0">
                          太陽能 <font-awesome-icon icon="bars" class="" />
                        </button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item>
                              <el-button type="text" @click="SolarControlDialog = true">
                                設備指令
                              </el-button>
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                    <div v-else class="text-center">
                      太陽能
                    </div>
                  </div>
                </div>
                <!-- ICON+箭頭 -->
                <div class="row p-0 m-0 ms-5">
                  <div class="col-3 p-0">
                    <div class="w-100 arrow-discharge text-start">
                      <font-awesome-icon icon="arrow-left-long" />
                    </div>
                    <div class="text-start">{{ METER_SUN.total_active_power }} kW</div>
                  </div>
                  <div class="col-4 p-0">
                    <img src="@/assets/solar-panel.png" style="height: 6rem; width: auto;" alt="" />
                  </div>
                </div>
              </div>
            </div>
            <!-- -------------------------------------- -->
            <div class="row p-0 m-0 mt-2 mb-2">
              <!-- -------------------工廠------------------- -->
              <div class="col-3 p-0 text-center">
                <br>
                <img src="@/assets/industry.png" style="height: 6rem; width: auto" alt="" />
              </div>
              <!-- -------------------工廠右邊------------------- -->
              <div class="col-9 p-0">
                <!-- -------------------PCS、BMS------------------- -->
                <!-- 文字+按鈕 -->
                <div class="row p-0 m-0 mb-2">
                  <div class="col p-0">
                  </div>
                  <div class="col-3 p-0">
                    <div class="text-center" v-if="$store.getters.userPriviagePage('P01-01')">
                      <el-dropdown>
                        <button type="button" class="btn btn-outline-secondary border-0">
                          PCS <font-awesome-icon icon="bars" class="" />
                        </button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item>
                              <el-button type="text" @click="PCSClick('PCS1', 'BMS1')">
                                設備指令
                              </el-button>
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                    <div class="text-center" v-else>PCS</div>
                  </div>
                  <div class="col p-0">
                  </div>
                  <div class="col-3 p-0">
                    <div class="text-center" v-if="$store.getters.userPriviagePage('P01-02')">
                      <el-dropdown>
                        <button type="button" class="btn btn-outline-secondary border-0">
                          BMS <font-awesome-icon icon="bars" class="" />
                        </button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item>
                              <el-button type="text"  @click="BMSClick('BMS1')">
                                設備指令
                              </el-button>
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                    <div class="text-center" v-else>BMS</div>
                  </div>
                </div>
                <!-- ICON+箭頭 -->
                <div class="row p-0 m-0 mb-2">
                  <div class="col p-0">
                    <div class="w-100 arrow-charge text-start" v-if="SocketDataALL?.pcs[0]?.active_power < 0">
                      <font-awesome-icon icon="arrow-right-long" />
                    </div>
                    <!-- <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0"> -->
                    <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0">
                      <font-awesome-icon icon="arrow-left-long" />
                    </div>
                    <div class="text-center">{{ SocketDataALL?.pcs[0]?.active_power }} kW</div>
                  </div>
                  <div class="col-3 p-0">
                    <font-awesome-icon icon="mobile-retro" style="font-size: 5rem;"
                      :class="'text-' + EquipmentStatusColor.PCS.find((x) => { return x.name == SocketDataALL?.pcs[0]?.working_status })?.color" />
                  </div>
                  <div class="col p-0">
                    <div class="w-100 arrow-charge text-start" v-if="SocketDataALL?.pcs[0]?.active_power < 0">
                      <font-awesome-icon icon="arrow-right-long" />
                    </div>
                    <!-- <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0"> -->
                    <div class="w-100 arrow-discharge text-end">
                      <font-awesome-icon icon="arrow-left-long" />
                    </div>
                  </div>
                  <div class="col-3 p-0">
                    <font-awesome-icon icon="battery-full" style="font-size: 5rem; transform: rotate(-90deg);"
                      :class="'text-' + EquipmentStatusColor.BMS.find((x) => { return x.name == SocketDataALL?.bms[0]?.working_status })?.color" />
                  </div>
                </div>
                <!-- 下方文字 -->
                <div class="row  p-0 m-0 mb-2">
                  <div class="col p-0  d-flex align-items-center ">
                  </div>
                  <div class="col-4 p-0">
                    <div>狀態：{{ SocketDataALL?.pcs[0]?.working_status }}</div>
                    <!-- <div>模式：{{ SocketDataALL?.pcs[0]?.working_mode }}</div> -->
                    <!-- <div>
                      {{ ![null, undefined].includes(SocketDataALL?.pcs[0]?.active_power) ?
                      (SocketDataALL?.pcs[0]?.active_power).toFixed(2).toLocaleString() : 'No Data' }} kW
                    </div> -->
                  </div>
                  <div class="col p-0 d-flex align-items-center">
                  </div>
                  <div class="col-4 p-0">
                    <div>
                      狀態：{{ SocketDataALL?.bms[0]?.working_status }}
                    </div>
                  </div>
                </div>
              </div>
              <!-- -------------------工廠右邊------------------- -->
            </div>
            <!-- -------------------------------------- -->
            <!-- ======================================================= -->
            <!-- <div class="row p-0 m-0 mb-2">
              <div class="col-3 p-0">
                <div class="text-center" v-if="$store.getters.userPriviagePage('P01-02')">
                  <el-dropdown>
                    <button type="button" class="btn btn-outline-secondary border-0">
                      LC <font-awesome-icon icon="bars" class="" />
                    </button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item>
                          <el-button type="text" @click="LCControlDialog = true">
                            設備指令
                          </el-button>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
                <div v-else class="text-center">
                  LC
                </div>
              </div>
              <div class="col p-0 d-flex align-items-center">
              </div>
              <div class="col-3 p-0">
                <div class="text-center" v-if="$store.getters.userPriviagePage('P01-03')">
                  <el-dropdown>
                    <button type="button" class="btn btn-outline-secondary border-0">
                      PCS <font-awesome-icon icon="bars" class="" />
                    </button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item>
                          <el-button type="text" @click="PCSStatusDialog = true">
                            設備指令
                          </el-button>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
                <div class="text-center" v-else>PCS</div>
              </div>
              <div class="col p-0 d-flex align-items-center">
              </div>
              <div class="col-3 p-0">
                <div class="text-center" v-if="$store.getters.userPriviagePage('P01-04')">
                  <el-dropdown>
                    <button type="button" class="btn btn-outline-secondary border-0">
                      BMS <font-awesome-icon icon="bars" class="" />
                    </button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item>
                          <el-button type="text" @click="BMSControlDialog = true">
                            設備指令
                          </el-button>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
                <div class="text-center" v-else>BMS</div>
              </div>
            </div>

            <div class="row  p-0 m-0 mb-2">
              <div class="col-3 p-0">
                <font-awesome-icon icon="toilet-portable" style="font-size: 5rem;"
                  :class="'text-' + EquipmentStatusColor.LC.find((x) => { return x.name == SocketDataALL?.lc[0]?.system_working_status })?.color" />
              </div>
              <div class="col p-0  d-flex align-items-center ">
                <div class="w-100 arrow-charge text-start" v-if="SocketDataALL?.pcs[0]?.active_power < 0">
                  <font-awesome-icon icon="arrow-right-long" />
                </div>
                <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0">
                  <font-awesome-icon icon="arrow-left-long" />
                </div>
              </div>
              <div class="col-3 p-0">
                <font-awesome-icon icon="mobile-retro" style="font-size: 5rem;"
                  :class="'text-' + EquipmentStatusColor.PCS.find((x) => { return x.name == SocketDataALL?.pcs[0]?.working_status })?.color" />
              </div>
              <div class="col p-0 d-flex align-items-center">
                <div class="w-100 arrow-charge text-start" v-if="SocketDataALL?.pcs[0]?.active_power < 0">
                  <font-awesome-icon icon="arrow-right-long" />
                </div>
                <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0">
                  <font-awesome-icon icon="arrow-left-long" />
                </div>
              </div>
              <div class="col-3 p-0">
                <font-awesome-icon icon="battery-full" style="font-size: 5rem; transform: rotate(-90deg);"
                  :class="'text-' + EquipmentStatusColor.BMS.find((x) => { return x.name == SocketDataALL?.bms[0]?.working_status })?.color" />
              </div>
            </div>

            <div class="row  p-0 m-0 mb-2">
              <div class="col-3 p-0">
                <div>狀態：{{ SocketDataALL?.lc[0]?.system_working_status }}</div>
                <div>模式：{{ SocketDataALL?.lc[0]?.working_mode }}</div>
              </div>
              <div class="col p-0  d-flex align-items-center ">
              </div>
              <div class="col-3 p-0">
                <div>狀態：{{ SocketDataALL?.pcs[0]?.working_status }}</div>
                <div>
                  {{ ![null, undefined].includes(SocketDataALL?.pcs[0]?.active_power) ?
                      (SocketDataALL?.pcs[0]?.active_power).toFixed(2).toLocaleString() : 'No Data' }} kW
                </div>
              </div>
              <div class="col p-0 d-flex align-items-center">
              </div>
              <div class="col-3 p-0">
                <div>
                  狀態：{{ SocketDataALL?.bms[0]?.working_status }}
                </div>
              </div>

            </div> -->
            <!-- ======================================================= -->
            <div class="col-12 row d-flex justify-content-around text-white">
              <!-- 儲能櫃01 -->
              <div class="col p-2 border cursor-pointer" @click="toCabinetList(SocketDataALL?.pcs[0]?.equipment_id)">
                <!-- <div class="row m-0 ">
                    <div :class="'col-6 border mb-1  d-flex justify-content-center align-items-center ' + getClass('CABINET_1' , 'air_abnormal')" style="height:3rem">空調</div>
                    <div :class="'col-6 border mb-1  d-flex justify-content-center align-items-center' + getClass('CABINET_1' , 'fire_abnormal')" style="height:3rem">消防</div>
                  </div> -->
                <div class="row p-0  m-0">
                  <div :class="'col-6 border mb-1' + getRackClass('rack_4')">R4</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_5')">R5</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_3')">R3</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_6')">R6</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_2')">R2</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_7')">R7</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_1')">R1</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_8')">R8</div>
                  <div :class="'col-6 border mb-1' + getClassFire">消防</div>
                  <div :class="'col-6 border mb-1' + getRackClass('rack_9')">R9</div>
                </div>
                <!-- <div class="row m-0">
                  <div :class="'border mb-1  d-flex justify-content-center align-items-center' + getClassBSC()"
                    style="height:6rem">BSC</div>
                </div> -->
                <!-- <div class="row m-0">
                  <div :class="'border mb-1  d-flex justify-content-center align-items-center' + getClassFire"
                    style="height:2rem">
                    消防</div>
                </div> -->
              </div>
            </div>
            <!-- ======================================================= -->
            <div class=" col-6 pt-2" v-for=" meter in SocketDataALL?.meter">
              <ChartAVWTASTO
                :chartObj="{ 
                  name: meter.parent_id, 
                  equipment_id: meter.equipment_id, 
                  ampere: meter.current_avg, 
                  voltage: meter.voltage_avg, 
                  kW: meter.total_active_power, 
                  q_total: meter.total_reactive_power, 
                  s_total: meter.total_apparent_power 
                  }">
              </ChartAVWTASTO>
            </div>

          </div>
        </div>

      </div>


    </div>

    <div class="col-8 row ms-2">
      <!-- 契約容量 -->
      <div class="col-12 ps-2 pe-1">
        <div class="shadow d-flex justify-content-center pt-3 pb-3 alert alert-success ">
          <!-- <div class="col"><b>系統可充電量：</b>{{ SocketDataALL?.lc[0]?.system_available_charge_energy ?? 0 }} kWh</div>
          <div class="col"><b>系統可放電量：</b>{{ SocketDataALL?.lc[0]?.system_available_discharge_energy ?? 0 }} kWh</div> -->
          <div class="col"><b>EMS狀態：</b>{{ myEMSStatus }} </div>
          <div class="col"> <b>目前用量：{{ SocketDataALL?.other?.contract_capacity?.toFixed(2) }}</b>kW</div>
          <div class="col"> <b>契約容量：{{ SystemConfig.contract_capacity }}</b>kW</div>
          <span class="" v-if="$store.getters.userPriviagePage('P01-01')">
              <el-button type="danger" @click="CloseClick">
                緊急控制 <font-awesome-icon icon="bars" class="ps-2 pb-1" />
              </el-button>
          </span>
        </div>
      </div>

      <div class="ms-2 me-2 pe-4">
        <div class="row shadow">
          <!-- 各櫃soh -->
          <div class="col-6 m-0 p-0">
            <div class="m-1">
              <ChartPower></ChartPower>
            </div>
          </div>
          <!-- 各櫃soc -->
          <div class="col-3 m-0 p-0 border-start border-end">
            <div class="m-1">
              <ChartGaugeSOC :socketData="SocketDataALL?.bms[0]?.soc"></ChartGaugeSOC>
            </div>
          </div>
          <!-- 運轉時間 -->
          <div class="col-3 m-0 p-2">
            <div class="m-1 text-center">
              <p class="">運轉狀況</p>

              <div v-for="bms in SocketDataALL?.bms" class="mt-1" style="font-size: smaller">
                <div class="">
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(103, 194, 58, 0.2)">
                    <span><font-awesome-icon icon="battery" />日充電量</span>
                    <span class="text-end"> {{ bms.daily_charging_capacity?.toLocaleString() }} kWh</span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(255, 127, 14, 0.3)">
                    <span><font-awesome-icon icon="bolt" />日放電量</span>
                    <span> {{ bms.daily_discharging_capacity?.toLocaleString() }} kWh </span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(103, 194, 58, 0.2)">
                    <span><font-awesome-icon icon="battery" />總充電量</span>
                    <span class="text-end"> {{ bms.total_charge_capacity?.toLocaleString() }} kWh</span>
                  </div>
                  <div class="rounded-3 d-flex justify-content-between mb-1"
                    style="background: rgba(255, 127, 14, 0.3)">
                    <span><font-awesome-icon icon="bolt" />總放電量</span>
                    <span> {{ bms.total_discharge_capacity?.toLocaleString() }} kWh </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 mb-4 ">
        <Schedule :Editable="false" :SOC="SocketDataALL?.bms[0]?.soc"></Schedule>
      </div>

    </div>
  </div>

  <el-dialog title="太陽能設備" v-model="SolarControlDialog" top="10px" class="dialog-width" :destroy-on-close="true">
    <SUNControl :sunKeyName="'METER_SUN'"></SUNControl>
  </el-dialog>

  <el-dialog :title="'PCS 控制-' + myPCS" v-model="PCSControlDialog" top="10px" class="dialog-width" :destroy-on-close="true">
    <PCSControl :PCSStoreID="myPCS" :BMSStoreID="myBMS"></PCSControl>
  </el-dialog>

  <el-dialog :title="'BMS 控制-' + myBMS" v-model="BMSControlDialog" top="10px" class="dialog-width" :destroy-on-close="true">
    <BMSControl :BMSStoreID="myBMS"></BMSControl>
  </el-dialog>

</template>
<script>
import Schedule from '@/components/Schedule.vue';
import ChartGaugeSOC from '@/components/ChartGaugeSOC.vue';
import ChartGaugeSOH from '@/components/ChartGaugeSOH.vue';
import ChartAVWTASTO from '@/components/ChartAVWTASTO.vue';
import ChartPower from '@/components/ChartPower.vue';
import { getSystemStorageSetting, postModbusControlEmergency } from '@/api/Api.js';
import ManualDischarge from '@/components/ManualDischarge.vue';
import FireControl from '@/components/FireControl.vue';
import ACBControl from '@/components/ACBControl.vue';
import VCBControl from '@/components/VCBControl.vue';
import moment from "moment";
import EnumList from '@/JSON/EnumList.json';
import FireAlarmCodeList from '@/JSON/FireAlarmCodeList.json';
import EquipmentStatusColor from '@/JSON/EquipmentStatusColor.json';
import { mapState } from "vuex";
import PCSControl from '@/components/PCSControl.vue';
import BMSControl from '@/components/BMSControl.vue';
import SUNControl from '@/components/SUNControl.vue';
import {
  getSystemElectricSetting,
} from '@/api/Api.js';

window.allCharts = [];

export default {
  components: {
    Schedule, ChartGaugeSOC, ChartGaugeSOH, ChartAVWTASTO, ManualDischarge, FireControl, ACBControl, ChartPower, PCSControl, BMSControl, VCBControl, SUNControl
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
    };
  },
  computed: {
    ...mapState(["SocketDataALL","METER_SUN", "METER_FACTORY", "METER_MAIN", "METER_CABINET"]),
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
  },
  mounted() {
    this.getSystemElectricSetting();
    this.LoadSetting();
  },
  created() {

  },
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
    getSystemElectricSetting() {
      const vm = this;
      getSystemElectricSetting()
        .then(response => {
          if (response.data.message == "Success") {
            var find = response.data.data.find(x => { return x.set == 1 });
            if (find) {
              vm.Setting.ElectSetting = JSON.parse(find.json_data);
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
    getRackClass(attr) {
      var find = this.SocketDataALL?.bms[0]?.rack.find(x => { return x.equipment_id == attr });
      if (find) {
        return find.abnormal ? ' bg-danger' : ' bg-success';
      }
      return ' bg-dark';
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
      vm.$confirm('確定送出指令?', '提示', {
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
  },
};
</script>
<style>
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