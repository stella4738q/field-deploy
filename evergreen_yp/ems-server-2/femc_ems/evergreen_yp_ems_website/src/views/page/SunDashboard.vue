<template>
  <div class="row gx-3 gy-3">
    <div class="col-12 col-md-12 col-lg-12">
      <!-- ======================================================= -->
       <!-- 顯示太陽能資訊 -->
      <div style="font-size: small;" class="row shadow justify-content-center align-items-center pt-3 pb-3 alert alert-warning ">
        <el-row :gutter="20">
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-lightning-fill'" :num="sunData.totalExpPower" :unit="'kWh'" :hint="'總發電量'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-lightning-fill'" :num="sunData.todayExpPower" :unit="'kWh'" :hint="'今日發電量'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-lightning-fill'" :num="sunData.realtimeExpPower" :unit="'kW'" :hint="'即時發電量'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-speedometer2'" :num="sunData.eqTime" :unit="'hr'" :hint="'平均發電量'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-sun'" :num="sunData.irr" :unit="'kWh/m²'" :hint="'日照量'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-graph-up'" :num="sunData.pr" :unit="'%'" :hint="'PR'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-hand-thumbs-up-fill'" :num="sunData.co2Diff" :unit="'kgCO₂e'" :hint="'減碳量'"></TextBlock></el-col>
            <el-col :xs="12" :sm="6" :md="4">
              <TextBlock :icon="'bi-tree-fill'" :num="sunData.createTree" :unit="'棵'" :hint="'造林樹'"></TextBlock></el-col>
        </el-row>
      </div>

      <!-- 顯示太陽能圖表 -->
      <div class="card shadow-sm border-0 mb-3">
        <div class="card-body row">
          <div class="col-12 col-md-12 col-lg-12" style="overflow-x: scroll; width: 100%; height: 350px;"> <!-- 設定固定高度 -->
            <ChartPowerSun></ChartPowerSun>
          </div>
        </div>
      </div>

       <!-- 顯示DCU -->
      <!-- ======================================================= -->
      <div class="shadow-sm border-0 mb-3">
        <el-row :gutter="20">
          <el-col v-for="(dcu, index) in dcuList" :key="dcu.equipment_id" :xs="24" :sm="24" :md="24" :lg="24">
            <DCUInfo :dcu="dcu" />
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>
<script>
import ChartPowerSun from '@/components/ChartPowerSun.vue';
import moment from "moment";
import { mapState } from "vuex";
import TextBlock from '@/components/TextBlock.vue';
import DCUInfo from '@/components/DCUInfo.vue';
import { getDashboardSunDataDB } from '@/api/Api.js';

window.allCharts = [];

export default {
  components: {
    ChartPowerSun,
    TextBlock,
    DCUInfo
  },
  data() {
    return {
      moment,
      intervalId: null,
      sunData: {
        totalExpPower: 0, //總發電量
        todayExpPower: 0, //今日發電量
        realtimeExpPower: 0, //即時發電量
        eqTime: 0, //等效發電小時
        co2Diff: 0, //減碳量
        createTree: 0, //造林樹
        irr: 0,
        pr: 0
      }
    };
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    dcuList: function() {
      return this.SocketDataALL.dcu.slice().sort((a, b) => {
        return a.equipment_id.localeCompare(b.equipment_id);
      });
    }
  },
  mounted() {
    this.getSunDashboard();
    let vm = this;
    if (vm.intervalId === null) {
      vm.intervalId = window.setInterval(vm.getSunDashboard, 10000);
    }
    this.calData();
  },
  beforeUnmount() {
    let vm = this;
    window.clearInterval(vm.intervalId);
    vm.intervalId = null;
  },
  watch: {
    SocketDataALL: {
      handler() {
        this.calData();
      },
      deep: true
    }
  },
  methods: {
    calData() {
      this.sunData.realtimeExpPower = 0;
      this.SocketDataALL.dcu.forEach(element => {
        element?.inverter?.forEach(ele => {
          this.sunData.realtimeExpPower += ele.dc_k_watt || 0;
        })
      });
      //小數處理
      this.sunData.realtimeExpPower = this.sunData.realtimeExpPower.toFixed(3)
    },
    async getSunDashboard() {
      const vm = this;
      getDashboardSunDataDB().then(response => {
          if (response.data.Success) {

            var data = response.data.Data;
            vm.sunData.totalExpPower = data.totalExpPower;
            vm.sunData.todayExpPower = data.todayExpPower;
            vm.sunData.eqTime = data.eqTime;
            vm.sunData.co2Diff = data.co2Diff;
            vm.sunData.createTree = data.createTree;
            vm.sunData.irr = data.irr;
            vm.sunData.pr = data.pr;
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
    },
  },
};
</script>
<style>
.el-col {
  margin-bottom: 20px; /* 控制卡片之間的上下間距 */
}

.el-col .el-card {
  /* 適當控制卡片的高度，確保內容顯示完整 */
  height: 100%;
}
</style>