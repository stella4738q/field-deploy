<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <div class="d-flex align-items-center mb-3">
        <el-form :model="Form" ref="Form" :rules="FormRule" :inline="true" label-position="top" class="align-items-end">
          <el-form-item label="開始時間" prop="start_date">
            <el-date-picker v-model="Form.start_date" type="date" value-format="YYYYMMDD" />
          </el-form-item>
          
          <el-form-item label="結束時間" prop="end_date">
            <el-date-picker v-model="Form.end_date" type="date" value-format="YYYYMMDD" />
          </el-form-item>

          <el-form-item label="資料類型" prop="time_type">
            <el-select v-model="Form.time_type" placeholder="請選擇">
              <el-option :key="1" label="日" :value="0" />
              <el-option :key="2" label="月" :value="1" />
              <el-option :key="3" label="年" :value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="getData">
              <font-awesome-icon icon="search" />
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="DownloadClick">
              <font-awesome-icon icon="download" />
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <br/>
      <br/>
      <div id="myChart" ref="myChart" style="height: 600px;"></div>
    </div>
  </div>
  
</template>

<script>
import moment from 'moment';
import * as echarts from "echarts";
import { markRaw, ref } from 'vue';
import { postCabinetReportChart } from '@/api/Api.js';
import libDownload from '@/lib/libDownload.js';

export default {
  data() {
    return {
      Form: {
        time_type: 0,
        action_type: 0,
        start_date: null,
        end_date: null,
      },
      FormRule: {
        start_date: [{ required: true, message: '請選擇開始時間', trigger: 'change' }],
        end_date: [{ required: true, message: '請選擇結束時間', trigger: 'change' }],
      },
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
  methods: {
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
    drawChart_grouped(data) {
      const seriesData = data.values.map(_d => ({
        name: _d.name,
        data: _d.values,
        type: 'bar',
        barGap: '-80%',
        barCategoryGap: '20%',
        itemStyle: {
            opacity: 0.8 
        }
      }));

      let fontSize = window.innerWidth <= 768 ? 8 : 14;
      let width = window.innerWidth <= 768 ? '14%' : '5%';
      let grid_width = window.innerWidth <= 768 ? '80%' : '90%';

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          textStyle: {
              fontSize: fontSize
          }
        },
        legend: {
          width: '100%',
          data: data.values.map(_d => _d.name),
          right: 0,
          left: 'center',
          bottom: '0%',
          textStyle: {
              fontSize: fontSize
          }
        },
        grid: {
          width: grid_width,
          left: width,
          right: width,
          containLabel: false,
        },
        xAxis: {
            type: 'category',
            data: data.key,
            nameTextStyle: {
              fontSize: fontSize
            },
            axisLabel: {
                fontSize: fontSize
            }
        },
        yAxis: {
          name: 'kWh',
          type: 'value',
          boundaryGap: [0, 0.01],
          nameTextStyle: {
            fontSize: fontSize
          },
          axisLabel: {
              fontSize: fontSize
          }
        },
        dataZoom: [
            {
                type: 'inside',
                show: true,
                start: 0,
                end: 100,
                throttle: 0 
            }
        ],
        series: seriesData,
      };

      this.chartInstance.setOption(option, true);
    },
    getData() {
      this.$loading(); 
      this.Form.action_type = 0
      postCabinetReportChart(this.Form).then(response => {
        if (response.data.Success) {
          this.chartInstance.clear();
          this.drawChart_grouped(response.data.Data); 
        } else {
          this.$message({ type: 'error', message: response.data.Msg });
        }
      }).catch(error => {
        this.$message({ type: 'error', message: error.message });
      }).finally(() => {
        this.$loading().close(); 
      });
      
    },
    DownloadClick() {
      this.$loading(); 
      this.Form.action_type = 1;
      postCabinetReportChart(this.Form).then(response => {
        const contentType = response.headers['content-type'];
        if (contentType && (contentType.startsWith('application/') || contentType.startsWith('text/csv'))) {
          const timeticket = new Date().getTime(); 
          const fileName = `儲能系統報表_${timeticket}.csv`;
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
  },
};
</script>
