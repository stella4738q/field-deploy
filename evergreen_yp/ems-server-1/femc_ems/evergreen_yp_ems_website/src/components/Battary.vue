<template>

    <div class="battary" style="width: 100% ; max-width:100px; min-width:60px; margin: 0 auto;">
        <div class="battaryTop"></div>
        <div class="battaryCell">
            <div class="cell" v-for="n in nData" :key="n">
                <div class="cellcolor " :style="getStyle(n)" ></div>
            </div> 
        </div>
    </div>
</template>

<script > 

import ColorList from '@/JSON/ColorRange.json';

    export default {
      props: {
        SOC: {
            type:Number,
            default : 37
        },
      },
      components: {
      },
      data() {
          return {
            ColorList,
             nData : [10,9,8,7,6,5,4,3,2,1]
          };
        },
        created() {
        },
        watch: {
          // "SOC" : function (newVal,oldVal) {
          //   this.initChart();
          // }
        },
        computed:{
          getColor:function () {
            const vm = this;
            var color = this.ColorList.SOC.Range.find((item) => { return vm.SOC >= item.range[0] && vm.SOC <= item.range[1] });
            return color?.color; 
          }
        },
        methods: {
           getStyle(n) {
            var nbegin = (n -1) * 10;
            var nEnd = n *10;
            var result = {};
            if (this.SOC > nEnd) {
              result.backgroundColor = this.getColor;
            } 
            else if (this.SOC < nbegin ) 
            { 
              result.height = '0';
            }  else {
              result.height = ((this.SOC - nbegin) * 10) + '%' ;
              result.backgroundColor = this.getColor;
            }  

            if (this.SOC > 64.0 && this.SOC < 65.0) {
            }

            return result;
           }, 
        },
    };
</script>
<style> 
  .battaryCell .cell:first-child  , .battaryCell .cell:first-child .cellcolor  {
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
  } 
  .battaryCell .cell:last-child , .battaryCell .cell:last-child .cellcolor {
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
  } 
  .battaryCell .cell {
    border: 1px solid #dee2e6 ;
    height: 20px;
    margin: 0 0.1rem 2px 0.1rem;
    position: relative;
    background-color: white;
  } 
  .battaryCell {
    border: 2px solid  #dee2e6;
    border-radius: 10px;
    padding-top:2px;
    position: relative;
    /* background-color: lightgray; */
  }
  .soc {
    position:absolute;
    top:45%;
    z-index: 99;
    width: 100%;
    text-align: center;
    background-color: rgba(255,255,255,0.5);
  }
  .soc .content{
    opacity: 1;
    color: lightslategray;
  }
  .cellcolor {
    height: 100%;
   
    width:100%;
    position: absolute;
    bottom: 0;
  }
  .battaryTop {
    width: 30%;
    height: 0.3rem;
    margin: 0 auto;
    background-color: #eee;
  }
</style>