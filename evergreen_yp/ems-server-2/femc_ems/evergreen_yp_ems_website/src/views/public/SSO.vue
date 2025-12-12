<template>
  <div class="bg d-flex d-flex align-items-center justify-content-center row m-0" style="width:100vw; height:100vh; background:rgb(7,30,61);">
    <div class="col-md-6" style="">
      <div class="ms-2 me-2 w-100 row  d-flex align-items-center justify-content-center" style="height: 90vh;  background:white; border-radius:2rem;">
          <div class=" row m-0" style="width: 20vw;">
            <img src="@/assets/FEMCBanner.png" alt="" class="mb-5" style="height:100px" >
        
            <div class=" text-center mt-3 "> 
              登入中…
            </div>
          </div>
      </div>
    </div>
    <div class="d-none d-md-block col-md-6 bg-green" style="height:100% "></div>
   
  </div>
</template>

<script >
import { SSO } from '@/api/Api.js'

export default {
  data() {
    return {
    };
  },
  created() {
    window.addEventListener('message', this.login)
  },
  watch: {
  },
  methods: {
    login(event) {
      const vm = this;
      var header = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        "Femc-Access-Token" : event.data
      };
      SSO({type: 2} , header ).then((response) => {
         if (response.data.Msg == "Success") {
          this.$store.commit('loginSuccess' ,response.data);
          this.$router.push({ name: "Dashboard" });
        } else {
          vm.$message({ type:'error' , message:"登入失敗" });
          this.$router.push({ name: "login" });
        
        }
      }).catch((response) => {
        vm.$message({ type:'error' , message:"登入失敗" });
        this.$router.push({ name: "login" });
      });
    },
  },
};
</script>
<style type="text/css" scoped>
.bg-green {
  background: no-repeat url('@/assets/loginBackgroud2.jpg') center;
  background-size: cover;
}

@media(max-width: 380px) {
  .wrapper {
    margin: 30px 20px;
    padding: 40px 15px 15px 15px
  }
}
</style>