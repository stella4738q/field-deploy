
<template>
    <teleport :disabled="!teleport" :to="teleport">
      <transition :name="animation">
        <div v-if="!transition" class="Meterportable">
          <!-- <Handle type="target" :position="Position.Top" /> -->
          <!-- {{ id }} -->
      <!-- <el-table id="exTable" stripe :data="CBData" border   class="rounded-3" :header-cell-style="{ border:'1px solid #3A86FF'}" :cell-style="{ border:'1px solid #3A86FF'}">
       <el-table-column align="center" width="" label="TK"  prop="TK"></el-table-column>
       <el-table-column align="center" width="" label="L/R" prop="L/R"></el-table-column>
       <el-table-column align="center" width="" label="Relay" prop="Relay"></el-table-column>
      </el-table>    
      <el-table id="exTable" stripe :data="CBData" border  class="rounded-3" :header-cell-style="{ border:'1px solid #3A86FF' }" :cell-style="{ border:'1px solid #3A86FF'}">
       <el-table-column align="center" width="" label="U" prop="U"></el-table-column>
       <el-table-column align="center" width="" label="I" prop="I"></el-table-column>
       <el-table-column align="center" width="" label="P"  prop="P"></el-table-column>
       <el-table-column align="center" width="" label="PF"  prop="PF"></el-table-column>
      </el-table> -->
<div class="d-flex">


<table class="" style="border-collapse: separate; border-spacing: 0; width: 200px;table-layout: fixed;">
  <tr>
      <th class="text-start">METER_SUN</th>
    </tr>
  <tr>
  <td class="text-center" style="border: 1px solid green;">P</td>
  <td class="text-end px-2" style="border: 1px solid green; ">{{ props.data.P?.toFixed(2) }}kW</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green;">Q</td>
  <td class="text-end px-2" style="border: 1px solid green;">{{ props.data.Q?.toFixed(2) }}kW</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green; ">S</td>
  <td class="text-end px-2" style="border: 1px solid green;">{{ props.data.S?.toFixed(2) }}kW</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green; ">V</td>
  <td class="text-end px-2" style="border: 1px solid green; ">{{ props.data.V?.toFixed(2) }}V</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green; ">I</td>
  <td class="text-end px-2" style="border: 1px solid green; ">{{ props.data.I?.toFixed(2) }}A</td>
</tr>
</table>
</div>
          <!-- <Handle type="source" :position="Position.Bottom" /> -->
        </div>
      </transition>
    </teleport>
  </template>

  <script setup>
    import { Handle, Position } from '@braks/vue-flow'
    import { useTransition } from '@/lib/useTransition.js'
    
    const props = defineProps({
  id: {
    type: String,
    required: true,
  }, data: {
    type: Object
  },
});
    
    const { animation, transition, teleport, onClick } = useTransition(props);
    const changeAnimation = () => {
      animation.value = animation.value === 'fade' ? 'shrink' : 'fade'
    };
    </script>
    
    <script>
    export default {
      inheritAttrs: false,
      data(){
        return{
          CBData:[
            {'TK':'Test','L/R':'Remote','Relay':'Trip','U':281.2,'I':205,'P':1192,'PF':0.97},
          ]
        }
      },
    }
    </script>
    