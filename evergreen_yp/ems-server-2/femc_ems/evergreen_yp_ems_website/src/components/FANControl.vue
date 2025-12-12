<template>

  <div class="row text-start g-3">
    <div class="col-12 col-md-4">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success p-0">狀態</p>
        <p class="fs-5 m-0 text-end mt-1">{{ SocketData?.fan_status ? '開啟' : '關閉' }}</p>
      </div>
    </div>
    <!-- <div class="col-12 col-md-4">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success p-0">溫度</p>
        <p class="fs-5 m-0 text-end mt-1">{{ SocketData?.temp_air }} °C</p>
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="card border-success p-2">
        <p class="fs-6 m-0 border-bottom border-success p-0">濕度</p>
        <p class="fs-5 m-0 text-end mt-1">{{ SocketData?.humidity_air }} %</p>
      </div>
    </div> -->
  </div>

  <table class="table w-100 table-bordered text-start align-middle mt-2">
    <tbody>
      <tr>
        <td style="width:80px">開/關機</td>
        <td colspan="3">
          <el-button-group>
            <el-button type="primary" :disabled="(SocketData?.fan_status) || !ControlPriviage"
              @click="AIR_ON_OFF(SocketData.equipment_id, true)">開</el-button>
            <el-button type="danger" :disabled="!(SocketData?.fan_status) || !ControlPriviage"
              @click="AIR_ON_OFF(SocketData.equipment_id, false)">關</el-button>
          </el-button-group>
        </td>
      </tr>
      <tr>
        <td>狀態</td>
        <td colspan="3">
          <div class=" json-display" style="max-height: 500px; overflow-y: auto ;">
            <!-- {{ JSON.stringify(SocketData, null, 2) }} -->
            {{ SocketData }}
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script>
import { mapState } from "vuex";
import { postModbusControl } from '@/api/Api.js';

export default {
  props: {
    SocketData: {
      type: Object,
      default: {}
    }
  },
  components: {
  },
  data() {
    return {

    };
  },
  computed: {
    ...mapState(["SocketDataALL", "OPERATE_MODE"]),
    ControlPriviage: function () { return this.$store.getters.userPriviagePage('P01-05') && this.OPERATE_MODE !== 1; },
  },
  mounted() {
  },
  created() {
  },
  watch: {
  },
  methods: {

    AIR_ON_OFF(id, value) {
      const vm = this;

      vm.$confirm(`${id} 確定執行【${value ? '開機' : '關機'}】指令？`, '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        var postData = {
          customer: "advanced",
          code: "FAN",
          action: "BMS_FAN_ON_OFF",
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