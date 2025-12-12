<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
    <h1 class="mb-2">儲能系統報表下載</h1>
    <!------------------------------------------------------------------------------------------->
    <el-tabs type="border-card" v-model="activeName">
        
    <el-tab-pane label="圖表查詢" name="tab4">
      <CabinetReportChart></CabinetReportChart>
    </el-tab-pane>
     <!------------------------------------------------------------------------------------------->
    <el-tab-pane label="日報" name="tab1">
      <CabinetReport ref="dc" class="mt-2 mb-2" :report_type="0" :use_pcs_key="false"></CabinetReport>
    </el-tab-pane>
    <!------------------------------------------------------------------------------------------->
    <el-tab-pane label="月報" name="tab2">
      <CabinetReport ref="mc" class="mt-2 mb-2" :report_type="1" :use_pcs_key="false"></CabinetReport>
    </el-tab-pane>
     <!------------------------------------------------------------------------------------------->
     <el-tab-pane label="年報" name="tab3">
      <CabinetReport ref="yc" class="mt-2 mb-2" :report_type="2" :use_pcs_key="false"></CabinetReport>
     </el-tab-pane>
  </el-tabs>
    <!------------------------------------------------------------------------------------------->
  </div>
</div>
</template>
<script>

import CabinetReport from '@/components/CabinetReport.vue';
import CabinetReportChart from '@/components/CabinetReportChart.vue';

export default {
  components: {
    CabinetReport,
    CabinetReportChart
  },
  data() {
    return {
      activeName: 'tab4',
    };
  },
  computed: {
  },
  mounted() {
  },
  beforeUnmount() {
  },
  created() {
    
  },
  watch: {
  },
  methods: {
   
  }
};
</script>
<style>
.el-tabs__item{
  font-size: 18px;
  color: rgb(7,30,61);
}
</style>