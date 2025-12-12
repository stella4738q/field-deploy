<template>
  <div class="row text-start g-1">
    <div class="col-12 col-md-3">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success">太陽能功率</p>
        <p class="fs-5 m-0 text-end mt-1">{{ ((inverterData1?.total_active_power ?? 0) + (inverterData2?.total_active_power ?? 0) + 
          (inverterData3?.total_active_power ?? 0) + (inverterData4?.total_active_power ?? 0) + (inverterData5?.total_active_power ?? 0)).toFixed(3) }}</p>
      </div>
    </div>


    <div class="col-12 col-md-3">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success">電表功率</p>
        <p class="fs-5 m-0 text-end mt-1">{{ sunData.kW.toFixed(3) }}</p>
      </div>
    </div>

    <div class="col-12 col-md-6">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success">inverter狀態</p>
        <div class="fs-5 p-0 text-end row m-0 text-white" v-if="inverterList">
          <div style="font-size: 18px;" class="col p-0 m-0 text-center border border-white mt-1" v-for="(inverter, ind) in inverterList.sort((a,b) => {return a.equipment_id > b.equipment_id ? 1 : -1})">
            <div :class="getInverterClass(inverter.equipment_id)"> {{ inverter.equipment_id.substr(inverter.equipment_id.length - 1) }}</div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <table class="table w-100 table-bordered text-start align-middle mt-2">
    <tbody>
      <tr>
        <td>逆變器1</td>
        <td>
          <table class="table w-100 table-bordered text-start align-middle mt-2">
            <tbody>
              <tr>
                <td style="width:60px">開/關機</td>
                <td style="width:100px">
                  <el-button-group>
                    <el-button type="primary" @click="SUN_ON_OFF(inverterData1.equipment_id, true)" :disabled="!(inverterData1?.inverter_state == 1) || !ControlPriviage">開</el-button>
                    <el-button type="danger" @click="SUN_ON_OFF(inverterData1.equipment_id, false)" :disabled="!(inverterData1?.inverter_state == 0) || !ControlPriviage">關</el-button>
                  </el-button-group>
                </td>
                <td style="width:60px">目前限制功率:{{inverterData1?.pure_power_percent}}%</td>
                <td style="width:100px">
                  <td>
                    <div class="input-group input-group-sm ">
                      <el-button type="primary" @click="SUN_PERCENT(inverterData1.equipment_id, 100)" :disabled="!(inverterData1?.pure_power_percent == 0) || !ControlPriviage">100%</el-button>
                      <el-button type="danger" @click="SUN_PERCENT(inverterData1.equipment_id, 0)" :disabled="!(inverterData1?.pure_power_percent == 100) || !ControlPriviage">0%</el-button>
                    </div>
                  </td>
                </td>
              </tr>
              <tr>
                <td style="width:80px">目前實功率(kW)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData1?.total_active_power?.toFixed(3) ?? 0 }}</div>
                </td>
                <td style="width:80px">目前虛功率(kVar)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData1?.total_reactive_power?.toFixed(3) ?? 0 }}</div>
                </td>
              </tr>
              <tr>
                <td style="width:80px">交流RST</td>
                <td colspan="3">
                  <div style="overflow-y: auto ;">{{ inverterData1?.ac_l1_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData1?.ac_l2_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData1?.ac_l3_phase_voltage?.toFixed(2) ?? 0 }} V</div>
                  <div style="overflow-y: auto ;">{{ inverterData1?.ac_l1_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData1?.ac_l2_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData1?.ac_l3_phase_current?.toFixed(3) ?? 0 }} A</div>
                </td>
                <!-- <td style="width:80px">功率因素(%)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData1.total_power_factor?.toFixed(2) ?? 0 }}</div>
                </td> -->
              </tr>
              <!-- <tr>
                <td style="width:80px">其他資訊</td>
                <td colspan="3">
                  <div class="json-display" style="max-height: 200px; overflow-y: auto ;">{{ inverterData1 }}</div>
                </td>
              </tr> -->
            </tbody>
          </table>
        </td>
      </tr>
      <!---->
      <tr>
        <td>逆變器2</td>
        <td>
          <table class="table w-100 table-bordered text-start align-middle mt-2">
            <tbody>
              <tr>
                <td style="width:60px">開/關機</td>
                <td style="width:100px">
                  <el-button-group>
                    <el-button type="primary" @click="SUN_ON_OFF(inverterData2.equipment_id, true)" :disabled="!(inverterData2?.inverter_state == 1) || !ControlPriviage">開</el-button>
                    <el-button type="danger" @click="SUN_ON_OFF(inverterData2.equipment_id, false)" :disabled="!(inverterData2?.inverter_state == 0) || !ControlPriviage">關</el-button>
                  </el-button-group>
                </td>
                <td style="width:60px">目前限制功率:{{inverterData2?.pure_power_percent}}%</td>
                <td style="width:100px">
                  <td>
                    <div class="input-group input-group-sm ">
                      <el-button type="primary" @click="SUN_PERCENT(inverterData2.equipment_id, 100)" :disabled="!(inverterData2?.pure_power_percent == 0) || !ControlPriviage">100%</el-button>
                      <el-button type="danger" @click="SUN_PERCENT(inverterData2.equipment_id, 0)" :disabled="!(inverterData2?.pure_power_percent == 100) || !ControlPriviage">0%</el-button>
                    </div>
                  </td>
                </td>
              </tr>
              <tr>
                <td style="width:80px">目前實功率(kW)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData2?.total_active_power?.toFixed(3) ?? 0 }}</div>
                </td>
                <td style="width:80px">目前虛功率(kVar)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData2?.total_reactive_power?.toFixed(3) ?? 0 }}</div>
                </td>
              </tr>
              <tr>
                <td style="width:80px">交流RST</td>
                <td colspan="3">
                  <div style="overflow-y: auto ;">{{ inverterData2?.ac_l1_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData2?.ac_l2_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData2?.ac_l3_phase_voltage?.toFixed(2) ?? 0 }} V</div>
                  <div style="overflow-y: auto ;">{{ inverterData2?.ac_l1_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData2?.ac_l2_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData2?.ac_l3_phase_current?.toFixed(3) ?? 0 }} A</div>
                </td>
                <!-- <td style="width:80px">功率因素(%)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData2.total_power_factor?.toFixed(2) ?? 0 }}</div>
                </td> -->
              </tr>
              <!-- <tr>
                <td style="width:80px">其他資訊</td>
                <td colspan="3">
                  <div class="json-display" style="max-height: 200px; overflow-y: auto ;">{{ inverterData2 }}</div>
                </td>
              </tr> -->
            </tbody>
          </table>
        </td>
      </tr>
      <!---->
      <tr>
        <td>逆變器3</td>
        <td>
          <table class="table w-100 table-bordered text-start align-middle mt-2">
            <tbody>
              <tr>
                <td style="width:60px">開/關機</td>
                <td style="width:100px">
                  <el-button-group>
                    <el-button type="primary" @click="SUN_ON_OFF(inverterData3.equipment_id, true)" :disabled="!(inverterData3?.inverter_state == 1) || !ControlPriviage">開</el-button>
                    <el-button type="danger" @click="SUN_ON_OFF(inverterData3.equipment_id, false)" :disabled="!(inverterData3?.inverter_state == 0) || !ControlPriviage">關</el-button>
                  </el-button-group>
                </td>
                <td style="width:60px">目前限制功率:{{inverterData3?.pure_power_percent}}%</td>
                <td style="width:100px">
                  <td>
                    <div class="input-group input-group-sm ">
                      <el-button type="primary" @click="SUN_PERCENT(inverterData3.equipment_id, 100)" :disabled="!(inverterData3?.pure_power_percent == 0) || !ControlPriviage">100%</el-button>
                      <el-button type="danger" @click="SUN_PERCENT(inverterData3.equipment_id, 0)" :disabled="!(inverterData3?.pure_power_percent == 100) || !ControlPriviage">0%</el-button>
                    </div>
                  </td>
                </td>
              </tr>
              <tr>
                <td style="width:80px">目前實功率(kW)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData3?.total_active_power?.toFixed(3) ?? 0 }}</div>
                </td>
                <td style="width:80px">目前虛功率(kVar)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData3?.total_reactive_power?.toFixed(3) ?? 0 }}</div>
                </td>
              </tr>
              <tr>
                <td style="width:80px">交流RST</td>
                <td colspan="3">
                  <div style="overflow-y: auto ;">{{ inverterData3?.ac_l1_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData3?.ac_l2_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData3?.ac_l3_phase_voltage?.toFixed(2) ?? 0 }} V</div>
                  <div style="overflow-y: auto ;">{{ inverterData3?.ac_l1_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData3?.ac_l2_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData3?.ac_l3_phase_current?.toFixed(3) ?? 0 }} A</div>
                </td>
                <!-- <td style="width:80px">功率因素(%)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData3.total_power_factor?.toFixed(2) ?? 0 }}</div>
                </td> -->
              </tr>
              <!-- <tr>
                <td style="width:80px">其他資訊</td>
                <td colspan="3">
                  <div class="json-display" style="max-height: 200px; overflow-y: auto ;">{{ inverterData3 }}</div>
                </td>
              </tr> -->
            </tbody>
          </table>
        </td>
      </tr>
      <!---->
      <tr>
        <td>逆變器4</td>
        <td>
          <table class="table w-100 table-bordered text-start align-middle mt-2">
            <tbody>
              <tr>
                <td style="width:60px">開/關機</td>
                <td style="width:100px">
                  <el-button-group>
                    <el-button type="primary" @click="SUN_ON_OFF(inverterData4.equipment_id, true)" :disabled="!(inverterData4?.inverter_state == 1) || !ControlPriviage">開</el-button>
                    <el-button type="danger" @click="SUN_ON_OFF(inverterData4.equipment_id, false)" :disabled="!(inverterData4?.inverter_state == 0) || !ControlPriviage">關</el-button>
                  </el-button-group>
                </td>
                <td style="width:60px">目前限制功率:{{inverterData4?.pure_power_percent}}%</td>
                <td style="width:100px">
                  <td>
                    <div class="input-group input-group-sm ">
                      <el-button type="primary" @click="SUN_PERCENT(inverterData4.equipment_id, 100)" :disabled="!(inverterData4?.pure_power_percent == 0) || !ControlPriviage">100%</el-button>
                      <el-button type="danger" @click="SUN_PERCENT(inverterData4.equipment_id, 0)" :disabled="!(inverterData4?.pure_power_percent == 100) || !ControlPriviage">0%</el-button>
                    </div>
                  </td>
                </td>
              </tr>
              <tr>
                <td style="width:80px">目前實功率(kW)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData4?.total_active_power?.toFixed(3) ?? 0 }}</div>
                </td>
                <td style="width:80px">目前虛功率(kVar)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData4?.total_reactive_power?.toFixed(3) ?? 0 }}</div>
                </td>
              </tr>
              <tr>
                <td style="width:80px">交流RST</td>
                <td colspan="3">
                  <div style="overflow-y: auto ;">{{ inverterData4?.ac_l1_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData4?.ac_l2_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData4?.ac_l3_phase_voltage?.toFixed(2) ?? 0 }} V</div>
                  <div style="overflow-y: auto ;">{{ inverterData4?.ac_l1_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData4?.ac_l2_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData4?.ac_l3_phase_current?.toFixed(3) ?? 0 }} A</div>
                </td>
                <!-- <td style="width:80px">功率因素(%)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData4.total_power_factor?.toFixed(2) ?? 0 }}</div>
                </td> -->
              </tr>
              <!-- <tr>
                <td style="width:80px">其他資訊</td>
                <td colspan="3">
                  <div class="json-display" style="max-height: 200px; overflow-y: auto ;">{{ inverterData4 }}</div>
                </td>
              </tr> -->
            </tbody>
          </table>
        </td>
      </tr>
      <!---->
      <tr>
        <td>逆變器5</td>
        <td>
          <table class="table w-100 table-bordered text-start align-middle mt-2">
            <tbody>
              <tr>
                <td style="width:60px">開/關機</td>
                <td style="width:100px">
                  <el-button-group>
                    <el-button type="primary" @click="SUN_ON_OFF(inverterData5.equipment_id, true)" :disabled="!(inverterData5?.inverter_state == 1) || !ControlPriviage">開</el-button>
                    <el-button type="danger" @click="SUN_ON_OFF(inverterData5.equipment_id, false)" :disabled="!(inverterData5?.inverter_state == 0) || !ControlPriviage">關</el-button>
                  </el-button-group>
                </td>
                <td style="width:60px">目前限制功率:{{inverterData5?.pure_power_percent}}%</td>
                <td style="width:100px">
                  <td>
                    <div class="input-group input-group-sm ">
                      <el-button type="primary" @click="SUN_PERCENT(inverterData5.equipment_id, 100)" :disabled="!(inverterData5?.pure_power_percent == 0) || !ControlPriviage">100%</el-button>
                      <el-button type="danger" @click="SUN_PERCENT(inverterData5.equipment_id, 0)" :disabled="!(inverterData5?.pure_power_percent == 100) || !ControlPriviage">0%</el-button>
                    </div>
                  </td>
                </td>
              </tr>
              <tr>
                <td style="width:80px">目前實功率(kW)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData5?.total_active_power?.toFixed(3) ?? 0 }}</div>
                </td>
                <td style="width:80px">目前虛功率(kVar)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData5?.total_reactive_power?.toFixed(3) ?? 0 }}</div>
                </td>
              </tr>
              <tr>
                <td style="width:80px">交流RST</td>
                <td colspan="3">
                  <div style="overflow-y: auto ;">{{ inverterData5?.ac_l1_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData5?.ac_l2_phase_voltage?.toFixed(2) ?? 0 }} V &nbsp;/&nbsp; {{ inverterData5?.ac_l3_phase_voltage?.toFixed(2) ?? 0 }} V</div>
                  <div style="overflow-y: auto ;">{{ inverterData5?.ac_l1_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData5?.ac_l2_phase_current?.toFixed(3) ?? 0 }} A &nbsp;/&nbsp; {{ inverterData5?.ac_l3_phase_current?.toFixed(3) ?? 0 }} A</div>
                </td>
                <!-- <td style="width:80px">功率因素(%)</td>
                <td>
                  <div style="overflow-y: auto ;">{{ inverterData5.total_power_factor?.toFixed(2) ?? 0 }}</div>
                </td> -->
              </tr>
              <!-- <tr>
                <td style="width:80px">其他資訊</td>
                <td colspan="3">
                  <div class="json-display" style="max-height: 200px; overflow-y: auto ;">{{ inverterData5 }}</div>
                </td>
              </tr> -->
            </tbody>
          </table>
        </td>
      </tr>
      <tr>
        <td>電表狀態</td>
        <td><div class="json-display" style="max-height: 500px; overflow-y: auto ;">
          {{ sunData }}
        </div></td>
      </tr>
    </tbody>
  </table>

</template>
<script>

import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";
import EC from '@/JSON/EquipmentColor.json';

export default {
  props: {
    sunKeyName: null,
  },
  components: {
  },
  data() {
    return {
      EC
    };
  },
  computed: {
    ...mapState(["SocketDataALL", "METER_SUN", "OPERATE_MODE", "INVERTER_1", "INVERTER_2", "INVERTER_3", "INVERTER_4", "INVERTER_5"]),
    ControlPriviage : function () { return this.$store.getters.userPriviagePage('P01-03'); },
    sunData: function () {
      return this[this.sunKeyName];
    },
    inverterData1: function () {
      return this["INVERTER_1"];
    },
    inverterData2: function () {
      return this["INVERTER_2"];
    },
    inverterData3: function () {
      return this["INVERTER_3"];
    },
    inverterData4: function () {
      return this["INVERTER_4"];
    },
    inverterData5: function () {
      return this["INVERTER_5"];
    },
    inverterList: function() {
      return [this.inverterData1, this.inverterData2, this.inverterData3, this.inverterData4, this.inverterData5];
    }
  },
  mounted() {

  },
  created() {
  },
  watch: {
  },
  methods: {
    getInverterClass(attr) {
      var find = this.SocketDataALL?.inverter.find(x => { return x.equipment_id == attr });
      if (find) {
        var state_color = find.inverter_state == 0 ? " bg-success" : " bg-dark";
        return find.abnormal ? ' bg-danger' : ' ' + state_color;
      }
      return ' bg-dark';
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
  padding: 10px;
}

.table-cell:first-child {
  min-width: 100px;
}
</style>