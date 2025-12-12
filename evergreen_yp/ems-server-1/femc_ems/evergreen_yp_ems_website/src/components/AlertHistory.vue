<template>
  <!-- 選擇bar -->
  <div class="d-flex justify-content-between align-items-center mt-3" style="">
    <el-form :model="Search" label-width="auto" inline>
      <el-form-item label="起始時間" prop="start_time">
        <el-date-picker v-model="Search.start_time" type="datetime" placeholder="請選擇日期時間"
          value-format="YYYYMMDDHHmmss"></el-date-picker>
      </el-form-item>
      <el-form-item label="結束時間" prop="end_time">
        <el-date-picker v-model="Search.end_time" type="datetime" placeholder="請選擇日期時間"
          value-format="YYYYMMDDHHmmss"></el-date-picker>
      </el-form-item>
      <el-form-item label="設備名稱" prop="equipment_id">
        <el-select v-model="Search.equipment_id" placeholder="請選擇設備" clearable>
          <el-option v-for="equipment in Option.Equipment" :key="equipment.id" :label="equipment.name" :value="equipment.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button @click="SearchClick" class="ms-2">
          <font-awesome-icon icon="search" />
        </el-button>
        <el-button @click="ExportClick" class="ms-2">
          <font-awesome-icon icon="file-arrow-down" />
        </el-button>
      </el-form-item>
    </el-form>
  </div>
  <el-table id="exTable" :data="DataList" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle" @sort-change="handleSortChange">
    <el-table-column width="180" align="center" label="告警時間" sortable prop="time">
      <template #default="scope">
        {{ scope.row.time ? moment(scope.row.time).format('YYYY-MM-DD HH:mm:ss') : '' }}
      </template>
    </el-table-column>
    <el-table-column width="100" align="center" label="等級" sortable prop="level"></el-table-column>
    <el-table-column width="180" align="center" label="設備名稱" sortable prop="equipment_id"></el-table-column>
    <el-table-column align="left" label="訊息" sortable prop="message"></el-table-column>
    <el-table-column width="150" align="center" label="解除時間" sortable prop="done_time">
      <template #default="scope">
        {{ scope.row.done_time != '-' ? moment(scope.row.done_time).format('YYYY-MM-DD HH:mm:ss') : '' }}
      </template>
    </el-table-column>
    <el-table-column width="130" align="center" label="持續時間" sortable prop="spend_time">
      <template #default="scope">
        {{ getDuration(scope.row.time, scope.row.done_time) }}
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
</template>

<script >
import moment from 'moment';
import { getAlertHistorical, getEquipments, getAlertHistoricalExport, getFields, getSystemDropdown } from '@/api/Api.js';
import libDownload from '@/lib/libDownload.js';

export default {
  components: {
  },
  data() {
    return {
      moment,
      DataCount: 0,
      DataLimit: [10, 15, 25, 50, 100],
      Query: {
        start_time: '',
        end_time: '',
        limit: 10,
        page: 1,
        order_type: 'desc',
        order_field: 'time',
        equipment_id: '',
      },
      Api: {
        getEquipments: {
          field_id: this.$store.getters.getField,
          parent_id: "",
          type: "",
          name: "",
          status: "",
          geo_location: "",
          code: "",
        }
      },
      Search: {
        // start_time: moment().add(-2, 'months').startOf('day').format("YYYYMMDDhhmmss") ,
        start_time: moment().startOf('day').format("YYYYMMDDHHmmss"),
        end_time: moment().endOf('day').format("YYYYMMDDHHmmss"),
        equipment_id: '',
      },
      Option: {
        Level: [
          { label: '全部', value: '' },
          { label: '事件', value: '1' },
          { label: '一級警報', value: '2' },
          { label: '二級警報', value: '3' },
          { label: '三級警報', value: '4' },
        ],
        Equipment: [
          { name: 'FemcStatus', id: 'FemcStatus' },
        ],
      },
      DataList: [],
      ApiResult: {
        getFields: [],
      }
    };
  },
  created() {
    this.SearchClick();
    this.getAlarmEquipmentDropdown();
  },
  watch: {
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
    getFields() {
      const vm = this;
      getFields()
        .then(response => {
          if (response.data.message == 'Success') {
            vm.ApiResult.getFields = response.data.data;
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {

        })
        .finally(() => { });
    },
    getDuration(begin, end) {
      var now = end != "-" ? moment(end) : moment();
      var beginTime = moment(begin);
      var duration = moment.duration(now.diff(beginTime));
      
      var seconds = duration.asSeconds();
      var minutes = duration.asMinutes();
      var hours = duration.asHours();

      if (seconds < 60) {
        return parseInt(seconds).toLocaleString() + "秒";
      } else if (seconds < 3600) {
        var displayMinutes = Math.floor(minutes);
        var displaySeconds = Math.floor(seconds % 60);
        return displayMinutes.toLocaleString() + "分 " + displaySeconds.toLocaleString() + "秒";
      } else {
        var displayHours = Math.floor(hours);
        var remainingMinutes = Math.floor((hours - displayHours) * 60);
        var remainingSeconds = Math.floor(seconds % 60);
        return displayHours.toLocaleString() + "時 " + remainingMinutes.toLocaleString() + "分 " + remainingSeconds.toLocaleString() + "秒";
      }
    },
    ExportClick() {
      const vm = this;
      getAlertHistoricalExport(vm.Query)
        .then((response) => {
          // debugger;
          libDownload(response, 'AlerList.csv');
        })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        }).finally(() => {
        });
    },
    SearchClick() {
      this.Query = Object.assign(this.Query, this.Search);
      this.Query.page = 1;
      this.getDataList();
    },
    getEquipment() {
      const vm = this;
      //vm.$loading();  vm.$loading().close();
      var a = this.$store.getters.getField;
      getEquipments(vm.Api.getEquipments)
        .then((response) => {
          this.Option.Equipment = this.Option.Equipment.concat(response.data.data);
        })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        }).finally(() => {
        });
    },
    getLevelName(typeVal) {
      if (typeVal) {
        return this.Option.Level.find((item) => { return item.value == typeVal })?.label;
      }
      return typeVal;
    },
    getDataList() {
      const vm = this;
      vm.$loading();
      getAlertHistorical(this.Query).then((response) => {
        if (response.data.message.toLowerCase() == "success") {
          vm.DataList = response.data.data.data;
          vm.DataCount = response.data.data.total_count;
        } else {
          vm.$message({ type: 'error', message: response.data.message });
        }
      })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        }).finally(() => {
          vm.$loading().close();
        });
    },
    PageOnChange(currentPage) {
      this.Query.page = currentPage;
      this.getDataList();
    },
    getAlarmEquipmentDropdown(){
      const vm = this;
      getSystemDropdown({'dropdown_type': 'alarm_equipments'})
        .then((response) => {
          this.Option.Equipment = this.Option.Equipment.concat(response.data.data);
        })
        .catch(() => {
          vm.$message({ type: 'error', message: "Error" });
        }).finally(() => {
        });
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
  },
};
</script>
<style scoped>
</style>