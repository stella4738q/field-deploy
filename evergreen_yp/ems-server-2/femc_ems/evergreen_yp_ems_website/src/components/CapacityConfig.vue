<template>
  <div class="card m-0 p-0">
    <div class="card-header  ">
      契約容量
    </div>
    <div class="card-body">
      <el-form :model="FormCapacityConfig" :rules="FormRuleCapacityConfig" ref="FormCapacityConfig" label-width="auto">

        <el-form-item label="契約容量" prop="contractCapacity">
          <el-input-number type="number" :min="0.1" v-model.number="FormCapacityConfig.contractCapacity">
            <template #append>MW</template>
          </el-input-number>
        
        </el-form-item>
        <el-form-item label="超約啟動" prop="contractCapacitySetting">
          <el-switch v-model="FormCapacityConfig.contractCapacitySetting" :active-value=1 active-text="啟用"
            :inactive-value=0 inactive-text="停用" />
        </el-form-item>
        <el-form-item label="超約設定" prop="nowCapacity">
          <el-input-number type="number" v-model.number="FormCapacityConfig.nowCapacity"
            :max="FormCapacityConfig.nowCapacity" placeholder="">
            <template #append>MW</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="執行功率"  prop="power">
          <el-input-number type="number" v-model.number="FormCapacityConfig.power">
            <template #append>kW</template>
          </el-input-number>
        </el-form-item>
      </el-form>
   
    </div>
  </div>
</template>
<script>

import { } from '@/api/Api.js';

import moment from 'moment';
export default {
  name: 'CapacityConfig',
  props: {

  },
  components: {
  },
  data() {
    return {
      moment,
      FormCapacityConfig: {
        nowCapacity: 15,
        contractCapacity: 15,
        contractCapacitySetting: 1,

      },
      FormRuleCapacityConfig: {
        contractCapacity: [{ required: true, type: 'number', message: ' ', trigger: 'blur' }],
      },
    }
  },
  watch: {

  },

  mounted() {
  },
  computed: {
  },
  methods: {
    SubmitCapacityConfig() {
      //待實作，目前沒有api
    },
  },
  created() {


  },
}
</script>
  