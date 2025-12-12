
<template>
    <div>
      <div class="text-center pt-2" style="width: 100%;height: 100%; font-size: 20px; color: white;" :style="{ backgroundColor: data.class }">
        {{ data.label }}
      </div>

      <Handle type="source" :position="sourcePosition" style="opacity: 0" />
      <Handle type="target" :position="targetPosition" style="opacity: 0"/>

    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue';
  import { Controls, VueFlow, useVueFlow, Position,  Handle} from '@braks/vue-flow'

  defineProps(['id', 'sourcePosition', 'targetPosition', 'data'])
  </script>

