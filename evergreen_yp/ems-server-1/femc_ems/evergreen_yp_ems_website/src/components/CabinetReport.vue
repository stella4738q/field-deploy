<template>
  <!-- 查詢條件 -->
  <!-- <pre>{{ Search }}</pre> -->
  <div class="d-flex justify-content-between align-items-center mt-3" style="">
    <el-form label-width="auto" inline>
      <!-- report_type === 0-->
      <el-form-item label="起始時間" v-if="report_type === 0">
        <el-date-picker v-model="Search0.start_date" type="date" placeholder="請選擇起始日期" value-format="YYYYMMDD"></el-date-picker>
      </el-form-item>
      <el-form-item label="結束時間" v-if="report_type === 0">
        <el-date-picker v-model="Search0.end_date" type="date" placeholder="請選擇結束日期" value-format="YYYYMMDD" :disabled-date="disDate" :disabled="startCheck"></el-date-picker>
      </el-form-item>
      <!-- report_type === 1--> 
      <el-form-item label="起始月" v-if="report_type === 1">
        <el-date-picker v-model="Search1.start_date" type="month" placeholder="請選擇起始月份" value-format="YYYYMM"></el-date-picker>
      </el-form-item>
      <el-form-item label="結束月" v-if="report_type === 1">
        <el-date-picker v-model="Search1.end_date" type="month" placeholder="請選擇結束月份" value-format="YYYYMM" :disabled-date="disDate" :disabled="startCheck"></el-date-picker>
      </el-form-item>
      <!-- report_type === 2-->
      <el-form-item label="起始年" v-if="report_type === 2">
        <el-date-picker v-model="Search2.start_date" type="year" placeholder="請選擇起始年" value-format="YYYY"></el-date-picker>
      </el-form-item>
      <el-form-item label="結束年" v-if="report_type === 2">
        <el-date-picker v-model="Search2.end_date" type="year" placeholder="請選擇結束年" value-format="YYYY" :disabled-date="disDate" :disabled="startCheck"></el-date-picker>
      </el-form-item>
      <!-- Search Button-->
      <el-form-item>
        <el-button @click="SearchClick">
          <font-awesome-icon icon="search" />
        </el-button>
      </el-form-item>
    </el-form>
  </div>
  <!-- Table -->
  <el-table :id="`exTable_${report_type}`" :data="DataList" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle" @sort-change="handleSortChange">
    <el-table-column width="150" align="center" prop="type" label="項目"></el-table-column>
    <el-table-column min-width="150" align="center" sortable prop="name" label="名稱"></el-table-column>
    <el-table-column width="200" align="center" label="">
        <template #default="scope">
          <el-button type="success" @click="postDownload(scope.row, true)">
            下載
          </el-button>
          <el-button type="primary" @click="postDownload(scope.row, false)">
            觀看
          </el-button>
        </template>
      </el-table-column>
  </el-table>

  <el-pagination 
    background
    layout="total, sizes, prev, pager, next, jumper" class="d-flex justify-content-end mt-2" 
    :total="DataCount" 
    :current-page="Query.page"
    :size="Query.limit"
    :page-sizes="DataLimit"
    @current-change="PageOnChange"
    @size-change="handleSizeChange">

       <!-- 總筆數 -->
      <template #total="{ total }">
        <span>&nbsp;&nbsp;共{{ total }}筆</span>
      </template>
      <!-- 每頁數量 -->
      <template #sizes="{ sizes, size }">
        <el-select v-model="Query.limit" class="pagination-sizes">
          <el-option v-for="item in sizes" :key="item" :label="item" :value="item" />
        </el-select>
      </template>
  </el-pagination>

  <!------------------------PDF預覽區域------------------------------------->
  <el-dialog title="報表預覽" v-model="ShowPDFDialog" width="100%" center :destroy-on-close="true">
    <iframe v-if="PDF.data" :src="PDF.data" width="100%" height="800px" frameborder="0"></iframe>
    <span slot="footer" class="dialog-footer">
      <el-button @click="ShowPDFDialog = false">關閉</el-button>
    </span>
  </el-dialog>
  
</template>

<script >
import { computed } from 'vue';
import moment from 'moment';
import { getCabinetReport, postCabinetReportDonwload } from '@/api/Api.js';
import libDownload from '@/lib/libDownload.js';

export default {
  name: 'ReportComponent',
  props: {
    report_type: {
      type: Number,
      required: true
    },
    use_pcs_key: {
      type: Boolean,
      default: true,
      required: false
    },
  },
  components: {
  },
  data() {
    return {
      moment,
      DataCount: 0,
      DataLimit: [10, 15, 25, 50, 100],
      Query: {
        type: this.report_type,
        start_date: '',
        end_date: '',
        limit: 10,
        page: 1,
        order_type: 'desc',
        order_field: 'date_time'
      },
      // Search: {
      //   start_date: this.report_type == 0 ? moment().startOf('month').format('YYYYMMDD') : this.report_type == 1 ? moment().startOf('day').format("YYYYMM") : moment().startOf('day').format("YYYY"),
      //   end_date: this.report_type == 0 ? moment().startOf('day').format('YYYYMMDD') : this.report_type == 1 ? moment().startOf('day').format("YYYYMM") : moment().startOf('day').format("YYYY")
      // },
      Search0: {
        start_date: moment().startOf('month').format('YYYYMMDD'),
        end_date: moment().startOf('day').format('YYYYMMDD'),
      },
      Search1: {
        start_date: moment().startOf('month').format('YYYYMM'),
        end_date: moment().startOf('month').format('YYYYMM')
      },
      Search2: {
        start_date: moment().startOf('year').format('YYYY'),
        end_date: moment().startOf('year').format('YYYY')
      },
      DataList: [],
      ShowPDFDialog: false,
      PDF: {
        'fileName': null,
        'data': null
      },
      disDate: (time) => {
        let returnDis = time.getTime() < new Date(this[`Search${this.report_type}`].start_date);
        if(this[`Search${this.report_type}`].start_date) {
          const sdate = moment(this[`Search${this.report_type}`].start_date, 'YYYYMMDD').format('YYYY-MM-DD');
          returnDis = time.getTime() < new Date(sdate);
        }
        return returnDis;
      },
      startCheck: computed(() => {
        let dis = true;
        if (this.report_type !== null && this.report_type !== undefined && this.report_type !== NaN) {
          dis = !this[`Search${this.report_type}`].start_date;
        }
          return dis;
      }),
    };
  },
  created() {
    //this.SearchClick();
  },
  watch: {
    'Search0.start_date': {
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          if(!newVal) {
            this[`Search${this.report_type}`].end_date = null;
          }
          if(newVal && this[`Search${this.report_type}`].end_date) {
            let sd = moment(this[`Search${this.report_type}`].start_date, 'YYYYMMDD').format('YYYY-MM-DD');
            let ed = moment(this[`Search${this.report_type}`].end_date, 'YYYYMMDD').format('YYYY-MM-DD');
            if(moment(sd).isAfter(ed)) {
              this[`Search${this.report_type}`].end_date = null;
            }
          }
        }
      },
    },
    'Search1.start_date': {
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          if(!newVal) {
            this[`Search${this.report_type}`].end_date = null;
          }
          if(newVal && this[`Search${this.report_type}`].end_date) {
            let sd = moment(this[`Search${this.report_type}`].start_date, 'YYYYMMDD').format('YYYY-MM-DD');
            let ed = moment(this[`Search${this.report_type}`].end_date, 'YYYYMMDD').format('YYYY-MM-DD');
            if(moment(sd).isAfter(ed)) {
              this[`Search${this.report_type}`].end_date = null;
            }
          }
        }
      },
    },
    'Search2.start_date': {
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          if(!newVal) {
            this[`Search${this.report_type}`].end_date = null;
          }
          if(newVal && this[`Search${this.report_type}`].end_date) {
            let sd = moment(this[`Search${this.report_type}`].start_date, 'YYYYMMDD').format('YYYY-MM-DD');
            let ed = moment(this[`Search${this.report_type}`].end_date, 'YYYYMMDD').format('YYYY-MM-DD');
            if(moment(sd).isAfter(ed)) {
              this[`Search${this.report_type}`].end_date = null;
            }
          }
        }
      },
    },
  },
  computed: {
    sortedData() {
      const data = [...this.tableData];
      if (this.sortProp) {
        data.sort((a, b) => {
          if (this.sortOrder === 'ascending') {
            return a[this.sortProp] > b[this.sortProp] ? 1 : -1;
          } else if (this.sortOrder === 'descending') {
            return a[this.sortProp] < b[this.sortProp] ? 1 : -1;
          }
          return 0;
        });
      }
      return data;
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = this.currentPage * this.pageSize;
      return this.sortedData.slice(start, end);
    },
    total() {
      return this.sortedData.length;
    }
  },
  methods: {
    SearchClick() {
      this.Query = Object.assign(this.Query, this[`Search${this.report_type}`]);
      this.Query.page = 1;
      this.getDataList();
    },
    getDataList() {
      const vm = this;
      vm.$loading();
      getCabinetReport(this.Query).then((response) => {
        var resp = response.data;
        if(resp.Success) {
          if(resp.Data){
            var temp_data = resp.Data.data;
            //tick to date
            temp_data.forEach(item => {
                const timestamp = item.date_time;
                const date = new Date(timestamp * 1000);
                item.date_time = date.toISOString();
                item.type = vm.report_type == 0 ? '日報': vm.report_type == 1 ? '月報' : '年報'
            });

            vm.DataList = temp_data;
            vm.DataCount = resp.Data.total_count;
          }
          else{
            vm.DataList = [];
            vm.DataCount = 0;
          }
          
        } else {
          vm.$message({ type: 'error', message: resp.Msg });
        }
      })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        }).finally(() => {
          vm.$loading().close();
        });
    },
    postDownload(row, needDownload){
      const vm = this;
      vm.$loading();

      var param = {
        "type": vm.report_type,
        "year": row.year,
        "use_pcs_key": vm.use_pcs_key
      };

      if(vm.report_type == 0){
        param['month'] = row.month;
        param['day'] = row.day;
      }
      else if(vm.report_type == 1){
        param['month'] = row.month;
      }

      postCabinetReportDonwload(param).then(response => {
        if(response.headers['content-type'] !== 'application/json'){
          let fileName = '晉瑜企業彰濱廠儲能系統';
          if(vm.report_type == 0){
            fileName += `-日報表_${row.name}.pdf`
          }
          else if(vm.report_type == 1){
            fileName += `-月報表_${row.name}.pdf`
          }
          else{
            fileName += `-年報表_${row.name}.pdf`
          }

          if(needDownload)
            libDownload(response, fileName);
          else{
            const blob = new Blob([response.data], { type: 'application/pdf' });
            vm.PDF.fileName = fileName
            vm.PDF.data = URL.createObjectURL(blob);
            vm.openPDF();
          }          

        } else {
          const text = new TextDecoder('utf-8').decode(new Uint8Array(response.data));
          const _response = JSON.parse(text);
          if(_response.Success){
            vm.$message({ type: 'success', message: _response.Msg });
          }
          else{
            vm.$message({ type: 'error', message: _response.Msg });
          }
        }
      }).catch(response => {
        vm.$message({ type: 'error', message: response.message });
      }).finally(() => {
        vm.$loading().close();
      });
    },
    PageOnChange(currentPage) {
      this.Query.page = currentPage;
      this.getDataList();
    },
    handleSortChange({ prop, order }) {
      if(prop !== null){
        this.Query.order_type = order === 'ascending' ? 'asc': 'desc';
        this.Query.order_field = prop;
        this.Query.page = 1;
        this.getDataList();
      }
    },
    handleSizeChange(size) {
      this.Query.limit = size;
      this.Query.page = 1;
      this.getDataList();
    },
    openPDF() {
      this.ShowPDFDialog = true;
    }
  },
};
</script>
<style scoped>
</style>