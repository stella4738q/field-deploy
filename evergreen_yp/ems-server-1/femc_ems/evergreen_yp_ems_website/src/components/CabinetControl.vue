<template>
  <div class="m-0 p-0 cabinet-control">
    <!-- ACB 狀態區 -->
    <div class="mb-3">
      <div
        class="rounded p-1 text-white text-center bg-success alert alert-success"
        v-if="myACB?.remote"
      >
        遠端控制：是
      </div>
      <div
        class="rounded p-1 text-white text-center bg-danger alert alert-success"
        v-if="myACB?.local"
      >
        遠端控制：否
      </div>

      <div
        v-if="myACB?.cb_closed"
        class="rounded p-1 text-white text-center bg-success alert alert-success"
      >
        狀態：CLOSE(閉合)
      </div>
      <div
        v-if="myACB?.cb_open"
        style="font-size: small;"
        class="rounded p-1 text-white text-center bg-danger alert alert-success"
      >
        狀態：OPEN(斷開)
      </div>
      <div
        v-if="myACB?.cb_serve"
        class="rounded p-1 text-white text-center bg-success alert alert-success"
      >
        狀態：Serve
      </div>
      <div
        v-if="myACB?.cb_test"
        style="font-size: small;"
        class="rounded p-1 text-white text-center bg-danger alert alert-success"
      >
        狀態：Test
      </div>
      <div
        v-if="myACB?.cb_trip"
        style="font-size: small;"
        class="rounded p-1 text-white text-center bg-danger alert alert-success"
      >
        狀態：TRIP
      </div>
    </div>

    <!-- 4 個控制區塊：用 2x2 卡片排版 -->
    <div class="row">
      <!-- CB 控制 -->
      <div class="col-12 col-md-6 mb-3">
        <div class="card shadow-sm h-100">
          <div class="card-header text-center fw-bold">CB 控制</div>
          <div class="card-body text-center">
            <div class="mb-2">
              <div class="small text-muted mb-1">
                ACB：{{ myACB.equipment_id || '-' }}
              </div>
              <div>
                <span v-if="myACB?.cb_closed"
                  class="badge"
                  :class="myACB?.cb_closed ? 'bg-success' : 'bg-secondary'"
                >
                  閉合
                </span>
                <span v-else="myACB?.cb_open"
                  class="badge ms-1"
                  :class="myACB?.cb_open ? 'bg-danger' : 'bg-secondary'"
                >
                  斷開
                </span>
              </div>
            </div>

            <el-button
              type="primary"
              class="me-2"
              @click="ACBOnOffClick(true)"
              :disabled="
                [undefined, null, true].includes(myACB?.cb_closed) ||
                myACB?.local ||
                myACB?.cb_test
              "
            >
              閉合
            </el-button>

            <el-button
              type="primary"
              @click="ACBOnOffClick(false)"
              :disabled="
                [undefined, null, true].includes(myACB?.cb_open) ||
                myACB?.local ||
                myACB?.cb_test
              "
            >
              斷開
            </el-button>
          </div>
        </div>
      </div>

      <!-- 幫浦控制 -->
      <div class="col-12 col-md-6 mb-3">
        <div class="card shadow-sm h-100">
          <div class="card-header text-center fw-bold">幫浦控制</div>
          <div class="card-body text-center">
            <div class="mb-2">
              <div class="small text-muted mb-1">
                幫浦：{{ pumpName || '-' }}
              </div>
              <div>
                <span class="badge" :class="pumpIsOn ? 'bg-danger' : 'bg-secondary'">
                  {{ pumpIsOn ? "運轉中": "停止"}}
                </span>
              </div>
            </div>

            <el-button
              type="primary"
              class="me-2"
              @click="PumpOnOffClick(true)" :disabled="pumpIsOn">
              啟動
            </el-button>

            <el-button
              type="primary"
              @click="PumpOnOffClick(false)"
              :disabled="!pumpIsOn">
              停止
            </el-button>
          </div>
        </div>
      </div>

      <!-- 電磁閥控制 -->
      <div class="col-12 col-md-6 mb-3">
        <div class="card shadow-sm h-100">
          <div class="card-header text-center fw-bold">電磁閥控制</div>
          <div class="card-body text-center">
            <div class="mb-2">
              <div class="small text-muted mb-1">
                電磁閥：{{ solName || '-' }}
              </div>
              <div>
                <span class="badge" :class="solenoidIsOpen ? 'bg-danger' : 'bg-secondary'">
                  {{ solenoidIsOpen? "開啟" : "關閉" }} 
                </span>
              </div>
            </div>

            <el-button
              type="primary"
              class="me-2"
              @click="SolenoidOnOffClick(true)" :disabled="solenoidIsOpen">
              開啟
            </el-button>

            <el-button
              type="primary"
              @click="SolenoidOnOffClick(false)" :disabled="!solenoidIsOpen">
              關閉
            </el-button>
          </div>
        </div>
      </div>

      <!-- 水流控制 -->
       <div class="col-12 col-md-6 mb-3">
        <div class="card shadow-sm h-100">
          <div class="card-header text-center fw-bold">水流控制</div>
          <div class="card-body text-center">
            <div class="mb-2">
              <div class="small text-muted mb-1">
                水流開關：{{ waterName || '-' }}
              </div>
              <div>
                <span class="badge" :class="waterIsOpen ? 'bg-danger' : 'bg-secondary'">
                  {{ waterIsOpen? "有水流" : "無水流" }} 
                </span>
              </div>
            </div>

            <el-button
              type="primary"
              class="me-2"
              @click="WaterOnOffClick(true)" :disabled="waterIsOpen">
              開啟
            </el-button>

            <el-button
              type="primary"
              @click="WaterOnOffClick(false)" :disabled="!waterIsOpen">
              關閉
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { postModbusControl } from '@/api/Api.js';

export default {
  name: 'CabinetControl',
  props: {
    CabinetNo: { type: Number, default: null },
  },
  data() {
    return {};
  },
  computed: {
    myACB() {
      if (this.CabinetNo === 1) {
        return this.$store?.state?.ACB_MP1 || null;
      } else if (this.CabinetNo === 2) {
        return this.$store?.state?.ACB_MP2 || null;
      }
      return null;
    },
    myPump() {
      return this.$store?.state?.IO_PUMP || null;
    },
    mySolenoid() {
      return this.$store?.state?.IO_SOL || null;
    },
    myWater() {
      return this.$store?.state?.IO_SOL || null;
    },
    pumpIsOn() {
      if (!this.myPump) return false;
      if (this.CabinetNo === 1) {
        return this.myPump?.pump_a_open;
      } else if (this.CabinetNo === 2) {
        return this.myPump?.pump_b_open;
      }
      return false;
    },
    solenoidIsOpen() {
      if (!this.mySolenoid) return false;
      if (this.CabinetNo === 1) {
        return this.mySolenoid?.xv_01_a_on;
      } else if (this.CabinetNo === 2) {
        return this.mySolenoid?.xv_01_b_on;
      }
      return false;
    },
    waterIsOpen() {
      if (!this.myWater) return false;
      if (this.CabinetNo === 1) {
        return this.myWater?.fs_01_a_on;
      } else if (this.CabinetNo === 2) {
        return this.myWater?.fs_01_b_on;
      }
      return false;
    },
    pumpName(){
      return this.CabinetNo == 1 ? "Pump-A" : "Pump-B";
    },
    solName(){
      return this.CabinetNo == 1 ? "XV-01A" : "XV-01B";
    },
    waterName(){
      return this.CabinetNo == 1 ? "FS-01A" : "FS-01B";
    }
  },
  methods: {
    ACBOnOffClick(on_off) {
      const vm = this;
      if (!this.myACB) return;

      vm
        .$confirm(
          `${this.myACB.equipment_id} 確定執行【${on_off ? "閉合": "斷開"}】指令?`, '提示',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning',
          },
        )
        .then(() => {
          vm.$loading();
          const postData = {
            customer: 'evergreen-yp',
            code: 'IO',
            action: 'ACB_ON_OFF',
            equipment_id: this.myACB?.equipment_id,
            value: on_off,
          };
          postModbusControl(postData)
            .then((response) => {
              if (response.data.Success) {
                vm.$message({ type: 'success', message: '指令已下達' });
              } else {
                vm.$message({
                  type: 'error',
                  message: response.data.Msg,
                });
              }
            })
            .catch(() => {
              vm.$message({ type: 'error', message: 'api error' });
            })
            .finally(() => {
              vm.$loading().close();
            });
        })
        .catch(() => {});
    },

    // ===== 幫浦 =====
    PumpOnOffClick(on_off) {
      const vm = this;
      if (!this.myPump) return;

      vm
        .$confirm(
          `${this.pumpName}確定執行【${on_off ? "啟動": "關閉"}】指令?`, '提示',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning',
          },
        )
        .then(() => {
          vm.$loading();
          const postData = {
            customer: 'evergreen-yp',
            code: 'IO',
            action: 'PUMP_ON_OFF',
            equipment_id: "IO_PUMP",
            value: on_off,
            parameter: this.CabinetNo
          };
          postModbusControl(postData)
            .then((response) => {
              if (response.data.Success) {
                vm.$message({ type: 'success', message: '指令已下達' });
              } else {
                vm.$message({
                  type: 'error',
                  message: response.data.Msg,
                });
              }
            })
            .catch(() => {
              vm.$message({ type: 'error', message: 'api error' });
            })
            .finally(() => {
              vm.$loading().close();
            });
        })
        .catch(() => {});
    },

    // ===== 電磁閥 =====
    SolenoidOnOffClick(on_off) {
      const vm = this;
      if (!this.mySolenoid) return;

      vm
        .$confirm(
          `${this.solName}確定執行【${on_off ? "開啟": "關閉"}】指令?`, '提示',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning',
          },
        )
        .then(() => {
          vm.$loading();
          const postData = {
            customer: 'evergreen-yp',
            code: 'IO',
            action: 'SOL_ON_OFF',
            equipment_id: "IO_SOL",
            value: on_off,
            parameter: this.CabinetNo
          };
          postModbusControl(postData)
            .then((response) => {
              if (response.data.Success) {
                vm.$message({ type: 'success', message: '指令已下達' });
              } else {
                vm.$message({
                  type: 'error',
                  message: response.data.Msg,
                });
              }
            })
            .catch(() => {
              vm.$message({ type: 'error', message: 'api error' });
            })
            .finally(() => {
              vm.$loading().close();
            });
        })
        .catch(() => {});
    },

    // ===== 水流 =====
    WaterOnOffClick(on_off) {
      const vm = this;
      if (!this.myWater) return;

      vm
        .$confirm(
          `${this.waterName}確定執行【${on_off ? "開啟": "關閉"}】指令?`, '提示',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning',
          },
        )
        .then(() => {
          vm.$loading();
          const postData = {
            customer: 'evergreen-yp',
            code: 'IO',
            action: 'WATER_ON_OFF',
            equipment_id: "IO_SOL",
            value: on_off,
            parameter: this.CabinetNo
          };
          postModbusControl(postData)
            .then((response) => {
              if (response.data.Success) {
                vm.$message({ type: 'success', message: '指令已下達' });
              } else {
                vm.$message({
                  type: 'error',
                  message: response.data.Msg,
                });
              }
            })
            .catch(() => {
              vm.$message({ type: 'error', message: 'api error' });
            })
            .finally(() => {
              vm.$loading().close();
            });
        })
        .catch(() => {});
    },
  },
};
</script>

<style scoped>
.cabinet-control .card {
  border-radius: 0.5rem;
}
.cabinet-control .card-header {
  background-color: #f8f9fa;
}
.cabinet-control .badge {
  font-size: 0.75rem;
}
</style>
