<template>

    <div class="p-1 sizeXLarge card border-0 shadow-sm">
      <div class="card-body">
        <h1 class="mb-2">LINE通知設定</h1>
        <!-- =============================================================== -->
        <div class="p-0">
          <el-tabs type="card">
            <!-- =============================================================== -->
            <!-- <el-tab-pane label="規則設定" v-if="$store.getters.userPriviagePage('P02-11-1')">
              <div class="p-0">
                <notifyRule></notifyRule>
              </div>
            </el-tab-pane> -->
            <!-- =============================================================== -->
            <el-tab-pane label="Token管理" v-if="$store.getters.userPriviagePage('P02-11-2')">
              <div class="p-0">
                <notifyToken @update-setting="refreshSetting"></notifyToken>
              </div>
            </el-tab-pane>
            <!-- =============================================================== -->
            <el-tab-pane label="發送設定" v-if="$store.getters.userPriviagePage('P02-11-3')">
              <div class="p-0">
                <notifySetting ref="notifySetting"></notifySetting>
              </div>
            </el-tab-pane>
            <!-- =============================================================== -->
            <el-tab-pane label="發送紀錄" v-if="$store.getters.userPriviagePage('P02-11-4')">
              <div class="p-0">
                <notifyLog></notifyLog>
              </div>
            </el-tab-pane>
            <!-- =============================================================== -->
          </el-tabs>
          <!-- =============================================================== -->
        </div>
      <!-- =============================================================== -->
    </div>
    </div>
  </template>
  <script>
  
  import { getSystemStorageSetting, postSystemStorageSetting, postModbusControl, getAllSchedule } from '@/api/Api.js';
  import Schedule from './Schedule.vue';
  import notifyRule from '@/views/page/c13_systemsetting/notifyRule.vue';
  import notifyToken from '@/views/page/c13_systemsetting/notifyToken.vue';
  import notifySetting from '@/views/page/c13_systemsetting/notifySetting.vue';
  import notifyLog from '@/views/page/c13_systemsetting/notifyLog.vue';
  
  export default {
    name: 'SystemConfig',
    props: {},
    components: {
      notifyRule,
      notifyToken,
      notifySetting,
      notifyLog,
    },
    data() {
      return {
      }
    },
    watch: {
  
    },
    mounted() {
    },
  
    computed: {
  
    },
    methods: {
      refreshSetting() {
        this.$refs.notifySetting.getNotifyToken();
      }
    },
    created() {},
  }
  </script>
  