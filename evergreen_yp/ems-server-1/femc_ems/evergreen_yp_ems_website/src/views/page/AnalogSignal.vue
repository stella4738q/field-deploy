<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <div class="p-3">
        <h1>保護訊號</h1>
        <table class="w-100 table table-bordered  table-hover text-center">
          <thead>
            <tr class="table-secondary">
              <th colspan="2">項目</th>
              <th>BMS_1</th>
              <th>BMS_2</th>
              <th>PCS</th>
              <th>其他</th>
            </tr>
          </thead>
          <tbody>

            <tr>
              <td colspan="2">通訊中斷</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.conn_abnormal_bms_1" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.conn_abnormal_bms_2" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.conn_abnormal_pcs" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
            </tr>

            <tr>
              <td rowspan="2" class="align-middle">過壓</td>
              <td>Alarm</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ov_1_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ov_1_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td>Fault</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ov_2_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ov_2_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>

            <tr>
              <td rowspan="2" class="align-middle">欠壓</td>
              <td>Alarm</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.uv_1_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.uv_1_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td>Fault</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.uv_2_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.uv_2_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            
            <tr>
              <td rowspan="2" class="align-middle">過流</td>
              <td>Alarm</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.oc_1_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.oc_1_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td>Fault</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.oc_2_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.oc_2_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td rowspan="2" class="align-middle">過溫</td>
              <td>Alarm</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ot_1_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ot_1_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td>Fault</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ot_2_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ot_2_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td rowspan="2" class="align-middle">低溫</td>
              <td>Alarm</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.u1_1_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.u1_1_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td>Fault</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ut_2_bms_1"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ut_2_bms_2"
                  icon="triangle-exclamation" class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td colspan="2">消防/火災</td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.fire_bms_1" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.fire_bms_2" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
              <td>
              </td>
            </tr>

            <tr>
              <td colspan="2">絕緣異常</td>
              <td>
              </td>
              <td>
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.insulation_fault" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
               
              </td>
            </tr>

            <tr>
              <td colspan="2">接地異常</td>
              <td>
              </td>
              <td>
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.ground_fault" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
              <td>
              </td>
            </tr>
            <tr>
              <td colspan="2">逆送電</td>
              <td>
              </td>
              <td>
              </td>
              <td>
              </td>
              <td>
                <font-awesome-icon v-if="SocketDataALL.env_status[0]?.reverse_power_main || SocketDataALL.env_status[0]?.reverse_power_factory" icon="triangle-exclamation"
                  class="text-danger" />
                <font-awesome-icon v-else icon="circle-check" class="text-success" />
              </td>
            </tr>
          </tbody>
        </table>


      </div>
    </div>
  </div>
</template>
<script>
import { mapState } from "vuex";

export default {
  components: {
  },
  data() {
    return {
    };
  },
  computed: {
    ...mapState(["SocketDataALL"]),
  },
  mounted() {
  },
  created() {
  },
  watch: {
  },
  methods: {
  }
};
</script>