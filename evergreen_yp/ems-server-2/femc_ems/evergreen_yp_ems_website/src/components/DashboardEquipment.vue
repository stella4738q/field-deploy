<template>
    <div class="row p-0 m-0 align-items-center justify-content-end mb-2">
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
    </div>
    <!-- ------------------- 台電 / 工廠 / PCS ICON與箭頭 ------------------- -->
    <div class="row p-0 m-0 align-items-center">
        <!-------------台電ICON---------------->
        <div class="col-3 p-0 text-center">
            <img src="@/assets/TAIPOWER.png" style="height: 5rem; width: auto;" alt="" />
        </div>
        <!-------------台電 >>> 工廠---------------->
        <div class="col p-0">
            <div class="w-100 arrow-charge text-start" v-if="METER_MAIN.total_active_power > 0">
                <font-awesome-icon icon="arrow-right-long" />
            </div>
            <!-- <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0"> -->
            <div class="w-100 arrow-discharge text-start text-danger" v-if="METER_MAIN.total_active_power < 0">
                <font-awesome-icon icon="arrow-left-long" />
            </div>
            
            <div :class="METER_MAIN?.total_active_power > 0 ? 'text-center fw-bold' : 'text-center fw-bold text-danger'">{{ (METER_MAIN?.total_active_power || 0).toLocaleString() }}<br>kW</div>
        </div>
        <!-------------工廠ICON---------------->
        <div class="col-3 p-0 text-center">
            <img src="@/assets/industry.png" style="height: 5rem; width: auto" alt="" />
        </div>
        <!-------------PCS >>> 工廠---------------->
        <div class="col p-0">
            <div class="w-100 arrow-charge text-start text-success" v-if="sumActivePower < 0">
                <font-awesome-icon icon="arrow-right-long" />
            </div>
            <!-- <div class="w-100 arrow-discharge text-end" v-if="SocketDataALL?.pcs[0]?.active_power > 0"> -->
            <div class="w-100 arrow-discharge text-start text-primary" v-if="sumActivePower > 0">
                <font-awesome-icon icon="arrow-left-long" />
            </div>                                                                                                                          
            <div :class="sumActivePower < 0 ? 'text-center text-success fw-bold' : 'text-center text-primary fw-bold'">{{ sumActivePower.toLocaleString() }}<br>kW</div>
        </div>
        <!------------PCS ICON---------------->
        <div class="col-3 p-0 text-center">
            <font-awesome-icon icon="mobile-retro" style="font-size: 5rem;"
                :class="`text-${GetPCSClass()}`" />
        </div>
    </div>
    <!-- ------------------- 太陽能 + BMS ICON & 箭頭 (放同欄位上下) ------------------- -->
    <div class="row p-0 m-0 align-items-center justify-content-end">
        <!-- ============= 太陽能 ============= -->
        <div class="col-4 p-0">
            <!--------太陽能 >>> 工廠 -------->
            <div class="d-flex align-items-center justify-content-center pt-2 pb-2">
                <div class="arrow-discharge-to-TAI text-start text-primary" v-if="sumActivePowerSun > 0">
                    <font-awesome-icon icon="arrow-up-long"/>
                </div>
                <div class="arrow-charge-from-TAI text-start text-success" v-if="sumActivePowerSun < 0">
                    <font-awesome-icon icon="arrow-down-long"/>
                </div>
                &nbsp;&nbsp;
                <div :class="sumActivePowerSun < 0 ? 'text-center text-success fw-bold' : 'text-center text-primary fw-bold'">{{ sumActivePowerSun.toLocaleString() }}kW</div>
            </div>
            <!--------太陽能 ICON------------->
            <img src="@/assets/solar-panel.png" style="height: 6rem; width: auto;" class="ms-1" alt="" />
            <!------- 太陽能 文字 + 按鈕 ------>
            <div class="text-center" v-if="$store.getters.userPriviagePage('P01-03')">
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
        <!-- ============= BMS ============= -->
        <div class="col-4 p-0">
            <!--------BMS >>> PCS -------->
            <div class="d-flex align-items-center justify-content-center pt-2 pb-4 ms-4 ms-md-5">
                <div class="arrow-discharge-to-TAI text-start text-primary" v-if="sumActivePower > 0">
                    <font-awesome-icon icon="arrow-up-long" />
                </div>
                <div class="arrow-charge-from-TAI text-start text-success" v-if="sumActivePower < 0">
                    <font-awesome-icon icon="arrow-down-long" />
                </div>
            </div>
            <!--------BMS ICON------------>
            <font-awesome-icon class="ms-4 ms-md-5" icon="battery-full" style="font-size: 5rem; transform: rotate(-90deg);"
                :class="`text-${GetBMSClass()}`" />
            <!------- BMS 文字 + 按鈕 ------>
            <div class="ms-4 ms-md-5" v-if="$store.getters.userPriviagePage('P01-02')">
                <el-dropdown>
                    <button type="button" class="btn btn-outline-secondary border-0">
                        BMS <font-awesome-icon icon="bars" class="" />
                    </button>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item>
                                <el-button type="text" @click="BMSClick('BMS1')">
                                    設備指令
                                </el-button>
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
            <div class="text-center mt-3 ms-5" v-else>BMS</div>
        </div>
    </div>


    <el-dialog title="太陽能設備" v-model="SolarControlDialog" top="10px" style="width: 90%;" :destroy-on-close="true">
        <DCUControl />
    </el-dialog>

    <el-dialog :title="'PCS 控制'" v-model="PCSControlDialog" top="10px" style="width: 90%;" :destroy-on-close="true">
        <el-tabs v-model="activePCSTab" type="card">
            <el-tab-pane
                v-for="(pcs, index) in SocketDataALL.pcs"
                :key="'PCS' + (index + 1)"
                :label="'PCS_' + (index + 1)"
                :name="'PCS' + (index + 1)"
                >
            <PCSControl :PCSStoreID="'PCS' + (index + 1)" :BMSStoreID="'BMS' + (index + 1)"></PCSControl>
            </el-tab-pane>
        </el-tabs>
    </el-dialog>

    <el-dialog title="BMS 控制" v-model="BMSControlDialog" top="10px" style="width: 90%;" :destroy-on-close="true">
        <el-tabs v-model="activeBMSTab" type="card">
            <el-tab-pane
                v-for="(bms, index) in SocketDataALL.bms"
                :key="'BMS' + (index + 1)"
                :label="'BMS_' + (index + 1)"
                :name="'BMS' + (index + 1)"
            >
            <BMSControl :BMSStoreID="'BMS' + (index + 1)" />
            </el-tab-pane>
        </el-tabs>
    </el-dialog>
</template>
<script>
import { mapState } from "vuex";
import PCSControl from '@/components/PCSControl.vue';
import BMSControl from '@/components/BMSControl.vue';
import DCUControl from '@/components/DCUControl.vue';
import EquipmentStatusColor from '@/JSON/EquipmentStatusColor.json';
import DCPControl from "./DCPControl.vue";

export default {
    props: {
    },
    components: {
        PCSControl, BMSControl, DCUControl, DCPControl
    },
    data() {
        return {
            EquipmentStatusColor,
            PCSControlDialog: false,
            myPCS: null,
            BMSControlDialog: false,
            myBMS: null,
            SolarControlDialog: false,
            DCPControlDialog: false,
            myDCP: null,
            activePCSTab: 'PCS1',
            activeBMSTab: 'BMS1',
        };
    },
    created() {
    },
    watch: {
    },

    computed: {
        ...mapState(["SocketDataALL", "METER_SUN1", "METER_SUN2", "METER_FACTORY", "METER_MAIN", "METER_CABINET"]),
        batteryIcon() {
            let icon  = 'battery-full';
            return icon;
        },
        sumActivePower() {
            return this.SocketDataALL?.pcs?.reduce((acc, pcs) => {
            return acc + (pcs?.active_power ?? 0)
            }, 0) ?? 0
        }
        ,
        sumActivePowerSun() {
            return this.SocketDataALL?.meter?.reduce((acc, meter) => {
                if(meter.equipment_id == 'METER_SUN1' || meter.equipment_id == 'METER_SUN2'){
                    return acc + (meter?.total_active_power ?? 0)
                }
                return acc
            }, 0) ?? 0
        }
    },
    methods: {
        PCSClick(item, item2) {
            this.myPCS = item;
            this.myBMS = item2;
            this.PCSControlDialog = true;
        },
        BMSClick(item) {
            this.myBMS = item;
            this.activeBMSTab = item;
            this.BMSControlDialog = true;
        },
        GetPCSClass(){
            var find = this.SocketDataALL?.pcs[0];
            if (find) {
                // 取得設備的狀態顏色
                const state_color = this.EquipmentStatusColor.PCS.find(x => x.name === find.running_status)?.color || '';
                
                // 檢查是否有 2 級或以上的告警
                const lv_2_alarm = find.warning?.find(ala => ala.level >= 2);
                
                // 判斷顏色邏輯
                if (lv_2_alarm || state_color.includes('danger')) {
                    return 'danger';
                }
                
                // 根據是否異常設定背景顏色
                return find.abnormal ? 'warning' : `${state_color}`;
            }
            return 'dark';
        },
        GetBMSClass() {
            const bmsList = this.SocketDataALL?.bms || [];
            if (!bmsList.length) return 'dark';

            // 整理所有的告警 level
            const allWarnings = bmsList.flatMap(bms => bms.warning || []);
            const maxLevel = allWarnings.reduce((max, w) => Math.max(max, w.level), 0);

            // 如果有 level >= 2，回傳 danger
            if (maxLevel >= 2) {
                return 'danger';
            }

            // 如果有任何設備是 abnormal，回傳 warning
            const hasAbnormal = bmsList.some(bms => bms.abnormal);
            if (hasAbnormal) {
                return 'warning';
            }

            // 如果沒有高等級告警或異常，就用第一筆的狀態顏色 fallback
            const fallbackStatus = bmsList[0]?.status;
            const state_color = this.EquipmentStatusColor.BMS.find(x => x.name === fallbackStatus)?.color || 'dark';

            return state_color.includes('danger') ? 'danger' : state_color || 'dark';
        }
    },
};
</script>
<style scoped>
/* arrow animation */

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
    transform: translateX(100%);
  }
  100% {
    transform: translateX(0%);
  }
}

@keyframes arrowChargefromT {
  0% {
    transform: translateY(-100%);
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
</style>