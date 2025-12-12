
<template>
    <div>
        <div class="text-center pt-2" style="width: 100%;font-size: 20px;">
  
        {{ data.label }}
      </div>
      <Handle type="source" :position="sourcePosition" style="opacity: 0" />
      <Handle type="target" :position="targetPosition" style="opacity: 0"/>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue';
  import { Controls, VueFlow, useVueFlow, Position,  Handle, useHandleConnections} from '@braks/vue-flow'
  defineProps(['id', 'sourcePosition', 'targetPosition', 'data'])
  // const props = defineProps({
  //   data: {
  //     type: Object,
  //   },
  // });
  </script>

  