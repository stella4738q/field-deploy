
<template>
    <teleport :disabled="!teleport" :to="teleport">
      <transition :name="animation">
        <div v-if="!transition" class="Racktable">
          <!-- {{ id }} -->
<div class="d-flex">

  <table class="text-center px-3" style="border-collapse: separate; border-spacing: 0; width: 300px;border-color: #3081D0">
<tr>
  <td style="border: 1px solid ;">電壓</td>
  <td style="border: 1px solid ;">{{ props.data?.rack_voltage?.toFixed(1)}}V</td>
  <!-- <td style="border: 1px solid ;">{{ props.data?.rack2_voltage}}V</td>
  <td style="border: 1px solid ;">{{ props.data?.rack3_voltage}}V</td>
  <td style="border: 1px solid ;">{{ props.data?.rack4_voltage}}V</td>
  <td style="border: 1px solid ;">{{ props.data?.rack5_voltage}}V</td>
  <td style="border: 1px solid ;">{{ props.data?.rack6_voltage}}V</td> -->
</tr>
<tr>
  <td style="border: 1px solid ;">電流</td>
  <td style="border: 1px solid ;">{{ props.data?.rack_current?.toFixed(1)}}A</td>
  <!-- <td style="border: 1px solid ;">{{ props.data?.rack2_current}}A</td>
  <td style="border: 1px solid ;">{{ props.data?.rack3_current}}A</td>
  <td style="border: 1px solid ;">{{ props.data?.rack4_current}}A</td>
  <td style="border: 1px solid ;">{{ props.data?.rack5_current}}A</td>
  <td style="border: 1px solid ;">{{ props.data?.rack6_current}}A</td> -->
</tr>
<tr>
  <td style="border: 1px solid ;">SOC</td>
  <td style="border: 1px solid ;">{{ props.data?.rack_soc}}%</td>
  <!-- <td style="border: 1px solid ;">{{ props.data?.rack2_soc}}%</td>
  <td style="border: 1px solid ;">{{ props.data?.rack3_soc}}%</td>
  <td style="border: 1px solid ;">{{ props.data?.rack4_soc}}%</td>
  <td style="border: 1px solid ;">{{ props.data?.rack5_soc}}%</td>
  <td style="border: 1px solid ;">{{ props.data?.rack6_soc}}%</td> -->
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
    