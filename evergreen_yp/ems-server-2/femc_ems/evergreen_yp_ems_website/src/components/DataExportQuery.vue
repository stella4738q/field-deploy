<template>
   <!-- <div>
    <p>Equipment ID: {{ equipment_id }}</p>
  </div> -->
  <el-table id="exTable" class="web-table rounded-3" :data="DataExportData" size="small" stripe border header-cell-class-name="tableHeaderStyle" style="font-size: large;">
    <el-table-column min-width="15%" align="center" label="起始日期" prop="start_date">
      <template #default="scope">
        {{ formatDate(scope.row.start_date) }}
      </template>
    </el-table-column>
    <el-table-column min-width="15%" align="center" label="結束日期" prop="end_date">
      <template #default="scope">
        {{ formatDate(scope.row.end_date) }}
      </template>
    </el-table-column>
    <el-table-column min-width="10%" align="center" label="是否完成" prop="process_done">
      <template #default="scope">
        {{ formatBool(scope.row.process_done) }}
      </template>
    </el-table-column>
    <el-table-column min-width="30%" align="center" label="訊息" prop="process_msg"></el-table-column>
    <el-table-column min-width="20%" align="center" label="建立時間" prop="created_on">
      <template #default="scope">
        {{ formatDate(scope.row.created_on) }}
      </template>
    </el-table-column>
    <el-table-column min-width="15%" align="center" label="">
        <template #default="scope">
          <el-button type="success" @click="downloadData(scope.row.equipment_id)" v-if="scope.row.process_done && scope.row.process_msg !== '查無相關資料'">
            下載
          </el-button>
          <el-button type="danger" @click="downloadData(scope.row.equipment_id)" v-if="scope.row.process_done && scope.row.process_msg === '查無相關資料'">
            清除
          </el-button>
          <el-button type="primary" @click="refreshData" v-if="!scope.row.process_done">
            刷新
          </el-button>
        </template>
      </el-table-column>
  </el-table>
  <!------------------------------------------------------------->
  <el-row class="mobile-table">
    <el-col :xs="24" :sm="12" v-for="(item, index) in DataExportData" :key="index">
      <div class="card">
        <ul class="card-body">
        <li><div class="label-style">起始日期</div><span class="text-primary">{{ formatDate(item.start_date) }}</span></li>
        <li><div class="label-style">結束日期</div><span class="text-primary">{{ formatDate(item.end_date) }}</span></li>
        <li><div class="label-style">是否完成</div><span :class="item.process_done ? 'text-success' : 'text-danger'">{{ formatBool(item.process_done) }}</span></li>
        <li><div class="label-style">建立時間</div><span class="text-primary">{{ formatDate(item.created_on) }}</span></li>
        <li><div class="label-style">訊息</div><span class="text-primary">{{ item.process_msg ? item.process_msg : '無訊息' }}</span></li>
        <li>
          <el-button type="success" class="w-100" @click="downloadData(item.equipment_id)" v-if="item.process_done && item.process_msg !== '查無相關資料'">下載</el-button>
          <el-button type="danger" class="w-100" @click="downloadData(item.equipment_id)" v-if="item.process_done && item.process_msg === '查無相關資料'">清除</el-button>
          <el-button type="primary" class="w-100" @click="refreshData" v-if="!item.process_done">刷新</el-button>
        </li>
      </ul>
      </div>
    </el-col>
  </el-row>
   <!------------------------------------------------------------->
</template>

<script>
import moment from 'moment';
import { getExportAsyncData, postExportAsyncData } from '@/api/Api.js';
import libDownload from '@/lib/libDownload.js';

export default {
  props: {
    equipment_id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      Query: {
        equipment_id: this.equipment_id,
      },
      DataExportData: []
    };
  },
  created() {
    this.getDataList();
  },
  methods: {
    getDataList() {
      var vm = this;
      vm.$loading();
      getExportAsyncData(vm.Query)
        .then(response => {
          if (response.data.success) {
            vm.DataExportData = response.data.data;
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch((error) => {
          vm.$message({ type: 'error', message: error });
        })
        .finally(() => {
          vm.$loading().close();
        });
    },
    formatDate(date) {
      return date ? moment(date).format('YYYY-MM-DD HH:mm:ss') : '';
    },
    formatBool(data) {
      return data ? "是" : "進行中";
    },
    refreshData(){
      this.getDataList();
    },
    downloadData(eqid){
      var vm = this;
      vm.$loading();
      let postData = {
        equipment_id: eqid,
        start_date: moment(vm.DataExportData[0].start_date).format('YYYYMMDDhhmmss'),
        end_date: moment(vm.DataExportData[0].end_date).format('YYYYMMDDhhmmss'),
      };
      postExportAsyncData(postData).then(response => {
        if(response.headers['content-type'] !== 'application/json'){
          if(response.headers['content-type'] == 'application/zip'){
            let fileName = `${eqid}紀錄_${moment(vm.DataExportData[0].start_date).format('YYYYMMDDHH')}-${moment(vm.DataExportData[0].end_date).format('YYYYMMDDHH')}.zip`;
            libDownload(response, fileName);
          }
          else{
            let fileName = `${eqid}紀錄_${moment(vm.DataExportData[0].start_date).format('YYYYMMDDHH')}-${moment(vm.DataExportData[0].end_date).format('YYYYMMDDHH')}.csv`;
            libDownload(response, fileName);
          }
        } else {
          const text = new TextDecoder('utf-8').decode(new Uint8Array(response.data));
          const _response = JSON.parse(text);
          if(_response.success){
            vm.$message({ type: 'success', message: _response.message });
          }
          else{
            vm.$message({ type: 'error', message: _response.message });
          }
        }
      }).catch(response => {
        vm.$message({ type: 'error', message: response.message });
      }).finally(() => {
        vm.$loading().close();
        vm.refreshData();
      });
    },
  },
};
</script>

<style scoped>
@media (min-width: 668px) {
  .web-table {
    display: block !important;
  }
  .mobile-table {
    display: none !important;
  }
}
@media (max-width: 667px) {
  .web-table {
    display: none !important;
  }
  .mobile-table {
    display: block !important;
  }
}
</style>
