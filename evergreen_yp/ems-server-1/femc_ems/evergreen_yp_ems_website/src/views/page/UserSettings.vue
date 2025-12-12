<template>
    <div class="p-3 card border-0 shadow-sm">
        <div class="card-body">
            <h3>使用者管理</h3>
            <!-- ============================================================ -->
            <el-form :inline="true" label-position="top" class="align-items-end">
                    <el-form-item label="姓名">
                        <el-input v-model="FormSearch.name"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="SearchClick">
                            <font-awesome-icon icon="search" />
                        </el-button>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" plain @click="Add" v-if="$store.getters.userPriviage('p_00055')">
                            <font-awesome-icon icon="user-plus" />
                        </el-button>
                    </el-form-item>
                </el-form>
            <div>
                <el-table :data="ApiResult.getUsers" size="small" class="rounded-3" header-cell-class-name="tableHeaderStyle" stripe border>
                        <el-table-column width="200" label="名稱" sortable prop="name" align="center"></el-table-column>
                        <el-table-column width="200" label="帳號" sortable prop="account" align="center"></el-table-column>
                        <el-table-column width="120" v-if="is_field_admin" label="案場管理員" sortable prop="is_field_admin" align="center">
                            <template #default="scope">
                                {{ scope.row.is_field_admin === 0 ? '否' : '是' }}
                            </template>
                        </el-table-column>
                        <el-table-column label="啟用" sortable prop="enable" align="center">
                            <template #default="scope">
                                {{ scope.row.enable === 0 ? '否' : '是' }}
                            </template>
                        </el-table-column>
                        <el-table-column width="250" label="操作" align="center">

                            <template #default="scope">
                                <el-button size="small" @click="Edit(scope.row)" v-if="$store.getters.userPriviage('p_00056')">
                                    <font-awesome-icon icon="edit" />
                                </el-button>


                                <el-popconfirm title="確定刪除？" @confirm="Delete(scope.row)" v-if="$store.getters.userPriviage('p_00057')">
                                    <template #reference>
                                        <el-button size="small" type="danger">
                                            <font-awesome-icon icon="trash-alt" />
                                        </el-button>
                                    </template>
                                </el-popconfirm>

                                <el-button size="small" @click="ResetPW(scope.row)" v-if="$store.getters.userPriviage('p_00074')">
                                    <font-awesome-icon icon="lock" />
                                </el-button>

                                <!-- <el-popconfirm title="確定重置？" @confirm="PasswordSubmit(scope.row)" v-if="$store.getters.userPriviage('p_00074')">
                                    <template #reference>
                                    <el-button size="small">
                                        <font-awesome-icon icon="lock" />
                                    </el-button>
                                </template>
                            </el-popconfirm> -->

                                <el-button size="small" type="primary" @click="PermissionClick(scope.row)" v-if="$store.getters.userPriviage('p_00074')">
                                    <font-awesome-icon icon="shield-halved" />
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
            </div>
        </div>
    </div>
    <!-- ============================================================ -->
    <el-dialog :title="Form.id ? '修改使用者' : '新增使用者'" v-model="Dialog.User" :show-close="false" :width="dialogWidth">
        <el-form :model="Form" :rules="Form_rules" ref="Form" label-position="top">
            <el-form-item label="名稱" prop="name">
                <el-input v-model="Form.name" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="登入帳號" prop="account" :disabled="Form.id !== ''">
                <el-input v-model="Form.account" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="登入密碼" prop="password" v-if="Form.id === null">
                <el-input v-model="Form.password" autocomplete="off" show-password></el-input>
            </el-form-item>
            <el-form-item label="案場管理員" v-if="is_field_admin">
                <el-switch v-model="Form.is_field_admin" active-color="#13ce66" :active-value="1"
                    inactive-color="#B3B3B3" :inactive-value="0">
                </el-switch>
            </el-form-item>
            <el-form-item label="啟用">
                <el-switch v-model="Form.enable" active-color="#13ce66" :active-value="1" inactive-color="#B3B3B3"
                    :inactive-value="0">
                </el-switch>
            </el-form-item>
        </el-form>
        <template #footer class="dialog-footer" align="end">
            <el-button @click="Dialog.User = false">
                <font-awesome-icon icon="times" />
            </el-button>
            <el-button type="primary" @click="FormSubmit">
                <font-awesome-icon icon="check" />
            </el-button>
        </template>
    </el-dialog>
    <!-- ============================================================ -->
    <el-dialog title="密碼重置" v-model="Dialog.PWD" :width="dialogWidth2" :show-close="false" center>
        <el-form :model="FormPWD" :rules="FormPWDRules" ref="FormPWD" label-width="auto" label-position="top">
            <el-form-item label="帳號">
                {{ FormPWD.user ? FormPWD.user.account : '' }}
            </el-form-item>
            <el-form-item label="名稱">
                {{ FormPWD.user ? FormPWD.user.name : '' }}
            </el-form-item>
            <el-form-item label="新密碼" prop="new_password">
                <el-input v-model="FormPWD.new_password" autocomplete="off" show-password></el-input>
            </el-form-item>
            <el-form-item label="再次輸入" prop="re_password">
                <el-input v-model="FormPWD.re_password" autocomplete="off" show-password></el-input>
            </el-form-item>

        </el-form>
        <template #footer class="dialog-footer" align="end">
            <el-button @click="closePWDReset">
                <font-awesome-icon icon="times" />
            </el-button>
            <el-button type="primary" @click="PasswordSubmit" :disabled="!FormPWD.user_id || !FormPWD.re_password || !FormPWD.new_password">
                <font-awesome-icon icon="check" />
            </el-button>
        </template>
    </el-dialog>
    <!-- ============================================================ -->
    <el-dialog title="權限設定" v-model="Dialog.Permission" :width="dialogWidth2" :show-close="false" custom-class="previewDialog">
        <div class="row mb-2 border-bottom" v-for="field in DataBaseEdit" :key="field.id">
            <div v-for=" role in field.roles" :key="role.id" class="me-2 p-2  ps-3">
                <el-checkbox v-model="role.enable" :label="role.name" />
            </div>
        </div>
        <template #footer class="dialog-footer" align="end">
            <el-button @click="Dialog.Permission = false">
                <font-awesome-icon icon="circle-xmark" />
            </el-button>
            <el-button @click="SubmitPremission">
                <font-awesome-icon icon="circle-check" />
            </el-button>
        </template>
    </el-dialog>
    <!-- ============================================================ -->
</template>

<script>
import {
    getUsers, postUsers, deleteUsers, resetUserPassword,
    getFields, getUserFields, postUserFields, deleteUserFields,
    getRoles, getUserRoles, postUserRoles, deleteUserRoles
} from '@/api/Api.js'
export default {
    components: {
    },
    data() {
        return {
            is_admin: false,
            is_field_admin: false,
            EditItem: {},
            Dialog: {
                User: false,
                PWD: false,
                Permission: false,
            },
            FormSearch: {
                id: '',
                name: '',
                email: '',
                mobile: '',
                is_admin: '',
                is_field_admin: '',
                company: '',
                account: '',
                enable: '',
            },
            FormQuery: {
                id: '',
                name: '',
                email: '',
                mobile: '',
                is_admin: '',
                is_field_admin: '',
                company: '',
                account: '',
                enable: '',
            },
            Form: {
                id: null,
                name: "",
                email: "",
                mobile: "",
                is_admin: null,
                is_field_admin: null,
                account: "",
                password: "",
                enable: 1,
                company: ""
            },
            FormTemplate: {
                id: null,
                name: "",
                email: "",
                mobile: "",
                is_admin: null,
                is_field_admin: null,
                account: "",
                password: "",
                enable: 1,
                company: ""
            },
            FormPWD: {
                user: null,
                user_id: "",
                new_password: "",
                re_password: ""
            },
            Form_rules: {
                name: [{ required: true, message: ' ', trigger: 'blur' },],
                email: [{ required: true, message: ' ', trigger: 'blur' }],
                account: [{ required: true, message: ' ', trigger: 'blur' }],
                password: [
                    { required: true, message: ' ', trigger: 'blur' },
                    { min: 6, message: '請輸入6~12字元密碼', trigger: 'blur' },
                    { max: 12, message: '請輸入6~12字元密碼', trigger: 'blur' }
                ],
                company: [{ required: true, message: ' ', trigger: 'blur' }]
            },
            FormPWDRules: {
                new_password: [
                { required: true, message: " ", trigger: "blur" },
                { min: 6, message: "請輸入6~12字元密碼", trigger: "blur" },
                { max: 12, message: "請輸入6~12字元密碼", trigger: "blur" }
                ],
                re_password: [
                { required: true, message: " ", trigger: "blur" },
                { min: 6, message: "請輸入6~12字元密碼", trigger: "blur" },
                { max: 12, message: "請輸入6~12字元密碼", trigger: "blur" }
                ],
            },
            Form_change_permission_uid: '',
            ApiResult: {
                getFields: [],
                getUsers: [],
                getRoles: [],
            },
            DataBase: [],
            DataBaseEdit: [],
            DataBaseRole: [],
            deleteId: '',
            dialogWidth: '85%',
            dialogWidth2: '400px',
        };
    },
    mounted() {
        window.onresize = () => {
            return (() => {
                  this.setDialogWidth();
          })();
        };
    },
    computed: {
        ApiRequest: function () {
            return {
                getUsers: this.FormQuery,
                getRoles: { id: '', name: '', enable: '', fields: '', },
                postUsers: this.Form,
                deleteUsers: { id: this.deleteId },
                getUserFields: { user_id: this.EditItem.id },
                getUserRoles: { user_id: this.EditItem.id },
            }
        }
    },
    created() {
        const vm = this;
        this.SearchClick(true);
        var p = [getFields(), getRoles(vm.ApiRequest.getRoles)];

        Promise.all(p).then(response => {
            if (response[0].data.message == "Success") {
                vm.ApiResult.getFields = response[0].data.data.map(x => { return { id: x._id, name: x.name, enable: false, } });
            }

            if (response[1].data.Success) {
                vm.ApiResult.getRoles = response[1].data.Data.map(x => { return { id: x._id, enable: x.enable, name: x.name, enable: false, field_id: x.field_id } });
            }

            vm.ApiResult.getFields.forEach(x => {
                x.roles = vm.ApiResult.getRoles.filter(xx => { return xx.field_id == x.id })
            });

            vm.DataBase = vm.ApiResult.getFields;

        }).catch(response => {

        }).finally(() => {

        })
    },
    watch: {
    },
    methods: {
        setDialogWidth() {
                let windowSize = document.body.clientWidth;
                if (windowSize < 767) {
                    this.dialogWidth = '85%';
                    this.dialogWidth2 = '65%';
                } else {
                    this.dialogWidth = '600px';
                    this.dialogWidth2 = '400px';
                }
        },
        SubmitPremission() {
            const vm = this;
            var p = [];
            // debugger;
            var addField = vm.DataBaseEdit.filter(x => { return !x.hasOwnProperty('UserFieldId') && x.enable }) //原本沒有後來新增
                .map(x => { return postUserFields({ user_id: vm.EditItem.id, field_id: x.id }) });
            p.push(...addField);//新增案場

            var removeField = vm.DataBaseEdit.filter(x => { return x.UserFieldId && x.enable == false }) // 原本有，後來沒有
                .map(x => { return deleteUserFields({ id: x.UserFieldId }) });
            p.push(...removeField);//刪除案場

            var addRule = vm.DataBaseRole.filter(x => { return !x.hasOwnProperty('UserRoleId') && x.enable })//原本沒有後來新增
                .map(x => { return postUserRoles({ user_id: vm.EditItem.id, role_id: x.id }) })
            p.push(...addRule);//新增角色

            var removeRole = vm.DataBaseRole.filter(x => { return x.UserRoleId && x.enable == false }) // 原本有，後來沒有
                .map(x => { return deleteUserRoles({ id_list: [x.UserRoleId] }) })
            p.push(...removeRole);//刪除角色

            vm.$loading();

            Promise.all(p).then(response => {
                vm.Dialog.Permission = false;

            }).catch(response => {

            }).finally(() => {
                vm.$loading().close();
            })

        },
        setFormIni(ini) {
            // 表單要不要出現系統管理員/案場管理員的 switch 按鈕，
            // 取決於查詢回來的資料單筆物件中是否有相關的欄位
            if (ini) {
                var obj = this.ApiResult.getUsers[0];
                this.is_admin = obj.hasOwnProperty('is_admin')
                this.is_field_admin = obj.hasOwnProperty('is_field_admin')
            }
        },
        PermissionClick(row) {
            const vm = this;
            vm.$loading();

            vm.EditItem = JSON.parse(JSON.stringify(row));
            vm.DataBaseRole = [];
            var p = [];
            p.push(getUserFields(vm.ApiRequest.getUserFields));
            p.push(getUserRoles(vm.ApiRequest.getUserRoles));

            Promise.all(p).then(response => {
                if (response[0].data.message == "Success" && response[1].data.message == "Success") {

                    vm.DataBaseEdit = JSON.parse(JSON.stringify(vm.DataBase));

                    vm.DataBaseEdit.forEach(x => {
                        vm.DataBaseRole.push(...x.roles);

                        var find = response[0].data.data.find(xx => { return xx.field_id == x.id });
                        if (find) {
                            x.enable = true;
                            x.UserFieldId = find._id;
                        }
                    });

                    response[1].data.data.forEach(x => {
                        var find = vm.DataBaseRole.find(xx => { return xx.id == x.role_id });

                        if (find) {
                            find.enable = true;
                            find.UserRoleId = x._id;
                        }
                    });

                    vm.Dialog.Permission = true;

                } else {
                    if (response[0].data.message != "Success") {
                        vm.$message({ type: 'error', message: response[0].data.message, center: true, })
                    }

                    if (response[1].data.message != "Success") {
                        vm.$message({ type: 'error', message: response[0].data.message, center: true, })
                    }
                }
            }).catch(response => {

            }).finally(() => {
                vm.$loading().close();
            })
        },
        Query(ini) {
            const vm = this;
            vm.ApiResult.getUsers = [];
            getUsers(vm.ApiRequest.getUsers).then((response) => {
                if (response.data.Success) {
                    response.data.Data.forEach(item => { item.id = item._id; });
                    vm.ApiResult.getUsers = response.data.Data;
                    vm.setFormIni(ini);
                }
                else {
                    vm.$message({ type: 'error', message: response.data.message, center: true, });
                }
            });
        },
        SearchClick(ini) {
            const vm = this;
            vm.FormQuery = JSON.parse(JSON.stringify(vm.FormSearch));
            vm.Query(ini);
        },
        Edit(row) {
            this.EditRow = row;
            this.Form = Object.assign({}, this.FormTemplate, row);
            this.Dialog.User = true;
        },
        ResetPW(row) {
            this.FormPWD.user = row;
            this.FormPWD.user_id = row.id;
            this.Dialog.PWD = true;
        },
        closePWDReset() {
            this.Dialog.PWD = false; 
            this.FormPWD = { user: null, user_id: '', new_password: '', re_password: '' };
        },
        Delete(row) {
            const vm = this;
            vm.deleteId = row._id;
            deleteUsers(vm.ApiRequest.deleteUsers).then((response) => {
                if (response.data.Success) {
                    vm.SearchClick();
                    vm.$message({ type: 'success', message: '刪除成功', center: true, });
                }
                else {
                    vm.$message({ type: 'error', message: response.data.Message, center: true, });
                }
            });
        },
        Add() {
            this.Form = Object.assign({}, this.FormTemplate);
            this.Dialog.User = true;
        },
        FormSubmit() {
            const vm = this;
            vm.$refs['Form'].validate((valid) => {
                if (valid) {
                    vm.$loading();
                    postUsers(vm.ApiRequest.postUsers)
                        .then((response) => {
                            if (response.data.Success) {
                                postUserFields({ user_id: response.data.Data[0]._id, field_id: vm.ApiResult.getFields[0].id }).then(r2 => {
                                    vm.Query();
                                    vm.Dialog.User = false;
                                })
                            }
                            else {
                                vm.$message({ type: 'error', message: response.data.Message, center: true, });
                            }
                        })
                        .catch(response => {
                            vm.$message({ type: 'error', message: response.Message, center: true, });
                        })
                        .finally(() => {
                            vm.$loading().close();
                        })
                }
            });
        },
        PasswordSubmit() {
            const vm = this;
            vm.$refs['FormPWD'].validate((valid) => {
                if (valid) {
                    if (vm.FormPWD.new_password !== vm.FormPWD.re_password) {
                        vm.$message({ type: 'error', message: '密碼不一致，請重新輸入', center: true, });
                        return false;
                    }
                    if (vm.FormPWD.new_password === vm.FormPWD.re_password) {
                        vm.$loading();
                        resetUserPassword({ user_id: vm.FormPWD.user_id, new_password: vm.FormPWD.new_password }).then((response) => {
                            if (response.data.Success) {
                                vm.$message({ type: 'success', message: '修改成功', center: true, });
                            }
                            else {
                                vm.$message({ type: 'error', message: response.data.Message, center: true, });
                            }
                        }).catch(response => {
                            vm.$message({ type: 'error', message: "Error!!!", center: true, });
                        }).finally(() => {
                            vm.$loading().close();
                            vm.closePWDReset();
                        });
                    }

                } else {
                    return false;
                }
            });
        },
        PasswordSubmit2(row) {
            const vm = this;
            vm.$loading();
            resetUserPassword({ user_id: row.id }).then((response) => {
                if (response.data.Success) {
                    vm.$message({ type: 'success', message: '密碼已重置，請至電子信箱收取新密碼通知', center: true, });
                }
                else {
                    vm.$message({ type: 'error', message: response.data.Message, center: true, });
                }
            }).catch(response => {
                vm.$message({ type: 'error', message: "Error!!!", center: true, });
            })
                .finally(() => {
                    vm.$loading().close();
                });

        },
    },
};
</script>