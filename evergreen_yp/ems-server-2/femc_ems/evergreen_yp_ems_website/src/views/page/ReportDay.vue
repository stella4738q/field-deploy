<template>
  <div class="p-5">
    <h1>營運日報表</h1>
    <div class="d-flex align-items-center mb-3">
      <el-form :model="Search" ref="Search" :rules="SearchRule" :inline="true" label-width="80px">
        <el-form-item label="時間" prop="date">
          <el-date-picker v-model="Form.date" type="daterange" range-separator="To" />
        </el-form-item>
      </el-form>
      <el-form-item>
        <button class="btn btn-primary btn-sm" @click="SearchClick"><font-awesome-icon icon="search" /></button>
      </el-form-item>
    </div>



    <div class="row">
      <div class="col-8">
        <div class="row  text-start ps-3 pe-3 mb-2"><!-- 總覽 -->
          <div class="col border rounded border-success me-2">
            <div class="border-bottom border-success p-0"> 充電度數 </div>
            <div class="p-0 text-end fw-bold">
              {{ TotalChargeDegree }}
            </div>
          </div>
          <div class="col border rounded border-success me-2">
            <div class="border-bottom border-success p-0"> 放電度數 </div>
            <div class="p-0 text-end fw-bold">
              {{ TotalDishargeDegree }}
            </div>
          </div>
          <div class="col border rounded border-success me-2">
            <div class="border-bottom border-success p-0"> 充電費用 </div>
            <div class="p-0 text-end fw-bold">
              {{ TotalChargeFee }}
            </div>
          </div>
          <div class="col border rounded border-success me-2">
            <div class="border-bottom border-success p-0"> 放電收入 </div>
            <div class="p-0 text-end fw-bold">
              {{ TotalDischargeFee }}
            </div>
          </div>
          <div class="col border rounded border-success me-2">
            <div class="border-bottom border-success p-0"> 總收益 </div>
            <div class="p-0 text-end fw-bold">
              {{ TotalRevenue }}
            </div>
          </div>
        </div>
        <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3"
          header-cell-class-name="tableHeaderStyle">
          <el-table-column label="日期" prop="date" align="center">
            <template #default="scope">
              {{ moment(scope.row.date).format("YYYY-MM-DD HH:mm:ss") }}
            </template>
          </el-table-column>
          <el-table-column label="持續時間" prop="duration" align="center">

          </el-table-column>
          <el-table-column label="儲/放電" prop="action" align="center"></el-table-column>
          <!-- <el-table-column label="SOC" prop="soc" align="center"></el-table-column> -->
          <el-table-column label="換算度數" prop="degree" align="center">
            <template #default="scope">
              {{ scope.row.degree?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="收益" prop="total_amount" align="center">
            <template #default="scope">
              {{ scope.row.total_amount?.toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
        <div class="d-flex justify-content-end">
          <el-pagination layout="prev, pager, next" v-model:currentPage="PageController.pageInd"
            :page-size="PageController.countPerPage" :total="PageController.DataSource.length"
            @current-change="(ind) => { PageChanged(ind, PageController) }" />
        </div>
      </div>
      <div class="col-4">
        <div id="ReportChartDay" style="height:400px"></div>
      </div>
    </div>

  </div>
</template>
<script>

import {
  getSystemElectricOperationReport
} from '@/api/Api.js';
import moment from 'moment';
import * as echarts from "echarts";
import reportDataData from '@/JSON/ReportDay.json';
let ReportChartDay = null;

export default {
  components: {
  },
  data() {
    return {
      reportDataData,
      moment,
      formLabelWidth: '100px',
      Form: {
        date: [],
      },
      FormRule: {
        date: [{ required: true, message: ' ', trigger: 'blur' }],
      },
      PageController: {
        pageInd: 1,
        countPerPage: 10,
        total: 0,
        CurrentData: [],
        DataSource: [],
      },
      PlotData: {
        charge: [],
        revenue: [],
        discharge: [],
        date: [],
      }
    };
  },
  computed: {
    TotalChargeDegree() {
      try {
        if (this.PageController.DataSource.length) {
          return parseFloat((
            this.PageController.DataSource.filter(x => { return x.action == 'charge' }).map(x => {
              return x.degree;
            }).reduce((accumulator, currentValue) => {
              return accumulator + currentValue
            }, 0)
          ).toFixed(2)).toLocaleString()
        }
      } catch { }
      return 0;
    },
    TotalDishargeDegree() {
      try {
        if (this.PageController.DataSource.length) {
          return parseFloat((
            this.PageController.DataSource.filter(x => { return x.action == 'discharge' }).map(x => {
              return x.degree;
            }).reduce((accumulator, currentValue) => {
              return accumulator + currentValue
            }, 0)
          ).toFixed(2)).toLocaleString();
        }
      } catch { }
      return 0;
    },
    TotalChargeFee() {
      try {
        if (this.PlotData.charge.length) {
          return parseFloat((
            this.PlotData.charge.reduce((accumulator, currentValue) => {
              return accumulator + currentValue
            }, 0)
          ).toFixed(0)).toLocaleString();
        }
      } catch { }
      return 0;

    },
    TotalDischargeFee() {
      try {
        if (this.PlotData.discharge.length) {
          return parseFloat((
            this.PlotData.discharge.reduce((accumulator, currentValue) => {
              return accumulator + currentValue
            }, 0)
          ).toFixed(0)).toLocaleString();
        }
      } catch { }
      return 0;
    },
    TotalRevenue() {
      try {
        if (this.PlotData.revenue.length) {
          return parseFloat((
            this.PlotData.revenue.reduce((accumulator, currentValue) => {
              return accumulator + currentValue
            }, 0)
          ).toFixed(0)).toLocaleString()
        }
      } catch { }
      return 0;
    },
    ApiRequest: function () {
      return {
        getSystemElectricOperationReport: {
          start_date: moment(this.Form.date[0]).format("YYYYMMDD"),
          end_date: moment(this.Form.date[1]).format("YYYYMMDD"),
          category: "0",
        }
      }
    },

  },
  mounted() {
  },
  beforeUnmount() {
    if (ReportChartDay) ReportChartDay.dispose();
    ReportChartDay = null;
  },
  created() {
  },
  watch: {
  },
  methods: {
    getData() {
      const vm = this;
      vm.$loading();
    

      getSystemElectricOperationReport(vm.ApiRequest.getSystemElectricOperationReport)
        .then(resopnse => {
          if (resopnse.data.message == "Success") {
            vm.PageController.DataSource = resopnse.data.data[0].raw_data;
            vm.PlotData = resopnse.data.data[0].plot_data;
            vm.PageChanged(1, vm.PageController);
            vm.ChartIni();
          } else {
            vm.$message({ type: 'error', message: resopnse.data.message });
          }
        }).catch(resopnse => {
          vm.$message({ type: 'error', message: resopnse.message });
        }).finally(() => {
          vm.$loading().close();
        });
    },
    SearchClick() {
      const vm = this;
      vm.getData();
    },
    PageChanged(ind, Controller) {
      Controller.pageInd = ind;
      var sliceBegin = (Controller.pageInd - 1) * Controller.countPerPage;
      var sliceEnd = (Controller.pageInd) * Controller.countPerPage;
      Controller.CurrentData = Controller.DataSource.slice(sliceBegin, sliceEnd);
    },

    ChartIni() {
      var option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          }
        },
        legend: {
          data: ['儲電', '放電', '收益']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: this.PlotData.date
          }
        ],
        yAxis: [
          {
            type: 'value',
            axisTick: {
              show: false
            },

          }
        ],
        series: [
          {
            name: '收益',
            type: 'line',
            label: {
              show: false,
              position: 'inside'
            },
            data: this.PlotData.revenue
          },
          {
            name: '放電',
            type: 'bar',
            stack: 'Total',
            label: {
              show: false
            },
            data: this.PlotData.discharge
          },
          {
            name: '儲電',
            type: 'bar',
            stack: 'Total',
            label: {
              show: false,
            },
            data: this.PlotData.charge
          }
        ]
      };
      this.$nextTick(function () {
        if (ReportChartDay == null) {
          ReportChartDay = echarts.init(document.getElementById("ReportChartDay"));
        }
        ReportChartDay.setOption(option);
      });
    },
  },
};
</script>