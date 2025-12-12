<template>
  <teleport :disabled="!teleport" :to="teleport">
    <transition :name="animation">
      <div v-if="!transition" class="PCStable">
        <div class="d-flex">

          <table class="text-center" style="border-collapse: separate; border-spacing: 0; width: 250px;">
            <tr>
      <!-- <th class="text-start">PCS</th> -->
    </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">運行模式</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.running_status}}</td>
            </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">實功</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.active_power?.toFixed(0)}}kW</td>
            </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">虛功</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.reactive_power?.toFixed(0)}}kW</td>
            </tr>
          </table>
          <table class="text-center ms-3" style="border-collapse: separate; border-spacing: 0; width: 250px;">
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">R-S 相電壓</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.volt_rs?.toFixed(1)}}V</td>
            </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">S-T 相電壓</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.volt_st?.toFixed(1)}}V</td>
            </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">T-R 相電壓</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.volt_tr?.toFixed(1)}}V</td>
            </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">DC電壓</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.battery_voltage?.toFixed(1)}}V</td>
            </tr>
            <tr>
              <td style="border: 1px solid ;border-color: #3081D0">DC電流</td>
              <td style="border: 1px solid ;border-color: #3081D0">{{ props.data?.dc_current_avg?.toFixed(1)}}A</td>
            </tr>
          </table>

          <!-- <table class="ms-3" style="border-collapse: separate; border-spacing: 0; width: 150px;">
  <tr>
  <td class="text-center" style="border: 1px solid green; ">P</td>
  <td class="text-end" style="border: 1px solid green; ">kW</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green;">Q</td>
  <td class="text-end" style="border: 1px solid green;">kW</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green; ">S</td>
  <td class="text-end" style="border: 1px solid green;">kW</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green; ">V</td>
  <td class="text-end" style="border: 1px solid green; ">V</td>
</tr>
<tr>
  <td class="text-center" style="border: 1px solid green; ">I</td>
  <td class="text-end" style="border: 1px solid green; ">I</td>
</tr>
</table> -->
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
    data() {
      return {
        CBData: [
          { 'TK': 'Test', 'L/R': 'Remote', 'Relay': 'Trip', 'U': 281.2, 'I': 205, 'P': 1192, 'PF': 0.97 },
        ]
      }
    },
  }
</script>