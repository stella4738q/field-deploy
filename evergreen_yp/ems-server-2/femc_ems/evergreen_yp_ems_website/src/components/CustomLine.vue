<template>
  {{isAbnormal}}
  <path
    :stroke="isAbnormal ? 'red' : defaultColor"
    :d="edgePath"
    fill="none"
    :class="{ flashing: isAbnormal }" :style="style"
  />
</template>

<script setup>
import { computed } from 'vue'
import { getSmoothStepPath } from '@braks/vue-flow'

const props = defineProps({
  data: Object,
  style: Object,
  sourceX: Number,
  sourceY: Number,
  targetX: Number,
  targetY: Number,
  sourcePosition: String,
  targetPosition: String
})

// 這裡的 data 讀取方式，請依照您利澤場主檔案的寫法決定
// 如果主檔案是 <CustomLine :data="props" />，請用下面這幾行
const customData = computed(() => props.data?.data || {});
const isAbnormal = computed(() => customData.value.isAbnormal ?? false);
const defaultColor = computed(() => customData.value.defaultColor ?? 'gray');

/* // 如果主檔案是 <CustomLine v-bind="props" />，請用下面這幾行
const isAbnormal = computed(() => props.data?.isAbnormal ?? false);
const defaultColor = computed(() => props.data?.defaultColor ?? 'gray');
*/

const edgePath = computed(() =>
  getSmoothStepPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    targetX: props.targetX,
    targetY: props.targetY,
    sourcePosition: props.sourcePosition,
    targetPosition: props.targetPosition
  })
)
</script>

<style scoped>
.flashing {
  animation: flash 1s infinite alternate;
}

@keyframes flash {
  0% {
    opacity: 1;
    stroke: red;
    stroke-width: 3;
  }
  100% {
    opacity: 0.1;
    stroke: red;
    stroke-width: 6;
  }
}
</style>