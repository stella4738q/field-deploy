<template>
  <div class="dcu-container">
    <!-- 標題區塊 -->
    <div class="dcu-header">
      <span class="dcu-title">{{ dcu.equipment_id }}（{{ dcu.operation_mode_name || '未知模式' }} / {{ dcu.pure_power_percent || '-' }}%）</span>
      <div class="dcu-metrics">
        <span>輸出百分比: {{ getInverterTotalPercent(dcu) }} %</span>
        <span>AC功率: {{ dcu.ac_power_kw?.toFixed(2) || 0 }} kW</span>
        <span>電流: {{ dcu.ac_current?.toFixed(2) || 0 }} A</span>
        <span>電壓: {{ dcu.ac_voltage_ab?.toFixed(2) || 0 }} / {{ dcu.ac_voltage_bc?.toFixed(2) || 0 }} / {{ dcu.ac_voltage_ca?.toFixed(2) || 0 }} V</span>
        <span>溫度: {{ dcu.temp_sink || 0 }} ℃</span>
        <span>最後更新時間: {{ formatTimestamp(dcu.data_time) }}</span>
      </div>
    </div>

    <!-- Inverter 卡片 -->
    <el-row :gutter="20" class="mb-3">
      <el-col
        v-for="inv in (dcu.inverter || [])"
        :key="inv.equipment_id"
        :xs="24" :sm="12" :md="8"
      >
        <el-card>
          <div class="inverter-title">逆變器 {{ inv.equipment_id }}</div>
          <div class="inverter-detail">
            <p>輸出百分比: {{ getInverterPercent(inv) }} %</p>
            <p>DC 功率: {{ inv.dc_k_watt?.toFixed(2) || 0 }} kW</p>
            <p>DC 電壓: {{ inv.dc_voltage?.toFixed(2) || 0 }} V</p>
            <p>DC 電流: {{ inv.dc_ampere?.toFixed(2) || 0 }} A</p>
            <p>溫度: {{ inv.temperature?.toFixed(0) || 0 }} ℃</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 優化器 toggle -->
    <el-button size="large" @click="showOptimizer = !showOptimizer" class="mb-1">
      {{ showOptimizer ? '隱藏優化器資訊' : '顯示優化器資訊' }}
    </el-button>

    <!-- 優化器表格 -->
    <el-table
      v-if="showOptimizer"
      :data="optimizer"
      border
      class="optimizer-table"
      style="width: 100%"
      :row-class-name="zebraStripe"
    >
      <el-table-column prop="no" label="#" width="50" />
      <el-table-column prop="serial_no" label="序號" />
      <el-table-column prop="dc_input_voltage" label="input 電壓(V)" :formatter="decimalFormatter" />
      <el-table-column prop="dc_input_current" label="input 電流(A)" :formatter="decimalFormatter" />
      <el-table-column prop="dc_input_power" label="input 功率(W)" :formatter="decimalFormatter" />
      <el-table-column prop="temperature" label="溫度" :formatter="decimalFormatter" />
      <el-table-column prop="dc_output_voltage" label="output 電壓(V)" :formatter="decimalFormatter" />
      <el-table-column prop="dc_output_current" label="output 電流(A)" :formatter="decimalFormatter" />
      <el-table-column prop="dc_output_power" label="output 功率(W)" :formatter="decimalFormatter" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { getEquipments, postModbusControl } from '@/api/Api.js';

const props = defineProps({
  dcu: Object
})

const showOptimizer = ref(false)
const optimizer = computed(() => props.dcu.optimizer || [])
const dcuCapacities = ref({})  // key: equipment_id, value: capacity
const inverterCapacities = ref({})  // key: equipment_id, value: capacity

function decimalFormatter(_, __, cellValue) {
  return cellValue != null ? Number(cellValue).toFixed(2) : '-'
}

function zebraStripe({ rowIndex }) {
  return rowIndex % 2 === 0 ? 'row-even' : 'row-odd'
}

function formatTimestamp(dateString) {
  const dt = new Date(dateString)
  const pad = (n) => n.toString().padStart(2, '0')
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ` +
         `${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`
}

function getInverterPercent(inv) {
  const power = inv?.dc_k_watt || 0
  const cap = inverterCapacities.value[inv.equipment_id] || 0
  if (!cap || cap === 0) return '0'
  return ((power / cap) * 100).toFixed(1)
}

function getInverterTotalPercent(dcu) {
  const list = dcu?.inverter || []
  let totalPower = 0
  let totalCap = 0
  for (const inv of list) {
    const power = inv?.dc_k_watt || 0
    const cap = inverterCapacities.value[inv.equipment_id] || 0
    if (cap > 0) {
      totalPower += power
      totalCap += cap
    }
  }
  if (totalCap === 0) return '0'
  return ((totalPower / totalCap) * 100).toFixed(1)
}

async function getEquipment(inverterId) {
  try {
    const res = await getEquipments({
      parent_id: props.dcu.equipment_id,
      equipment_type: 3,
      name: inverterId
    })
    const cap = res.data?.data?.[0]?.capacity ?? 0
    inverterCapacities.value[inverterId] = cap
  } catch (err) {
    console.error('取得設備資訊失敗', err)
  }
}

watch(
  () => props.dcu.inverter,
  (inverters) => {
    if (Array.isArray(inverters)) {
      inverters.forEach(inv => {
        if (inv?.equipment_id && inverterCapacities.value[inv.equipment_id] == null) {
          getEquipment(inv.equipment_id)
        }
      })
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.dcu-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 6px 12px;
  background-color: rgba(255, 255, 255, 0.9); /* 白底微透明 */
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);       /* 微陰影 */
  color: #2d3748; /* 深灰字 */
  font-weight: 500;
}

.dcu-container {
  padding: 12px;
  border: 1px solid #dcdfe6;
  margin-bottom: 24px;
  border-radius: 4px;
}

.dcu-header {
  background-color: #2f855a;
  color: white;
  padding: 10px 20px;
  font-weight: bold;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.dcu-title {
  font-size: 18px;
}

.dcu-metrics span {
  margin-right: 16px;
  font-size: 14px;
}

.inverter-title {
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 8px;
}

.inverter-detail {
  font-size: 16px;
}

.optimizer-table {
  font-size: 14px;
}

.el-table th {
  font-weight: bold;
}

/* Zebra row stripe */
::v-deep(.row-even) {
  background-color: #f9f9f9;
}
::v-deep(.row-odd) {
  background-color: #ffffff;
}
</style>
