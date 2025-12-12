<template>
  <div>
    <button type="button" class="btn btn-text text-white" style="width: 100%" @click="onClick(color)">{{ props.data.label }}</button>

  </div>
</template>
<script setup>

const props = defineProps({
  data: {
    type: Object,
  },
})

const emit = defineEmits(['myClick'])

function onClick() {
  emit('myClick')
}
</script>