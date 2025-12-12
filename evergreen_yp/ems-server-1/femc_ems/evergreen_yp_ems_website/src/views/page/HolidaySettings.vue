<template>
  <div class="card border-0 shadow-sm" style="">
    <div class="card-body">
      <h1 class="mb-2">台電假日設定</h1>
      <!-- =============================================== -->
      <el-form label-width="auto" :inline="true" label-position="top" class="align-items-end">
        <!-- ========================================== -->
        <el-form-item label="目前顯示年份">
          <el-date-picker v-model="year" type="year" value-format="YYYY" placeholder="目前顯示年份" />
        </el-form-item>
        <!-- ========================================== -->
        <el-form-item label="選擇上傳年份">
          <el-date-picker v-model="uploadYear" type="year" value-format="YYYY" placeholder="選擇要上傳的年份" />
        </el-form-item>
        <!-- ========================================== -->
        <el-form-item label="">
          <el-button type="primary" @click="updInputReset" :disabled="!this.uploadYear">
              上傳範本
              <input id="upload" type="file" ref="uploadInput" @change="changUpdVal" accept=".csv" hidden />
          </el-button>
        </el-form-item>
        <!-- ========================================== -->
        <el-form-item label="">
          <el-button type="primary" @click="downloadTmp">下載範本</el-button>
        </el-form-item>
        <!-- ========================================== -->
      </el-form>
      <!-- =============================================== -->
      <el-row :gutter="8">
        <el-col class="mb-2" :xs="24" :sm="8" v-for="(item, idx) in all_year" :index="idx">
          <!-- {{ defaultShow[idx] }} -->
          <!-- {{ item }} -->
          <el-calendar :model-value="item" style="text-align: center;">
            <template #header="{ date }">
              <span style="font-weight: bold;">
                {{ date }}
              </span>
            </template>
            <template #date-cell="{ data }">
                <div :class="this.hoildaysData === null ? 'notHoilday' : (this.hoildaysData.data.indexOf(data.day) === -1 ? 'notHoilday' : 'isHoilday')">
                  {{ this.getData(data.day) }}
                </div>
            </template>
          </el-calendar>
        </el-col>
      </el-row>
      <!-- <el-calendar v-model="value">
          <template  #date-cell="{ data }">
            <pre>{{ data }}</pre>
          </template>
        </el-calendar> -->
    </div>
  </div>
</template>

<script>
import { computed } from "vue";
import moment from "moment";
import { getHoildays, UpTemplate } from "@/api/Api.js";
import libDownload from "@/lib/libDownload.js";

export default {
  components: {},
  mounted() {
    this.getHoildayApi();
  },
  data() {
    return {
      searchData: {
        year: moment().format("YYYY"),
      },
      year: moment().format("YYYY"),
      uploadYear: null,
      value: null,
      all_year: computed(() => {
        const allmonth = [];
        for (let month = 0; month < 12; month++) {
          const startDate = new Date(this.year, month, 1);
          allmonth.push(startDate);
        }
        if (this.isLeap(this.year)) {
          allmonth[1] = new Date(this.year, 1, 29);
        }
        return allmonth;
      }),
      hoildaysData: null,
    };
  },
  created() {},
  watch: {},
  methods: {
    isLeap(yyyy) {
      if ((yyyy % 4 == 0 && yyyy % 100 != 0) || yyyy % 400 == 0) {
        return 1;
      }
      return 0;
    },
    getHoildayApi() {
      const vm = this;
      vm.$loading();
      getHoildays({ year: vm.year })
        .then(response => {
          if (response.data.message === 'Success') {
            if (response.data.data.data.length) {
              vm.hoildaysData = response.data.data;
            } else {
              vm.hoildaysData = null;
              vm.$message({ type: 'warning', message: `年份【${vm.year}】查無休假資料` });
            }
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .finally(() => {
          vm.$loading().close();
        })
    },
    getData(date) {
      return moment(date).format('DD');
    },
    downloadTmp() {
      const vm = this;
      let dataSend = new FormData();
      dataSend.append('year', vm.year);
      dataSend.append('action', 0)

      vm.$loading();
      UpTemplate(dataSend)
        .then(response => {
          if (response.headers['content-type'] === 'text/csv; charset=utf-8') {
            libDownload(response, `${vm.year}_台電假日設定設定範本.csv`);
          }
          if (response.headers['content-type'] === 'application/json') {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .finally(() => {
          vm.$loading().close();
        })
    },
    updInputReset() {
      this.$refs.uploadInput.value = '';
      this.$refs.uploadInput.click();
    },
    changUpdVal(d) {
      let typeCheck;
      if (d.target.files[0].type === 'text/csv') {
        typeCheck = true;
      } else {
        typeCheck = false;
        this.$message({ type: 'error', message: `檔案【${d.target.files[0].name}】非指定檔案類型、無法上傳！` });
      }
      if (typeCheck === true) {
        this.uploadTmp(d.target.files[0]);
      }
    },
    uploadTmp(fff) {
      let dataSend = new FormData();
      dataSend.append('year', this.uploadYear);
      dataSend.append('action', 1);
      dataSend.append('file', fff);
      UpTemplate(dataSend)
        .then((res) => {
          // console.log(res.data);
          if (res.data.message === 'Success') {
            this.$message({ type: 'success', message: `【${fff.name}】上傳成功。` });
            this.year = this.uploadYear; // 重新取得資料
          } else {
            this.$message({ type: 'error', message: `【${fff.name}】上傳失敗。錯誤代碼：${res.data.message}` });
          }
          this.getHoildayApi(); // 重新取得資料
        })
        .catch((error) => {
          // console.log(error);
          this.$message({ type: 'error', message: `【${fff.name}】上傳失敗(error)。錯誤代碼：${JSON.stringify(error)}` });
          this.getHoildayApi(); // 重新取得資料
        });
    }
  },
  watch: {
    year: {
      handler(newVal, oldVal) { 
        if (newVal && newVal !== oldVal) {
          this.getHoildayApi();
        } else {
          const vm = this;
          vm.$message({ type: 'error', message: '年份不可為空' });
        }
      },
      deep: true,
    },
  },
};
</script>
<style>
.el-calendar-table .el-calendar-day {
  padding: 0px;
}
.notHoilday {
  padding: 8px;
}
.isHoilday{
  padding: 8px;
  background-color: #ffa173;
  color: #fff;
  width: 100%;
  height: 100%;
}
.is-selected{
  background-color: transparent !important;
}
.prev, .next{
  visibility: hidden !important;
}
.prev .isHoilday, .next .isHoilday{
  padding: 8px;
  background-color: inherit;
  color: inherit;
  width: 100%;
  height: 100%;
}
.calendar-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
  padding: 10px;
  border: 2px solid #ccc;
  border-radius: 8px;
}
.el-calendar {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}
.el-calendar__header{
  background-color: rgba(228, 235, 249, 0.542);
}
</style>
