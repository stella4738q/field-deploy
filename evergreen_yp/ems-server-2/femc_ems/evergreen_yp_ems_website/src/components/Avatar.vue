<template>
  <font-awesome-icon v-if="SocketDataALL?.alarm == null || SocketDataALL?.alarm?.length == 0" icon="bell"
    class="text-white fs-5 me-4" style="top:2px" />
  <el-dropdown v-else trigger="click" class="me-4" style="top:2px">
    <el-badge :value="SocketDataALL?.alarm.length ?? 0" class="item cursor-pointer">
      <font-awesome-icon icon="bell" class="text-white fs-5" />
    </el-badge>
    <template #dropdown>
      <el-dropdown-menu class="scrollable-dropdown">
        <el-dropdown-item v-for="item in SocketDataALL?.alarm" :key="item.id">
          <div @click="GoToBell" :class="'row rounded-3 bg-' + (item.level == 1 ? 'warning' : item.level == 2 ? 'danger' : 'body')"
            style="width:300px; max-width:30vw;--bs-bg-opacity: .1;">
            <div class="text-danger">
              <font-awesome-icon icon="warning" />
              {{ item.equipment_id }}
            </div>
            <div class="text-truncate text-dark">
              <small>{{ item.message }}</small> <small style="float:right ;font-style: italic;">{{ item.time }}</small>
            </div>
          </div>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>

  </el-dropdown>
  <el-avatar size="small" src="https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png" />
  <el-dropdown trigger="click" class="ms-2 ">
    <span class="el-dropdown-link cursor-pointer">
      <font-awesome-icon icon="angle-down" />
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item @click="this.twoFactorKey.show = true;">
          <font-awesome-icon icon="user" class="me-2" />
          {{ userName }}
        </el-dropdown-item>
        <el-dropdown-item divided @click="ChangePassword">
          <font-awesome-icon icon="lock" class="me-2" />
          修改密碼
        </el-dropdown-item>
        <el-dropdown-item divided>
          <font-awesome-icon icon="maximize" class="me-2" />
          <el-select v-model="ZoomSize" placeholder="請選擇" @change="ZoomSizeChange" style="width:100px">
            <el-option label="80%" :value="80" />
            <el-option label="100%" :value="100" />
            <el-option label="110%" :value="110" />
            <el-option label="120%" :value="120" />
            <el-option label="130%" :value="130" />
            <el-option label="150%" :value="150" />
            <el-option label="170%" :value="170" />
            <el-option label="200%" :value="200" />
          </el-select>
        </el-dropdown-item>
        <el-dropdown-item divided @click="Logout">
          <font-awesome-icon icon="right-from-bracket" class="me-2" />
          登出
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
  <!-- ======================================================================== -->
  <el-dialog title="密碼修改" v-model="Dialog.PWD" width="400px" label :show-close="false" center>
    <el-form :model="FormPWD" :rules="FormPWDRules" ref="FormPWD" label-width="auto">
      <el-form-item label="原密碼" prop="old_password">
        <el-input v-model="FormPWD.old_password" autocomplete="off" show-password></el-input>
      </el-form-item>
      <el-form-item label="新密碼" prop="new_password">
        <el-input v-model="FormPWD.new_password" autocomplete="off" show-password></el-input>
      </el-form-item>
      <el-form-item label="再次輸入" prop="re_password">
        <el-input v-model="FormPWD.re_password" autocomplete="off" show-password></el-input>
      </el-form-item>
    </el-form>
    <template #footer class="dialog-footer" align="end">
      <el-button @click="Dialog.PWD = false">
        <font-awesome-icon icon="times" />
      </el-button>
      <el-button type="primary" @click="PasswordSubmit" :disabled="!FormPWD.old_password || !FormPWD.new_password || !FormPWD.re_password">
        <font-awesome-icon icon="check" />
      </el-button>
    </template>
  </el-dialog>
  <!-- ======================================================================== -->
  <el-dialog title="兩階段驗證設定" v-model="twoFactorKey.show" width="30%" :show-close="false" :close-on-click-modal="false" destroy-on-close center>
    <!-- =================================== -->
    <div class="d-flex align-items-center flex-column">
      <el-avatar :src="require('@/assets/iconMan.png')" class="mb-3" />
      <h6 class="fw-bolder">{{ this.$store.state.user.UserInfo.name }}</h6>
      <el-switch v-model="twoFactorKey.enable" active-text="開啟兩階段驗證" inactive-text="關閉兩階段驗證" />
    </div>
    <!-- =================================== -->
    <template #footer>
      <div class="dialog-footer" align="center">
        <el-button @click="twoFactorKey.show = false; twoFactorKey.enable = this.$store.state.user.UserInfo.enable_otp; twoFactorKey.QRcode = '';">
        <font-awesome-icon icon="times" class="me-2" />取消
      </el-button>
      <el-button type="primary" @click="submitTwoFactorKey" :disabled="twoFactorKey.enable === this.$store.state.user.UserInfo.enable_otp">
        <font-awesome-icon icon="check" class="me-2" />儲存設定
      </el-button>
      <el-button type="success" @click="submitTwoFactorKey" v-if="twoFactorKey.enable === true && this.$store.state.user.UserInfo.enable_otp === true">
        <font-awesome-icon icon="refresh" class="me-2" />重新取得 QR Code
      </el-button>
      </div>
    </template>
    <!-- =================================== -->
  </el-dialog>
  <!-- ======================================================================== -->
  <el-dialog title="QR Code驗證" v-model="QRcode.show" width="400px" center :close-on-click-modal="false">
    <div align="center">請使用 Google Authenticator 或 Microsoft Authenticator 掃描下方QR Code ，以取得登入驗證碼。</div>
    <img :src="QRcode.pic" alt="" style="width: 350px">
    <template #footer>
      <!-- <el-button @click="QRcode.show = false; QRcode.pic = '';">
        <el-icon class="me-2"><Close /></el-icon> 關閉視窗
      </el-button> -->
      <el-button type="primary" @click="qrcodeSubmit">
        <font-awesome-icon icon="check" class="me-2" />完成
      </el-button>
    </template>
  </el-dialog>
  <!-- ======================================================================== -->
</template>

<script >
import { mapState } from "vuex";
import { changeUserPassword, twoFactorAuth } from '@/api/Api.js';
export default {
  props: {

  },
  data() {
    return {
      ZoomSize: 100,
      userName: this.$store.getters.user?.UserInfo?.name,
      Dialog: {
        User: false,
        PWD: false,
        Permission: false,
      },
      FormPWD: {
        user_id: '',
        old_password: '',
        new_password: '',
        re_password: ''
      },
      FormPWDTemplate: {
        user_id: this.$store.getters.user?.UserInfo?.id,
        old_password: '',
        new_password: '',
        re_password: ''
      },
      FormPWDRules: {
          old_password: [
            { required: true, message: " ", trigger: "blur" },
          ],
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
      twoFactorKey: {
        show: false,
        enable: this.$store.state.user.UserInfo.enable_otp,
      },
      QRcode: {
        show: false,
        pic: '',
      },
    };
  },
  computed: {
    ...mapState(["SocketDataALL"]),
    ApiRequest: function () {
      return {
        changeUserPassword: this.FormPWD,
      }
    }
  },
  created() {
    this.ZoomSize = this.$store.getters.getZoomSize;
  },
  unmounted() {
  },
  watch: {
  },
  methods: {
    ZoomSizeChange() {
      this.$store.commit('setZoomSize' , this.ZoomSize );
    },
    ChangePassword() {
      this.FormPWD = Object.assign({}, this.FormPWDTemplate);
      this.Dialog.PWD = true;
    },
    GoToBell() {
      this.$router.push({ name: 'Alert' });
    },
    Logout() {
      this.$store.commit('logOut');
      this.$router.push({ name: 'login' });
    },
    PasswordSubmit() {
      const vm = this;
      vm.$refs['FormPWD'].validate((valid) => {
        if (valid) {
          if (vm.FormPWD.new_password != vm.FormPWD.re_password) {
            vm.$message({ type: 'error', message: '密碼不一致，請重新輸入', center: true, });
            return false;
          }
          if (vm.FormPWD.new_password === vm.FormPWD.re_password) {
            delete vm.FormPWD.re_password;
            // vm.$message({ type: 'success', message: `密碼一致：${JSON.stringify(vm.FormPWD)}`, center: true, });
            changeUserPassword(vm.ApiRequest.changeUserPassword).then((response) => {
            if (response.data.Success) {
              vm.Dialog.PWD = false;
              this.FormPWD = Object.assign({}, this.FormPWDTemplate);
              vm.$message({ type: 'success', message: '修改成功', center: true, });
            }
            else {
              vm.$message({ type: 'error', message: response.data.Message, center: true, });
              this.FormPWD = Object.assign({}, this.FormPWDTemplate);
            }
          });
          }
        } else {
          return false;
        }
      });
    },
    submitTwoFactorKey() {
      const vm = this;
      vm.$loading();
      //
      twoFactorAuth({ enable: this.twoFactorKey.enable })
        .then((res) => {
          console.log(res);
          //
          if (res.data.Success) {
            this.twoFactorKey.show = false;
            this.$store.commit('storeOtpSetting', this.twoFactorKey.enable); // 更新目前設定結果資料
            // 設定為開啟
            if (this.twoFactorKey.enable) {
              this.QRcode.pic = res.data.Data;
              this.QRcode.show = true;
            }
            if (!this.twoFactorKey.enable) {
              vm.$message({ type: 'success', message: '二階段認證設定成功，已關閉二階段驗證。', center: true, });
  
            }
            //
          } else {
            vm.$message({ type: 'error', message: `二階段認證設定失敗。錯誤訊息：${res.data.Message}`, center: true, });
          }
        })
        .catch((error) => {
          console.log(error);
          vm.$message({ type: 'error', message: `二階段認證設定失敗(error)。錯誤訊息。錯誤訊息：${error}`, center: true, });
        })
        .finally(() => {
          vm.$loading().close();
        });
    },
    qrcodeSubmit() {
      const vm = this;
      vm.$loading();
      //
      twoFactorAuth({ enable: this.twoFactorKey.enable, accept_submit: true })
        .then((res) => {
          console.log(res);
          //
          if (res.data.Success) {
            this.QRcode.show = false;
            vm.$message({ type: 'success', message: '二階段認證設定完成，下次登入將會開啟二次驗證登入。', center: true, });
            //
          } else {
            vm.$message({ type: 'error', message: `二階段認證設定失敗(QRcode)。錯誤訊息：${res.data.Message}`, center: true, });
          }
        })
        .catch((error) => {
          // console.log(error);
          vm.$message({ type: 'error', message: `二階段認證設定失敗(QRcode)(error)。錯誤訊息：${error}`, center: true, });
        })
        .finally(() => {
          vm.$loading().close();
        });
    },
  },
};
</script>