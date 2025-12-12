<template>
     <div class="card border-0 shadow-sm" style="">
      <div class="card-body">
         <el-tabs v-model="activeName" type="card">
              <el-tab-pane label="即時警報" name="immediate"><AlarmTable></AlarmTable></el-tab-pane>
              <el-tab-pane label="歷史警報" name="history"><alertHistory></alertHistory></el-tab-pane>
          </el-tabs>
        </div>
      </div>
</template>

<script>
import AlarmTable from '@/components/AlarmTable.vue'
import alertHistory from '@/components/AlertHistory.vue'

    export default {
      components:{
        alertHistory, AlarmTable
      },
        data() {
            return {
              activeName:'immediate',
            };
        },
        created() {
        },
        watch: {
        },
        methods: { 
        },
    };
</script>
<style>
.el-tabs__item{
  font-size: 18px;
  color: rgb(7,30,61);
}
</style>