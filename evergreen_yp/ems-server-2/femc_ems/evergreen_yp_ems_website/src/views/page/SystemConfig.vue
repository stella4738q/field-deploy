<template>
  <div class="sizeXLarge card border-0 shadow-sm">
    <div class="card-body">
    <!-- =============================================================== -->
    <el-form :model="Form" label-width="auto" label-position="top">
      <el-tabs type="border-card" v-model="activeName">
          <!-- =============================================================== -->
          <el-tab-pane label="儲能設定" name="Setting1" v-if="$store.getters.userPriviagePage('P02-01')">
            <h3 class="border-bottom p-2">儲能設定</h3>
              <!-- =============================================================== -->
              <el-row class="ps-2 pt-2" gutter="25">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="充電模式">
                    <el-switch v-model="Form.charge_type" :active-value="1" active-text="自動離峰儲電" :inactive-value="0"
                  inactive-text="手動排程" />
                  </el-form-item>
                  <el-form-item label="充放電是否考慮超約">
                  <el-switch v-model="Form.schedule_with_demand" :active-value=true active-text="是" :inactive-value=false
                  inactive-text="否" />
                </el-form-item>
                <el-form-item label="排程表選擇">
                  <el-select v-model="Form.charge_type_rundown" :disabled="Form.charge_type === 1" style="max-width:300px" >
                    <el-option v-for="(iii, index) in ApiResponse.scheduleList" :key="``" :label="iii.name" :value="iii['_id']" />
                  </el-select>
                </el-form-item>
                <el-form-item label="逆送電偵測">
                    <el-switch v-model="Form.enable_reverse_power_detect" :active-value="true" active-text="啟用" :inactive-value="false"
                      inactive-text="關閉" />
                  </el-form-item>


                </el-col>
                <!-- =============================================================== -->
                <el-col :xs="24" :sm="12">
                  <el-form-item label="儲電上限 SOC (%)">
                    <el-input-number type="number" v-model.number="Form.max_soc">
                    </el-input-number>
                  </el-form-item>
                  <el-form-item label="保護電力 SOC (%)">
                    <el-input-number type="number" v-model.number="Form.min_soc">
                    </el-input-number>
                  </el-form-item>
                  <el-form-item label="電流限制-電表類別">
                  <el-radio-group v-model.number="Form.max_current_type" size="medium">
                      <el-radio-button :label="0">不啟用</el-radio-button>
                      <el-radio-button :label="1">高壓總表</el-radio-button>
                      <el-radio-button :label="2">低壓分表</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="電表最高電流限制(A)">
                    <el-input-number type="number" v-model.number="Form.max_current" :min="0">
                    </el-input-number>
                  </el-form-item>
                  <!-- <el-form-item label="太陽能自動補電">
                    <el-switch v-model="Form.enable_auto_replenishment" :active-value="true" active-text="啟用" :inactive-value="false"
                      inactive-text="關閉" />
                  </el-form-item>
                  <el-form-item label="太陽能自動補電-SOC上限">
                    <el-input-number type="number" v-model.number="Form.replenishment_max_soc" :disabled="!Form.enable_auto_replenishment"></el-input-number>
                  </el-form-item> -->
                </el-col>
              </el-row>
             <!-- =============================================================== -->
            <!-- ------------------------------------------ -->
            <h3 class="border-bottom p-2 mt-5">ESSCI</h3>
            <div class="ps-2 pt-2">
              <el-form-item label="警戒值" prop="eci_warning_std">
                <el-input-number type="number" :min="0.1" :max="1" :step="0.1" v-model.number="Form.eci_warning_std">
                </el-input-number>
              </el-form-item>
              <!-- <el-form-item label="Threshold" prop="eci_threshold">
                <el-input-number type="number" :min="0.1" :max="1" v-model.number="Form.eci_threshold"> </el-input-number>
              </el-form-item> -->
            </div>
          </el-tab-pane>
          <!-- =============================================================== -->
          <el-tab-pane label="抑低用電" name="Setting2" >
            <h3 class="border-bottom p-2">抑低用電</h3>
            <!-- ========================================================= -->
            <el-row class="ps-2 pt-2" gutter="25">
              <el-col :xs="24" :sm="12">
                <el-form-item label="是否啟用">
                <el-switch v-model="Form.automatic_power_control" :active-value="true" active-text="是"
                  :inactive-value="false" inactive-text="否" />
                </el-form-item>
                <!-- <el-form-item label="目標值(kW)" prop="power_control_target">
                  <el-input-number type="number" :min="0" v-model.number="Form.power_control_target">
                    <template #append>kW</template>
                  </el-input-number>
                </el-form-item> -->
                <el-form-item label="啟用通知">
                <el-switch v-model="Form.power_control_enable_alarm" :active-value="true" active-text="是"
                  :inactive-value="false" inactive-text="否" />
              </el-form-item>
              <el-form-item label="開始前N天通知" prop="power_control_warning_n_day">
                <el-input-number type="number" :min="0" v-model.number="Form.power_control_warning_n_day" :disabled="!Form.power_control_enable_alarm">
                  <template #append>天</template>
                </el-input-number>
              </el-form-item>
              <el-form-item label="結束前N天通知" prop="power_control_alarm_n_day">
                <el-input-number type="number" :min="0" v-model.number="Form.power_control_alarm_n_day" :disabled="!Form.power_control_enable_alarm">
                  <template #append>天</template>
                </el-input-number>
              </el-form-item>
              </el-col>
              <!-- ========================================================= -->
              <el-col :xs="24" :sm="12">
                <el-form-item label="保留SOC(%)" prop="power_control_protect_soc">
                  <el-input-number type="number" :min="Form.min_soc" :max="Form.max_soc" v-model.number="Form.power_control_protect_soc">
                    <template #append>%</template>
                  </el-input-number>
                </el-form-item>
                  <el-form-item label="開始日期" prop="power_control_start_date">
                    <el-date-picker v-model="Form.power_control_start_date" type="date" placeholder="請選擇日期時間"
                      value-format="YYYYMMDD"></el-date-picker>
                  </el-form-item>
                  <el-form-item label="結束日期" prop="power_control_end_date">
                    <el-date-picker v-model="Form.power_control_end_date" type="date" placeholder="請選擇日期時間"
                      value-format="YYYYMMDD"></el-date-picker>
                  </el-form-item>
                  <!-- <el-form-item label="開始時間" prop="power_control_start_time">
                    <el-time-picker v-model="Form.power_control_start_time" placeholder="Please input"
                      value-format="HHmmss" :disabled="checkSetting2Editable" />
                  </el-form-item>
                  <el-form-item label="結束時間" prop="power_control_end_time">
                    <el-time-picker v-model="Form.power_control_end_time" placeholder="Please input"
                      value-format="HHmmss" :disabled="checkSetting2Editable" />
                  </el-form-item> -->
              </el-col>
              <!-- ========================================================= -->
            </el-row>
            <!-- ========================================================= -->
          </el-tab-pane>
          <!-- =============================================================== -->
          <el-tab-pane label="超約設定" name="Setting3" >
            <h3 class="border-bottom p-2">超約設定</h3>
            <!-- ========================================================= -->
            <el-row class="ps-2 pt-2" gutter="25">
              <!-- ========================================================= -->
              <el-col :xs="24" :sm="24">
                <el-form-item label="超約啟動" prop="automatic_demand">
                  <el-switch v-model="Form.automatic_demand" :active-value="true" active-text="啟用" :inactive-value="false" inactive-text="停用" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="24">
                <el-form-item label="預估超約功率(kW)" prop="contract_forecast_power">
                  <el-input-number type="number" :min="0" :step="1" v-model.number="Form.contract_forecast_power">
                  </el-input-number>
                </el-form-item>
                <el-form-item label="週六半尖峰契約容量(kW)" prop="saturday_contract_capacity">
                  <el-input-number type="number" :min="0" :step="1" v-model.number="Form.saturday_contract_capacity">
                  </el-input-number>
                </el-form-item>
              </el-col>
              <!-- ========================================================= -->
              <el-col :xs="24" :sm="12">
                <h5 class="border-bottom p-2">夏月</h5>
          <el-form-item label="契約容量 (MW)" prop="contract_capacity">
            <el-input-number type="number" :min="0.1" v-model.number="Form.contract_capacity">
              <template #append>MW</template>
            </el-input-number>
          </el-form-item>
          <el-form-item label="超約控制 (MW)" prop="Capacity">
            <el-input-number type="number" v-model.number="Form.automatic_capacity" :max="Form.contract_capacity"
              placeholder="">
              <template #append>MW</template>
            </el-input-number>
          </el-form-item>
          <!-- <el-form-item label="超約控制持續時間 (分鐘)" prop="automatic_duration">
            <el-input-number type="number" v-model.number="Form.automatic_duration">
              <template #append>分鐘</template>
            </el-input-number>
          </el-form-item> -->
          <!-- <el-form-item label="執行功率 (kW)" prop="power">
            <el-input-number type="number" v-model.number="Form.demand_power" :disabled="Form.demand_power_auto_cal" :max="1045">
              <template #append>kW</template>
            </el-input-number>
          </el-form-item> -->
              </el-col>
              <!-- ========================================================= -->
              <el-col :xs="24" :sm="12">
                <h5 class="border-bottom p-2">非夏月</h5>
          <el-form-item label="契約容量(MW)" prop="nonsummer_contract_capacity">
            <el-input-number type="number" :min="0" :step="0.1" v-model.number="Form.nonsummer_contract_capacity">
            </el-input-number>
          </el-form-item>
          <el-form-item label="超約控制 (MW)" prop="Capacity">
            <el-input-number type="number" v-model.number="Form.nonsummer_automatic_capacity" :max="Form.nonsummer_contract_capacity"
              placeholder="">
              <template #append>MW</template>
            </el-input-number>
          </el-form-item>
          <!-- <el-form-item label="超約控制持續時間 (分鐘)" prop="nonsummer_automatic_duration">
            <el-input-number type="number" v-model.number="Form.nonsummer_automatic_duration">
              <template #append>分鐘</template>
            </el-input-number>
          </el-form-item> -->
          <!-- <el-form-item label="執行功率 (kW)" prop="nonsummer_demand_power">
            <el-input-number type="number" v-model.number="Form.nonsummer_demand_power" :disabled="Form.demand_power_auto_cal" :max="1045" >
              <template #append>kW</template>
            </el-input-number>
          </el-form-item> -->
              </el-col>
              <!-- ========================================================= -->
            </el-row>
            <!-- ========================================================= -->
          </el-tab-pane>
          <!-- =============================================================== -->
          <el-tab-pane label="即時備轉設定" name="Setting4" >
            <h3 class="border-bottom p-2">即時備轉設定</h3>
            <!-- ========================================================= -->
            <el-row class="ps-2 pt-2" gutter="25">
              <!-- ========================================================= -->
              <el-col :xs="24" :sm="24">
                <el-form-item label="待命量監控" prop="enable_spinning_reserve_compensate">
                  <el-switch v-model="Form.enable_spinning_reserve_compensate" :active-value="true" active-text="啟用" :inactive-value="false" inactive-text="停用" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="24">
                <el-form-item label="CT/PT表計系數" prop="spinning_cbl_rate">
                  <el-input-number type="number" :min="0" :max="1" :step="0.1" v-model.number="Form.spinning_cbl_rate">
                  </el-input-number>
                </el-form-item>
                <el-form-item label="待命量誤差調整值(kW)" prop="spinning_cbl_difference">
                  <el-input-number type="number" :min="0" :step="1" v-model.number="Form.spinning_cbl_difference">
                  </el-input-number>
                </el-form-item>
              </el-col>
            </el-row>
            <!-- ========================================================= -->
          </el-tab-pane>
          <el-tab-pane label="客製化系統保護" name="Setting5" >
            <h3 class="border-bottom p-2">客製化系統保護</h3>
            <el-row class="ps-2 pt-2" gutter="25">
              <el-col :xs="24" :sm="24">
                <el-form-item label="客製化系統保護" prop="custom_protect">
                  <el-switch v-model="Form.custom_protect" :active-value="true" active-text="啟用" :inactive-value="false" inactive-text="停用" />
                </el-form-item>
              </el-col>
              <el-col :md="8" :xs="24">
                <el-form-item label="連線異常">
                  <el-input type="number" v-model.number="ProtectForm.conn_fault_time" placeholder=" ">
                    <template #append>秒</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :md="8" :xs="24">
                <el-form-item label="火警反應時間">
                  <el-input type="number" v-model.number="ProtectForm.fire_fault_time" placeholder=" ">
                    <template #append>秒</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            
            <table class="table table-bordered">
              <thead class="text-center">
                <tr>
                  <th></th>
                  <th colspan="2">Level 0</th>
                  <th colspan="2" class="text-center">Level 1</th>
                  <th colspan="2" class="text-center">Level 2</th>
                </tr>
                <tr>
                  <th></th>
                  <th>值</th>
                  <th>持續時間</th>
                  <th>值</th>
                  <th>持續時間</th>
                  <th>值</th>
                  <th>持續時間</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>過壓</td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_max_l0" placeholder=" ">
                    <template #append>V</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_max_l0_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_max_l1" placeholder=" ">
                    <template #append>V</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_max_l1_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_max_l2" placeholder=" ">
                    <template #append>V</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_max_l2_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                </tr>
                <tr>
                  <td>欠壓</td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_min_l0" placeholder=" ">
                    <template #append>V</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_min_l0_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_min_l1" placeholder=" ">
                    <template #append>V</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_min_l1_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_min_l2" placeholder=" ">
                    <template #append>V</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_volt_min_l2_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                </tr>
                <tr>
                  <td>過電流</td>
                  <td><el-input type="number" v-model.number="ProtectForm.current_max_l0" placeholder=" ">
                    <template #append>A</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.current_max_l0_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.current_max_l1" placeholder=" ">
                    <template #append>A</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.current_max_l1_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.current_max_l2" placeholder=" ">
                    <template #append>A</template> </el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.current_max_l2_time" placeholder=" ">
                    <template #append>秒</template> </el-input></td>
                </tr>
                <tr>
                  <td nowrap="nowrap">電芯過溫</td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_max_l0" placeholder=" ">
                      <template #append>°C</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_max_l0_time" placeholder=" ">
                      <template #append>秒</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_max_l1" placeholder=" ">
                      <template #append>°C</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_max_l1_time" placeholder=" ">
                      <template #append>秒</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_max_l2" placeholder=" ">
                      <template #append>°C</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_max_l2_time" placeholder=" ">
                      <template #append>秒</template></el-input></td>
                </tr>
                <tr>
                  <td nowrap="nowrap">電芯低溫</td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_min_l0" placeholder=" ">
                      <template #append>°C</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_min_l0_time" placeholder=" ">
                      <template #append>秒</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_min_l1" placeholder=" ">
                      <template #append>°C</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_min_l1_time" placeholder=" ">
                      <template #append>秒</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_min_l2" placeholder=" ">
                      <template #append>°C</template></el-input></td>
                  <td><el-input type="number" v-model.number="ProtectForm.cell_temp_min_l2_time" placeholder=" ">
                      <template #append>秒</template></el-input></td>
                </tr>
              </tbody>
            </table>
          </el-tab-pane>
          <!-- =============================================================== -->
        </el-tabs>
    </el-form>
    <!-- =============================================================== -->
    <div class="dialog-footer mt-5 text-center">
      <el-button @click="LoadSetting" class="ms-2">
        <font-awesome-icon icon="circle-xmark" />
      </el-button>
      <!-- <el-button @click="Reload" class="ms-2">
        <font-awesome-icon icon="retweet" />
      </el-button> -->
      <el-button type="primary" @click="Submit" class="ms-2" v-if="$store.getters.userPriviage('p_00023')" :disabled="checkSubmit">
        <font-awesome-icon icon="circle-check" />
      </el-button>
    </div>
    <!-- =============================================================== -->
    <div class="p-1" v-if="activeName === 'Setting2'">
      <!-- 修改抑低用電每日設定
      <el-switch v-model="this.Setting2Editable" :active-value="true" active-text="開啟" :inactive-value="false" inactive-text="關閉" />
      <br><span class="text-danger">修改期間無法更改開始/結束時間</span>
      <hr> -->
      <powerControlSchedule :editable="true" :sysSettingData="this.Form" @powerSchChange="getSetting2Detail"></powerControlSchedule>
    </div>
  </div>
  </div>
</template>
<script>
import moment from 'moment';
import { getSystemStorageSetting, postSystemStorageSetting, postModbusControl, getAllSchedule, getPowerOneDaySchedule,
  getSystemCustomProtect, postSystemCustomProtect
} from '@/api/Api.js';
import powerControlSchedule from '@/components/powerControlSchedule.vue';

export default {
  name: 'SystemConfig',
  props: {},
  components: {
    powerControlSchedule,
  },
  data() {
    return {
      moment,
      activeName: 'Setting1',
      Setting2Editable: false,
      Form: {
        charge_type: 0,// 充電模式 1自動離峰儲電 0手動排程
        charge_type_rundown: null,//排程是否考慮超約,1:考慮 0:不考慮
        schedule_with_demand: true,
        max_soc: null,//儲電上限 SOC
        min_soc: null,//保護電力 SOC
        max_current_type: 0, // 0:不啟用, 1:高壓 2:低壓
        max_current: null, //電表最高電流偵測
        //
        automatic_power_control: true, // 抑低用電啟用
        power_control_target: 20, // 抑低用電-目標值(kW)
        power_control_protect_soc: 20, //抑低用電-保留SOC(%)
        power_control_start_date: null, // 抑低用電-開始日期
        power_control_end_date: null, // 抑低用電-結束日期
        power_control_enable_alarm: true, // 抑低用電-啟用通知
        power_control_warning_n_day: null, // 抑低用電-開始前N天通知
        power_control_alarm_n_day: null, // 抑低用電-結束前N天通知
        //
        // emergency_power: 0,//緊急供電保留 (MW)
        automatic_demand: true,//自動需量啟動 (MW) 
        contract_capacity: 15,//契約容量 (MW)
        contract_forecast_power: 700, //超約計算使用功率
        saturday_contract_capacity: 300,//周六半尖峰(kW)
        automatic_capacity: 9650,//需量反應啟動基準(MW) 
        //
        nonsummer_contract_capacity: 15,//非夏月契約容量 (MW)
        nonsummer_automatic_capacity: true,//非夏月需量反應啟動基準(MW) 
        //
        eci_warning_std: 0.85,//ECI 警戒值
        // eci_threshold: 0.1 //ECI Threshold//隱藏，固定為0.1
        enable_reverse_power_detect: null,
        enable_auto_replenishment: null,
        replenishment_max_soc: null,

        //
        enable_spinning_reserve_compensate: false,
        spinning_cbl_difference: 0,
        spinning_cbl_rate: 1,
        //
        custom_protect: false,
      },
      ProtectForm: {
        // Custom Protect
        cell_temp_max_l0: 0,
        cell_temp_max_l1: 0,
        cell_temp_max_l2: 0,
        cell_temp_max_l0_time: 0,
        cell_temp_max_l1_time: 0,
        cell_temp_max_l2_time: 0,
        current_max_l0: 0,
        current_max_l1: 0,
        current_max_l2: 0,
        current_max_l0_time: 0,
        current_max_l1_time: 0,
        current_max_l2_time: 0,
        cell_volt_min_l0: 0,
        cell_volt_min_l1: 0,
        cell_volt_min_l2: 0,
        cell_volt_min_l0_time: 0,
        cell_volt_min_l1_time: 0,
        cell_volt_min_l2_time: 0,
        cell_volt_max_l0: 0,
        cell_volt_max_l1: 0,
        cell_volt_max_l2: 0,
        cell_volt_max_l0_time: 0,
        cell_volt_max_l1_time: 0,
        cell_volt_max_l2_time: 0,
        cell_temp_min_l0: 0,
        cell_temp_min_l1: 0,
        cell_temp_min_l2: 0,
        cell_temp_min_l0_time: 0,
        cell_temp_min_l1_time: 0,
        cell_temp_min_l2_time: 0,
        conn_fault_time: 15,
        fire_fault_time: 15,
      },
      FormOrganize: {
        charge_type: 0,// 充電模式 1自動離峰儲電 0手動排程
        charge_type_rundown: null,//排程是否考慮超約,1:考慮 0:不考慮
        schedule_with_demand: true,
        max_soc: null,//儲電上限 SOC
        min_soc: null,//保護電力 SOC
        max_current_type: 0, // 0:不啟用, 1:高壓 2:低壓
        max_current: null, //電表最高電流偵測
        //
        automatic_power_control: true, // 抑低用電啟用
        power_control_target: 20, // 抑低用電-目標值(kW)
        power_control_protect_soc: 20, //抑低用電-保留SOC(%)
        power_control_start_date: null, // 抑低用電-開始日期
        power_control_end_date: null, // 抑低用電-結束日期
        power_control_enable_alarm: true, // 抑低用電-啟用通知
        power_control_warning_n_day: null, // 抑低用電-開始前N天通知
        power_control_alarm_n_day: null, // 抑低用電-結束前N天通知
        //
        automatic_demand: true,//自動需量啟動 (MW) 
        contract_forecast_power: 700, //超約計算使用功率
        contract_capacity: 15,//契約容量 (MW)
        saturday_contract_capacity: 300,//周六半尖峰(kW)
        automatic_capacity: 13,//超約控制反應執行功率(kW)
        //
        nonsummer_contract_capacity: 15,//非夏月契約容量 (MW)
        nonsummer_automatic_capacity: true,//非夏月需量反應啟動基準(MW) 
        //
        eci_warning_std: 0.85,//ECI 警戒值
        // eci_threshold: 0.1 //ECI Threshold//隱藏，固定為0.1
        enable_reverse_power_detect: null,
        enable_auto_replenishment: null,
        replenishment_max_soc: null,
        //
        enable_spinning_reserve_compensate: false, //即時備轉-待命量監控
        spinning_cbl_difference: 0, //即時備轉-待命量誤差調整值
        spinning_cbl_rate: 1, //即時備轉-CTPT係數
        //
        custom_protect: false
      },
      black_start: false,//BLACK STAR
      black_start_old: null,
      ApiResponse: {
        getSystemStorageSetting: null,
        getSystemCustomProtect: null,
        scheduleList: null,
      },
      // oldData => 用來比對是否有修改 or 改回舊值
      oldData: {},
      oldProtectData: {},
      powerSchDetail: [],
    }
  },
  watch: {
    'Form.contract_capacity'(newVal) {
      this.checkContractCapacity(newVal);
    },
    'Form.nonsummer_contract_capacity'(newVal){
      this.checkNonContractCapacity(newVal);
    }
  },
  mounted() {
    this.getSchList(); // 取得腳本列表
    this.LoadSetting();
    this.getPowerControlSchedule();
    // this.getBlackStart();
  },
  computed: {
    checkSetting2Editable() {
      return this.Setting2Editable;
    },
    checkSubmit() {
      let dis = true;
      let change = 0;
      Object.entries(this.Form).forEach(([key, value]) => {
        if (this.Form[key] !== this.oldData[key]) {
          change += 1;
        }
      });
      Object.entries(this.ProtectForm).forEach(([key, value]) => {
        if (this.ProtectForm[key] !== this.oldProtectData[key]) {
          change += 1;
        }
      });
      if(change) {
        dis = false;
      }
      return dis;
    },
  },
  methods: {
    checkContractCapacity(newVal) {
      if (newVal < this.Form.automatic_capacity) {
        this.Form.automatic_capacity = newVal;
      }
    },
    checkNonContractCapacity(newVal) {
      if (newVal < this.Form.nonsummer_automatic_capacity) {
        this.Form.nonsummer_automatic_capacity = newVal;
      }
    },
    Reload() {
      const vm = this;
      vm.$confirm('還原至出初始設定，目前的修改將被複寫，是否確定?', '提示', {
        confirmButtonText: '確定', cancelButtonText: '取消', type: 'warning'
      }).then(() => {
        vm.Form = JSON.parse(JSON.stringify(vm.FormOrganize));
        vm.Submit();
      }).catch(() => {
      });
    },
    getSchList() {
      const vm = this;
      getAllSchedule()
        .then(response => {
          vm.ApiResponse.scheduleList = response.data.data;
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
    },
    // getBlackStart() {
    //   const vm = this;
    //   var postData = {
    //     customer: "tasco",
    //     code: "LC",
    //     action: "GET_BLACK_START",
    //     equipment_id: null,
    //   };
    //   postModbusControl(postData).then(response => {
    //     if (response.data.Success) {
    //       vm.black_start = response.data.Data;
    //       vm.black_start_old = response.data.Data;
    //     } else {
    //       vm.$message({ type: 'error', message: response.data.Msg });
    //     }
    //   }).catch(response => {
    //     vm.$message({ type: 'error', message: "api error" });
    //   }).finally(() => { });
    // },
    submitBlackStart() {
      const vm = this;
      return false;
      if (vm.black_start != vm.black_start_old) {
        var postData = {
          customer: "tasco",
          code: "LC",
          action: "LC_BLACK_START_ON_OFF",
          equipment_id: null,
          value: vm.black_start,
        };
        postModbusControl(postData).then(response => {
          if (response.data.Success) {

          } else {
            vm.$message({ type: 'error', message: "全黑啟動設定：" + response.data.Msg });
          }
        }).catch(response => {
          vm.$message({ type: 'error', message: "全黑啟動設定：api error" });
        }).finally(() => { });
      }
    },
    LoadSetting() {
      const vm = this;
      vm.$loading();
      Promise.all([
        getSystemStorageSetting(),
        getSystemCustomProtect()
      ])
        .then(([settingRes, protectRes]) => {
          // 處理 settingRes
          if (settingRes.data.message == "Success") {
            var responseData = settingRes.data.data;
            vm.ApiResponse.getSystemStorageSetting = responseData;
            //
            Object.entries(vm.Form).forEach(([key, value]) => {
              vm.Form[key] = responseData.find(x => { return x.key == key })?.value
              vm.oldData[key] = responseData.find(x => { return x.key == key })?.value
            });
            //
          } else {
            vm.$message({ type: 'error', message: settingRes.data.message });
          }

          // 處理 protectRes
          if (protectRes.data.message == "Success") {
            var responseData = protectRes.data.data;
            vm.ApiResponse.getSystemCustomProtect = responseData;
            //
            Object.entries(vm.ProtectForm).forEach(([key, value]) => {
              vm.ProtectForm[key] = responseData.find(x => { return x.key == key })?.value
              vm.oldProtectData[key] = responseData.find(x => { return x.key == key })?.value
            });
            //
          } else {
            vm.$message({ type: 'error', message: protectRes.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        })
        .finally(() => {
          vm.$loading().close();
        })
    },
    checkForm() {
      if (this.Form.automatic_capacity > this.Form.contract_capacity) {
        this.$message.error('(夏月)契約容量，需大於超約控制功率');
        return false;
      }
      if (this.Form.nonsummer_automatic_capacity > this.Form.nonsummer_contract_capacity) {
        this.$message.error('(非夏月)契約容量，需大於超約控制功率');
        return false;
      }
      return true;
    },
    // 確認起始時間與結束時間段全部都有排程
    checkTimeRange() {
      let ST = this.moment(this.Form.power_control_start_time, 'HH:mm:ss');
      let ET = this.moment(this.Form.power_control_end_time, 'HH:mm:ss');
      let allTimes = Math.abs(ST.diff(ET, 'seconds')); // 起始時間與結束時間的總時間，Math.abs強制轉正
      // console.log(`allTimes: ${allTimes}`);
      //
      let detailTimes = 0;
      let idx = 0;
      this.powerSchDetail.forEach((item) => {
        // console.log(item);
        let dST = this.moment(item.start_time, 'HH:mm:ss');
        let dET = this.moment(item.end_time, 'HH:mm:ss');
        // console.log(dET.diff(dST, 'seconds'));
        detailTimes += Math.abs(dET.diff(dST, 'seconds'));
        allTimes = allTimes - 1; // 因為都設定到 xx:59:59 所以有幾個項目就會差幾秒
        idx += 1;
      });
      if (idx === this.powerSchDetail.length) {
        // console.log(`allTimes: ${allTimes}`);
        // console.log(`detailTimes:${detailTimes}`);
        if (detailTimes < allTimes) {
          this.$message.warning('提醒：抑低用電開始與結束時間有無排程區段');
          // this.Form.power_control_start_time = this.oldData['power_control_start_time'];
          // this.Form.power_control_end_time = this.oldData['power_control_end_time'];
          // this.Setting2Editable = true;
          // return false;
        }
        // } else {
        //   // return true; 
        // }
      }
    },
    checkPowerControl() {
      if(this.Form.automatic_power_control) {
        if(this.powerSchDetail.length === 0) {
          this.$message.warning('提醒：抑低用電開始與結束時間無任何排程區段');
        }
      }
    },
    Submit() {
      const vm = this;
      // this.checkTimeRange(); // 確認起始時間與結束時間段全部都有排程
      this.checkPowerControl(); // 如果抑低用電開關為開啟 => 確認至少有一個排程、沒有就跳提醒
      if (this.checkForm()) {
        vm.$loading();
        var PostData = { data: [] };
        var ProtectPostData = { data: [] };
        Object.entries(vm.Form).forEach(([key, value]) => {
          var find = vm.ApiResponse.getSystemStorageSetting?.find(x => { return x.key == key });
          PostData.data.push({
            "_id": find?._id,
            "value": value,
          });
        });
        Object.entries(vm.ProtectForm).forEach(([key, value]) => {
          var find = vm.ApiResponse.getSystemCustomProtect?.find(x => { return x.key == key });
          ProtectPostData.data.push({
            "_id": find?._id,
            "value": value,
          });
        });
        console.log(PostData);
        console.log(ProtectPostData);
        // vm.submitBlackStart();

        Promise.all([
          postSystemStorageSetting(PostData),
          postSystemCustomProtect(ProtectPostData)
        ])
          .then(([settingRes, protectRes]) => {
            if (settingRes.data.message == "Success") {
              vm.$message({ type: 'success', message: "儲能設定完成" });
            } else {
              vm.$message({ type: 'error', message: settingRes.data.message });
            }
            if (protectRes.data.message == "Success") {
              vm.$message({ type: 'success', message: "客製化系統保護完成" });
            } else {
              vm.$message({ type: 'error', message: protectRes.data.message });
            }
          })
          .catch(response => {
            vm.$message({ type: 'error', message: response.message });
          })
          .finally(() => {
            vm.$loading().close();
            this.LoadSetting();
          })
      }
    },
    getSetting2Detail(d) {
      this.powerSchDetail = d;
    },
    getPowerControlSchedule(){
      if(this.powerSchDetail.length === 0){
        getPowerOneDaySchedule()
        .then(response => {
          if (response.data.Success) {
            this.powerSchDetail = response.data.Data;
          } else {
            vm.$message({ type: 'error', message: response.data.Msg });
          }
        })
        .catch(response => { 
            vm.$message({ type: 'error', message: response });
        })
        .finally(() => { })
      }
    }
  },
  created() {},
}
</script>
