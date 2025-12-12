<template>
  <div class=" m-0 p-0">
    <el-form :model="Form" :rules="FormRule" ref="Form" label-width="auto" inline>
      <el-form-item label="日期" prop="DateRange">
        <el-date-picker v-model="Form.DateRange" type="daterange" placeholder="請選擇日期時間"></el-date-picker>
      </el-form-item>
    </el-form>
    <div class="text-center">
      <el-button type="primary" @click="Submit">
        下載
      </el-button>
    </div>
  </div>
</template>
<script>



import moment from 'moment';
import { getMeterGetDataExport } from '@/api/Api.js';
import DownloadToCSV from '@/lib/libDownloadTxtCSV';
export default {
  name: 'MeterDataExport',
  props: {
  },
  components: {
  },
  data() {
    return {
      moment,
      Form: {
        DateRange: [],
      },
      FormRule: {
        DateRange: [{ type: "array", required: true, message: ' ', trigger: 'blur' }],
      },
    }
  },
  computed: {},
  watch: {},
  created() { },
  mounted() {
    this.Form.DateRange = [
      this.moment().add(-7, 'day').startOf('isoWeek').toDate()
      ,this.moment().add(-7, 'day').endOf('isoWeek').toDate()
    ];
  },

  methods: {
    Submit() {
      const vm = this;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          vm.$loading();
          getMeterGetDataExport({
            equipment_id: "PM5350-1",
            start_time: vm.moment(vm.Form.DateRange[0]).startOf('day').format("YYYYMMDDHHmmss"),
            end_time: vm.moment(vm.Form.DateRange[1]).endOf('day').format("YYYYMMDDHHmmss")
          })
            .then(response => {
              if (response.data.message == "Success") {
                let fileName =
                  "周前表計資料"
                  + vm.moment(vm.Form.DateRange[0]).format("YYYYMMDD")
                  + "-"
                  + vm.moment(vm.Form.DateRange[1]).format("YYYYMMDD");

                DownloadToCSV(response.data.data.raw_data, fileName);
              } else {
                vm.$message({ type: 'error', message: response.data.message });
              }
            })
            .catch(response => {
              vm.$message({ type: 'error', message: response.message });
            })
            .finally(() => {
              vm.$loading().close();
            });
        }
      });
    },
  },

}
</script>
  