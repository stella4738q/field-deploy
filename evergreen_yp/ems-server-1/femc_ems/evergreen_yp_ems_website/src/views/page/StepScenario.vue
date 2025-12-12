<template>
    <div class="p-5">
        <h1 class="mb-5">步階腳本</h1>

        <div class="row">
            <div class="d-flex justify-content-between align-items-center mt-3">
                <!-- <el-table size="small" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle"> -->
                <el-table :data="PageController.CurrentData" size="small" stripe border class="rounded-3"
                    header-cell-class-name="tableHeaderStyle">
                    <el-table-column label="代碼" prop="code" align="center"></el-table-column>
                    <el-table-column label="名稱" prop="name" align="center"></el-table-column>
                    <el-table-column label="每步驟持續時間" prop="step_second" align="center"></el-table-column>
                    <el-table-column label="n步驟" prop="data" align="center">
                        <template #default="scope">
                            {{ scope.row.data?.length }}
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
                <!-- <div class="d-flex justify-content-end">
                    <el-pagination layout="prev, pager, next" v-model:currentPage="PageController.pageInd"
                        :page-size="PageController.countPerPage" :total="PageController.DataSource.length"
                        @current-change="(ind) => { PageChanged(ind, PageController) }" />
                </div> -->
            </div>
        </div>


        <el-dialog :title="edit_mode == false ? '新增腳本' : '修改腳本'" v-model="show_form" width="600px" :show-close="false">

            <el-form :model="Form" :rules="Form_rules" ref="Form" label-width="auto">


                <el-form-item label="代碼" prop="code">
                    <el-input v-model="Form.code" autocomplete="off"></el-input>
                </el-form-item>
                <el-form-item label="名稱" prop="name">
                    <el-input v-model="Form.name" autocomplete="off"></el-input>
                </el-form-item>
                <el-form-item label="每步驟持續時間" prop="step_second">
                    <el-input type="number" v-model.number="Form.step_second" autocomplete="off"></el-input>
                </el-form-item>


                <el-table :data="Form.data" size="small" stripe border class="rounded-3"
                    header-cell-class-name="tableHeaderStyle">

                    <el-table-column label="頻率" prop="freq" align="center">
                        <template #default="scope">
                            <el-input type="number" v-model.number="scope.row.freq" autocomplete="off"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column label="中心頻率" prop="freq_center" align="center">
                        <template #default="scope">
                            <el-input type="number" v-model.number="scope.row.freq_center"
                                autocomplete="off"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" align="center" width="120px">
                        <template v-slot:header>
                            <div class="text-center">
                                <el-button type="info" size="small" plain @click="add">
                                    <font-awesome-icon icon="add" />
                                </el-button>
                            </div>
                        </template>
                        <template #default="scope">
                            <el-button size="small" type="danger" @click="deleteRow(scope.$index)">
                                <font-awesome-icon icon="trash-alt" />
                            </el-button>
                        </template>
                    </el-table-column>

                </el-table>

            </el-form>


            <template #footer>
                <div  class="dialog-footer" align="end">
                    <el-button @click="Form_Cancel">
                        <font-awesome-icon icon="times" />
                    </el-button>
                    <el-button type="primary" @click="Form_Submit">
                        <font-awesome-icon icon="check" />
                    </el-button>
                </div>
            </template>

        </el-dialog>

    </div>
</template>

<script>

import {
    getSystemStepScenario, postSystemStepScenario, delSystemStepScenario
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
            PageController: {
                pageInd: 1,
                countPerPage: 10,
                total: 0,
                CurrentData: [],
                DataSource: [],
            },
            Form_rules: {
                code: [
                    { required: true, message: '請輸入腳本代碼', trigger: 'blur' },
                ],
                name: [
                    { required: true, message: '請輸入腳本名稱', trigger: 'blur' },
                ],
            },
            Form: {
                _id: '',
                code: '',
                name: '',
                step_second: '',
                data: [],
            },
            Form_temp: {
                _id: '',
                code: '',
                name: '',
                step_second: '',
                data: [],
            },
        };
    },
    computed: {
        ApiRequest: function () {
            return {
                getSystemStepScenario: {
                }
            }
        },

    },
    mounted() {
    },
    created() {
        const vm = this;
        vm.getData();
    },
    watch: {
    },
    methods: {
        getData() {
            const vm = this;
            vm.$loading();
            getSystemStepScenario(vm.ApiRequest.getSystemStepScenario)
                .then(resopnse => {
                    if (resopnse.data.message == "Success") {
                        vm.PageController.DataSource = resopnse.data.data;
                        vm.PageChanged(1, vm.PageController);
                    } else {
                        vm.$message({ type: 'error', message: resopnse.data.message });
                    }
                }).catch(resopnse => {
                    vm.$message({ type: 'error', message: resopnse.message });
                }).finally(() => {
                    vm.$loading().close();
                });
        },
        SearchClick() {
            const vm = this;
            vm.data_step = [];
            getSystemStepScenario({
                '_id': null,
                'code': null,
                'name': null,
                'step_second': null,
                'data': null
            }).then((response) => {
                if (response.data.message == 'Success') {
                    var data = response.data.data;
                    for (var i in data) {
                        vm.data_step.push({
                            '_id': data[i]._id,
                            'code': data[i].code,
                            'name': data[i].name,
                            'step_second': data[i].step_second,
                            'data': data[i].data,
                        })
                    }
                }
                else {
                    vm.$message({ type: 'error', message: response.data.message, center: true, });
                }
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
            this.show_form = true;
        },
        handleDelete(index, row) {
            var vm = this;
            if (confirm('您確定刪除執行腳本?')) {
                var post_data = {
                    '_id': row._id
                }
                delSystemStepScenario(post_data).then((response) => {
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
            vm.$refs['Form'].validate((valid) => {
                if (valid) {
                    if (this.edit_mode) {
                        //Update
                        var post_data = {
                            '_id': vm.Form._id,
                            'code': vm.Form.code,
                            'name': vm.Form.name,
                            'step_second': vm.Form.step_second,
                            'data': vm.Form.data,
                        }
                        postSystemStepScenario(post_data).then((response) => {
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
                            'code': vm.Form.code,
                            'name': vm.Form.name,
                            'step_second': vm.Form.step_second,
                            'data': vm.Form.data,
                        }
                        postSystemStepScenario(post_data).then((response) => {
                            if (response.data.message == 'Success') {
                                var data = response.data.data;
                                vm.data_step.push({
                                    '_id': data[0]._id,
                                    'code': data[0].code,
                                    'name': data[0].name,
                                    'step_second': data[0].step_second,
                                    'data': data[0].data,
                                })
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

        add() {
            this.Form.data.push({ freq: null, freq_center: null });
        },
        deleteRow(index) {//删除改行
            this.Form.data.splice(index, 1);
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