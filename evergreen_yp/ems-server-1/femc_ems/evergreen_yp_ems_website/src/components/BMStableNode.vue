
<template>
    <teleport :disabled="!teleport" :to="teleport">
      <transition :name="animation">
        <div v-if="!transition" class="BMStable">
          <!-- {{ id }} -->
<div class="d-flex">

  <table class="text-center" style="border-collapse: separate; border-spacing: 0; width: 250px;border-color: #3081D0">
    <!-- <tr>
      <th class="text-start">BMS</th>
    </tr> -->
  <tr>
  <td style="border: 1px solid ;">運行模式</td>
  <td style="border: 1px solid ;">{{ props.data?.status}}</td>
</tr>
<tr>
  <td style="border: 1px solid ;">系統電壓</td>
  <td style="border: 1px solid ;">{{ props.data?.voltage?.toFixed(2)}}V</td>
</tr>
<tr>
  <td style="border: 1px solid ;">系統電流</td>
  <td style="border: 1px solid ;">{{ props.data?.current?.toFixed(2)}}A</td>
</tr>
<tr>
  <td style="border: 1px solid ;">SOC</td>
  <td style="border: 1px solid ;">{{ props.data?.soc}}%</td>
</tr>
<tr>
  <td style="border: 1px solid ;">SOH</td>
  <td style="border: 1px solid ;">{{ props.data?.soh}}%</td>
</tr>
</table>
<table class="text-center ms-3" style="border-collapse: separate; border-spacing: 0; width: 250px;border-color: #3081D0">
<tr>
  <td style="border: 1px solid ;">CV(Max)</td>
  <td style="border: 1px solid ;">{{ props.data?.max_cell_voltage?.toFixed(2)}}V</td>
</tr>
<tr>
  <td style="border: 1px solid ;">CV(Min)</td>
  <td style="border: 1px solid ;">{{ props.data?.min_cell_voltage?.toFixed(2)}}V</td>
</tr>
<tr>
  <td style="border: 1px solid ;">CT(Max)</td>
  <td style="border: 1px solid ;">{{ props.data?.max_cell_temperature}}°C</td>
</tr>
<tr>
  <td style="border: 1px solid ;">CT(Min)</td>
  <td style="border: 1px solid ;">{{ props.data?.min_cell_temperature}}°C</td>
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
    
    const { animation, transition, teleport, onClick } = useTransition(props.id);
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
    