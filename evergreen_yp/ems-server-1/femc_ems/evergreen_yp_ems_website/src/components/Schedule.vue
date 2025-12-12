<template>
  <div>
    <!-- <h1 v-if="Editable">充放電排程</h1> -->
    <!-- 系統設定 -->
    <div class="mb-2 row" v-if="Editable">
      <p style="font-style: italic;">(裝置容量 * ( 儲電上限 - 電池保護電力 ) - 保留緊急供電) / 裝置容量 = 可放電總合百分比</p>
      <div class="col fs-5">
        <el-row :gutter="8">
          <!-- ============================================= -->
          <el-col :xs="24" :sm="8" :md="6" :lg="4">
            <b>離峰儲電：</b>
            {{ Setting.Schedule?.charge_type == 1 ? '是' : '否' }}
          </el-col>
          <!-- ============================================= -->
          <el-col :xs="24" :sm="8" :md="6" :lg="4">
            <b class="">裝置總容量：</b>
            {{ Setting?.Schedule?.total_capacity }} MW
          </el-col>
          <!-- ============================================= -->
          <el-col :xs="24" :sm="8" :md="6" :lg="4">
            <b class="">儲電 SOC 上限：</b>
          {{ Setting?.Schedule?.upper_soc }} %
          </el-col>
          <!-- ============================================= -->
          <el-col :xs="24" :sm="8" :md="6" :lg="4">
            <b class="">電池保護電力：</b>
          {{ Setting?.Schedule?.protect_power }} %
          </el-col>
          <!-- ============================================= -->
          <el-col :xs="24" :sm="8" :md="6" :lg="5">
            <b class="">可放電總合：</b>
          {{ Setting?.Schedule?.total_discharge }} %
          </el-col>
          <!-- ============================================= -->
        </el-row>
        <!-- ============================================= -->
      </div>
      <div class="col-12 text-end">
        <el-tooltip :content="Setting?.ElectSetting?.Render" raw-content effect="light"><el-button>?</el-button></el-tooltip>
        <el-button @click="Clear"><font-awesome-icon icon="trash" /></el-button>
        <el-button @click="Add"><font-awesome-icon icon="plus" /></el-button>
      </div>
    </div>
    <!-- ============================================= -->
    <div style="overflow-x: auto;">
    <div class="scheduleCompoment">
      <div class="text-center mt-4 mb-2">
        <span class="text-secondary me-3" v-if="!Editable"> 充電模式: {{this.chargeType}}</span>
        <br/>
        <span class="text-danger me-3"> <font-awesome-icon icon="square" />尖峰</span>
        <span class="text-primary me-3"> <font-awesome-icon icon="square" />半尖峰</span>
        <span class="text-success"> <font-awesome-icon icon="square" />離峰</span>
        <span class="ms-3 p-2 ddd"><font-awesome-icon icon="square" />抑低(kW)</span>
      </div>
      <!-- 排程 -->
      <div>
        <!-- 24小時 -->
        <div class="row text-center" style="height: 30px;">
          <div class="col-1 borderHead"></div>
          <div class="col">
            <div class="row">
              <div class="col text-center borderHead">00</div>
              <div class="col text-center borderHead">01</div>
              <div class="col text-center borderHead">02</div>
              <div class="col text-center borderHead">03</div>
              <div class="col text-center borderHead">04</div>
              <div class="col text-center borderHead">05</div>
              <div class="col text-center borderHead">06</div>
              <div class="col text-center borderHead">07</div>
              <div class="col text-center borderHead">08</div>
              <div class="col text-center borderHead">09</div>
              <div class="col text-center borderHead">10</div>
              <div class="col text-center borderHead">11</div>
              <div class="col text-center borderHead">12</div>
              <div class="col text-center borderHead">13</div>
              <div class="col text-center borderHead">14</div>
              <div class="col text-center borderHead">15</div>
              <div class="col text-center borderHead">16</div>
              <div class="col text-center borderHead">17</div>
              <div class="col text-center borderHead">18</div>
              <div class="col text-center borderHead">19</div>
              <div class="col text-center borderHead">20</div>
              <div class="col text-center borderHead">21</div>
              <div class="col text-center borderHead">22</div>
              <div class="col text-center borderHead">23</div>
            </div>
          </div>
        </div>
        <!-- 星期一的color  -->
        <div class="row color-row">
          <div class="col-1 p-0 border"></div>
          <div class="col p-0 border">
            <div class="row">
              <div v-for="time in hourData" :class="'col p-0 ' + getColorBar(1, time)" :key="time"></div>
            </div>
          </div>
        </div>
        <!-- 星期一的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(1)">星期一</div>
          <div class="col p-0" style="position: relative;">
            <div class="row">
              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 1 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
            </div>

          </div>
        </div>

        <!-- 星期二的color  -->
        <div class="row color-row">
          <div class="col-1 p-0 border"></div>
          <div class="col p-0 border">
            <div class="row">
              <div v-for="time in hourData" :class="'col ' + getColorBar(2, time)" :key="time"></div>
            </div>
          </div>

        </div>
        <!-- 星期二的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(2)">星期二</div>
          <div class="col" style="position: relative;">
            <div class="row">

              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 2 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->

              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
            </div>
          </div>
        </div>

        <!-- 星期三的color  -->
        <div class="row color-row">
          <div class="col-1 border"></div>
          <div class="col border">
            <div class="row">
              <div v-for="time in hourData" :class="'col ' + getColorBar(3, time)" :key="time"></div>
            </div>
          </div>

        </div>
        <!-- 星期三的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(3)">星期三</div>
          <div class="col" style="position: relative;">
            <div class="row">
              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 3 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->

              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>

            </div>

          </div>
        </div>


        <!-- 星期四的color  -->
        <div class="row color-row">
          <div class="col-1 border"></div>
          <div class="col border">
            <div class="row">
              <div v-for="time in hourData" :class="'col ' + getColorBar(4, time)" :key="time"></div>
            </div>
          </div>

        </div>
        <!-- 星期四的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(4)">星期四</div>
          <div class="col" style="position: relative;">
            <div class="row">
              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 4 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->

              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
            </div>
          </div>
        </div>



        <!-- 星期五的color  -->
        <div class="row color-row">
          <div class="col-1 border"></div>
          <div class="col border">
            <div class="row">
              <div v-for="time in hourData" :class="'col ' + getColorBar(5, time)" :key="time"></div>
            </div>
          </div>
        </div>
        <!-- 星期五的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(5)">星期五</div>
          <div class="col" style="position: relative;">
            <div class="row">
              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 5 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->

              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>

            </div>

          </div>
        </div>

        <!-- 星期六的color  -->
        <div class="row color-row">
          <div class="col-1 border"></div>
          <div class="col border">
            <div class="row">
              <div v-for="time in hourData" :class="'col ' + getColorBar(6, time)" :key="time"></div>
            </div>
          </div>

        </div>
        <!-- 星期六的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(6)">星期六</div>
          <div class="col" style="position: relative;">
            <div class="row">
              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 6 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->

              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>

            </div>

          </div>
        </div>

        <!-- 星期日的color  -->
        <div class="row color-row">
          <div class="col-1 border"></div>
          <div class="col border">
            <div class="row">
              <div v-for="time in hourData" :class="'col ' + getColorBar(7, time)" :key="time"></div>
            </div>
          </div>

        </div>
        <!-- 星期日的排程 -->
        <div class="row text-center" style="position: relative;">
          <div :class="'col-1 border' + getWeekClass(0)">星期日/離峰日</div>
          <div class="col" style="position: relative;">
            <div class="row">
              <!-- =========================================== -->
              <span v-for=" item in Setting.Schedule?.schedule?.filter(x => { return x.week == 7 })" :key="item.id"
                :class="item.type == 3 ? 'SchedultItem2' : this.Editable ? 'SchedultItem cursor-pointer' : 'SchedultItem'"
                @click="Edit(item)" :style="getPosition(item)">
                <!-- ---------------------------------------------- -->
                <font-awesome-icon icon="battery-full" v-if="item.type == 0" />
                <font-awesome-icon icon="bolt" v-if="item.type == 1" />
                <span v-if="item.type != 3">{{ item.soc }}%{{ item.kw? `(${item.kw} kW)` : '' }}</span>
                <!-- <img src="@/assets/down.png" style="width:25px;" v-if="item.type == 3"> -->
                <span v-if="item.type == 3">{{ item.soc }}</span>
                <!-- ---------------------------------------------- -->
              </span>
              <!-- =========================================== -->

              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>
              <div class="col border"></div>

            </div>

          </div>
        </div>
      </div>
      <div v-if="operationMode != 1" class="fw-bold text-center mt-2 mb-2 ">逆送電偵測 > 手動充放電 > 抑低容量 > 超約控制 > 排程充放電 > 自動離峰充電</div>
      <div v-if="operationMode == 1" class="fw-bold text-center mt-2 mb-2 ">逆送電偵測 > 超約控制 > 遠端手動控制 > 抑低容量 > 排程充放電 > 自動離峰充電</div>
    </div>
  </div>
    <!-- ============================================= -->
    <el-dialog title="儲放電設定" center v-model="Dialog" :close-on-click-modal="false" :show-close="false" width="400px">
      <!-- <pre>{{ Form }}</pre> -->
      <el-form :model="Form" :rules="FormRule" ref="Form" label-width="auto">
        <el-form-item label="每週" prop="week">
          <el-select v-model="Form.week" placeholder="請選擇">
            <el-option label="星期一" value="1" />
            <el-option label="星期二" value="2" />
            <el-option label="星期三" value="3" />
            <el-option label="星期四" value="4" />
            <el-option label="星期五" value="5" />
            <el-option label="星期六" value="6" />
            <el-option label="星期日" value="7" />
          </el-select>
        </el-form-item>
        <el-form-item label="開始時間" prop="start_time">
          <el-time-picker v-model="Form.start_time" placeholder="Please input" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="結束時間" prop="end_time">
          <el-time-picker v-model="Form.end_time" placeholder="Please input" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="儲/放電" prop="type">
          <el-radio-group v-model="Form.type">
            <el-radio-button :label="1">放電</el-radio-button>
            <el-radio-button :label="0" :disabled="Setting.Schedule?.charge_type == 1">充電</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="目標SOC(%)" prop="soc">
          <el-input-number type="number" v-model.number="Form.soc" placeholder="" :min="Setting?.Schedule?.protect_power"
            :max="Setting?.Schedule?.upper_soc">
          </el-input-number>
        </el-form-item>
        <el-form-item label="固定功率(kW)" prop="kw">
          <el-input-number v-model="Form.kw" placeholder="" @change="kwOnChange" :min="0" :max="1045" :step="1">
          </el-input-number>
        </el-form-item>
      </el-form>
      <div class="dialog-footer mt-5 text-center">
        <el-button @click="Dialog = false">
          <font-awesome-icon icon="circle-xmark" />
        </el-button>
        <el-popconfirm title="確定刪除" confirm-button-text="確定" cancel-button-text="取消" @confirm="Delete" v-if="Form['_id']">
          <template #reference>
            <el-button>
              <font-awesome-icon icon="trash" />
            </el-button>
          </template>
        </el-popconfirm>

        <el-button type="primary" @click="Submit" :disabled="dialogSubmit">
          <font-awesome-icon icon="circle-check" />
        </el-button>
      </div>
    </el-dialog>

  </div>
</template>
<script>

import {
  getSystemStorageSetting, getSystemElectricSetting, getPowerSchedule,
  getScheduleDetail, postScheduleDetail, delScheduleDetail,
} from '@/api/Api.js';

import moment from 'moment';

export default {
  name: 'Schedule',
  props: {
    Editable: {
      type: Boolean,
      default: true
    },
    SOC: {
      type: Number,
      default: 0
    },
    dataId: {
      type: String,
      default: null,
    },
    chargeType: {
      type: String,
      default: null,
    },
    operationMode: {
      type: Number,
      default: 0,
    }
  },
  components: {
  },
  data() {
    let maxSoc = (rule, value, callback) => {
      if (this.Form.type == 1 && value == 100) {
        callback('放電設定不可設定為SOC 100');
      } else if (this.Form.type == 0 && value == 0) {
        callback('充電設定不可設定為SOC 0');
      } else {
        callback();
        // var total = this.Setting.Schedule.schedule.filter((x) => {
        //   return x.week == this.Form.week && (this.From.id == '' || x._id != this.Form._id)
        // }).reduce(function (accumulator, currentValue) {
        //   return accumulator + currentValue.soc;
        // }, 0);

        // if (total > this.Setting?.Schedule?.total_discharge) {
        //   callback('超出可放電總合' + Setting?.Schedule?.total_discharge)
        // }
        // else {
        //   callback()
        // }
      }
    }

    return {
      Dialog: false,
      ManualDischargeDialog: false,
      moment,
      hourData: [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5],
      Form: {
        parent_id: this.dataId,
        _id: '',
        week: "",
        start_time: "",
        end_time: "",
        type: 1,
        soc: undefined,
        kw: null,
      },
      FormTemplate: {
        parent_id: this.dataId,
        _id: '',
        week: "",
        start_time: "12:00:00",
        end_time: "12:00:00",
        type: 1,
        soc: undefined,
        kw: null,
      },
      FormManualDischarge: {
        min: 15,
        power: 1000,
      },
      FormManualDischargeTemplate: {
        min: 15,
        power: 1000,
      },
      FormRule: {
        week: [{ required: true, message: ' ', trigger: 'blur' }],
        start_time: [{ required: true, message: ' ', trigger: 'blur' }],
        end_time: [{ required: true, message: ' ', trigger: 'blur' }],
        type: [{ required: true, type: 'number', message: ' ', trigger: 'blur' }],
        soc: [
          { type: "number", required: true, message: ' ', trigger: 'blur' }, 
          { validator: maxSoc, message: ' ', trigger: 'blur' }
        ]
      },
      Setting: {
        summer_time_start: '',
        summer_time_end: '',
        Schedule: null,
        ElectSetting: null,
        charge_type_rundown: null,
        power_control_rundown: null,
        power_control_target: null,
      },
    }
  },
  watch: {

  },

  mounted() {
    this.getSystemStorageSetting();
    this.getSystemElectricSetting();
    // if (this.dataId) {
    //   this.getOnlyOneSchedule();
    // } else {
    //   this.getIndexSchedule();
    // }
  },
  computed: {
    dialogSubmit() {
      const vm = this;
      let isDisabled = true;
      let vvv = 0;
      Object.keys(vm.Form).forEach((kkk) => {
        if (kkk !== 'parent_id' && kkk != '_id' && kkk != 'kw') {
          if (vm.Form[kkk] !== '' && vm.Form[kkk] !== null) {
            vvv += 1;
          }
        }
      })
      if(vvv === 5) {
        isDisabled = false;
      }
      return isDisabled;
    }
  },
  methods: {
    kwOnChange(value) {
      if (value === null || value === '' || value === 0) {
        this.Form.kw = null; // 清除時設置為 null
      }
    },
    Clear() {
      const vm = this;

      vm.$confirm('確定清除所有排程設定?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {

        vm.$loading();
        var p = vm.Setting.Schedule?.schedule.map(x => {
          return delScheduleDetail({ id: x._id });
        });

        Promise.all(p).then((response) => {
          vm.getOnlyOneSchedule(this.dataId);
        }).finally(() => {
          vm.$loading().close();
        })
      }).catch(() => {
      });
    },
    getSystemStorageSetting() {
      const vm = this;
      getSystemStorageSetting({ equipment_type: 1 })
        .then(response => {
          if (response.data.message == "Success") {
            var responseData = response.data.data;
            vm.Setting.charge_type_rundown = responseData.find(x => { return x.key == "charge_type_rundown" }).value;
            // 帶 getScheduleDetail (/electric/schedule_detail?parent_id=6637b3ae20c1b6473100cf63)
            //
            if (this.dataId) {
              this.getOnlyOneSchedule(this.dataId);
            } else {
              this.getIndexSchedule();
            }
            //
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .finally(() => {
        })
    },
    // 排程設定內編輯讀取
    getOnlyOneSchedule(dataId) {
      const vm = this;
      getScheduleDetail({ parent_id: dataId })
        .then(response => {
          if (response.data.message == "Success") {
            vm.Setting.Schedule = response.data.data[0];
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .then(() => {
          // ==============================================
          getPowerSchedule()
            .then(powerRes => {
              if (powerRes.data.message == "Success") {
                if(powerRes.data.data.length) {
                  powerRes.data.data.forEach((ppp)=> {
                    vm.Setting.Schedule.schedule.push(ppp);
                  });
                }
              } else {
                vm.$message({ type: 'error', message: response.data.message });
              }
            })
            .catch(powerRes => {
              vm.$message({ type: 'error', message: powerRes.message });
            })
          // ==============================================
        })
    },
    // 首頁顯示
    getIndexSchedule() {
      const vm = this;
      getScheduleDetail({ parent_id: vm.Setting.charge_type_rundown })
        .then(response => {
          if (response.data.message == "Success") {
            vm.Setting.Schedule = response.data.data[0];
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .then(() => {
          // ==============================================
          getPowerSchedule()
            .then(powerRes => {
              if (powerRes.data.message == "Success") {
                if(powerRes.data.data.length) {
                  powerRes.data.data.forEach((ppp)=> {
                    vm.Setting.Schedule.schedule.push(ppp);
                  });
                }
              } else {
                vm.$message({ type: 'error', message: response.data.message });
              }
            })
            .catch(powerRes => {
              vm.$message({ type: 'error', message: powerRes.message });
            })
          // ==============================================
        })
    },
    // getSystemScheduleSetting() {
    //   const vm = this;
    //   getSystemScheduleSetting()
    //     .then(response => {
    //       if (response.data.message == "Success") {
    //         vm.Setting.Schedule = response.data.data[0];
    //       } else {
    //         vm.$message({ type: 'error', message: response.data.message });
    //       }
    //     })
    //     .catch(response => { })
    //     .finally(() => { })
    // },
    getSystemElectricSetting() {
      const vm = this;
      getSystemElectricSetting({
        is_set: 1
      }).then(response => {
          if (response.data.message == "Success") {
            vm.Setting.summer_time_start = response.data.data.summer_date_start.replace('-', '')
            vm.Setting.summer_time_end = response.data.data.summer_date_end.replace('-', '')
            var find = response.data.data.data.find(x => { return x.is_set == 1 });
            if (find) {
              vm.Setting.ElectSetting = find;
            }
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => { })
        .finally(() => { })
    },
    Delete() {
      const vm = this;
      delScheduleDetail({ id: vm.Form._id })
        .then(response => {
          if (response.data.message == "Success") {
            vm.Dialog = false;
            vm.getOnlyOneSchedule(this.dataId);
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .finally(() => {
        });
    },
    chkSchedule() {
      const vm = this;
      // debugger;
      let SameWeekItem = vm.Setting.Schedule?.schedule?.filter((x) => {
        // return x.week == vm.Form.week && (vm.Form._id == '' || x._id != vm.Form._id)
        return x.week == vm.Form.week && x.type !== 3;
      });
      let SameTimeItem = SameWeekItem?.filter((x) => {
        vm.moment(vm.Form.start_time, 'HHmmss');
        const dateBaseStart = vm.moment(vm.Form.start_time, 'HHmmss');
        const dateBaseEnd = vm.moment(vm.Form.end_time, 'HHmmss');
        const dateStart = vm.moment(x.start_time, 'HHmmss');
        const dateEnd = vm.moment(x.end_time, 'HHmmss');
        return dateBaseStart.isBetween(dateStart, dateEnd, undefined, "[]") || dateBaseEnd.isBetween(dateStart, dateEnd, undefined, "[]")
      });

      return SameTimeItem;

    },
    postScheduleFunc(SameTimeItem) {
      const vm = this;
      vm.$loading();
      // delete vm.Form['_id'];
      let p = [postScheduleDetail(vm.Form)];
      //
      // console.log(SameTimeItem);
      SameTimeItem?.forEach((x) => {
        if(x.type !== 3) {
          if (x._id && x._id !== vm.Form['_id']) {
            p.push(delScheduleDetail({ id: x._id }));
          }
        }
      });
      //
      Promise.all(p).then(response => {
        // debugger;
        let ErrorMessage = response.filter((x) => x.data.message != "Success").map(x => { return x.data.message }).join(' ; ');
        if (!ErrorMessage) {
          vm.getOnlyOneSchedule(this.dataId);
          vm.Dialog = false;
        } else {
          vm.$message({ type: 'error', message: ErrorMessage });
        }
      }).catch(response => {
        vm.$message({ type: 'error', message: response.message });
      }).finally(() => {
        vm.$loading().close();
      });
    },
    Submit() {
      const vm = this;
      // debugger;
      vm.$refs.Form.validate((valid) => {
        if (valid) {
          const SameTimeItem = vm.chkSchedule();
          console.log(SameTimeItem);
          //
          if (SameTimeItem?.length) {
            if (SameTimeItem.length === 1 && SameTimeItem[0]['_id'] === vm.Form['_id']) {
              vm.postScheduleFunc(SameTimeItem);
            } else {
              vm.$confirm(`排程時間重疊，送出後將寫入目前的設定，並移除重疊的排程?`, '提示', {
              confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
              }).then(() => {
                vm.postScheduleFunc(SameTimeItem);
              }).catch(() => { });
            }
          } else {
            vm.postScheduleFunc(SameTimeItem);
          }
        }
      });
    },
    Edit(row) {
      if (this.Editable && row.type !== 3) {
        var data = JSON.parse(JSON.stringify(row));
        this.Form = Object.assign({}, this.FormTemplate, data);
        this.Form._id = data._id;
        this.Dialog = true;
      }
    },
    Add() {
      this.Form = Object.assign({}, this.FormTemplate);
      this.Dialog = true;
    },
    getColorBar(weekDay, hour) {

      var currentDate = this.moment()
      var targetDate = currentDate.add(weekDay - currentDate.isoWeekday(), 'days');

      var SummerBegin = this.moment(new Date().getFullYear() + this.Setting.summer_time_start);
      var SummerEnd = this.moment(new Date().getFullYear() + this.Setting.summer_time_end);
      var isSummer = this.moment(targetDate).isBetween(SummerBegin, SummerEnd, 'day', '[]');
      
      if (this.Setting.ElectSetting?.data) {
        var weekDaySetting = this.Setting.ElectSetting.data?.filter(x => {
          return ((weekDay >= x.day_start && weekDay <= x.day_end) || (weekDay == x.day_start)) && 
                 ((isSummer && x.summer_type == '夏月') || (!isSummer && x.summer_type == '非夏月'))
        });
        if (weekDaySetting) {
          var find = weekDaySetting.find(x => {
            return this.moment("1999-01-01 00:00:00").add(hour, 'hours').add(1, 'minutes').isBetween(this.moment("1999-01-01 " + x.time_start + ":00"), this.moment("1999-01-01 " + x.time_end + ":00"), 'minute', true)
          });

          if (find) {
            if (Array.isArray(this.Setting.ElectSetting.holidays) && this.Setting.ElectSetting.holidays.includes(weekDay)){
              return "bg-success";
            } else {
              if (find.price_level == "離峰") return "bg-success";
              if (find.price_level == "尖峰") return "bg-danger";
              if (find.price_level == "半尖峰") return "bg-primary"
            }
          } else if (weekDay == 7) {
            return "bg-success";
          }
        }
      }
      return "bg-dark"
    },
    getPosition(row) {
      var dayPart = this.moment().format("YYYY-MM-DD ");
      var todayBegin = this.moment(dayPart + "00:00:00");
      var startTime = this.moment(dayPart + row.start_time);
      var endTime = this.moment(dayPart + row.end_time);
      var left = (startTime.diff(todayBegin, 'minutes', true) / 1440 * 100).toFixed(2);
      var width = (endTime.diff(startTime, 'minutes', true) / 1440 * 100).toFixed(2);

      return { left: left + '%', width: width + '%' };
    },
    getWeekClass(week) {
      const today = new Date();
      const day = today.getDay();
      if (day === week) {
        return ' bg-warning';
      }
        return '';
    }
  },
  created() {


  },
}
</script>

<style scoped>
.scheduleCompoment {
  min-width: 900px;
}
.scheduleCompoment .col,
.scheduleCompoment .col-1 {
  height: 4.2rem;
}

.scheduleCompoment .color-row .col-1,
.scheduleCompoment .color-row .col {
  height: 8px;
}

.SchedultItem {
  position: absolute;
  height: 2rem;
  margin-top: 4px;
  color: black;
  opacity: .7;
  background-color: gray;
  display: inline-block;
  white-space: nowrap;
  padding-top: 4px;
}

.SchedultItem2 {
  position: absolute;
  height: 2rem;
  margin-top: 35px;
  color: black;
  opacity: .65;
  background-color: rgb(242 209 98);
  display: block;
  white-space: nowrap;
  padding-top: 4px;
  box-shadow: 0px 0px 10px #a5381b;
}
.ddd {
  color: rgb(241 201 69);
}

.scheduleCompoment .col,
.scheduleCompoment .row {
  padding: 0;
  margin: 0;
}

.borderHead {
  border: 1px solid #ccc;
  height: 2rem !important;
}
</style>