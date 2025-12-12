<template>
    <div class="row text-start ps-3 pe-3 mb-2">
      <div class="col border rounded border-success me-2 ">
        <div class="fs-6 border-bottom border-success p-0"> {{ equipmentId }} - 狀態</div>
        <div class="fs-5 p-0 text-end">{{ SocketData ? (SocketData.abnormal ? '告警' : '正常') : "連線異常"  }}</div>
      </div>
  
    </div>
  
    <table class="table w-100 table-bordered text-start align-middle">
      <tbody>
        <tr>
          <td style="width:80px">開/關</td>
          <td colspan="3">
            <el-button-group>
              <el-button type="primary" :disabled="SocketData == null || [undefined, null, true].includes(SocketData?.cb_closed) || SocketData?.local || SocketData?.cb_test" @click="CB_ON_OFF(true)" >開</el-button>
              <el-button type="primary" :disabled="SocketData == null || [undefined, null, true].includes(SocketData?.cb_open) || SocketData?.local || SocketData?.cb_test" @click="CB_ON_OFF(false)">關</el-button>
            </el-button-group>
          </td>
        </tr>
              <tr>
        <td>狀態</td>
        <td>
          <div class="row">
            <div class="col-3"><font-awesome-icon icon="circle" :class="SocketData?.cb_closed ? 'text-danger' : ''" /> CB ON</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="SocketData?.cb_open ? 'text-danger' : ''" /> CB OFF</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_51 ? 'text-danger' : ''" /> 51-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_50_1 ? 'text-danger' : ''" /> 50I-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_51n ? 'text-danger' : ''" /> 51N-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_50n_2 ? 'text-danger' : ''" /> 50NI-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="alarm_27 ? 'text-danger' : ''" /> 27-Alarm</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_27 ? 'text-danger' : ''" /> 27-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="alarm_59 ? 'text-danger' : ''" /> 59-Alarm</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_59 ? 'text-danger' : ''" /> 59-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_59vo ? 'text-danger' : ''" /> 59Vo-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="alarm_81 ? 'text-danger' : ''" /> 81H/L-Alarm</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_81h ? 'text-danger' : ''" /> 81H-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="trip_81l ? 'text-danger' : ''" /> 81L-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="tr_33_alarm ? 'text-danger' : ''" /> 33-Alarm</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="tr_96_trip ? 'text-danger' : ''" /> 96-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="tr_26_alarm ? 'text-danger' : ''" /> 26-Alarm</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="tr_26_trip ? 'text-danger' : ''" /> 26-TRIP</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="tsc_alarm ? 'text-danger' : ''" /> TSC-Alarm</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="SocketData?.local ? 'text-danger' : ''" /> Local</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="SocketData?.remote ? 'text-danger' : ''" /> Remote</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="SocketData?.test ? 'text-danger' : ''" /> Test</div>
            <div class="col-3"><font-awesome-icon icon="circle" :class="SocketData?.serve ? 'text-danger' : ''" /> Serv</div>
          </div>
        </td>
      </tr>
        <tr>
          <td>
            告警訊息
          </td>
          <td>
            <div class=" json-display" style="max-height: 500px; overflow-y: auto ;">
              {{ SocketData }}
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </template>
  <script>
  import { mapState } from "vuex";
  import { iecVCBControl, postModbusControl } from '@/api/Api.js';
  
  export default {
    props: {
      equipmentId: { type: String, default: null },
      SocketData: { type: Object, default: {} },
      iecControl: { type: Boolean, default: false }
    },
    components: {
    },
    data() {
      return {
  
      };
    },
    computed: {
      trip_51: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_51'));
      },
      trip_50_1: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_50_1'));
      },
      trip_51n: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_51n')); 
      },
      trip_50n_2: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_50n_2')); 
      },
      alarm_27: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('start_27')); 
      },
      trip_27: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_27')); 
      },
      alarm_59: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('start_59')); 
      },
      trip_59: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_59')); 
      },
      trip_59vo: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_59vo')); 
      },
      alarm_81: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('start_81')); 
      },
      trip_81h: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_81h')); 
      },
      trip_81l: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_81l')); 
      },
      tr_33_alarm: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('start_33')); 
      },
      tr_96_trip: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_96')); 
      },
      tr_26_alarm: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('start_26')); 
      },
      tr_26_trip: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('trip_26')); 
      },
      tsc_alarm: function() {
        return this.SocketData?.warning?.some(w => w.code?.includes('tsc_alarm')); 
      },
    },
    mounted() {
    },
    created() {
      
    },
    watch: {
    },
    methods: {
      CB_ON_OFF(on_off) {
        if(this.iecControl){
          const vm = this;
          vm.$confirm(
            `${this.SocketData.equipment_id} 確定執行【${on_off ? "閉合": "斷開"}】指令?`,
            '提示', {confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'})
          .then(() => {
            vm.$loading();
            iecVCBControl({
              customer: "evergreen-yp", 
              code: "VCB", 
              equipment_id: this.SocketData?.equipment_id, 
              action: "VCB_ON_OFF", 
              value: on_off })
            .then(response => {
              if (response.data.success) {
                vm.$message({ type: 'success', message: "指令已下達" });
              } else {
                vm.$message({ type: 'error', message: response.data.message });
              }
            }).catch(response => {
              vm.$message({ type: 'error', message: "api error" });
            }).finally(() => {
              vm.$loading().close();
            });

          }).catch(() => {
          });
        }
        else{
          const vm = this;
          if (!this.SocketData) return;

          vm
            .$confirm(
              `${this.SocketData.equipment_id} 確定執行【${on_off ? "閉合": "斷開"}】指令?`, '提示',
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
                equipment_id: this.SocketData?.equipment_id,
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
        }
      },
    }
  };
  </script>
  <style>.table {
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
  }</style>