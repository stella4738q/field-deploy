<template>
  <el-tabs v-model="TabActiveName" @tab-change="TabChange" :lazy="true">
    <el-tab-pane label="ECI" name="ECI">
      <RackECI ref="rackECI" :RackData="RackData" :RackName="RackName"></RackECI>
    </el-tab-pane>
    <el-tab-pane label="電芯電壓" name="v">
      <myChartV :RackData="RackData" :dif="dif" ></myChartV>
    </el-tab-pane>
    <el-tab-pane label="模組溫度" name="t">
      <myChartT :RackData="RackData"></myChartT>
    </el-tab-pane>
    <el-tab-pane label="模組極柱溫度" name="t2">
      <myChartT2 :RackData="RackData" :Parameter="'cell_terminal_temp'" ></myChartT2>
    </el-tab-pane>
  </el-tabs>

</template>

<script >

import myChartV from '@/components/ChartV.vue';
import myChartT from '@/components/ChartT.vue';
import myChartT2 from '@/components/ChartT2.vue';
import RackECI from '@/components/RackECI.vue';

export default {
props: {
  // BMSIndex: {
  //   type:Object,
  //   default: -1,
  // },
  RackIndex: {
    type:Number,
    default: -1,
  },
  TabName: {
    type:String,
    default:'ECI'
  },
  RackData:{
    type:Object,
    default: null,
  },
  RackName: {
    type:String,
    default:'Rack'
  },
  dif: {
    type:Number,
    default: 1,
  }
  
},
components: {
  myChartV, myChartT, myChartT2, RackECI
},
data() {
  return {
    TabActiveName: 'ECI',
  }
},
created() {
    this.TabActiveName = this.TabName??this.TabActiveName;
},
beforeUnmount() {
},
watch: {
},
computed: {
},
methods: {
  TabChange(name) {
    if (name == 't') {
      // if (!this.Drawed[name]) {
      //   this.Drawed[name] = true;
      // }
    }
    else if (name == 'ECI'){
      this.$refs.rackECI.ChartResize();
    }
  },
},
};
</script>
<style></style>