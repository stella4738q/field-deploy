<template>
    <div class="p-3 card border-0 shadow-sm">
        <div class="card-body">
        <h3>角色管理</h3>
        <!-- ============================================================ -->
        <el-form :inline="true" label-position="top" class="align-items-end">
                <el-form-item label="名稱">
                    <el-input v-model="FormSearch.name"> </el-input>
                </el-form-item>
                <el-form-item label="">
                    <el-button type="primary" @click="SearchClick">
                        <font-awesome-icon icon="search" />
                    </el-button>
                </el-form-item>
                <el-form-item label="">
                    <el-button type="primary" @click="AddClick" v-if="$store.getters.userPriviage('p_00052')">
                        <font-awesome-icon icon="add" />
                    </el-button>
                </el-form-item>
        </el-form>
        <!-- ============================================================ -->
        <div>
            <el-table height="643" :data="ApiResult.getRoles" size="small" class="rounded-3" header-cell-class-name="tableHeaderStyle" stripe border>
                <el-table-column width="100" label="名稱" sortable prop="name" align="center"></el-table-column>
                <el-table-column width="100" label="啟用" sortable prop="enable" align="center">
                    <template #default="scope">
                        {{ scope.row.enable === 1 ? '啟用' : '停用' }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" align="center">
                    <template #default="scope">
                        <el-button size="small" @click="Edit(scope.row)" v-if="$store.getters.userPriviage('p_00053')">
                            <font-awesome-icon icon="edit" />
                        </el-button>
                        <el-popconfirm title="確定刪除?" @confirm="Delete(scope.row)" v-if="$store.getters.userPriviage('p_00054')">
                            <template #reference>
                                <el-button size="small" type="danger">
                                    <font-awesome-icon icon="trash-alt" />
                                </el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
        </div>
        <!-- ============================================================ -->
    </div>
    </div>
        <el-dialog :title="Form.id ? '修改角色' : '新增角色'" v-model="Dialog" width="800px" :show-close="false">
            <el-form :model="Form" :rules="FormRules" ref="Form" inline>
                <!-- <el-form-item label="案場" prop="field_id">
                    <el-select v-model="Form.field_id" placeholder="請選擇" clearable filterable :disabled="Form.id ? true : false " >
                        <el-option v-for="item in ApiResult.getFields" :key="item._id" :label="item.name" :value="item._id"/>
                    </el-select>
                </el-form-item> -->
                <el-form-item label="名稱" prop="name">
                    <el-input v-model="Form.name" autocomplete="off"></el-input>
                </el-form-item>
                <el-form-item label="啟用">
                    <el-switch v-model="Form.enable" :active-value="1" active-color="#13ce66" :inactive-value="0"
                        inactive-color="#B3B3B3">
                    </el-switch>
                </el-form-item>
            </el-form>

            <el-tabs v-model="TabName">
                <el-tab-pane v-for="(menu, ind) in BaseFlatPriviage.flatRule" :label="menu.name" :name="menu.name"
                    :key="ind">
                    <div class="row border-bottom">
                        <div class="col-3 p-2 ps-3">功能</div>
                        <div class="col-1 p-2  ps-3">狀態</div>
                        <div class="col p-2  ps-3 ">操作權限</div>
                    </div>
                    <div class="row mb-2 border-bottom" v-for="(menuItem, ind2) in menu.menu" :key="ind2">
                        <div class="col-3 p-2  ps-3">{{ menuItem.name }}</div>
                        <div class="col-1 p-2  ps-3">
                            <el-switch v-model="menuItem.enable" size="small"></el-switch>
                        </div>
                        <div class="col p-2  ps-3">
                            <span v-for=" (api, ind3) in menuItem.api_list" :key="ind3">
                                <span class="me-2">
                                    <el-checkbox v-model="api.enable" :label="api.description" />
                                </span>
                            </span>
                        </div>
                    </div>
                </el-tab-pane>
            </el-tabs>

            <template #footer class="dialog-footer" align="end">
                <el-button @click="Dialog = false">
                    <font-awesome-icon icon="times" />
                </el-button>
                <el-button type="primary" @click="Submit">
                    <font-awesome-icon icon="check" />
                </el-button>
            </template>
        </el-dialog>
</template>

<script>
import flatMenu from '@/lib/flatMenu.js';
import { getRoles, postRoles, deleteRoles, getFields, getPermissionMenuItem } from '@/api/Api.js'
export default {
    components: {
    },
    data() {
        return {

            TabName: null,
            formLabelWidth: '100px',
            Dialog: false,
            BasePriviage: [],
            BaseFlatPriviage: {
                flatRule: [],
                flatApi: [],
            },
            EditPriviage: [],
            EditFlatPriviage: {
                flatRule: [],
                flatApi: [],
            },
            EditItem: {},
            FormSearch: {
                id: null,
                name: '',
                enable: null,
                fields: ''
            },
            FormQuery: {
                id: null,
                name: '',
                enable: null,
                fields: ''
            },
            Form: {
                id: '',
                name: '',
                enable: true,
                field_id: '',
            },
            FormTemplate: {
                id: '',
                name: '',
                enable: true,
                field_id: '',
            },
            FormRules: {
                field_id: [{ required: true, message: ' ', trigger: 'blur' }],
                name: [{ required: true, message: ' ', trigger: 'blur' },]
            },
            ApiResult: {
                getRoles: [],
                getFields: [],
                getPermissionMenuItem: [],
            },
        };
    },
    computed: {
        ApiRequest: function () {
            return {
                getRoles: this.FormQuery,
                postRoles: {
                    id: this.Form.id,
                    name: this.Form.name,
                    enable: this.Form.enable,
                    field_id: this.Form.field_id,
                    menu_items: this.BasePriviage,
                },
                deleteRoles: { id: this.EditItem.id },

            }

        }
    },
    mounted() {

    },
    created() {
        this.Query();
        this.getFieldsData();
        this.getPermissionMenuItemData();
    },
    watch: {
    },
    methods: {

        getPermissionMenuItemData() {
            const vm = this;
            getPermissionMenuItem()
                .then((response) => {
                    if (response.data.Success) {
                        vm.ApiResult.getPermissionMenuItem = response.data.Data;
                    }
                    else {
                        vm.$message({ type: 'error', message: response.data.Msg, center: true, });
                    }
                })
                .catch(response => {
                    vm.$message({ type: 'error', message: response.message, center: true, });
                })
                .finally(() => {
                })
        },
        getFieldsData() {
            const vm = this;
            vm.ApiResult.getFields = [];
            getFields().then(response => {
                vm.FormTemplate.field_id = response.data.data[0]._id;
                response.data.data.forEach(item => {
                    item.id = item._id;
                });
                vm.ApiResult.getFields = response.data.data;
            });
        },
        Query() {
            const vm = this;
            vm.$loading();
            vm.ApiResult.getRoles = [];
            getRoles(vm.ApiRequest.getRoles)
                .then((response) => {
                    if (response.data.Success) {
                        response.data.Data.forEach(item => {
                            item.id = item._id;
                        });
                        vm.ApiResult.getRoles = response.data.Data;
                    }
                    else {
                        vm.$message({ type: 'error', message: response.data.Msg, center: true, });
                    }
                })
                .catch(response => {
                    vm.$message({ type: 'error', message: response.message, center: true, });
                })
                .finally(() => {
                    vm.$loading().close();
                })
        },
        SearchClick() {
            this.FormQuery = JSON.parse(JSON.stringify(this.FormSearch));
            this.Query();
        },
        AddClick() {
            const vm = this;
            vm.Form = Object.assign({}, this.FormTemplate);
            vm.BasePriviage = JSON.parse(JSON.stringify(vm.ApiResult.getPermissionMenuItem));
            vm.BaseFlatPriviage = flatMenu(vm.BasePriviage);

            vm.BaseFlatPriviage.flatRule.forEach(main => {
                main.menu.forEach(x => { x.enable = false; })
            });

            vm.BaseFlatPriviage.flatApi.forEach(main => {
                main.enable = false;
            });
            vm.TabName = vm.BaseFlatPriviage.flatRule[0].name;
            vm.Dialog = true;
        },
        Edit(row) {
            const vm = this;
            vm.EditItem = JSON.parse(JSON.stringify(row));
            vm.BasePriviage = JSON.parse(JSON.stringify(vm.ApiResult.getPermissionMenuItem));
            vm.BaseFlatPriviage = flatMenu(vm.BasePriviage);
            vm.EditPriviage = JSON.parse(JSON.stringify(vm.EditItem.permission));
            vm.EditFlatPriviage = flatMenu(vm.EditPriviage);

            vm.BaseFlatPriviage.flatRule.forEach(main => {

                main.menu.forEach(x => {
                    var find = null;

                    for (var i = 0; i < vm.EditFlatPriviage.flatRule.length; i++) {
                        find = vm.EditFlatPriviage.flatRule[i].menu.find(xx => { return x.code == xx.code });
                        if (find) {
                            break;
                        }
                    }
                    x.enable = find ? find.enable : false;
                })
            });

            vm.BaseFlatPriviage.flatApi.forEach(main => {
                var find = vm.EditFlatPriviage.flatApi.find(x => { return x.code == main.code });
                main.enable = find ? find.enable : false;
            });

            Object.assign(vm.Form, row);
            vm.Form.id = row.id;
            vm.TabName = vm.BaseFlatPriviage.flatRule[0].name;
            vm.Dialog = true;
        },
        Delete(row) {
            var vm = this;
            deleteRoles({ 'id': row.id }).then((response) => {
                if (response.data.Success) {
                    vm.Query();
                    vm.$message({ type: 'success', message: '刪除成功', center: true, });
                }
                else {
                    vm.$message({ type: 'error', message: response.data.Msg, center: true, });
                }
            });
        },
        Submit() {
            const vm = this;

            vm.$refs['Form'].validate((valid) => {
                if (valid) {
                    vm.$loading();
                    postRoles(this.ApiRequest.postRoles)
                        .then(response => {
                            if (response.data.Success) {
                                vm.Query();
                                vm.Dialog = false;
                            }
                            else {
                                vm.$message({ type: 'error', message: response.data.Msg, center: true, });
                            }
                        })
                        .catch(response => {
                            vm.$message({ type: 'error', message: response.message, center: true, });
                        })
                        .finally(() => {
                            vm.$loading().close();
                        })
                }
            });
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