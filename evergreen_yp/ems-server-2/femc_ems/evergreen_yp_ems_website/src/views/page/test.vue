<template>
  <video style="height: 100vh;" src="rtsp://192.168.100.85:554/user=admin&password=admin&channel=1&stream=1.sdp?real_stream--rtp-ca">

  </video>
</template> 
<script>

export default {
  components: {

  },
  data() {
    return {

    };
  },
  computed: {
  },
  mounted() {

  },
  created() {

  },
  methods: {


  },
};
</script> 
<style>
.cube-container {
      width: 200px;
      height: 200px;
      perspective: 800px;
    }
    .cube {
      position: relative;
      width: 100%;
      height: 100%;
      transform-style: preserve-3d;
    }
    .face {
      position: absolute;
      width: 200px;
      height: 200px;
      background-color: #ff5722;
      opacity: 0.7;
    }
    .front {
      transform: translateZ(100px);
    }
    .back {
      transform: translateZ(-100px) rotateY(180deg);
    }
    .right {
      transform: rotateY(90deg) translateZ(100px);
    }
    .left {
      transform: rotateY(-90deg) translateZ(100px);
    }

    @keyframes rotate {
      from {
        transform: rotateY(0);
      }
      to {
        transform: rotateY(360deg);
      }
    }
</style>