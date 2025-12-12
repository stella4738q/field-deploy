<template>
 <div class="p-3 card border-0 shadow-sm">
    <div class="card-body">
    <h1>BMS歷史記錄下載</h1>
    <div class="d-flex align-items-center mb-3">
      <el-form :model="Form" ref="Form" :rules="FormRule" label-width="100px">
        <el-form-item label="BMS" prop="bms">
          <el-select v-model="Form.bms" placeholder="請選擇...">
            <el-option value="BMU_1" label="BMU 1"> </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="起始日期" prop="start_date">
          <el-date-picker v-model="Form.start_date" type="date" value-format="YYYYMMDD" :disabled-date="DisableStart" />
        </el-form-item>
        <el-form-item label="起始時間" prop="start_time">
          <el-time-select v-model="Form.start_time" start="00:00" step="00:01" end="23:59" placeholder="Select time" />
        </el-form-item>
        <el-form-item label="結束日期" prop="end_date">
          <el-date-picker v-model="Form.end_date" type="date" value-format="YYYYMMDD" :disabled-date="DisableEnd" />
        </el-form-item>
        <el-form-item label="結束時間" prop="end_time">
          <el-time-select v-model="Form.end_time" start="00:00" step="00:01" end="23:59" placeholder="Select time" />
        </el-form-item>
        <el-form-item>
          <div class="text-center">
            <el-button class="btn btn-primary btn-sm" @click="SearchClick">
              <font-awesome-icon icon="search" /></el-button>
          </div>
        </el-form-item>
        <el-form-item label="">
        </el-form-item>
      </el-form>
    </div>
    </div>
    <DataExportQuery ref="dataExportQuery" equipment_id="BMU_1"></DataExportQuery>
  </div>
</template>
<script>

import moment from 'moment';
import DataExportQuery from '@/components/DataExportQuery.vue'
import { getBMSGetDataExport, postExportAsyncData } from '@/api/Api.js';
import libDownloadZip from '@/lib/libDownloadZip.js';



export default {
  components: {
    DataExportQuery
  },
  data() {
    var chkEndDate = (rule, value, callback) => {
      if (!this.Form.start_date || !this.Form.start_time || !this.Form.end_date || !this.Form.end_time) {
        return callback();
      } else {
        let startDateTime = this.moment(this.Form.start_date + this.Form.start_time , "YYYYMMDDHH:mm");
        let endDateTime = this.moment(this.Form.end_date + this.Form.end_time , "YYYYMMDDHH:mm");

        if (startDateTime.isAfter(endDateTime)) {
          return callback(new Error('結束時間不可大於開始時間'));
        }
        else {
          return callback();
        }
      }
    };
    return {
      moment,
      today: moment().startOf('day'),
      Form: {
        daterange: [],
        bms: 'BMU_1',
        start_date: moment().format('YYYYMMDD'),
        start_time: (moment().subtract(1, 'hours').format('HH:mm')),
        end_date: moment().format('YYYYMMDD'),
        end_time: moment().format('HH:MM'),
      },
      FormRule: {
        bms: [{ type: 'string', required: true, message: ' ', trigger: 'blur' }],
        start_date: [{ type: 'string', required: true, message: ' ', trigger: 'blur' }],
        start_time: [{ type: 'string', required: true, message: ' ', trigger: 'blur' }],
        end_date: [{ type: 'string', required: true, message: ' ', trigger: 'blur' }],
        end_time: [{ type: 'string', required: true, message: ' ', trigger: 'blur' },
        { validator: chkEndDate, trigger: 'blur' }
        ],
      },

    }
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
    DisableStart(Date) {
      if (this.Form.end_date) {
        return this.moment(this.Form.end_date).isBefore(this.moment(Date.getTime())) || this.today.isBefore(this.moment(Date.getTime()));
      }
      return this.today.isBefore(this.moment(Date.getTime()));
    },
    DisableEnd(Date) {
      if (this.Form.start_date) {
        return this.moment(this.Form.start_date).isAfter(this.moment(Date.getTime())) || this.today.isBefore(this.moment(Date.getTime()));
      }
      return this.today.isBefore(this.moment(Date.getTime()));
    },
    SearchClick() {
      const vm = this;
      const postData = {
        equipment_id: vm.Form.bms,
        start_date: vm.Form.start_date + vm.Form.start_time.replace(':', '') + "00", 
        end_date: vm.Form.end_date + vm.Form.end_time.replace(':', '') + "59"
      };
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          vm.$loading();
          
          postExportAsyncData(postData).then(response => {
            if(response.headers['content-type'] !== 'application/json'){
              var sdate = vm.Form.start_date + vm.Form.start_time.replace(':', '') + "00";
              var edate = vm.Form.end_date + vm.Form.end_time.replace(':', '') + "59";
              let fileName = `BMS紀錄_${vm.moment(sdate, 'YYYYMMDDHHmmss').format("YYMMDDHH")}-${vm.moment(edate, 'YYYYMMDDHHmmss').format("YYMMDDHH")}.zip`;
              libDownloadZip(response, fileName);
              vm.$refs.dataExportQuery.refreshData();
            }
            else{
              const text = new TextDecoder('utf-8').decode(new Uint8Array(response.data));
              const _response = JSON.parse(text);
              if(_response.success){
                vm.$message({ type: 'success', message: _response.msg });
                vm.$refs.dataExportQuery.refreshData();
              }
              else{
                vm.$message({ type: 'error', message: _response.msg });
              }
            }
          }).catch(response => {
            vm.$message({ type: 'error', message: response.message });
          }).finally(() => {
            vm.$loading().close();
          });
          
          // getBMSGetDataExport(postData).then(response => {
          //   if(response.headers['content-type'] !== 'application/json'){
          //     libDownloadZip(response, fileName);
          //   }
          //   else{
          //     const text = new TextDecoder("utf-8").decode(response.data);
          //     const _response = JSON.parse(text);
          //     vm.$message({ type: 'error', message: _response.message });
          //   }
          // }).catch(response => {
          //   vm.$message({ type: 'error', message: response.message });
          // }).finally(() => {
          //   vm.$loading().close();
          // });
        }
      });
    }
  },
};
</script>