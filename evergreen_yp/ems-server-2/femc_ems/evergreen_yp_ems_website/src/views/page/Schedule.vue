<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <div class="p-3">
        <div class="d-flex justify-content-between">
          <h1>充放電 排程表清單</h1>
          <el-button @click="addSchDialog.show = true" :disabled="nowIsEditing" v-if="$store.getters.userPriviage('p_00040')">
            <font-awesome-icon icon="plus" />
          </el-button>
        </div>
        <!-- =========================== -->
        <el-table :data="ApiResult.scheduleTables" size="small" class="rounded-3" header-cell-class-name="tableHeaderStyle" stripe border>
          <el-table-column width="140" label="排程表名稱" sortable prop="name" align="center">
            <template #default="scope">
              <el-link type="primary" @click="Edit(scope.row)">{{ scope.row['name'] }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="備註" sortable prop="memo" align="center"></el-table-column>
          <el-table-column width="180" label="操作" align="center">
            <template #default="scope">
              <el-button size="small" @click="Edit(scope.row)" :disabled="nowIsEditing" v-if="$store.getters.userPriviage('p_00041')">
                <font-awesome-icon icon="edit" />
              </el-button>
              <!-- =========================== -->
              <el-popconfirm title="確定刪除？" @confirm="DeleteSchSend(scope.row)" v-if="$store.getters.userPriviage('p_00042')">
                <template #reference>
                  <el-button size="small" type="danger" :disabled="nowIsEditing">
                    <font-awesome-icon icon="trash-alt" />
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <!-- =========================== -->
      <div class="p-2">
        <div v-if="nowIsEditing">
          <div class="d-flex justify-content-between">
            <h1>{{ this.nowEdit.name }} 排程表編輯</h1>
            <el-button type="danger" @click="editModeClose" plain>
              <font-awesome-icon icon="times" class="me-2" />取消編輯
            </el-button>
          </div>
          <ScheduleTable v-if="nowEditId" :dataId="nowEditId" :Editable="true"></ScheduleTable>
        </div>
        <el-alert v-if="!nowIsEditing" title="請選擇排程表" type="info" :closable="false" show-icon />
      </div>
    </div>
  </div>
  <!-- =========================== -->
  <el-dialog title="新增排程表" center v-model="addSchDialog.show" :close-on-click-modal="false" :show-close="false"
    width="400px">
    <el-form :model="addSchDialog.data" ref="Form" label-width="auto">
      <el-form-item label="排程表名稱" prop="name">
        <el-input v-model="addSchDialog.data.name" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="備註" prop="memo">
        <el-input v-model="addSchDialog.data.memo" autocomplete="off"></el-input>
      </el-form-item>
      <div class="dialog-footer mt-5 text-center">
        <el-button @click="addSchDialog.show = false">
          <font-awesome-icon icon="circle-xmark" />
        </el-button>
        <el-button type="primary" @click="AddScheduleSend"
          :disabled="!addSchDialog.data.name || !addSchDialog.data.memo">
          <font-awesome-icon icon="circle-check" />
        </el-button>
      </div>
    </el-form>
  </el-dialog>
  <!-- =========================== -->
</template>
<script>

import ScheduleTable from '@/components/Schedule.vue';
import { getAllSchedule, postSchedule, delSchedule } from '@/api/Api.js';

export default {
  name: 'Schedule',
  props: {
    Editable: {
      type: Boolean,
      default: true
    }
  },
  components: {
    ScheduleTable
  },
  data() {
    return {
      addSchDialog: {
        show: false,
        data: {
          name: null,
          memo: null,
        },
      },
      ApiResult: {
        scheduleTables: [
          {
            _id: '',
            name: '123',
            memo: '111',
          }
        ],
      },
      nowEdit: null,
      nowEditId: null,
    }
  },
  watch: {

  },

  mounted() {
    this.getAllSch();
  },
  computed: {
    nowIsEditing() {
      return this.nowEdit !== null && this.nowEditId !== null
    },
  },
  methods: {
    getAllSch() {
      const vm = this;
      getAllSchedule()
        .then(response => {
          vm.ApiResult.scheduleTables = response.data.data;
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        });
    },
    AddScheduleSend() {
      const vm = this;
      postSchedule(this.addSchDialog.data)
        .then(response => {
          if (response.data.message == "Success") {
            vm.getAllSch();
            vm.$message({ type: 'success', message: '新增排程成功', center: true, });
            vm.addSchDialog.show = false;
            vm.addSchDialog.data = {
              name: null,
              memo: null,
            };
          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        });
    },
    DeleteSchSend(row) {
      const vm = this;
      delSchedule({ id: row['_id'] })
        .then(response => {
          if (response.data.message == "Success") {
            vm.getAllSch();
            vm.$message({ type: 'success', message: '刪除排程成功', center: true, });
            //

          } else {
            vm.$message({ type: 'error', message: response.data.message });
          }
        })
        .catch(response => {
          vm.$message({ type: 'error', message: response.message });
        });
    },
    editModeClose() {
      this.nowEdit = null;
      this.nowEditId = null;
    },
    //
    Edit(row) {
      // console.log(row);
      this.nowEdit = JSON.parse(JSON.stringify(row));
      this.nowEditId = row['_id'];
    },
  },
}
</script>

<style scoped></style>