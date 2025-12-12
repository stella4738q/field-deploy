<template>
    <div class="p-5">
        <h1 class="mb-5">步階排程</h1>

        <div class="row">
            <div class="d-flex justify-content-between align-items-center mt-3">
                <!-- <el-table size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle"> -->
                <el-table :data="DataSource" size="small" stripe border class="rounded-3"
                    header-cell-class-name="tableHeaderStyle">
                    <el-table-column label="報價代碼" prop="case_id" align="center">
                        <template #default="scope">
                            {{ CaseList.find(x => { return x.case_id == scope.row.case_id })?.code }}
                        </template>
                    </el-table-column>
                    <el-table-column label="腳本" prop="scenario_id" align="center">
                        <template #default="scope">
                            {{ ScenarioList.find(x => { return x._id == scope.row.scenario_id })?.code }}
                        </template>
                    </el-table-column>
                    <el-table-column label="執行時間" prop="start_time" align="center">
                        <template #default="scope">
                            {{ scope.row.start_time }} ~ {{ scope.row.end_time }}
                        </template>
                    </el-table-column>
                    <el-table-column label="循環" prop="repeat" align="center">
                        <template #default="scope">
                            {{ scope.row.repeat === false ? '否' : '是' }}
                        </template>
                    </el-table-column>

                    <el-table-column label="操作" align="center" width="120px">
                        <template v-slot:header>
                            <div class="text-center">
                                <el-button type="info" size="small" plain @click="handleCreate">
                                    <font-awesome-icon icon="add" />
                                </el-button>
                            </div>
                        </template>

                        <template #default="scope">
                            <el-button size="small" @click="handleEdit(scope.$index, scope.row)">
                                <font-awesome-icon icon="edit" />
                            </el-button>
                            <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">
                                <font-awesome-icon icon="trash-alt" />
                            </el-button>
                        </template>
                    </el-table-column>

                </el-table>
            </div>
        </div>

        <el-dialog :title="edit_mode == false ? '新增排程' : '修改排程'" v-model="show_form" width="600px" :show-close="false">

            <el-form :model="Form" :rules="Form_rules" ref="Form" label-width="auto">

                <el-form-item label="報價代碼" prop="case_id">
                    <el-select v-model="Form.case_id" placeholder="請選擇" clearable filterable class="me-2">
                        <el-option v-for="item in CaseList" :key="item.case_id" :label="item.code" :value="item.case_id">
                            {{ item.code }} - {{ item.service }}
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="腳本" prop="scenario_id">
                    <el-select v-model="Form.scenario_id" placeholder="請選擇" clearable filterable class="me-2">
                        <el-option v-for="item in ScenarioList" :key="item._id" :label="item.code" :value="item._id">
                            {{ item.code }}
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="執行時間" prop="date">
                    <el-date-picker v-model="Form.date" type="datetimerange" range-separator="To"
                        value-format="YYYYMMDDHHmmss" />
                </el-form-item>
                <el-form-item label="循環" prop="repeat">
                    <el-switch v-model="Form.repeat" active-color="#13ce66" :active-value="1" inactive-color="#B3B3B3"
                        :inactive-value="0">
                    </el-switch>
                </el-form-item>


            </el-form>


            <template #footer class="dialog-footer" align="end">
                <el-button @click="Form_Cancel">
                    <font-awesome-icon icon="times" />
                </el-button>
                <el-button type="primary" @click="Form_Submit">
                    <font-awesome-icon icon="check" />
                </el-button>
            </template>

        </el-dialog>

</div>
</template>

<script>




import {
    getScenarioSchedule, postScenarioSchedule, delScenarioSchedule, getCaseOption, getSystemStepScenario, getResourceByCaseID
} from '@/api/Api.js';
import moment from 'moment';
import EnumList from '@/JSON/EnumList.json'
import * as echarts from "echarts";


export default {
    components: {
    },
    data() {
        return {
            moment,
            edit_mode: false,
            show_form: false,
            formLabelWidth: '100px',
            CaseList: [],
            ScenarioList: [],
            DataSource: [],
            Form_rules: {
                date: [{ type: 'array', required: true, message: ' ', trigger: 'blur' }],
                case_id: [
                    { required: true, message: '請輸入報價代碼', trigger: 'blur' },
                ],
                scenario_id: [
                    { required: true, message: '請輸入腳本名稱', trigger: 'blur' },
                ],
            },
            Form: {
                _id: '',
                date: [],
                case_id: '',
                scenario_id: '',
                repeat: '',
            },
            Form_temp: {
                _id: '',
                date: [],
                case_id: '',
                scenario_id: '',
                repeat: '',
            },
            ApiResult: {
                // getCaseOption: [],
                getResourceByCaseID: [],
            }
        };
    },
    computed: {
        ApiRequest: function () {
            return {
                getScenarioSchedule: {
                },
            }
        },

    },
    mounted() {
        this.getCase();
    },
    created() {
        const vm = this;
        vm.getData();
        vm.getCase();
        vm.getScenario();
    },
    watch: {
    },
    methods: {
        getScenario() {
            const vm = this;
            vm.ScenarioList = [];
            getSystemStepScenario()
                .then(resopnse => {
                    if (resopnse.data.message == "Success") {
                        vm.ScenarioList = resopnse.data.data;

                    } else {
                        vm.$message({ type: 'error', message: resopnse.data.message });
                    }
                }).catch(response => {
                    vm.$message({ type: 'error', message: response.message });
                }).finally(() => {
                });
        },
        getCase() {
            const vm = this;
            vm.CaseList = [];
            getCaseOption()
                .then(resopnse => {
                    if (resopnse.data.message == "Success") {
                        vm.CaseList = resopnse.data.data;

                    } else {
                        vm.$message({ type: 'error', message: resopnse.data.message });
                    }
                }).catch(response => {
                    vm.$message({ type: 'error', message: response.message });
                }).finally(() => {
                });
        },

        getData() {
            const vm = this;
            vm.$loading();
            getScenarioSchedule(vm.ApiRequest.getScenarioSchedule)
                .then(resopnse => {
                    if (resopnse.data.message == "Success") {
                        vm.DataSource = resopnse.data.data;
                    } else {
                        vm.$message({ type: 'error', message: resopnse.data.message });
                    }
                }).catch(resopnse => {
                    vm.$message({ type: 'error', message: resopnse.message });
                }).finally(() => {
                    vm.$loading().close();
                });
        },

        PageChanged(ind, Controller) {
            Controller.pageInd = ind;
            var sliceBegin = (Controller.pageInd - 1) * Controller.countPerPage;
            var sliceEnd = (Controller.pageInd) * Controller.countPerPage;
            Controller.CurrentData = Controller.DataSource.slice(sliceBegin, sliceEnd);
        },
        handleCreate() {
            this.edit_mode = false;
            Object.assign(this.Form, this.Form_temp);
            this.show_form = true;
        },
        handleEdit(index, row) {
            this.edit_mode = true;
            Object.assign(this.Form, row);
            this.Form.id = row.id
            this.Form.date = [row.start_time, row.end_time]
            this.show_form = true;
        },
        handleDelete(index, row) {
            var vm = this;
            if (confirm('您確定刪除排程?')) {
                var post_data = {
                    'id': row._id
                }
                delScenarioSchedule(post_data).then((response) => {
                    if (response.data.message == 'Success') {
                        vm.getData();
                        vm.$message({ type: 'success', message: '刪除成功', center: true, });
                    }
                    else {
                        vm.$message({ type: 'error', message: response.data.message, center: true, });
                    }
                });
            }
        },

        Form_Submit() {
            const vm = this;
            vm.data_step = [];
            vm.$refs['Form'].validate((valid) => {
                if (valid) {
                    if (this.edit_mode) {
                        //Update
                        var post_data = {
                            '_id': vm.Form._id,
                            'case_id': vm.Form.case_id,
                            'scenario_id': vm.Form.scenario_id,
                            'start_time': vm.Form.date[0],
                            'end_time': vm.Form.date[1],
                            'repeat': vm.Form.repeat,
                        }
                        postScenarioSchedule(post_data).then((response) => {
                            if (response.data.message == 'Success') {
                                vm.getData();
                                vm.Form_Cancel();
                                vm.$message({ type: 'success', message: '修改成功', center: true, });
                            }
                            else {
                                vm.$message({ type: 'error', message: response.data.message, center: true, });
                            }
                        });
                    }
                    else {
                        //Create
                        var post_data = {
                            'case_id': vm.Form.case_id,
                            'scenario_id': vm.Form.scenario_id,
                            'start_time': vm.Form.date[0],
                            'end_time': vm.Form.date[1],
                            'repeat': vm.Form.repeat,
                        }
                        postScenarioSchedule(post_data).then((response) => {
                            if (response.data.message == 'Success') {
                                var data = response.data.data;
                                vm.data_step.push({
                                    '_id': data[0]._id,
                                    'case_id': data[0].case_id,
                                    'scenario_id': data[0].scenario_id,
                                    'start_time': data[0].start_time,
                                    'end_time': data[0].end_time,
                                    'repeat': data[0].repeat,
                                })
                                vm.getData();
                                vm.Form_Cancel();
                                vm.$message({ type: 'success', message: '新增成功', center: true, });
                            }
                            else {
                                vm.$message({ type: 'error', message: response.data.message, center: true, });
                            }
                        });
                    }
                } else {
                    return false;
                }
            });
        },
        Form_Cancel() {
            this.show_form = false;
            Object.assign(this.Form, this.Form_temp);
        },

    },
};
</script>

<style>
.previewDialog.el-dialog .el-dialog__header {
    display: none;
}

.previewDialog.el-dialog .dj-dialog-content {
    padding: 0;
    overflow: unset;
}
</style>
