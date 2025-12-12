<template>
  <div class="row g-3">
    <!-- =========================== 最上面的表 =========================== -->
    <div class="col-12">
      <div class="card shadow-sm border-0">
        <div class="card-body row g-2">
          <div class="col-12 col-md d-flex flex-column align-items-center">
            <ChartGauge title="SOC" unit="%" :val="Number((SocketDataALL?.bms[BMSIndex]?.soc ?? 0).toFixed(2))"
              :color="ColorList.SOC.Percentage"></ChartGauge>
          </div>
          <div class="col-12 col-md d-flex flex-column align-items-center">
            <ChartGauge title="最高電芯溫度" unit="℃"
              :val="Number((SocketDataALL?.bms[BMSIndex]?.max_cell_temperature ?? 0).toFixed(1))"
              :color="ColorList.TemperatureEnv.Percentage"></ChartGauge>
          </div>
          <div class="col-12 col-md d-flex flex-column align-items-center">
            <ChartGauge title="變壓器油溫" unit="℃"
              :val="Number((SocketDataALL?.tr[0]?.temperature ?? 0).toFixed(2))"
              :color="ColorList.TemperatureTR.Percentage"></ChartGauge>
          </div>
          <div class="col-12 col-md d-flex flex-column align-items-center">
            <h5 class="text-center"> 溫溼度 </h5>
            <ul class="list-group list-group-flush">
              <li class="list-group-item"><b>溫度/濕度(液冷櫃內)：</b>{{ this.SocketDataALL?.bms[BMSIndex].container_temp_a }} °C / {{
              this.SocketDataALL?.bms[BMSIndex].container_humidity_a }} %</li>
              <li class="list-group-item"><b>溫度/濕度(DCP)：</b>
                {{ this.SocketDataALL?.dehu?.[0].temperature }} °C / 
                {{ this.SocketDataALL?.dehu?.[0].humidity }} %
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <!-- =========================== 第二排最左 =========================== -->
    <div class="col-12 col-md-3">
      <div class="card shadow-sm border-0">
        <div class="card-body">
          <p class="text-center fs-4">PCS</p>
          <ul class="list-group list-group-flush">
            <li class="list-group-item"><b>設備代號：</b>{{ SocketDataALL?.pcs[PCSIndex]?.equipment_id }}</li>
            <!-- <li class="list-group-item"><b>電網狀態：</b>{{ SocketDataALL?.pcs[PCSIndex]?.grid_status }}</li> -->
            <!-- <li class="list-group-item"><b>運行模式：</b>{{ SocketDataALL?.pcs[PCSIndex]?.working_mode }}</li> -->
            <li class="list-group-item"><b>運行狀態：</b>{{ SocketDataALL?.pcs[PCSIndex]?.running_status }}</li>
            <li class="list-group-item"><b>電網頻率：</b>{{ SocketDataALL?.pcs[PCSIndex]?.frequency?.toFixed(2) }} Hz
            </li>
            <li class="list-group-item"><b>實功率：</b>{{ SocketDataALL?.pcs[PCSIndex]?.active_power?.toFixed(2) }} kW
            </li>
            <li class="list-group-item"><b>虛功率：</b>{{ SocketDataALL?.pcs[PCSIndex]?.reactive_power?.toFixed(2) }} kVar
            </li>
            <!-- <li class="list-group-item"><b>視在功率：</b>{{ SocketDataALL?.pcs[PCSIndex]?.apparent_power?.toFixed(2) }} KVA
            </li> -->
            <li class="list-group-item"><b>電壓/電流(R)：</b>
              {{ SocketDataALL?.pcs[PCSIndex]?.volt_rs?.toFixed(2) }} V /
              {{ SocketDataALL?.pcs[PCSIndex]?.current_r?.toFixed(2) }} A
            </li>
            <li class="list-group-item"><b>電壓/電流(S)：</b>
              {{ SocketDataALL?.pcs[PCSIndex]?.volt_st?.toFixed(2) }} V /
              {{ SocketDataALL?.pcs[PCSIndex]?.current_s?.toFixed(2) }} A
            </li>
            <li class="list-group-item"><b>電壓/電流(T)：</b>
              {{ SocketDataALL?.pcs[PCSIndex]?.volt_tr?.toFixed(2) }} V /
              {{ SocketDataALL?.pcs[PCSIndex]?.current_t?.toFixed(2) }} A
            </li>
            <li class="list-group-item"><b>環境溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.ambient_temperature?.toFixed(2) }}
              ℃</li>
            <li class="list-group-item"><b>IGBT模組1溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.igbt_temp_m1?.toFixed(2) }} ℃
            </li>
            <!-- <li class="list-group-item"><b>IGBT模組2溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.igbt_temp_m2?.toFixed(2) }} ℃
            </li> -->
            <li class="list-group-item"><b>控制區塊溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.ctrl_section_temp?.toFixed(2) }}
              ℃</li>
            <li class="list-group-item"><b>儲能櫃模組1溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.cabinet_temp_m1?.toFixed(2) }}
              ℃</li>
            <!-- <li class="list-group-item"><b>儲能櫃模組2溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.cabinet_temp_m2?.toFixed(2) }}
              ℃</li> -->
            <li class="list-group-item"><b>LCL模組1溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.lcl_section_temp_m1?.toFixed(2)
              }} ℃</li>
            <!-- <li class="list-group-item"><b>LCL模組2溫度：</b>{{ SocketDataALL?.pcs[PCSIndex]?.lcl_section_temp_m2?.toFixed(2)
              }} ℃</li> -->
          </ul>
        </div>
      </div>
    </div>
    <!-- =========================== pcs 資訊 第二排中間 =========================== -->
    <div class="col-12 col-md-6">
      <div class="card shadow-sm border-0">
        <div class="card-body">
          <CabinetESSCI v-if="SocketDataALL?.bms[BMSIndex]?.rack?.length"></CabinetESSCI>
        </div>
      </div>
    </div>
    <!-- =========================== 電池資訊 第二排最右邊 =========================== -->
    <div class="col-12 col-md-3">
      <div class="card shadow-sm border-0">
        <div class="card-body">
          <div @click="outerVisible = true" class="">
            <div class="m-0" style="flex-wrap:wrap;">
              <div v-for="(item, ind) in SocketDataALL?.bms[BMSIndex]?.rack" :key="ind" class="rounded-2 col mb-3"
                style="">
                <div class="m-0 text-center" @click="ShowRackDetail(item.equipment_id, ind, 'ECI', item)">
                  <div>{{ item.equipment_id }}</div>
                </div>
                <div class="p-1 row m-0 p-0" @click="ShowRackDetail(item.equipment_id, ind, 'v', item)">
                  <div style="width:20px">
                    <font-awesome-icon icon="battery-full" />
                  </div>
                  <div class="col">
                    <el-progress :text-inside="true" :stroke-width="18" :percentage="item.soc >= 100 ? 100 : item.soc < 0 ?  0 : item.soc"
                      :color="ColorList.SOC.Progress">
                      {{ (item.soc).toFixed(1) }}%
                    </el-progress>
                  </div>
                </div>
                <div class="p-1 row m-0 p-0" @click="ShowRackDetail(item.equipment_id, ind, 't', item)">
                  <div style="width:20px">
                    <font-awesome-icon icon="temperature-low" />
                  </div>
                  <div class="col">
                    <el-progress :text-inside="true" :stroke-width="18" :percentage="item.max_cell_temperature >= 100 ? 100 : item.max_cell_temperature < 0 ?  Math.abs(item.max_cell_temperature) : item.max_cell_temperature"
                      :color="ColorList.TemperatureBMS.Progress">
                      {{ item.max_cell_temperature.toFixed(0) }}&deg;C
                    </el-progress>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
  <!-- ======================================= -->
  <el-dialog :title="RackDetailTitle" v-model="outerVisible" top="10px" :destroy-on-close="true" :width="screenWidth < 800 ? '95%' : '65%'">
    <!-- <CabinetDetail :BMSIndex="BMSIndex" :RackIndex="RackIndex" :RackName="RackDetailTitle" :TabName="RackTabName">
    </CabinetDetail> -->
    <CabinetDetail :RackData="RackData" :dif="myDif" :RackName="RackDetailTitle" :TabName="RackTabName">
    </CabinetDetail>
  </el-dialog>
</template>

<script>
import CabinetDetail from '@/components/CabinetDetail.vue';
import { computed } from 'vue';
import myBattary from '@/components/Battary.vue';
import ChartGauge from '@/components/ChartGauge.vue';
import CabinetESSCI from '@/components/CabinetESSCI.vue';
import ColorList from '@/JSON/ColorRange.json';
import FireAlarmCodeList from '@/JSON/FireAlarmCodeList.json';
import { mapState } from "vuex";

export default {
  props: {
    BMSIndex: {
      type: Number,
      default: -1,
    },
    PCSIndex: {
      type: Number,
      default: -1,
    },
  },
  components: {
    CabinetDetail, myBattary, ChartGauge, CabinetESSCI
  },
  mounted() {
    this.$nextTick(() => {
      window.addEventListener('resize', this.onResize);
    })
  },
  data() {
    return {
      ColorList,
      RackIndex: -1,
      FireAlarmCodeList,
      equipment_id: '',
      CurrentTitle: computed(() => {
        return

      }),
      Api: {
        getCabinetInfo: {
          field_id: this.$store.getters.getField,
          equipment_id: this.equipment_id,
        }
      },
      ApiResult: null,
      outerVisible: false,
      Rack_equipment_id: '',
      RackDetailTitle: '',
      RackTabName: '',
      RackData: null,
      myDif: 1,
      screenWidth: window.innerWidth,
    };
  },
  computed: {
    ...mapState(["SocketDataALL"])
  },
  created() {

  },
  watch: {
  },
  methods: {
    ShowRackDetail(equipment_id, ind, tabname, rackItem) {
      this.RackData = rackItem;
      this.RackIndex = ind;
      this.Rack_equipment_id = equipment_id;
      this.RackDetailTitle = equipment_id;
      this.outerVisible = true;
      this.RackTabName = tabname;
      this.myDif = 1;
    },
    onResize() {
      this.screenWidth = window.innerWidth
    },
  },
};
</script>
<style>
ul li {
  border-radius: unset;
}

.dialog-air-width,
.dialog-rack-width {
  width: 100% !important;
}

@media(min-width: 800px) {
  .dialog-air-width {
    width: 800px !important;
  }

  .dialog-rack-width {
    width: 1100px !important;
  }
}
</style>