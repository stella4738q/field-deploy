<template>
  <div class="bg-green" style="height:100vh;">
    <div id="login-block">
      <div class="login-content">
        <div class="text-center"><img src="@/assets/FEMCBanner.png" alt=""></div>
        <div class="d-flex align-items-center justify-content-center">
          <el-form>
            <div class="mt-3">
              <el-input style="height:5vh; " type="text" v-model="acc" @keyup.enter="login('')" placeholder="Username">
              </el-input>
            </div>
            <div class="mt-3">
              <el-input style="height:5vh; " type="password" v-model="pwd" @keyup.enter="login('')" placeholder="Password">
              </el-input>
            </div>
            <div class="mt-3"><el-button class="" @click="login('')" style="" type="primary">Login</el-button></div>
          </el-form>
        </div>
      </div>
    </div>
    <!--====================================-->
    <el-dialog title="驗證碼" v-model="otpDia" :width="'35%'" :show-close="false" :close-on-click-modal="false">
      <div class="d-flex align-items-center flex-column">
        <div class="otp-icon">
          <font-awesome-icon icon="lock" />
        </div>
      </div>
      <div class="mt-3">
        <div class="otp-input-container">
          <input v-for="(value, index) in otpValues" :key="`otp_${index}`" v-model="otpValues[index]" class="otp-input" :maxlength="1"
            @input="handleOptInput(index)" @keydown.backspace="moveToPrevious(index)" ref="optIp" />
        </div>
      </div>
      <div class="dialog-footer mt-4" align="center">
        <el-button type="danger" @click="clearOtp">清除輸入</el-button>
        <el-button @click="otpDia = false; this.otpValues = ['', '', '', '', '', '']">關閉視窗</el-button>
        <el-button type="primary" @click="login(this.otpValues.join(''))" :disabled="this.otpValues.some(i => i === '')" :loading="login_loading">確定</el-button>
      </div>
    </el-dialog>
    <!--====================================-->
  </div>
  <!-- =================================== -->
</template>

<script>
import { LOGIN, getPermissionMenuItem } from '@/api/Api.js'
import flatMenu from '@/lib/flatMenu.js'
export default {
  data() {
    return {
      login_loading: false,
      otpValues: ['', '', '', '', '', ''],
      acc: '',
      pwd: '',
      otpDia: false,
    };
  },
  created() {
  },
  watch: {
  },
  methods: {
    getMenu() {
      return new Promise((resolve) => {
        getPermissionMenuItem()
          .then(response => {
            resolve({ success: true, data: response.data.Data });
          })
          .catch(response => {
            resolve(false);
          })
      });
    },
    async login(otpVal) {
      const vm = this;
      let sendData = {
        account: vm.acc,
        password: vm.pwd,
        type: 1,
        otp: otpVal
      };
      vm.login_loading = true;
      LOGIN(sendData).then((response) => {
        // =================================================
        if (!response.data.Success) {
          if (response.data.Otp) {
            this.otpValues = ['', '', '', '', '', ''];
            this.otpDia = true; // 二階段驗證視窗
            if (response.data.Msg !== '登入成功，您需要兩階段驗證，請輸入OTP') {
              vm.$message({ type: 'error', message: `登入失敗。錯誤代碼：${response.data.Msg}`, center: true, });
            }
          }
          else{
            vm.$message({ type: 'error', message: '登入失敗:' + response.data.Msg, center: true, });
          }
        }
        // =================================================
        if (response.data.Success) {
          this.$store.commit('loginSuccess', response.data);
          this.otpValues = ['', '', '', '', '', ''];
          vm.getMenu().then(menuResult => {
            if (menuResult) {
              vm.$store.commit('userMenu', menuResult.data);
              var flatData = flatMenu(menuResult.data);
              vm.$store.commit('userApi', flatData.flatApi);
              // debugger;
              // console.error("flatData.flatApi");
              // console.error(flatData.flatApi);
              vm.$store.commit('userPage', flatData.flatPage);
              // console.error("flatData.flatPage");
              // console.error(flatData.flatPage);
              vm.$router.push({ name: "Dashboard" });
            }
          })
        }
        vm.login_loading = false;
      }).catch((response) => {
        vm.$message({ type: 'error', message: '登入失敗:' + response.message, center: true, });
        vm.login_loading = false;
      });
    },
    // 處理輸入事件
    handleOptInput(index) {
      if (this.otpValues[index]) {
      // 如果是最後一個輸入框，執行特定函數
        if (index === this.otpValues.length - 1) {
          this.login(this.otpValues.join(''));
        } else if (index < this.otpValues.length - 1) {
        // 跳到下一個輸入框
          this.$refs['optIp'][index + 1].focus();
        }
      }
    },
    // 清空驗證碼
    clearOtp() {
      this.otpValues = ['', '', '', '', '', ''];
      this.$refs['optIp'][0].focus();
    },
    // 按下 Backspace 返回上一個輸入框
    moveToPrevious(index) {
      if (index > 0 && this.otpValues[index] === '' && this.$refs['optIp'][index - 1].value) {
        this.$refs['optIp'][index - 1].focus();
      }
    },
  },
};
</script>
<style type="text/css" scoped>
#login-block {
  width: 50%;
  height: 80%;
  background: #fff;
  border-radius: 51px;
  text-align: center;
  box-shadow: 0px 7px 10px rgb(7, 30, 61);
  bottom: -10%;
  margin: 0 43px;
  position: relative;
  padding: 2%;
}

#login-block img {
  height: 100px;
}

#login-block .el-form {
  min-width: 320px;
  margin-top: 15px;
}
.login-content {
  position: relative;
  top:30%;
}

.bg-green {
  background: no-repeat url('@/assets/loginBackgroud2.jpg');
  background-size: cover;
  background-position: top;
  display: flex;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: -moz-flex;
  display: -webkit-flex;
  display: -ms-flex;
}
@media(max-width: 767px) {
  #login-block {
    width: 100%;
  }
  
}
@media(max-width: 485px) {
  #login-block {
    margin: 0 auto;
  }
}
.otp-input-container {
    display: flex;
    justify-content: center;
  }

  .otp-input {
    width: 40px;
    height: 40px;
    padding: 5px;
    margin: 0 10px;
    font-size: 20px;
    border-radius: 4px;
    border: 1px solid rgba(0, 0, 0, 0.3);
    text-align: center;
  }

  .otp-input::-webkit-inner-spin-button,
  .otp-input::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  .otp-icon {
    border-radius: 100%;
    padding: 10px;
    background-color: rgb(78, 189, 181);
    color: #ffffff;
    font-size: 25px;
    width: 56px;
    text-align: center;
  }
</style>