import { createStore } from "vuex";
// import { LOGIN } from '@/api/Api.js'
import EquipmentColor from "@/JSON/EquipmentColor.json";
import createPersistedState from "vuex-persistedstate";

const EC = EquipmentColor;
const store = createStore({
  state() {
    return {
      LineChartDataPower: [],
      LineChartDataPowerSun: [],
      ZoomSize: 100,
      BMS1: {
        mystatus: "black",
        CanOn: false,
        CanOff: false,
        equipment_id: "BMU_1",
        data: null,
        content: "",
      },
      BMS2: {
        mystatus: "black",
        CanOn: false,
        CanOff: false,
        equipment_id: "BMU_2",
        data: null,
        content: "",
      },
      PCS1: {
        id: "",
        mystatus: "black",
        CanOn: false,
        CanOff: true,
        CanBSOn: true,
        CanBSOff: false,
        CanPower: false,
        active_power: 0,
        equipment_id: "PCS_1",
        content: "",
        running_status: "",
        data: null,
      },
      PCS2: {
        id: "",
        mystatus: "black",
        CanOn: false,
        CanOff: true,
        CanBSOn: true,
        CanBSOff: false,
        CanPower: false,
        active_power: 0,
        equipment_id: "PCS_2",
        content: "",
        running_status: "",
        data: null,
      },
      METER_MAIN: {},
      METER_VCB: {},
      METER_MP1: {},
      METER_MP2: {},
      METER_SUN1: {},
      METER_SUN2: {},
      IO_MP1: {},
      IO_MP2: {},
      IO_PUMP: {},
      IO_SOL: {},
      VCB: {},
      ACB: {},
      SocketDataALL: {
        pcs: [],  //*2
        bms: [],  //*2
        meter: [],  //*6
        io: [],  //*5
        relay: [], //*2
        tr: [], //*1
        ups: [],  //*1
        alarm: []
      },
      user: {
        loginType: -1,
        priviage: -1,
        id: "",
        name: "",
        token: "",
        UserInfo: {
          name: "",
        },
      },
      userMenu: [],
      userApi: [],
      userPage: [],
      OPERATE_MODE: 0,
    };
  },
  getters: {
    DiasbledAction(state) {
      return !process.env.VUE_APP_Admin_UserName.split(",").includes(
        state.user.UserInfo?.name?.toUpperCase()
      );
    },
    getSocketDataALL(state) {
      return state.SocketDataALL;
    },
    user(state) {
      return state.user;
    },
    userApi(state) {
      return state.userApi;
    },
    userPriviage: (state) => (code) => {
      // debugger;
      return (
        state.userApi.findIndex((x) => {
          return x.code == code;
        }) > -1
      );
    },
    userPriviagePage: (state) => (code) => {
      if (code.includes("*")) {
        const regex = new RegExp("^" + code.replace(/\*/g, ".*") + "$");
        return state.userPage.some((page) => regex.test(page));
      } else {
        return state.userPage.includes(code);
      }
    },
    userMenu(state) {
      return state.userMenu;
    },
    userPage(state) {
      return state.userApi;
    },
    getZoomSize(state) {
      return state.ZoomSize;
    },
  },
  mutations: {
    setZoomSize(state, val) {
      state.ZoomSize = val;
    },
    userMenu(state, val) {
      state.userMenu = val;
    },
    userApi(state, val) {
      state.userApi = val;
    },
    userPage(state, val) {
      state.userPage = val;
    },
    loginSuccess(state, user) {
      state.user = user;
    },
    logOut(state) {
      state.field = "";
      state.user = {
        Data: null,
        FieldId: "",
        Msg: "",
        Otp: false,
        Success: false,
        Token: "",
        UserInfo: {
          company: null,
          enable_otp: false,
          id: "",
          name: "",
        },
      };
    },
    setSocketDataALL(state, val) {
      state.SocketDataALL = val;

      if(state.SocketDataALL?.bms?.length){
        state.SocketDataALL.bms = state.SocketDataALL.bms.sort((a, b) => {
          return a.equipment_id.localeCompare(b.equipment_id);
        }); 
      }

      //
      // status_code
      // 0: 初始化, 1: 充電, 2: 放電, 3: 就緒, 4: 集群維護,
      // 5: 禁止充電, 6: 禁止放電, 7: 禁止充放電, 8: 故障,
      // 9:故障恢復, 10:測試模式, 11:關機, 12:關機完成
      //
      let myBMS1 = state.SocketDataALL.bms.find((x) => {
        return x.equipment_id == "BMU_1";
      });
      if (myBMS1) {
        state.BMS1 = Object.assign({}, state.BMS1, myBMS1);
        state.BMS1.mystatus =
          myBMS1.abnormal == true
            ? "danger"
            : EC.BMS.find((x) => {
                return x.key == myBMS1.status_code;
              })?.color;
        state.BMS1.CanOn = true;
        state.BMS1.CanOff = true;
        state.BMS1.content = JSON.stringify(myBMS1, null, 2);
      }
      //
      let myBMS2 = state.SocketDataALL.bms.find((x) => {
        return x.equipment_id == "BMU_2";
      });
      if (myBMS2) {
        state.BMS2 = Object.assign({}, state.BMS2, myBMS2);
        state.BMS2.mystatus =
          myBMS2.abnormal == true
            ? "danger"
            : EC.BMS.find((x) => {
                return x.key == myBMS2.status_code;
              })?.color;
        state.BMS2.CanOn = true;
        state.BMS2.CanOff = true;
        state.BMS2.content = JSON.stringify(myBMS2, null, 2);
      }
      //
      let myPCS1 = state.SocketDataALL.pcs.find((x) => {
        return x.equipment_id == "PCS_1";
      });
      if (myPCS1) {
        state.PCS1 = Object.assign({}, state.PCS1, myPCS1);
        state.PCS1.mystatus =
          myPCS1.abnormal == true ||
          myPCS1.warning.find((x) => {
            return x.code.indexOf("CONNECTION_ERROR") > -1;
          })
            ? "danger"
            : EC.PCS.find((x) => {
                return x.key == myPCS1.running_status;
              })?.color ?? "dark";
        // PCS: 轉換器運作模式:
        // 0: 待機, 1: 靜態補償, 2: 連接電池,
        // 3: 服務模式, 4: 委託模式, 5: 斷開,
        // 6: 斷開中, 7: 連接中, 8: 連接電網
        // state.PCS1.CanOn = myPCS1.running_status == '停機' && (["運行中", "正常"].includes(myBMS1.status));
        // state.PCS1.CanOff = ["待機", "故障"].includes(myPCS1.running_status);
        // state.PCS1.CanPower = ["待機", "充電", "放電", "充電降額", "放電降額"].includes(myPCS1.running_status) && ems_status != 5;
        state.PCS1.CanOn = true;
        state.PCS1.CanOff = true;
        state.PCS1.CanBSOn = true;
        state.PCS1.CanBSOff = true;
        state.PCS1.CanPower = ["電池已連接", "運作中", "除錯模式"].includes(
          myPCS1.running_status
        );
        state.PCS1.active_power = myPCS1.active_power;
        state.PCS1.equipment_id = myPCS1.equipment_id;
        state.PCS1.content = JSON.stringify(myPCS1, null, 2);
      }
      //
      let myPCS2 = state.SocketDataALL.pcs.find((x) => {
        return x.equipment_id == "PCS_2";
      });
      if (myPCS2) {
        state.PCS2 = Object.assign({}, state.PCS2, myPCS2);
        state.PCS2.mystatus =
          myPCS2.abnormal == true ||
          myPCS2.warning.find((x) => {
            return x.code.indexOf("CONNECTION_ERROR") > -1;
          })
            ? "danger"
            : EC.PCS.find((x) => {
                return x.key == myPCS2.running_status;
              })?.color ?? "dark";
        // PCS: 轉換器運作模式:
        // 0: 待機, 1: 靜態補償, 2: 連接電池,
        // 3: 服務模式, 4: 委託模式, 5: 斷開,
        // 6: 斷開中, 7: 連接中, 8: 連接電網
        // state.PCS2.CanOn = myPCS2.running_status == '停機' && (["運行中", "正常"].includes(myBMS1.status));
        // state.PCS2.CanOff = ["待機", "故障"].includes(myPCS2.running_status);
        // state.PCS2.CanPower = ["待機", "充電", "放電", "充電降額", "放電降額"].includes(myPCS2.running_status) && ems_status != 5;
        state.PCS2.CanOn = true;
        state.PCS2.CanOff = true;
        state.PCS2.CanBSOn = true;
        state.PCS2.CanBSOff = true;
        state.PCS2.CanPower = ["電池已連接", "運作中", "除錯模式"].includes(
          myPCS2.running_status
        );
        state.PCS2.active_power = myPCS2.active_power;
        state.PCS2.equipment_id = myPCS2.equipment_id;
        state.PCS2.content = JSON.stringify(myPCS2, null, 2);
      }

      // Line 圖
      // if (state.LineChartDataPower.length > 86400) {
      //   state.LineChartDataPower.shift();
      // }
      state.LineChartDataPower = [
        myPCS1?.data_time.split(".")[0],
        myPCS1?.active_power,
        myPCS2?.active_power,
        Math.min(myBMS1?.soc, myBMS2?.soc), //SOC
        Math.max(myBMS1?.container_temp_a, myBMS2?.container_temp_a) //Temp
      ];

      state.LineChartDataPowerSun = val.dcu;
      
      // 太陽能電表1
      let MeterSun1 = state.SocketDataALL.meter.find((x) => {
        return x.equipment_id == "METER_SUN1";
      });
      if (MeterSun1) {
        state.METER_SUN1 = Object.assign({}, state.METER_SUN1, MeterSun1);
        state.METER_SUN1.equipment_id = MeterSun1.equipment_id;
        state.METER_SUN1.kW = MeterSun1.total_active_power;
        state.METER_SUN1.voltage = MeterSun1.voltage_avg;
        state.METER_SUN1.ampere = MeterSun1.current_avg;
        state.METER_SUN1.q_total = MeterSun1.total_reactive_power;
        state.METER_SUN1.s_total = MeterSun1.total_apparent_power;
        state.METER_SUN1.field_id = MeterSun1.field_id;
      }
      // 太陽能電表2
      let MeterSun2 = state.SocketDataALL.meter.find((x) => {
        return x.equipment_id == "METER_SUN2";
      });
      if (MeterSun2) {
        state.METER_SUN2 = Object.assign({}, state.METER_SUN2, MeterSun2);
        state.METER_SUN2.equipment_id = MeterSun2.equipment_id;
        state.METER_SUN2.kW = MeterSun2.total_active_power;
        state.METER_SUN2.voltage = MeterSun2.voltage_avg;
        state.METER_SUN2.ampere = MeterSun2.current_avg;
        state.METER_SUN2.q_total = MeterSun2.total_reactive_power;
        state.METER_SUN2.s_total = MeterSun2.total_apparent_power;
        state.METER_SUN2.field_id = MeterSun2.field_id;
      }
      // 11.4kV 電表
      let MeterMain = state.SocketDataALL.meter.find((x) => {
        return x.equipment_id == "METER_MAIN";
      });
      if (MeterMain) {
        state.METER_MAIN = Object.assign({}, state.METER_MAIN, MeterMain);
      }
      // MP-BESS1
      let MeterMP1 = state.SocketDataALL.meter.find((x) => {
        return x.equipment_id == "METER_MP1";
      });
      if (MeterMP1) {
        state.METER_MP1 = Object.assign({}, state.METER_MP1, MeterMP1);
      }
      // MP-BESS2
      let MeterMP2 = state.SocketDataALL.meter.find((x) => {
        return x.equipment_id == "METER_MP2";
      });
      if (MeterMP2) {
        state.METER_MP2 = Object.assign({}, state.METER_MP2, MeterMP2);
      }
      // VCB電表
      let MeterV = state.SocketDataALL.meter.find((x) => {
        return x.equipment_id == "METER_VCB";
      });
      if (MeterV) {
        state.METER_VCB = Object.assign({}, state.METER_VCB, MeterV);
      }
      // VCB
      let VCB = state.SocketDataALL.relay.find((x) => {
        return x.equipment_id == "VCB";
      });
      if (VCB) {
        state.VCB = Object.assign({}, state.VCB, VCB);
      }
      // ACB_IO_MP1
      let ACB_MP1 = state.SocketDataALL.relay.find((x) => {
        return x.equipment_id == "ACB_IO_MP1";
      });
      if (ACB_MP1) {
        state.ACB_MP1 = Object.assign({}, state.ACB_MP1, ACB_MP1);
      }
      // ACB_IO_MP2
      let ACB_MP2 = state.SocketDataALL.relay.find((x) => {
        return x.equipment_id == "ACB_IO_MP2";
      });
      if (ACB_MP2) {
        state.ACB_MP2 = Object.assign({}, state.ACB_MP2, ACB_MP2);
      }
      // IO_PUMP
      let IO_PUMP = state.SocketDataALL.pump.find((x) => {
        return x.equipment_id == "IO_PUMP";
      });
      if (IO_PUMP) {
        state.IO_PUMP = Object.assign({}, state.IO_PUMP, IO_PUMP);
      }
      // IO_SOL
      let IO_SOL = state.SocketDataALL.sol.find((x) => {
        return x.equipment_id == "IO_SOL";
      });
      if (IO_SOL) {
        state.IO_SOL = Object.assign({}, state.IO_SOL, IO_SOL);
      }
      // 控制模式
      state.OPERATE_MODE = state.SocketDataALL.other.operation_mode ?? 0;
    },
    storeOtpSetting(state, enableOtp) {
      state.user.UserInfo.enable_otp = enableOtp;
    },
  },
  actions: {},
  modules: {},
  plugins: [
    createPersistedState({
      storage: window.sessionStorage,
    }),
  ],
});
export default store;
