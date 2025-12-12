<template>
  <div class="textblock">
    <el-row :gutter="8">
      <el-col :span="6">
        <div class="iconblock">
          <i :class="`bi ${icon}`"></i>
        </div>
      </el-col>
      <el-col :span="18">
        <span class="number">{{ parsedNum }} {{ unit }}</span><br />
        <span class="hint">{{ hint }}</span>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'TextBlock',
  props: {
    icon: {
      type: String,
      default: 'bi-lightning-fill',
    },
    num: {
      type: [String, Number],
      default: 0,
    },
    unit: {
      type: String,
      default: '',
    },
    hint: {
      type: String,
      default: '',
    },
  },
  computed: {
    parsedNum() {
      const parsed = parseFloat(this.num);
      return isNaN(parsed) ? this.num : parsed.toLocaleString();
    },
  },
};
</script>

<style scoped>
.textblock {
  font-size: 16px;
}

.iconblock i {
  font-size: 24px;
}

.number {
  font-size: 20px;
  font-weight: bold;
}

.hint {
  color: #666;
  font-size: 16px;
}
</style>
