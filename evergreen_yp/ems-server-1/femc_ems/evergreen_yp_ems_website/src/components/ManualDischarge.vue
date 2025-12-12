<template>
  <div class=" m-0 p-0">
    <div class="rounded  p-1 text-white text-center   bg-success mb-2">
      <div>LC： {{ SocketDataALL.lc[0]?.system_working_status ?? "N/A" }} </div>
      <div>PCS： {{ SocketDataALL.pcs[0]?.working_status ?? "N/A" }} </div>
      <div>Power： {{ SocketDataALL.lc[0]?.active_power }} kW </div>
      <div>目前SOC： {{ SocketDataALL?.lc[0]?.system_soc }}%</div>
    </div>

    <el-form :model="Form" ref="Form" label-width="auto">
      <!-- <el-form-item label="持續時間" prop="min">
        <el-select v-model="Form.min" placeholder="請選擇">
          <el-option label="15分鐘" :value="15" />
          <el-option label="30分鐘" :value="30" />
          <el-option label="45分鐘" :value="45" />
          <el-option label="1小時" :value="60" />
        </el-select>
      </el-form-item> -->
      <el-form-item label="放電功率" prop="power">
        <div class="row">
          <div class="col-10">
            <el-input type="number" v-model.number="Form.apower" placeholder="" :min="0"
              :max="SocketDataALL.lc[0]?.rated_power">
              <template #append>kW</template>
            </el-input>
          </div>
          <div class="col-2">
            <el-button type="primary" @click="Submit(Form.apower, 1)" :disabled="lcDisable || pcsDisable || stateDisable">
              放電
            </el-button>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="充電功率" prop="power">
        <div class="row">
          <div class="col-10">
            <el-input type="number" v-model.number="Form.bpower" placeholder="" :min="0"
              :max="SocketDataALL.lc[0]?.rated_power">
              <template #append>kW</template>
            </el-input>
          </div>
          <div class="col-2">
            <el-button type="primary" @click="Submit(Form.bpower, -1)"
              :disabled="lcDisable || pcsDisable || stateDisable">
              充電
            </el-button>
          </div>
        </div>

      </el-form-item>
    </el-form>
  </div>
</template>
<script>

import { postModbusControl } from '@/api/Api.js';
import { mapState } from "vuex";
import EquipmentStatusColor from '@/JSON/EquipmentStatusColor.json'; 

import moment from 'moment';
export default {
  name: 'ManualDischarge',
  props: {
    SOC: {
      type: Number,
      default: 0
    }
  },
  components: {
  },
  data() {
    return {
      moment,
        EquipmentStatusColor,
      Form: {
        min: 15,
        power: 0,
        apower: 0,
        bpower: 0,
      },

    }
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    lcDisable: function () {//lc 在 '待機','運行'才可設定功率
      return [null, undefined, '停機', '保留', '自檢', '啟動中', '故障停機中', '停機中', '自檢失敗', '啟動失敗', '停機失敗', '低電量補償']
        .includes(this.SocketDataALL.lc[0]?.system_working_status);
    },
    pcsDisable: function () {//pcs 在 '運行','待機',才可設定功率
      return [undefined, null, '按鍵關機', '保留', '啟動中', '關機中', '故障停機', '告警運行', '降額運行', '通信異常']
        .includes(this.SocketDataALL.pcs[0]?.working_status);
    },
    stateDisable: function () {//bms、pcs、lc ，三者都是綠色才能執行充放電控制
      let lc = this.SocketDataALL.lc[0]?.system_working_status;
      let lcSuccess = this.EquipmentStatusColor?.LC?.find((x) => { return x.name == lc && x.discharge == true }) == null;
      let pcs = this.SocketDataALL.pcs[0]?.working_status;
      let pcsSuccess = this.EquipmentStatusColor?.PCS?.find((x) => { return x.name == pcs && x.discharge == true }) == null;
      let bms = this.SocketDataALL.bms[0]?.working_status;
      let bmsSuccess = this.EquipmentStatusColor?.BMS?.find((x) => { return x.name == bms && x.discharge == true }) == null;

      return lcSuccess || pcsSuccess || bmsSuccess;
    }
  },

  mounted() {
  },
  methods: {

    Submit(power, abVal) {
      const vm = this;
      if (power < 0 || power === "" || power === null || power === undefined || power > this.SocketDataALL.lc[0]?.rated_power) {
        vm.$message({ type: 'error', message: "請輸入 0 ~ " + this.SocketDataALL.lc[0]?.rated_power + "功率" });
        return false;
      }

      vm.$confirm('確定送出指令?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.$loading();
        var postData = {
          customer: "tasco",
          code: "LC",
          equipment_id: null,
          action: "LC_SET_POWER",
          value: power * abVal
        };
        postModbusControl(postData).then(response => {
          if (response.data.Success) {
            vm.$message({ type: 'success', message: "指令已下達" });
          } else {
            vm.$message({ type: 'info', message: JSON.stringify(response.data) });
          }
        }).catch(response => {
          vm.$message({ type: 'error', message: "api error" });
        }).finally(() => {
          vm.$loading().close();
        })
      }).catch(() => {
      });

    },
  },
  created() {


  },
}
</script>
  