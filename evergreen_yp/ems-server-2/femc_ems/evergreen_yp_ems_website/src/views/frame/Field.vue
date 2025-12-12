<template>
    <!--nav-->
    <!-- {{ screenWidth }} -->
    <nav class="d-flex justify-content-between align-items-center p-2 ps-3 pe-3 shadow-sm navbar-dark fixed-top">
        <div class="d-flex pe-2">
            <button id="mobileBtn" class="navbar-toggler me-2" type="button" data-bs-toggle="collapse"
                data-bs-target="#mobileBlock" aria-controls="mobileBlock" aria-expanded="false"
                aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
            <a class="navbar-brand d-flex align-items-center" href="#" style="font-weight:bold;color: #fff;">
                <img src="@/assets/logo.png" alt="" class="me-2 bannerClass ">
                {{ ProjectName }}
            </a>
        </div>
        <div id="webMenu">
            <ul class="localMenu d-flex justify-content-center align-items-center m-0 ps-0">
                <router-link :to="{ name: 'Dashboard' }" style="">
                    <li class="pe-3 ps-3">案場首頁</li>
                </router-link>
                <router-link :to="{ name: 'Alert' }">
                    <li class="pe-3 ps-3">警報事件</li>
                </router-link>
                <router-link :to="{ name: 'ElectricLine' }">
                    <li class="pe-3 ps-3">電力單線圖</li>
                </router-link>
                <router-link :to="{ name: 'CommunicateLine' }">
                    <li class="pe-3 ps-3">通訊架構圖</li>
                </router-link>
                <router-link :to="{ name: 'CabinetList' }">
                    <li class="pe-3 ps-3">儲能櫃</li>
                </router-link>
                <el-dropdown trigger="hover" class="loadMenuDropDown d-flex align-items-center">
                    <li class="pe-3 ps-3">系統設定 <font-awesome-icon icon="angle-down" class="ms-2"
                            style="font-size: small;" /></li>
                    <template #dropdown>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-01')">
                            <router-link :to="{ name: 'SystemConfig' }" class="loadMenuDropDownLi">
                                儲能設定</router-link>
                        </el-dropdown-menu>
                        <!-- <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-02')">
                            <router-link :to="{ name: 'ResourcesSettings' }" class="loadMenuDropDownLi">
                                資源設定</router-link>
                        </el-dropdown-menu> -->
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-09')">
                            <router-link :to="{ name: 'PriceConfig' }" class="loadMenuDropDownLi">
                                電價設定</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-05')">
                            <router-link :to="{ name: 'Schedule' }" class="loadMenuDropDownLi"> 充放電排程設定</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-10')">
                            <router-link :to="{ name: 'HolidaySettings' }" class="loadMenuDropDownLi"> 台電假日設定 </router-link>
                        </el-dropdown-menu>
                        <!-- <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-11-2') || $store.getters.userPriviagePage('P02-11-3') || $store.getters.userPriviagePage('P02-11-4')">
                            <router-link :to="{ name: 'LineSetting' }" class="loadMenuDropDownLi">
                                Line通知</router-link>
                        </el-dropdown-menu> -->
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-12-2') || $store.getters.userPriviagePage('P02-12-3') || $store.getters.userPriviagePage('P02-12-4')">
                            <router-link :to="{ name: 'MsgSetting' }" class="loadMenuDropDownLi">
                                即時訊息通知</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu>
                            <router-link :to="{ name: 'AnalogSignal' }" class="loadMenuDropDownLi">
                                保護訊號</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-07')">
                            <router-link :to="{ name: 'UserSettings' }" class="loadMenuDropDownLi">
                                使用者管理</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-08')">
                            <router-link :to="{ name: 'RoleSettings' }" class="loadMenuDropDownLi">
                                角色管理</router-link>
                        </el-dropdown-menu>
                        <!-- <el-dropdown-menu v-if="$store.getters.userPriviagePage('P01-02')">
                                <a class="loadMenuDropDownLi" :href="LC_URL" target="_blank"> LC 設定</a>
                            </el-dropdown-menu>
                            <el-dropdown-menu v-if="$store.getters.userPriviagePage('P01-03')">
                                <a class="loadMenuDropDownLi" :href="PCS_URL" target="_blank"> PCS 設定</a>
                            </el-dropdown-menu>
                            <el-dropdown-menu v-if="$store.getters.userPriviagePage('P01-04')">
                                <a class="loadMenuDropDownLi" :href="BESS_URL" target="_blank"> BSC設定</a>
                            </el-dropdown-menu> -->
                        <!-- <el-dropdown-menu>
                                <a class="loadMenuDropDownLi" :href="Moniter_URL" target="_blank"> 監視器畫面</a>
                            </el-dropdown-menu> -->
                    </template>
                </el-dropdown>
                <el-dropdown trigger="hover" class="loadMenuDropDown d-flex align-items-center">
                    <li class="pe-3 ps-3">報表 <font-awesome-icon icon="angle-down" class="ms-2"
                            style="font-size: small;" /></li>
                    <template #dropdown>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-01')">
                            <router-link :to="{ name: 'MeterChart' }" class="loadMenuDropDownLi">電錶記錄</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-02')">
                            <router-link :to="{ name: 'PCSHistory' }" class="loadMenuDropDownLi">PCS記錄</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-03')">
                            <router-link :to="{ name: 'BMSHistory' }" class="loadMenuDropDownLi">BMS記錄</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-04')">
                            <router-link :to="{ name: 'CabinetReports' }" class="loadMenuDropDownLi">儲能系統報表</router-link>
                        </el-dropdown-menu>
                        <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-05')">
                            <router-link :to="{ name: 'SunCabinetReports' }" class="loadMenuDropDownLi">太陽能系統報表</router-link>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>

            </ul>
        </div>
        <div class="text-end d-flex align-items-center justify-content-end">
            <avatar></avatar>
        </div>
    </nav>
    <div id="mobileBlock" ref="mobileBlock" class="navbar-collapse collapse">
        <ul class="localMenu mobileMenu p-2 m-0 ps-2 d-flex flex-column align-items-center">
            <router-link :to="{ name: 'Dashboard' }" @click="closeMobileBlock">
                <li class="p-2">案場首頁</li>
            </router-link>
            <router-link :to="{ name: 'Alert' }" @click="closeMobileBlock">
                <li class="p-2">警報事件</li>
            </router-link>
            <router-link :to="{ name: 'ElectricLine' }" @click="closeMobileBlock">
                <li class="p-2">電力單線圖</li>
            </router-link>
            <router-link :to="{ name: 'CommunicateLine' }" @click="closeMobileBlock">
                <li class="p-2">通訊架構圖</li>
            </router-link>
            <router-link :to="{ name: 'CabinetList' }" @click="closeMobileBlock">
                <li class="p-2">儲能櫃</li>
            </router-link>
            <el-dropdown trigger="hover" ref="sysDropdown" class="loadMenuDropDown d-flex align-items-center" :hide-on-click="true">
                <li class="p-2 mt-1">系統設定 <font-awesome-icon icon="angle-down" class="ms-2" style="font-size: small;" />
                </li>
                <template #dropdown>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-01')">
                        <router-link :to="{ name: 'SystemConfig' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            儲能設定</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-02')">
                        <router-link :to="{ name: 'ResourcesSettings' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            資源設定</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-09')">
                        <router-link :to="{ name: 'PriceConfig' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            電價設定</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-05')">
                        <router-link :to="{ name: 'Schedule' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')"> 充放電排程設定</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu>
                        <router-link :to="{ name: 'HolidaySettings' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')"> 台電假日設定</router-link>
                    </el-dropdown-menu>
                    <!-- <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-11-1') || $store.getters.userPriviagePage('P02-11-2') || $store.getters.userPriviagePage('P02-11-3') || $store.getters.userPriviagePage('P02-11-4')">
                        <router-link :to="{ name: 'LineSetting' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            Line通知</router-link>
                    </el-dropdown-menu> -->
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-12-1') || $store.getters.userPriviagePage('P02-12-2') || $store.getters.userPriviagePage('P02-12-3') || $store.getters.userPriviagePage('P02-12-4')">
                        <router-link :to="{ name: 'MsgSetting' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            即時訊息通知</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu>
                        <router-link :to="{ name: 'AnalogSignal' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            保護訊號</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-07')">
                        <router-link :to="{ name: 'UserSettings' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            使用者管理</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P02-08')">
                        <router-link :to="{ name: 'RoleSettings' }" class="loadMenuDropDownLi" @click="closeDrop('sysDropdown')">
                            角色管理</router-link>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
            <el-dropdown trigger="hover" ref="reportDropdown" class="loadMenuDropDown d-flex align-items-center">
                <li class="p-2 mt-1">報表 <font-awesome-icon icon="angle-down" class="ms-2" style="font-size: small;" />
                </li>
                <template #dropdown>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-01')">
                        <router-link :to="{ name: 'MeterChart' }" class="loadMenuDropDownLi" @click="closeDrop('reportDropdown')">電錶記錄</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-02')">
                        <router-link :to="{ name: 'PCSHistory' }" class="loadMenuDropDownLi" @click="closeDrop('reportDropdown')">PCS記錄</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-03')">
                        <router-link :to="{ name: 'BMSHistory' }" class="loadMenuDropDownLi" @click="closeDrop('reportDropdown')">BMS記錄</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-04')">
                        <router-link :to="{ name: 'CabinetReports' }" class="loadMenuDropDownLi" @click="closeDrop('reportDropdown')">儲能系統報表</router-link>
                    </el-dropdown-menu>
                    <el-dropdown-menu v-if="$store.getters.userPriviagePage('P03-05')">
                        <router-link :to="{ name: 'SunCabinetReports' }" class="loadMenuDropDownLi" @click="closeDrop('reportDropdown')">太陽能系統報表</router-link>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </ul>
    </div>
    <!--nav-->
    <!--content-->
    <div class="row m-0">
        <!--content-->
        <main id="main"><router-view :key="$route.fullPath"></router-view></main>
        <!-- <div class=" siteMinHeight p-0" style="overflow-x:auto;">
                <div class="container-fluid p-0 rounded">
                </div>
            </div> -->
        <footer class="text-white w-100 p-2" style="background: rgb(7, 30, 61)">
            <div class="row justify-content-center align-items-center">
                <div class="col-auto footerCol_1">
                    <div class="d-flex">
                        <img src="@/assets/FEMCLogo.png" alt="" class="bannerClass">
                        <span>福能股份有限公司<br>Copyright © 2022 FEMC Inc.</span>
                    </div>
                </div>
                <div class="col-auto footerCol_2">
                    <div class="d-flex">
                        <span class="me-2">運維專線：</span>
                        <span>0911-702-371<br>(07) 550-8936</span>
                    </div>
                </div>
                <div class="col-auto footerCol_3">
                    <div class="textblock">
                    <div>LINE ID：@FEMC</div>
                    <div>E-Mail：support@femctw.com</div>
                    </div>
                </div>
            </div>
        </footer>
    </div>

    <el-dialog title="周前表計資料匯出" v-model="MeterExportDialog" width="450px" :destroy-on-close="true">
        <MeterExport></MeterExport>
    </el-dialog>
</template>

<script>
import avatar from '@/components/Avatar.vue';
import MeterExport from '@/components/MeterExport.vue'
import newwebsocket from '@/lib/NewWebSocket.js';
import sucketDataDemo from '@/JSON/sucketData.json';
import { mapState } from "vuex";

export default {
    components: {
        'avatar': avatar, MeterExport
    },
    data() {
        return {
            active: false,
            D_URL: process.env.VUE_APP_3D,
            LC_URL: process.env.VUE_APP_LC_URL,
            PCS_URL: process.env.VUE_APP_PCS_URL,
            BESS_URL: process.env.VUE_APP_BSC_URL,
            Moniter_URL: process.env.VUE_APP_Moniter,
            isCollapse: true,
            ProjectName: process.env.VUE_APP_Project,
            isDemo: process.env.VUE_APP_DemoData == 1,
            SocketDataALL: null,
            sucketDataDemo,
            MeterExportDialog: false,
            webSocket: null,
            screenWidth: window.innerWidth,
            isNavbarOpen: false
        };
    },
    computed: {
        ...mapState(["ZoomSize"]),
    },
    mounted() {
        this.reSetScale();
        this.$nextTick(() => {
            window.addEventListener('resize', this.onResize);
        })
    },
    beforeUnmount() {
        try {
            this.webSocket.close();
        } catch (e) {

        }
    },
    created() {
        this.CreateSocket();
    },
    watch: {
        "ZoomSize": {
            handler: function () {
                window.location.reload();
            },
            deep: true,
            immediate: false,
        },
        // 寬度超過 1160 把已開啟的手機下拉選單隱藏
        screenWidth: {
            handler(newVal, oldVal) {
                if (newVal <= 1160) {
                    if(this.$refs.mobileBlock.classList.value !== 'navbar-collapse collapse') {
                        this.$refs.mobileBlock.classList.value = 'navbar-collapse collapse';
                    }
                }
            },
        },
    },
    methods: {
        reSetScale() {
            document.body.style.zoom = `${this.ZoomSize}%`;
        },
        CreateSocket() {
            const vm = this;
            function MessageCallBack(SocketData) {
                var data = JSON.parse(SocketData);
                vm.SocketDataALL = data;
                vm.$store.commit('setSocketDataALL', vm.SocketDataALL, vm.CreateSocket);
            }

            if (vm.isDemo) {
                vm.SocketDataALL = vm.sucketDataDemo;
                vm.$store.commit('setSocketDataALL', vm.SocketDataALL);
            } else {
                const token = vm.$store.getters.user.Token;
                vm.webSocket = newwebsocket(MessageCallBack, null, null, null, token);
            }
        },
        onResize() {
            this.screenWidth = window.innerWidth
        },
        closeMobileBlock() {
            if (this.$refs.mobileBlock.classList.value !== 'navbar-collapse collapse') {
                        this.$refs.mobileBlock.classList.value = 'navbar-collapse collapse';
            }
            this.$refs.reportDropdown.handleClose();
        },
        closeDrop(drpName) {
            if (this.$refs.mobileBlock.classList.value !== 'navbar-collapse collapse') {
                        this.$refs.mobileBlock.classList.value = 'navbar-collapse collapse';
            }
            this.$refs[drpName].handleClose();
        },
    },
};
</script>
<style scoped>
nav {
    background: rgb(7, 30, 61);
}

#main {
    padding: 75px 1rem 1rem 1rem;
    min-height: 80vh;
}

#mobileBlock {
    background: rgb(7, 30, 61);
    position: fixed;
    top: 56px;
    right: 0;
    left: 0;
    z-index: 1030;
}

.mobileMenu a {
    margin: 0;
}

#mobileBtn {
    display: none;
}

@media screen and (min-width: 1161px) {
    #webMenu {
        display: block;
    }
    .loadMenuDropDown .el-tooltip__trigger,.loadMenuDropDown .el-tooltip__trigger li  {
        height: 30px!important;
    }
}

@media screen and (max-width: 1160px) {
    #webMenu {
        display: none;
    }

    #mobileBtn {
        display: block;
    }
}
@media screen and (min-width: 775px) {
    footer .row {
        padding: 2% 0%;
    }
    footer .row .footerCol_1 {
        border-right: 1px solid #dee2e6
    }
    footer .row .footerCol_2 {
        border-right: 1px solid #dee2e6
    }
    footer .row .footerCol_1 .d-flex {
        min-width: 270px;
    }
    footer .row .footerCol_1 .d-flex img {
        margin-right: 5%;
    }
    footer .row .footerCol_3 .textblock div {
        margin-left: .5rem;
    }
}
@media screen and (max-width: 774px) {
    footer .row {
        padding: 3% 0%;
    }
    footer .row .footerCol_1 {
        width: 100%;
    }
    footer .row .footerCol_1 .d-flex {
        justify-content: center;
        padding-bottom: 20px;
    }
    footer .row .footerCol_1 .d-flex img {
        margin-right: 15px;
    }
    footer .row .footerCol_2 {
        border-right: 1px solid #dee2e6
    }
    footer .row .footerCol_2,
    footer .row .footerCol_3 {
        width: 50%;
    }
    footer .row .footerCol_2 .d-flex {
        justify-content: end;
    }
    footer .row .footerCol_3 .textblock div {
        margin-left: 0rem;
    }
}
@media screen and (max-width: 500px) {
    footer .row {
        padding: 1% 0%;
    }
    footer .row .footerCol_1 .d-flex img {
        display: none;
    }
    footer .row .footerCol_1,
    footer .row .footerCol_2,
    footer .row .footerCol_3 {
        width: 100%;
        border-left: 10px solid #ffffff;
        border-right: 10px solid #ffffff;
        margin-bottom: .5rem;
    }
    footer .row .footerCol_1 .d-flex,
    footer .row .footerCol_2 .d-flex {
        padding-bottom: 10px;
    }
    footer .row .footerCol_1 .d-flex,
    footer .row .footerCol_2 .d-flex,
    footer .row .footerCol_3 .textblock {
        justify-content: start;
        margin-left: 28%;
    }
    footer .row .footerCol_3 .textblock {
        display: grid;
    }
}
@media screen and (max-width: 440px) {
    footer .row .footerCol_1 .d-flex,
    footer .row .footerCol_2 .d-flex,
    footer .row .footerCol_3 .textblock {
        margin-left: 25%;
    }
}
@media screen and (max-width: 391px) {
    footer .row .footerCol_1 .d-flex,
    footer .row .footerCol_2 .d-flex,
    footer .row .footerCol_3 .textblock {
        margin-left: 20%;
    }
}
@media screen and (max-width: 321px) {
    footer .row .footerCol_1 .d-flex,
    footer .row .footerCol_2 .d-flex,
    footer .row .footerCol_3 .textblock {
        margin-left: 16%;
    }
}
@media screen and (max-width: 311px) {
    footer .row .footerCol_1 .d-flex,
    footer .row .footerCol_2 .d-flex,
    footer .row .footerCol_3 .textblock {
        margin-left: 0%;
    }
}
</style>