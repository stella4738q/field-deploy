<template>
<!-- {{ this.sysSettingData.power_control_start_date }}
{{ this.sysSettingData.power_control_end_date }}
{{ this.sysSettingData.power_control_start_time }}
{{ this.sysSettingData.power_control_end_time }} -->
<div id="powerControlSch" class="scheduleCompoment" style="overflow-x: auto;">
    <div class="mb-2 row align-items-center">
      <div class="col-10">
        <h3>抑低用電每日設定</h3>
      </div>
      <div class="col-2 text-end">
        <el-button @click="Add" :disabled="!this.editable">
          <font-awesome-icon icon="plus" />
        </el-button>
      </div>
    </div>
    <div class="mb-2" style="min-width:1100px;">
    <!-- =========== 24小時 ===========-->
    <div id="hoursRow" class="row text-center" style="height: 40px;">
        <div class="col-1 border">每日設定</div>
        <div class="col">
          <div class="row">
            <div class="col text-center border">00</div>
            <div class="col text-center border">01</div>
            <div class="col text-center border">02</div>
            <div class="col text-center border">03</div>
            <div class="col text-center border">04</div>
            <div class="col text-center border">05</div>
            <div class="col text-center border">06</div>
            <div class="col text-center border">07</div>
            <div class="col text-center border">08</div>
            <div class="col text-center border">09</div>
            <div class="col text-center border">10</div>
            <div class="col text-center border">11</div>
            <div class="col text-center border">12</div>
            <div class="col text-center border">13</div>
            <div class="col text-center border">14</div>
            <div class="col text-center border">15</div>
            <div class="col text-center border">16</div>
            <div class="col text-center border">17</div>
            <div class="col text-center border">18</div>
            <div class="col text-center border">19</div>
            <div class="col text-center border">20</div>
            <div class="col text-center border">21</div>
            <div class="col text-center border">22</div>
            <div class="col text-center border">23</div>
          </div>
        </div>
    </div>
    <!-- =========== 排程 ===========-->
    <div class="row text-center" style="position: relative;">
        <div class="col-1 border"></div>
        <div class="col" style="position: relative;">
          <div class="row">
            <!-- =========================================== -->
            <span v-for=" item in oneDaySetting" :key="item['_id']" @click="Edit(item)" :style="getPosition(item)" :class="this.editable ? 'SchedultItem2 cursor-pointer' : 'SchedultItem2'">
              <!-- ---------------------------------------------- -->
              <!-- <img src="@/assets/down.png" style="width:25px;"> -->
              <span>{{ item.kw }}</span>
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
    <!-- =========== 增加排程 ===========-->
    <el-dialog :title="Object.keys(sendData).indexOf('_id') === -1 ? '新增排程' : '編輯排程'" center v-model="Dialog" :close-on-click-modal="false" :show-close="false" width="400px">
      <!-- <pre>{{ sendData }}</pre> -->
      <el-form :model="sendData" :rules="FormRule" ref="Form">
        <el-form-item label="開始時間" prop="start_time">
          <el-time-picker v-model="sendData.start_time" :default-value="new Date(2024, 8, 16, 0, 0, 0)" placeholder="開始時間" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="結束時間" prop="end_time">
          <el-time-picker v-model="sendData.end_time" :default-value="new Date(2024, 8, 16, 0, 59, 59)" placeholder="結束時間" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="目標用電(kW)" prop="kw">
          <el-input-number v-model="sendData.kw" placeholder="kW" @change="kwOnChange" :min="0" :max="1045" :step="1">
          </el-input-number>
        </el-form-item>
      </el-form>
      <div class="dialog-footer mt-5 text-center">
        <el-button @click="DialogClose">
          <font-awesome-icon icon="circle-xmark" />
        </el-button>
        <el-popconfirm title="確定刪除" confirm-button-text="確定" cancel-button-text="取消" @confirm="Delete" v-if="sendData['_id']">
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
    <!-- =========== ======= ===========-->
</div>
</template>
<script>
import moment from 'moment';
import { getPowerOneDaySchedule, postPowerOneDaySchedule, delPowerOneDaySchedule } from '@/api/Api.js';

export default {
  name: 'PowerControlSch',
  emits: ['powerSchChange'],
  props: {
    editable: {
     type: Boolean,
     default: false,
    },
    sysSettingData: {
      type: Object,
    },
  },
  components: {},
  data() {
    return {
        moment,
        hourData: [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5],
        oneDaySetting: [],
        Dialog: false,
        sendData: {
            // _id: '',
            start_time: null,
            end_time: null,
            kw: undefined,
        },
        FormTemplate: {
            // _id: '',
            start_time: null,
            end_time: null,
            kw: undefined,
        },
        FormRule: {
        start_time: [{ required: true, message: ' ', trigger: 'blur' }],
        end_time: [{ required: true, message: ' ', trigger: 'blur' }],
        kw: [
          { type: "number", required: true, message: ' ', trigger: 'blur' }, 
        ]
      },
    };
  },
  mounted() {
    this.getOneDayData();
  },
  computed: {
    dialogSubmit() {
      const vm = this;
      let isDisabled = true;
      let vvv = 0;
      Object.keys(vm.sendData).forEach((kkk) => {
        if (kkk != '_id') {
          if (vm.sendData[kkk] !== '' && vm.sendData[kkk] !== null) {
            vvv += 1;
          }
        }
      })
      if(vvv === 3) {
        isDisabled = false;
      }
      return isDisabled;
    }
  },
  methods: {
    getOneDayData() {
        getPowerOneDaySchedule()
        .then(response => {
          if (response.data.Success) {
            this.oneDaySetting = response.data.Data;
            this.$emit('powerSchChange', response.data.Data);
          } else {
            vm.$message({ type: 'error', message: response.data.Msg });
          }
        })
        .catch(response => { 
            vm.$message({ type: 'error', message: response });
        })
        .finally(() => { })
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
    Add() {
      this.sendData = Object.assign({}, this.FormTemplate);
      this.Dialog = true;
    },
    kwOnChange(value) {
      if (value === null || value === '' || value === 0) {
        this.sendData.kw = null; // 清除時設置為 null
      }
    },
    Edit(row) {
      if (this.editable) {
        let data = JSON.parse(JSON.stringify(row));
        this.sendData = Object.assign({}, this.FormTemplate, data);
        this.sendData['_id'] = data['_id'];
        this.Dialog = true;
      }
    },
    Submit() {
      // this.checkTimeRange();
      this.SubmitData();
    },
    SubmitData() {
        const vm = this;
        vm.$loading();
        vm.sendData.start_time = `${vm.sendData.start_time.substr(0, 5)}:00`;
        vm.sendData.end_time = `${vm.sendData.end_time.substr(0, 5)}:59`;
        //
        let mode = '新增';
        if(vm.sendData['_id']) {
            mode = '修改';
        }
        // console.log(vm.sendData);
        vm.$refs.Form.validate((valid) => {
            if (valid) {
                postPowerOneDaySchedule(this.sendData)
                .then(response => {
                if (response.data.Msg == "Success") {
                    this.DialogClose();
                    vm.$message({ type: 'success', message: `排程${mode}成功` });
                    this.getOneDayData(); // 更新資料
                    // this.checkAllTimeRange(); // 如果全部設定的範圍沒有 >= 總設定範圍送出 => 跳提醒
                } else {
                    vm.$message({ type: 'error', message: response.data.Msg });
                }
                })
                .catch(response => {
                vm.$message({ type: 'error', message: response.Msg });
                })
                .finally(() => {
                    vm.$loading().close();
                });
            }
        });
    },
    DialogClose() {
      this.sendData = Object.assign({}, this.FormTemplate);
      this.Dialog = false;
    },
    Delete() {
      const vm = this;
      delPowerOneDaySchedule({ id: vm.sendData['_id'] })
        .then(response => {
          if (response.data.Success) {
            vm.DialogClose();
            vm.getOneDayData(); // 更新資料
            // vm.checkAllTimeRange(); // 如果全部設定的範圍沒有 >= 總設定範圍送出 => 跳提醒
            vm.$message({ type: 'success', message: '排程刪除成功' });
          } else {
            vm.$message({ type: 'error', message: response.data.Msg });
          }
        })
        .catch(response => {
          // console.log(response);
          vm.$message({ type: 'error', message: response });
        })
        .finally(() => {
        });
    },
    // 確認新增修改的時間
    // 1. 設定超過範圍提醒但仍可送出
    // 2. 如果全部設定的範圍沒有 >= 總設定範圍送出 後跳提醒
    checkTimeRange() {
        const vm = this;
        let allStart = vm.moment(vm.sysSettingData['power_control_start_time'], 'HH:mm:ss');
        let allEnd = vm.moment(vm.sysSettingData['power_control_end_time'], 'HH:mm:ss');
        let settingStart = vm.moment(`${vm.sendData.start_time}:00`, 'HH:mm:ss');
        let settingEnd = vm.moment(`${vm.sendData.end_time}:59`, 'HH:mm:ss');
        if (settingStart.isBetween(allStart, allEnd, undefined, "[]") === false || settingEnd.isBetween(allStart, allEnd, undefined, "[]") === false) {
          // this.$message.warning('提醒：每日設定超過開始結束時間');
          this.checkTimeRangeConfirm();
        } else {
          this.SubmitData();
        }
    },
    // 設定超過範圍提醒但仍可送出
    checkTimeRangeConfirm() {
      const vm = this;
      vm.$confirm('提醒：每日設定超過抑低用電開始/結束時間，確定送出？', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        this.SubmitData();
      }).catch(() => {
      });
    },
    // 如果全部設定的範圍沒有 大於等於 總設定範圍，送出後跳提醒
    checkAllTimeRange() {
      let ST = this.moment(this.sysSettingData['power_control_start_time'], 'HH:mm:ss');
      let ET = this.moment(this.sysSettingData['power_control_end_time'], 'HH:mm:ss');
      let allTimes = Math.abs(ST.diff(ET, 'seconds')); // 起始時間與結束時間的總時間，Math.abs強制轉正
      //
      let detailTimes = 0;
      let idx = 0;
      this.oneDaySetting.forEach((item) => {
        // console.log(item);
        let dST = this.moment(item.start_time, 'HH:mm:ss');
        let dET = this.moment(item.end_time, 'HH:mm:ss');
        // console.log(dET.diff(dST, 'seconds'));
        detailTimes += Math.abs(dET.diff(dST, 'seconds'));
        allTimes = allTimes - 1; // 因為都設定到 xx:59:59 所以有幾個項目就會差幾秒
        idx += 1;
      });
      if (idx === this.oneDaySetting.length) {
        // console.log(`allTimes: ${allTimes}`);
        // console.log(`detailTimes:${detailTimes}`);
        if (detailTimes < allTimes) {
          this.$message.warning('提醒：抑低用電開始與結束時間有無排程區段');
        }
      }
    },
  },
  created() {},
  watch: {},
}
</script>
<style scoped>
#hoursRow .col,
#hoursRow .col-1 {
    line-height: 2.5rem;
}

.scheduleCompoment .col,
.scheduleCompoment .col-1 {
  height: 3rem;
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
  height: 2.3rem;
  margin-top: 9px;
  color: black;
  opacity: .65;
  background-color: rgb(242 209 98);
  display: block;
  white-space: nowrap;
  padding-top: 8px;
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
</style>