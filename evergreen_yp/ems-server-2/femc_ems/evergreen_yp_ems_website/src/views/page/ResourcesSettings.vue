<template>

    <div class="card shadow-sm border-0">
        <div class="card-body">
            <h5 class="fw-bolder">資源設定</h5>
            <el-table height="643" :data="data_equipments" size="small" class="rounded-3" header-cell-class-name="tableHeaderStyle" row-key="_id" highlight-current-row
                @current-change="HandleCurrentChange" ref="tbeq" stripe border>
                <el-table-column width="140" label="設備名稱" sortable prop="name" align="center"></el-table-column>
                <el-table-column width="140" label="設備代碼" sortable prop="code" align="center"></el-table-column>
                <el-table-column width="140" label="設備類型" sortable prop="equipment_type" align="center">
                    <template #default="scope">
                        {{ EquipmentType.find(x => { return x.id == scope.row.equipment_type })?.label }}
                    </template>
                </el-table-column>
                <el-table-column width="140" label="廠牌" sortable prop="brand" align="center"></el-table-column>
                <el-table-column width="180" label="ip" sortable prop="ip" align="center"></el-table-column>
                <el-table-column width="120" label="port" sortable prop="port" align="center"></el-table-column>
                <el-table-column width="120" label="容量" sortable prop="capacity" align="center">
                    <template #default="scope">
                        {{ scope.row.capacity }}
                    </template>
                </el-table-column>
                <el-table-column width="160" label="base address" sortable prop="base_address" align="center"></el-table-column>
                <!-- <el-table-column label="unit id" sortable prop="unit_id" align="center"></el-table-column> -->
                <el-table-column width="140" label="操作" align="center">
                    <template #default="scope">
                        <el-button size="small" @click="handleEdit(scope.$index, scope.row)" v-if="$store.getters.userPriviage('p_00028')">
                            <font-awesome-icon icon="edit" />
                        </el-button>
                        <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)" v-if="$store.getters.userPriviage('p_00028')">
                            <font-awesome-icon icon="trash-alt" />
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </div>

    <el-dialog :title="edit_mode == false ? '新增設備' : '修改設備'" v-model="show_form" :width="dialogWidth" :show-close="false">
        <el-form :model="Form" :rules="Form_rules" ref="Form">
            <el-form-item label="上層設備" :label-width="formLabelWidth" prop="parent_id">
                <el-select v-model="Form.parent_id" placeholder="請選擇..." :disabled="true">
                    <el-option v-for="item in option_parent_equipment" :key="item.id" :value="item.id"
                        :label="item.label">
                        {{ item.label }}
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="設備名稱" :label-width="formLabelWidth" prop="name">
                <el-input v-model="Form.name" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="設備代碼" :label-width="formLabelWidth" prop="code">
                <el-input v-model="Form.code" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="設備類型" :label-width="formLabelWidth" prop="">
                <el-select v-model="Form.equipment_type" placeholder="請選擇...">
                    <el-option v-for="item in EquipmentType" :key="item.id" :value="item.id" :label="item.label">
                        {{ item.label }}
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="廠牌" :label-width="formLabelWidth" prop="brand">
                <el-input v-model="Form.brand" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="ip" :label-width="formLabelWidth" prop="ip">
                <el-input v-model="Form.ip" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="port" :label-width="formLabelWidth" prop="port">
                <el-input type="number" v-model.number="Form.port" autocomplete="off" />
            </el-form-item>
            <el-form-item label="容量" :label-width="formLabelWidth" prop="capacity">
                <el-input type="number" v-model.number="Form.capacity" autocomplete="off" />
            </el-form-item>
            <el-form-item label="base address" :label-width="formLabelWidth" prop="base_address">
                <el-input type="number" v-model.number="Form.base_address" autocomplete="off" />
            </el-form-item>
            <el-form-item label="unit id" :label-width="formLabelWidth" prop="unit_id">
                <el-input type="number" v-model.number="Form.unit_id" autocomplete="off" />
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

</template>

<script>
    import { getCaseOption, getFields, getSystemEquipments, postSystemEquipments, delSystemEquipments } from '@/api/Api.js'
    export default {
        components: {
        },
        data() {
            return {
                dialogWidth: '90%',
                CaseList: [],
                formLabelWidth: '100px',
                currentRow: null,
                edit_mode: false,
                show_form: false,
                data_fields: [],
                data_equipments: [],
                option_parent_equipment: [],
                SearchName: '',
                Form: {
                    id: '',
                    equipment_type: '',
                    code: '',
                    name: '',
                    parent_id: '',
                    brand: '',
                    ip: '',
                    port: '',
                    capacity: '',
                    base_address: '',
                    unit_id: '',
                },
                Form_temp: {
                    id: '',
                    equipment_type: '',
                    code: '',
                    name: '',
                    parent_id: '',
                    brand: '',
                    ip: '',
                    port: '',
                    capacity: '',
                    base_address: '',
                    unit_id: '',
                },
                Form_rules: {
                    equipment_type: [
                        { required: true, message: '請輸入設備種類', trigger: 'blur' },
                    ],
                    code: [
                        { required: true, message: '請輸入設備代碼', trigger: 'blur' },
                    ],
                    name: [
                        { required: true, message: '請輸入設備名稱', trigger: 'blur' },
                    ]
                },
                EquipmentType: [
                    {
                        'id': 0,
                        'label': 'CABINET'
                    },
                    {
                        'id': 1,
                        'label': 'PCS'
                    },
                    {
                        'id': 2,
                        'label': 'BMS'
                    },
                    {
                        'id': 3,
                        'label': 'RACK'
                    },
                    {
                        'id': 4,
                        'label': 'METER'
                    },
                    {
                        'id': 5,
                        'label': 'AIR'
                    },
                    {
                        'id': 6,
                        'label': 'FIRE'
                    },
                    {
                        'id': 7,
                        'label': 'DOOR'
                    },
                    {
                        'id': 8,
                        'label': 'INVERTER'
                    },
                    {
                        'id': 9,
                        'label': 'UPS'
                    }
                ]
            };
        },
        mounted() {
            window.onresize = () => {
                return (() => {
                    this.setDialogWidth();
            })();
            };
        },
        created() {
            var vm = this;
            vm.GetAllEquipment();
        },
        watch: {
        },
        methods: {
            setDialogWidth() {
                let windowSize = document.body.clientWidth;
                const defaultWidth = 600; // 預設寬度
                if (windowSize < 767) {
                    this.dialogWidth = "85%";
                } else {
                    this.dialogWidth = defaultWidth + "px";
                }
            },
            getCase() {
                const vm = this;
                vm.CaseList = [];
                getCaseOption().then(resopnse => {
                    if (resopnse.data.message == "Success") {
                        vm.CaseList = resopnse.data.data;

                    } else {
                        console.error(response);
                        vm.$message({ type: 'error', message: resopnse.data.message });
                    }
                }).catch(response => {
                    console.error(response);
                    vm.$message({ type: 'error', message: response.message });
                }).finally(() => {
                });
            },
            GetAllEquipment() {
                const vm = this;
                vm.data_equipments = [];
                getSystemEquipments({
                }).then((response) => {
                    if (response.data.message == 'Success') {
                        var data = response.data.data;
                        vm.option_parent_equipment = data.map(item => { return { id: item._id, label: item.name } })
                        if (data && data.length > 0) {
                            var temp_data = [];
                            var group_parent = this.GroupBy(data, 'parent_id');

                            var base_data = group_parent['None'];
                            base_data.forEach((item, i) => {
                                item = vm.LookupChildren(vm, group_parent, item);
                                temp_data.push(item);
                            })
                            vm.data_equipments = temp_data
                        }
                    }
                    else {
                        console.error(response);
                        vm.$message({ type: 'error', message: response.data.message, center: true, });
                    }
                });
            },
            GroupBy(objectArray, property) {
                return objectArray.reduce((acc, obj) => {
                    const key = obj[property];
                    if (!acc[key]) {
                        acc[key] = [];
                    }
                    acc[key].push(obj);
                    return acc;
                }, {});
            },
            LookupChildren(vm, group_data, item) {
                var target = vm.data_fields.find(d => d.id == item.field_id);
                item.field_name = target ? target.label : '';
                var children = group_data[item._id];
                if (children) {
                    children.forEach((c, i) => {
                        vm.LookupChildren(vm, group_data, c)
                    });
                    item['children'] = children;
                }
                return item;
            },
            GetChildrenID(vm, target) {
                var rtnlist = []
                rtnlist.push(target._id);
                var children = target.children;
                if (children) {
                    for (var i in children) {
                        var addList = vm.GetChildrenID(vm, children[i])
                        for (var x in addList)
                            rtnlist.push(addList[x]);
                    }
                }
                return rtnlist;
            },
            SearchClick() {
                const vm = this;
                vm.data_equipments = [];
                getSystemEquipments({
                    'name': vm.SearchName,
                }).then((response) => {
                    if (response.data.message == 'Success') {
                        var data = response.data.data;
                        if (data && data.length > 0) {
                            var temp_data = [];
                            var group_parent = this.GroupBy(data, 'parent_id');

                            var base_data = group_parent['nan'];
                            base_data.forEach((item, i) => {
                                item = vm.LookupChildren(vm, group_parent, item);
                                temp_data.push(item);
                            })
                            vm.data_equipments = temp_data
                        }
                    }
                    else {
                        console.error(response);
                        vm.$message({ type: 'error', message: response.data.message, center: true, });
                    }
                });
            },
            handleEdit(index, row) {
                this.edit_mode = true;
                Object.assign(this.Form, row);
                this.Form.id = row.id
                this.show_form = true;
            },
            handleDelete(index, row) {
                var vm = this;
                if (confirm('您確定刪除設備(子階層將一併被刪除)?')) {
                    var idList = vm.GetChildrenID(vm, row);
                    var errList = [];
                    for (var i in idList) {
                        var post_data = {
                            'id': idList[i]
                        }
                        delSystemEquipments(post_data).then((response) => {
                            if (response.data.message == 'Success') {
                                vm.SearchClick();
                                vm.currentRow = null;
                                vm.option_parent_equipment = [];
                            }
                            else {
                                errList.push(response.data.message);
                                console.error(response);
                                vm.$message({ type: 'error', message: response.data.message, center: true, });
                            }
                        });
                    }
                    if (errList.length == 0)
                        vm.$message({ type: 'success', message: '刪除成功', center: true, });
                }
            },
            handleCreate() {
                Object.assign(this.Form, this.Form_temp);
                this.option_parent_equipment = []
                if (this.currentRow) {
                    this.option_parent_equipment.push({
                        'id': this.currentRow._id,
                        'label': this.currentRow.name
                    })
                    this.Form.parent_id = this.currentRow._id;
                    this.Form.field_id = this.currentRow.field_id;
                    this.Form.field_name = this.currentRow.field_name;
                }

                this.edit_mode = false;
                this.show_form = true;
            },
            Form_Submit() {
                const vm = this;
                vm.$refs['Form'].validate((valid) => {
                    if (valid) {
                        if (this.edit_mode) {
                            //Update Field
                            var post_data = {
                                '_id': vm.Form._id,
                                'field_id': vm.Form.field_id,
                                'parent_id': vm.Form.parent_id,
                                'equipment_type': vm.Form.equipment_type,
                                'code': vm.Form.code,
                                'name': vm.Form.name,
                                'case_id': vm.Form.case_id,
                                'brand': vm.Form.brand,
                                'ip': vm.Form.ip,
                                'port': vm.Form.port,
                                'capacity': vm.Form.capacity,
                                'base_address': vm.Form.base_address,
                                'unit_id': vm.Form.unit_id,
                            }
                            postSystemEquipments(post_data).then((response) => {
                                if (response.data.message == 'Success') {
                                    vm.SearchClick();
                                    vm.Form_Cancel();
                                    vm.$message({ type: 'success', message: '修改成功', center: true, });
                                }
                                else {
                                    console.error(response);
                                    vm.$message({ type: 'error', message: response.data.message, center: true, });
                                }
                            });
                        }
                        else {
                            //Create Field
                            var post_data = {
                                '_id': vm.Form._id,
                                'field_id': vm.Form.field_id,
                                'parent_id': vm.Form.parent_id,
                                'equipment_type': vm.Form.equipment_type,
                                'code': vm.Form.code,
                                'name': vm.Form.name,
                                'case_id': vm.Form.case_id,
                                'brand': vm.Form.brand,
                                'ip': vm.Form.ip,
                                'port': vm.Form.port,
                                'capacity': vm.Form.capacity,
                                'base_address': vm.Form.base_address,
                                'unit_id': vm.Form.unit_id,
                            }
                            postSystemEquipments(post_data).then((response) => {
                                if (response.data.message == 'Success') {
                                    vm.SearchClick();
                                    vm.Form_Cancel();
                                    vm.$message({ type: 'success', message: '新增成功', center: true, });
                                }
                                else {
                                    console.error(response);
                                    vm.$message({ type: 'error', message: response.data.message, center: true, });
                                }
                            });
                        }
                        vm.currentRow = null;
                        vm.option_parent_equipment = [];
                    } else {
                        return false;
                    }
                });
            },
            Form_Cancel() {
                this.show_form = false;
                this.currentRow = null;
                this.option_parent_equipment = [];
                Object.assign(this.Form, this.Form_temp);
            },

            HandleCurrentChange(val) {
                this.currentRow = val;
            }
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