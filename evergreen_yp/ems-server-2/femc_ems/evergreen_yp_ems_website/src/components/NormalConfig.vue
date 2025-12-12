<template>
  <div class="card p-0 m-0">
    <div class="card-header">
      <span>基礎設定</span>
    </div>
    <div class="card-body">
      <el-form :model="Form" label-width="auto">
        <el-form-item label="Black Start">
          <el-switch v-model="Form.BlackStart" active-value="1" active-text="啟用" inactive-value="0"
            inactive-text="停用"/>
        </el-form-item>
        <el-form-item label="充電設定">
          <el-switch v-model="Form.charge_type" active-value="1" active-text="離峰儲電" inactive-value="0"
            inactive-text="手動排程" />
        </el-form-item>
        <el-form-item label="儲電上限 SOC">
          <el-input type="number" v-model.number="Form.soc">
            <template #append>%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="保護電力 SOC">
          <el-input type="number" v-model.number="Form.protect_power">
            <template #append>%</template>
          </el-input>
        </el-form-item>

        <el-form-item label="緊急供電保留">
          <el-input type="number" v-model.number="Form.emergency_power">
            <template #append>MWh</template>
          </el-input>
        </el-form-item>

      </el-form>
      <div class="dialog-footer mt-5 text-center">
        <el-button @click="LoadSetting" class="ms-2">
          <font-awesome-icon icon="circle-xmark" />
        </el-button>
        <el-button type="primary" @click="Submit" class="ms-2">
          <font-awesome-icon icon="circle-check" />
        </el-button>
      </div>
    </div>
  </div>
</template>
<script>

import moment from 'moment';
import { getSystemStorageSetting, postSystemStorageSetting } from '@/api/Api.js';
export default {
  name: 'SystemConfig',
  props: {},
  components: {
  },
  data() {
    return {
      moment,
      Form: {
        charge_type: null,//charge_type
        emergency_power: null, //emergency_power
        soc: null,//soc
        protect_power: null,
      },
      ApiResponse: {
        getSystemStorageSetting: null,
      }
    }
  },
  watch: {

  },
  mounted() {
    this.LoadSetting();
  },

  computed: {
    ApiRequest: function () {
      return {
        postSystemStorageSetting: {
          data: [
            {
              "_id": this.ApiResponse.getSystemStorageSetting.find(x => { return x.key == "charge_type" })._id,
              "key": "charge_type",
              "value": this.Form.charge_type,
              "type": 0
            },
            {
              "_id": this.ApiResponse.getSystemStorageSetting.find(x => { return x.key == "emergency_power" })._id,
              "key": "emergency_power",
              "value": this.Form.emergency_power,
              "type": 0
            },
            {
              "_id": this.ApiResponse.getSystemStorageSetting.find(x => { return x.key == "soc" })._id,
              "key": "soc",
              "value": this.Form.soc,
              "type": 0
            },
            {
              "_id": this.ApiResponse.getSystemStorageSetting.find(x => { return x.key == "protect_power" })._id,
              "key": "protect_power",
              "value": this.Form.protect_power,
              "type": 0
            },
          ]
        }
      }
    },
  },
  methods: {

    LoadSetting() {
      const vm = this;
      vm.$loading();
      getSystemStorageSetting({ equipment_type: 1 })
        .then(response => {
          if (response.data.message == "Success") {
            var responseData = response.data.data;
            vm.ApiResponse.getSystemStorageSetting = responseData;
            vm.Form.charge_type = responseData.find(x => { return x.key == "charge_type" }).value;
            vm.Form.emergency_power = responseData.find(x => { return x.key == "emergency_power" }).value;
            vm.Form.soc = responseData.find(x => { return x.key == "soc" }).value;
            vm.Form.protect_power = responseData.find(x => { return x.key == "protect_power" }).value;
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
    Submit() {
      const vm = this;
      vm.$loading();
      postSystemStorageSetting(vm.ApiRequest.postSystemStorageSetting)
        .then(response => {
          if (response.data.message == "Success") {
            vm.$message({ type: 'success', message: "完成" });
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

    }
  },
  created() {


  },
}
</script>
 
<style scoped></style>