<template>
  <div class="row text-start g-3">

    <div class="col-12 col-md-1">
      <div class="card border-success p-2">
        <p class="fs-5 m-0 border-bottom border-success">告警</p>
        <div :class="'fs-5 m-0 text-end mt-1' + getBMSClass()">&nbsp;</div>
      </div>
    </div>

    <div class="col-12 col-md-3">
      <div class="card border-success p-2">
        <p class="fs-5 m-0 border-bottom border-success">狀態</p>
        <p class="fs-5 m-0 text-end mt-1">{{ myBMS.status }}</p>
      </div>
    </div>


    <div class="col-12 col-md-8">
      <div class="card border-success p-2">
        <p class="fs-5 m-0 border-bottom border-success">RACK狀態</p>
        <div class="fs-5 p-0 text-end row m-0 text-white" v-if="myBMS.rack">
          <div class="col p-0 m-0 text-center border border-white mt-1" v-for="(rack, ind) in myBMS.rack.sort((a,b) => {return a.rack_no > b.rack_no ? 1 : -1})">
            <div :class="getRackClass(rack.equipment_id)"> {{ rack.rack_no }} </div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <table class="table w-100 table-bordered text-start align-middle mt-2">
    <tbody>
      <tr>
        <td style="width:80px">故障清除</td>
        <td colspan="3">
          <el-button type="primary" :disabled="!ControlPriviage" @click="BMS_FAULT_RESET(myBMS.equipment_id, true)">故障清除</el-button>
        </td>
      </tr>
      <tr>
        <td style="width:80px">上高壓</td>
        <td>
          <el-button-group>
            <el-button type="primary" @click="BMS_ON_OFF(myBMS.equipment_id, true)" :disabled="!(myBMS?.CanOn == true) || !ControlPriviage">開</el-button>
            <el-button type="danger" @click="BMS_ON_OFF(myBMS.equipment_id, false)" :disabled="!(myBMS?.CanOff == true) || !ControlPriviage">關</el-button>
            <!-- <el-button type="primary" :disabled="!(myBMS?.CanOn == true)" @click="BMS_ON_OFF(myBMS.id, true)">開</el-button>
            <el-button type="primary" :disabled="!(myBMS?.CanOff == true)"
              @click="BMS_ON_OFF(myBMS.id, false)">關</el-button> -->
          </el-button-group>
        </td>
      </tr>
      <tr>
        <td>狀態</td>
        <td><div class="json-display" style="max-height: 500px; overflow-y: auto ;">
          {{ myBMS.content }}
        </div></td>
      </tr>
    </tbody>
  </table>

</template>
<script>

import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";
import EquipmentStatusColor from '@/JSON/EquipmentStatusColor.json';

export default {
  props: {
    BMSStoreID: null,
  },
  components: {
  },
  data() {
    return {
      EquipmentStatusColor
    };
  },
  computed: {
    ...mapState(["SocketDataALL", "BMS1", "BMS2", "OPERATE_MODE"]),
    ControlPriviage : function () { return this.$store.getters.userPriviagePage('P01-02') && this.OPERATE_MODE !== 1;},
    myBMS: function () {
      return this[this.BMSStoreID];
    }
  },
  mounted() {

  },
  created() {
  },
  watch: {
  },
  methods: {
    getBMSClass() {
        if (this.myBMS?.abnormal) {
          const level_list = [];
          this.myBMS.warning?.forEach(x => {
            level_list.push(x.level);
          });

          const max_level = Math.max(...level_list, 0); // 預防空陣列
          let state_color = '';
          if (max_level >= 2) {
            state_color = ' bg-danger';
          } else if (max_level >= 1) {
            state_color = ' bg-warning';
          } else {
            state_color = ' bg-success';
          }

          return state_color;
        }

        return ' bg-success';
    },
    getRackClass(attr) {
      var find = this.myBMS?.rack.find(x => { return x.equipment_id == attr });
      if (find) {
        var state_color = this.EquipmentStatusColor.RACK.find((x) => { return x.name == find.rack_state })?.color
        if (find.abnormal){
          var level_list = []
          find.warning.forEach(x => {
            level_list.push(x.level)
          });
          var max_level = Math.max(...level_list);
          console.log(level_list)
          var state_color = max_level >= 2 ? ' bg-danger' :   max_level >= 0 ? " bg-warning": state_color;
          return state_color;
        }
        return find.abnormal ? ' bg-danger' : ' ' + state_color;
      }
      return ' bg-dark';
    },
    postRackList(value) {
      let p = [];
      const vm = this;
      vm.myBMS.rack.forEach(x => {
        let postData = {
          customer: "advanced",
          code: "RACK",
          action: "RACK_ON_OFF",
          equipment_id: x.equipment_id,
          value: value,
        };

        p.push(postModbusControl(postData));


      });

      return p;
    },
    BMS_ON_OFF(id, value) {
      const vm = this;

      vm.$confirm(`${id} 確定執行【${value ? '上高壓' : '下高壓'}】指令？`, '提示', {
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
            code: "BMS",
            action: "BMS_ON_OFF",
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
    BMS_FAULT_RESET(id, value) {
      const vm = this;
      vm.$confirm(`${id} 確定執行【故障清除】指令？`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
        var postData = {
          customer: "advanced",
          code: "BMS",
          action: "BMS_FAULT_RESET",
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
    BMS_DC_SWITCH_ONOFF(id, value) {
      const vm = this;
      vm.$confirm(`${id} 確定執行【${value ? 'DC開啟' :  'DC關閉'}】指令？`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
        var postData = {
          customer: "advanced",
          code: "BMS",
          action: "BMS_DC_SWITCH_ONOFF",
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