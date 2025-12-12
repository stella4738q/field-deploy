<template>

    <div class="p-1 sizeXLarge card border-0 shadow-sm">
      <div class="card-body">
        <h1 class="mb-2">即時訊息通知設定</h1>
        <!-- =============================================================== -->
        <div class="p-0">
          <el-tabs type="card">
            <!-- =============================================================== -->
            <!-- <el-tab-pane label="規則設定" v-if="$store.getters.userPriviagePage('P02-12-1')">
              <div class="p-0">
                <notifyRule></notifyRule>
              </div>
            </el-tab-pane> -->
            <!-- =============================================================== -->
            <el-tab-pane label="Token管理" v-if="$store.getters.userPriviagePage('P02-12-2')">
              <div class="p-0">
                <notifyToken @update-setting="refreshSetting"></notifyToken>
              </div>
            </el-tab-pane>
            <!-- =============================================================== -->
            <el-tab-pane label="發送設定" v-if="$store.getters.userPriviagePage('P02-12-3')">
              <div class="p-0">
                <notifySetting ref="notifySetting"></notifySetting>
              </div>
            </el-tab-pane>
            <!-- =============================================================== -->
            <el-tab-pane label="發送紀錄" v-if="$store.getters.userPriviagePage('P02-12-4')">
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
  import notifyRule from '@/views/page/msg_setting/notifyRule.vue';
  import notifyToken from '@/views/page/msg_setting/notifyToken.vue';
  import notifySetting from '@/views/page/msg_setting/notifySetting.vue';
  import notifyLog from '@/views/page/msg_setting/notifyLog.vue';
  
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
  