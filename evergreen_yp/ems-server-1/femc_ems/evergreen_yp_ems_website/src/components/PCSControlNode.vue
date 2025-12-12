<template>
    <div class="row text-start g-3">
      <div class="col-12 col-md-6">
        <div class="card border-success p-2">
          <p class="fs-6 m-0 border-bottom border-success">{{ equipmentId }} -狀態</p>
          <p class="fs-5 m-0 text-end mt-1">{{ myPCS.running_status }}</p>
        </div>
      </div>
      <div class="col-12 col-md-6">
        <div class="card border-success p-2">
          <p class="fs-6 m-0 border-bottom border-success">功率</p>
          <p class="fs-5 m-0 text-end mt-1">{{ myPCS.active_power }}</p>
        </div>
      </div>
    </div>
  
  
  
    <table class="table w-100 table-bordered text-start align-middle mt-2">
    <tbody>
      <tr>
        <td style="width:80px">故障清除</td>
        <td colspan="3">
          <el-button type="primary" :disabled="!ControlPriviage" @click="PCS_FAULT_RESET(myPCS.equipment_id, true)">故障清除</el-button>
        </td>
      </tr>
      <tr>
        <td style="width:80px">開/關機</td>
        <td colspan="3">
          <el-button-group>
            <el-button type="primary" :disabled="!(myPCS?.CanOn == true) || !ControlPriviage"
              @click="PCS_ON_OFF(myPCS.equipment_id, true)">開</el-button>
            <el-button type="danger" :disabled="!(myPCS?.CanOff == true) || !ControlPriviage"
              @click="PCS_ON_OFF(myPCS.equipment_id, false)">關</el-button>
          </el-button-group>
        </td>
      </tr>
      <tr v-if="false">
        <td style="width:80px">全黑啟動</td>
        <td colspan="3">
          <el-button-group>
            <el-button type="primary" :disabled="!(myPCS?.CanBSOn == true) || !ControlPriviage"
              @click="PCS_BLACK_START_ON_OFF(myPCS.equipment_id, true)">開</el-button>
            <el-button type="danger" :disabled="!(myPCS?.CanBSOff == true) || !ControlPriviage"
              @click="PCS_BLACK_START_ON_OFF(myPCS.equipment_id, false)">關</el-button>
          </el-button-group>
        </td>
      </tr>
      <tr>
        <td>功率設定</td>
        <td>
          <div class="input-group input-group-sm ">
            <span class="input-group-text">放電</span>
            <input type="number" min="0" max="10" v-model.number="power1" class=" text-end form-control">
            <span class="input-group-text">(kW)</span>
            <button class="btn btn-primary" type="button" :disabled="!(myPCS?.CanPower == true) || !ControlPriviage"
              @click="PCS_SET_POWER(myPCS.equipment_id, power1, 1)">送出</button>
          </div>
          <div class="input-group input-group-sm mt-2">
            <span class="input-group-text">充電</span>
            <input type="number" min="0" max="10" v-model.number="power2" class=" text-end form-control">
            <span class="input-group-text">(kW)</span>
            <button class="btn btn-success" type="button" :disabled="!(myPCS?.CanPower == true) || !ControlPriviage"
              @click="PCS_SET_POWER(myPCS.equipment_id, power2, -1)">送出</button>
          </div>

        </td>
      </tr>
      <!-- <tr>
        <td>狀態</td>
        <td colspan="3">
          <div class="json-display" style="max-height: 500px; overflow-y: auto ;">
            {{ myPCS.content }}
          </div>
        </td>
      </tr> -->
    </tbody>
  </table>
  </template>
  <script>
  import { mapState } from "vuex";
  import { postModbusControl } from '@/api/Api.js';
  
  export default {
    props: {
      PCSStoreID: null,
      BMSStoreID: null,
      SocketData: {
        type: Object,
        default: {}
      },
      equipmentId: {
        type: String,
        default: '',
      },
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
      ControlPriviage: function () { return this.$store.getters.userPriviagePage('P01-01') && this.OPERATE_MODE !== 1; },
      ...mapState(["SocketDataALL", "PCS1", "OPERATE_MODE"]),
      myPCS: function () {
        return this[this.PCSStoreID];
      },
      myBMS: function () {
        return this[this.BMSStoreID];
      },
      allPCS: function () {
        return [this['PCS1']];
      },
    },
    mounted() {
    },
    created() {
    },
    watch: {
    },
    methods: {
      PCS_SET_CC_CV(id, value) {
      const vm = this;
      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
        var postData = {
          customer: "advanced",
          code: "PCS",
          action: "PCS_SET_CC_CV",
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
      VoltageChange() {
        if (this.voltage > 1057) this.voltage = 1057;
        if (this.voltage < 0) this.voltage = 0;
      },
      CurrentChange() {
        if (this.current > 1068) this.current1 = 1068;
        if (this.current < 0) this.current1 = 0;
      },
  
      PCS_SET_MODE(id, value) {
        const vm = this;
        vm.$confirm('確定送出指令?', '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "PCS",
            action: "PCS_SET_MODE",
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
      PCS_ON_OFF(id, value) {
        const vm = this;
  
        vm.$confirm(`${id} 確定執行【${ value ? '開機': '關機' }】指令？`, '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
  
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "PCS",
            action: "PCS_ON_OFF",
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
      PCS_SET_VOLTAGE(id, value) {
        const vm = this;
  
        vm.$confirm('確定送出指令?', '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "PCS",
            action: "PCS_SET_VOLTAGE",
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
      PCS_SET_CURRENT(id, value, ab) {
        const vm = this;
  
        vm.$confirm('確定送出指令?', '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "PCS",
            action: "PCS_SET_CURRENT",
            equipment_id: id,
            value: (value * ab),
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
      PCS_SET_POWER(id, value, ab) {
        const vm = this;
  
        vm.$confirm(`PCS-${id} 【${ab === 1 ? '放電' : '充電'}】確定送出指令？`, '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "PCS",
            action: "PCS_SET_POWER",
            equipment_id: id,
            value: (value * ab),
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
      PCS_SET_POWER_2(pcs_list, value, ab) {
        const vm = this;
        vm.$confirm('確定送出指令?', '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          pcs_list.forEach(x => {
            var postData = {
              customer: "advanced",
              code: "PCS",
              action: "PCS_SET_POWER",
              equipment_id: x.equipment_id,
              value: (value * ab),
            };
            postModbusControl(postData);
          });
  
          vm.$message({ type: 'success', message: "指令已下達" });
          vm.$loading().close();
  
        }).catch(() => {
        });
      },
      EMERGENCY_STOP(id, value) {
        const vm = this;
  
        vm.$confirm('確定送出指令?', '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "IO",
            action: "EMERGENCY_STOP",
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
      PCS_FAULT_RESET(id, value) {
        const vm = this;
  
        vm.$confirm(`${id} 確定執行【故障清除】指令?`, '提示', {
          confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
        }).then(() => {
          vm.$loading();
          var postData = {
            customer: "advanced",
            code: "PCS",
            action: "PCS_FAULT_RESET",
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
      PCS_BLACK_START_ON_OFF(id, value) {
      const vm = this;

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        var postData = {
          customer: "advanced",
          code: "PCS",
          action: "PCS_BLACK_START_ON_OFF",
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