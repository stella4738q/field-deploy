<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <h1 class="mb-2">太陽能系統報表下載</h1>
      <div class="d-flex align-items-center mb-3">
        <el-form :model="Form" ref="Form" :rules="FormRule" :inline="true" label-position="top" class="align-items-end">
          <el-form-item label="開始時間" prop="start_date">
            <el-date-picker v-model="Form.start_date" type="date" value-format="YYYYMMDD" />
          </el-form-item>
          
          <el-form-item label="結束時間" prop="end_date">
            <el-date-picker v-model="Form.end_date" type="date" value-format="YYYYMMDD" :disabled="isEndDateDisabled" />
          </el-form-item>

          <el-form-item label="資料類型" prop="time_type" :rules="[{ required: true, message: '請選擇資料類型', trigger: 'change' }]">
            <el-select v-model="Form.time_type" placeholder="請選擇" @change="handleTimeTypeChange">
              <el-option :key="0" label="時" :value="0" />
              <el-option :key="1" label="日" :value="1" />
              <el-option :key="2" label="月" :value="2" />
              <el-option :key="3" label="年" :value="3" />
              <el-option :key="4" label="原始數據圖表" :value="4" />
              <el-option :key="5" label="區間統計資訊" :value="5" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="聚合方式" prop="type" :rules="[{ required: true, message: '請選擇聚合方式', trigger: 'change' }]">
            <el-select v-model="Form.type" placeholder="請選擇" :disabled="isAggregationDisabled">
              <el-option :key="0" label="總和" :value="0" />
              <el-option :key="1" label="依設備" :value="1" />
              <el-option :key="2" label="依設備子項" :value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="getData">
              <font-awesome-icon icon="search" />
            </el-button>
            <el-button type="primary" class="ms-2" @click="DownloadClick">
              <font-awesome-icon icon="download" />
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <br/>
      <br/>

      <!-- stats mode (time_type=5): show table -->
      <div v-if="isStatsMode">
        <el-table :data="tableData" size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle" style="width: 100%">
          <!-- 展開列：顯示 inverter_kwh 明細 -->
          <el-table-column type="expand">
            <template #default="scope">
              <el-table :data="(scope.row?.inverter_kwh || [])" size="small" stripe border class="rounded-3" header-cell-class-name="subHeaderStyle">
                <el-table-column label="設備ID" prop="equipment_id" min-width="140" />
                <el-table-column label="發電量(kWh)" min-width="140">
                  <template #default="s">
                    {{ formatNumber(s.row.kwh) }}
                  </template>
                </el-table-column>
              </el-table>
            </template>
          </el-table-column>

          <!-- 區間/日期名稱 -->
          <el-table-column label="日期" prop="data_time" min-width="160" />

          <!-- 指標欄位 -->
          <el-table-column label="總發電量 (kWh)" min-width="160">
            <template #default="scope">
              {{ formatNumber(scope.row?.total_kwh ?? 0) }}
            </template>
          </el-table-column>

          <el-table-column label="日照量 (kWh/m²)" min-width="160">
            <template #default="scope">
              {{ (scope.row?.irr_kwh_m2 ?? 0).toFixed(4) }}
            </template>
          </el-table-column>

          <el-table-column label="涵蓋時數 (h)" min-width="140">
            <template #default="scope">
              {{ (scope.row?.hours_in_window ?? 0).toFixed(3) }}
            </template>
          </el-table-column>

          <el-table-column label="建置量 (kW)" min-width="140">
            <template #default="scope">
              {{ (scope.row?.capacity_kw ?? 0).toFixed(3) }}
            </template>
          </el-table-column>

          <el-table-column label="IRR (%)" min-width="120">
            <template #default="scope">
              {{ scope.row?.irr_pct == null ? '-' : (scope.row.irr_pct).toFixed(2) }}
            </template>
          </el-table-column>

          <el-table-column label="PR (%)" min-width="120">
            <template #default="scope">
              {{ scope.row?.pr_pct == null ? '-' : (scope.row.pr_pct).toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      <!-- chart mode: 0/1/2/3/4 -->
      <div v-else>
        <div id="myChart" ref="myChart" style="height: 600px;"></div>
      </div>

    </div>
  </div>
  
</template>

<script>
import moment from 'moment';
import * as echarts from "echarts";
import { markRaw, ref } from 'vue';
import { getSunReport, getSunReportDownload } from '@/api/Api.js';
import libDownload from "@/lib/libDownload.js";

export default {
  data() {
    return {
      Form: {
        action: null,
        start_date: null,
        end_date: null,
        time_type: 1,
        type: 0,
      },
      FormRule: {
        start_date: [{ required: true, message: '請選擇開始時間', trigger: 'change' }],
        end_date: [{ required: true, message: '請選擇結束時間', trigger: 'change' }],
      },
      chartInstance: ref(null),
      tableData: [],
    }
  },
  mounted() {
    this.initChart();
    this.initializeForm();
    window.addEventListener('resize', this.resizeChart);
    window.onresize = () => {
        return (() => {
          this.resizeChart();
      })();
    };
  },
  beforeUnmount() {
    this.chartInstance.dispose(); 
    window.removeEventListener('resize', this.resizeChart);
  },
  computed: {
    isAggregationDisabled() {
      return this.Form.time_type === 4 || this.Form.time_type === 5;
    },
    isEndDateDisabled() {
      return this.Form.time_type === 4;
    },
    isStatsMode() {
      return this.Form.time_type === 5;
    }
  },
  methods: {
    handleTimeTypeChange() {
      if (this.Form.time_type === 4) {
        this.Form.type = 1;
      } else if (this.Form.time_type === 5) {
        this.Form.type = 0;
      }
    },
    initChart() {
      this.chartInstance = markRaw(echarts.init(this.$refs.myChart));
    },
    initializeForm() {
      const today = moment();
      this.Form.start_date = today.startOf('day').format("YYYYMMDD");
      this.Form.end_date = today.endOf('day').format("YYYYMMDD");
    },
    resizeChart() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },
    drawChart_simple(data) {

      let fontSize = window.innerWidth <= 768 ? 8 : 14;
      const sideWidth = window.innerWidth <= 768 ? '14%' : '5%';
      const gridWidth = window.innerWidth <= 768 ? '80%' : '90%';
      
      const categories = Array.isArray(data?.key) ? data.key : [];
      const barSeries = {
        name: '發電量', 
        type: 'bar',
        data: Array.isArray(data?.values) ? data.values : [],
      };

      let y2Series = {
        name: '等效發電小時',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        showSymbol: true,
        symbolSize: 6,
        lineStyle: { width: 2 },
        z: 5,
        connectNulls: true,
        data: Array.isArray(data?.y2_values) ? data.y2_values : [],
      };

      const series = [barSeries];
      if (Array.isArray(data?.y2_values) && data.y2_values.length) {
        series.push(y2Series);
      }

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          formatter(params) {
            const lines = params.map(p => {
            const num = Number(p.value);
            const isNum = Number.isFinite(num);

            if (p.seriesName && (p.seriesName.includes('等效發電小時') || p.seriesName.includes('等效小時'))) {
              const out = isNum ? num.toLocaleString() : '-';
              return `${p.marker}${p.seriesName}: ${out} h`;
            }

            // 預設：kWh
            const out = isNum ? num.toLocaleString() : '-';
            return `${p.marker}${p.seriesName}: ${out} kWh`;
          });

          return `${params[0].name}<br/>` + lines.join('<br/>');
          },
          textStyle: { fontSize }
        },
        grid: {
          bottom: '15%',
          width: gridWidth,
          left: sideWidth,
          right: sideWidth,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: { fontSize },
          nameTextStyle: { fontSize }
        },
        yAxis: [
          {
            type: 'value',
            name: '總發電量(kWh)',
            min: 0,
            axisLabel: {
              fontSize,
              formatter: v => Number(v).toLocaleString()
            },
            nameTextStyle: { fontSize }
          },
          {
            type: 'value',
            name: '等效發電小時',
            min: 0,
            axisLabel: {
              fontSize,
              formatter:v => `${v} h`
            },
            nameTextStyle: { fontSize }
          }
        ],
        dataZoom: [{ type: 'inside', show: true, start: 0, end: 100, throttle: 0 }],
        series: series,
        animation: true
      };
      this.chartInstance.setOption(option, true);
    },
    drawChart_grouped(data) {
      const fontSize  = window.innerWidth <= 768 ? 8  : 14;
      const sideWidth = window.innerWidth <= 768 ? '14%' : '5%';
      const gridWidth = window.innerWidth <= 768 ? '80%' : '90%';

      const categories = Array.isArray(data?.key) ? data.key : [];
      const barSeries = (data?.values || []).map(inv => ({
        name: inv.name,
        type: 'bar',
        data: Array.isArray(inv.data) ? inv.data : [],
        emphasis: { focus: 'series' }
      }));
      let y2Series = [];
      if (Array.isArray(data?.y2_values) && data.y2_values.length) {
        const first = data.y2_values[0];
        y2Series = data.y2_values.map(y2 => ({
          name: y2.name + '等效發電小時',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          showSymbol: true,
          symbolSize: 6,
          lineStyle: { width: 2 },
          z: 5,
          connectNulls: true,
          data: Array.isArray(y2.data) ? y2.data : []
        }));
      }

      const legendData = [
        ...barSeries.map(s => s.name),
        ...y2Series.map(s => s.name)
      ];

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          formatter(params) {
            const lines = params.map(p => {
            const num = Number(p.value);
            const isNum = Number.isFinite(num);

            if (p.seriesName && (p.seriesName.includes('等效發電小時') || p.seriesName.includes('等效小時'))) {
              const out = isNum ? num.toLocaleString() : '-';
              return `${p.marker}${p.seriesName}: ${out} h`;
            }

            // 預設：kWh
            const out = isNum ? num.toLocaleString() : '-';
            return `${p.marker}${p.seriesName}: ${out} kWh`;
          });

          return `${params[0].name}<br/>` + lines.join('<br/>');
          },
          textStyle: { fontSize }
        },
        legend: {
          data: legendData,
          left: 'center',
          bottom: '0%',
          textStyle: { fontSize }
        },
        grid: {
          bottom: '15%',
          width: gridWidth,
          left: sideWidth,
          right: sideWidth,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: { fontSize },
          nameTextStyle: { fontSize }
        },
        yAxis: [
          {
            type: 'value',
            name: '總發電量(kWh)',
            min: 0,
            axisLabel: {
              fontSize,
              formatter: v => Number(v).toLocaleString()
            },
            nameTextStyle: { fontSize }
          },
          {
            type: 'value',
            name: '等效發電小時',
            min: 0,
            axisLabel: {
              fontSize,
              formatter:v => `${v} h`
            },
            nameTextStyle: { fontSize }
          }
        ],
        dataZoom: [{ type: 'inside', show: true, start: 0, end: 100, throttle: 0 }],
        series: [...barSeries, ...y2Series],
        animation: true
      };

      this.chartInstance.setOption(option, true);
    },
    drawLineChart(data) {
      let fontSize = window.innerWidth <= 768 ? 8 : 14;
      let width = window.innerWidth <= 768 ? '10%' : '5%';
      let grid_width = window.innerWidth <= 768 ? '80%' : '90%';

      const option = {
        legend: {
          data: ['DCU_1'],
          orient: 'horizontal',
          left: 'center',
          bottom: '0%',
          textStyle: {
            color: '#333',
            fontSize: fontSize
          }
        },
        grid: {
          width: grid_width,
          top: '10%',
          bottom: '20%',
          left: width,
          right: width,
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const time = moment(params[0].axisValue).format("YYYY-MM-DD HH:mm:ss");
            let tooltipContent = `<div>${time}</div>`;
            params.forEach(item => {
              tooltipContent += `
                <div>
                  <span style="color:${item.color}">●</span> ${item.seriesName}: ${this.formatNumber(item.data[1])}
                </div>`;
            });
            return tooltipContent;
          }
        },
        xAxis: {
          type: 'time',
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: {
            formatter: function (value) {
              return moment(value).format("HH:mm");
            }
          }
        },
        yAxis: [
          {
            type: 'value',
            max: function (value) {
              return (value.max + 10).toFixed(0);
            },
            min: 0,
            scale: true,
            position: 'left',
            name: '功率 (kW)',
          }
        ],
        series: [
          {
            name: 'DCU_1',
            yAxisIndex: 0,
            data: data['dcu_1'],
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            showSymbol: false,
          }
        ],
        dataZoom: [
          {
            type: "inside",
            start: this.dataZoomStart,
            end: this.dataZoomEnd,
            throttle: 0
          }
        ]
      };
      this.chartInstance.setOption(option, true);
    },
    getData() {
      this.$loading(); 
      this.Form.action=0;
      getSunReport(this.Form).then(response => {
        if (response.data.message === "Success") {
          if(this.Form.time_type == 5){
            this.tableData = response.data.data;
          }
          else if(this.Form.time_type == 4){
            this.tableData = null;
            this.chartInstance.clear();
            this.drawLineChart(response.data.data);
          }
          else{
            this.tableData = null;
            if(this.Form.type == 0){
              this.chartInstance.clear();
              this.drawChart_simple(response.data.data); 
            }
            else{
              this.chartInstance.clear();
              this.drawChart_grouped(response.data.data);
            }
          }
        } else {
          this.$message({ type: 'error', message: response.data.message });
        }
      }).catch(error => {
        this.$message({ type: 'error', message: error.message });
      }).finally(() => {
        this.$loading().close(); 
      });
    },
    DownloadClick() {
      this.$loading(); 
      this.Form.action = 1;
      getSunReportDownload(this.Form).then(response => {
        const contentType = response.headers['content-type'];
        if (contentType && (contentType.startsWith('application/') || contentType.startsWith('text/csv'))) {
          const timeticket = new Date().getTime(); 
          const fileName = `太陽能報表_${timeticket}.csv`;
          libDownload(response, fileName);
        } else {
          this.$message({ type: 'error', message: response.data.message });
        }
      }).catch(error => {
        this.$message({ type: 'error', message: error.message });
      }).finally(() => {
        this.$loading().close(); 
      });
    },
    formatNumber(value) {
      if(value === 'NaN' || Number.isNaN(value) || value === null || value === undefined){
        return 0;
      }
      return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
  },
};
</script>

<style>
.tipsText{
  font-size:14px;
  color:#666;
  font-weight:400;
  line-height:1;
  display: block;
}
.tipBlock {
  display:block;
  margin-top: 2px;
}
.tipBlockT {
  font-size:14px;
  color:#666;
  font-weight:400;
  margin-left:4px;
}
.tipBlockV {
  font-size:14px;
  color:#666;
  font-weight:900;
  float:right;
  margin-left:20px;
}
.PCSsymbol {
  display:inline-block;
  /* margin-right:4px; */
  border-radius:10px;
  width:10px;
  height:10px;
  background-color:#5470c6;
}
.SOCsymbol {
  display:inline-block;
  /* margin-right:4px; */
  width:10px;
  height:10px;
  background-color:#91cc75;
}
.TMPsymbol {
  display:inline-block;
  /* margin-right:4px; */
  /* background-color:purple; */
  width:0;
  height:0;
  border-width:0 5px 10px ;
  border-style:solid;
  border-color:transparent transparent purple;
}
</style>
