<template>
  <VueFlow v-model="elements" fit-view-on-init class="basicflow" :zoomOnScroll="true" :min-zoom="0.2" :max-zoom="4"
    ref="myVueFlow" style="height:100vh; width:100%">
    <template #node-teleportable="props">
      <TeleportableNode v-bind="props" />
    </template>
    <template #node-PCSportable="props">
      <PCStableNode v-bind="props" />
    </template>
    <template #node-TRportable="props">
      <TRtableNode v-bind="props" />
    </template>
    <template #node-BMSportable="props">
      <BMStableNode v-bind="props" />
    </template>
    <template #node-RACKportable="props">
      <RACKtableNode v-bind="props" />
    </template>
    <template #node-INVportable="props">
      <INVtableNode v-bind="props" />
    </template>
    <template #node-custom="props">
      <CustomNode v-bind="props" :data="props" @myClick="myClick(props)" 
       :disabled="controlDisabled" />
    </template>
    <template #node-color="props">
      <ColorNode v-bind="props" :data="props" />
    </template>
    <Controls :showInteractive="false" />
  </VueFlow>

  <el-dialog v-model="Dialog" width="850px" :show-close="false">
    <CBControl :equipmentId="vcbId" :SocketData="cbData" :iecControl="cbData.equipment_id == 'VCB'" ></CBControl>
  </el-dialog>
</template>

<script setup>

  import { ref, computed, watch } from 'vue';
  import { useStore, mapState } from 'vuex';
  import { Controls, VueFlow, useVueFlow } from '@braks/vue-flow';

  // import ElectricData from '@/JSON/ElectricData.json'
  import TeleportableNode from '@/components/TeleportableNode.vue';
  import PCStableNode from '@/components/PCStableNode.vue';
  import TRtableNode from '@/components/TRtableNode.vue';
  import BMStableNode from '@/components/BMStableNode.vue';
  import RACKtableNode from '@/components/RACKtableNode.vue';
  import CustomNode from '@/components/CustomNode.vue';
  import CBControl from '@/components/CBControl.vue';
  import ColorNode from '@/components/CustomColorNode.vue';
  import EquipmentStatusColor from '@/JSON/EquipmentStatusColor.json';


  const { onPaneReady, onConnect, addEdges, setTransform, toObject, nodes, addNodes, setNodes, setEdges, dimensions, fitView, setInteractive } = useVueFlow();
  const store = useStore();

  let Dialog = ref(false);
  let vcbId = ref('');
  let cbData = ref({});
  const myClick = ((node) => {
    vcbId.value = node?.id;
    Dialog.value = true;
    cbData.value = node?.data;
  });
  const controlDisabled = computed(() =>
    store.getters.userPriviagePage('P01-09')
  );

  const storeState = mapState(["SocketDataALL"]);
  const resultStoreState = {};
  Object.keys(storeState).map((item) => {
    const resFuc = storeState[item];
    resultStoreState[item] = computed(resFuc.bind({ $store: store }));
  });
  const { SocketDataALL } = { ...resultStoreState };

  const METER_MP1= SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_MP1' });
  const annM1 = ref(METER_MP1?.total_active_power ? (METER_MP1?.total_active_power < 0 ? 'reverse' : 'normal') : null); // 这里将 annM1 变为 ref，使其响应式

  const METER_MP2= SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_MP2' });
  const annM2 = ref(METER_MP2?.total_active_power ? (METER_MP2?.total_active_power < 0 ? 'reverse' : 'normal') : null); // 这里将 annM2 变为 ref，使其响应式
  //太陽能流向//跟儲能相反
  const METER_SUN1 = SocketDataALL.value.meter?.find(x => x.equipment_id == 'METER_SUN1');
  const annSun1 = ref(METER_SUN1?.total_active_power ? (METER_SUN1?.total_active_power < 0 ? 'normal' : 'reverse') : null); 

  const METER_SUN2 = SocketDataALL.value.meter?.find(x => x.equipment_id == 'METER_SUN2');
  const annSun2 = ref(METER_SUN2?.total_active_power ? (METER_SUN2?.total_active_power < 0 ? 'normal' : 'reverse') : null); 
 
  const METER_VCB = SocketDataALL.value.meter?.find(x => x.equipment_id == 'METER_VCB');
  const annVCB = ref(METER_VCB?.total_active_power ? (METER_VCB?.total_active_power < 0 ? 'reverse' : 'normal') : null); 

  watch(annM1, (newValue, oldValue) => {
    console.log(oldValue);
    if ((newValue == null || oldValue == undefined) && (oldValue == null || oldValue == undefined)) {
      if (newValue !== oldValue) {
        location.reload(); // 重新载入网页
      }
    }
  }, { immediate: false });

  watch(annM2, (newValue, oldValue) => {
    if ((newValue == null || oldValue == undefined) && (oldValue == null || oldValue == undefined)) {
      if (newValue !== oldValue) {
        location.reload(); // 重新载入网页
      }
    }
  }, { immediate: false });

  watch(annSun1, (newValue, oldValue) => {
    if ((newValue == null || oldValue == undefined) && (oldValue == null || oldValue == undefined)) {
      if (newValue !== oldValue) {
        location.reload(); // 重新载入网页
      }
    }
  }, { immediate: false });
 
  watch(annSun2, (newValue, oldValue) => {
    if ((newValue == null || oldValue == undefined) && (oldValue == null || oldValue == undefined)) {
      if (newValue !== oldValue) {
        location.reload(); // 重新载入网页
      }
    }
  }, { immediate: false });

  const elements = computed(() => {
    let VCB = SocketDataALL.value.relay?.find(x => { return x.equipment_id == 'VCB' });
    let ACB_1 = SocketDataALL.value.relay?.find(x => { return x.equipment_id == 'ACB_IO_MP1' });
    let ACB_2 = SocketDataALL.value.relay?.find(x => { return x.equipment_id == 'ACB_IO_MP2' });

    let PCS1data = SocketDataALL.value.pcs ?.find(x => { return x.equipment_id == 'PCS_1' });
    let PCS2data = SocketDataALL.value.pcs ?.find(x => { return x.equipment_id == 'PCS_2' });
    let BMS1data = SocketDataALL.value.bms?.find(x => { return x.equipment_id == 'BMU_1' });
    let BMS2data =  SocketDataALL.value.bms?.find(x => { return x.equipment_id == 'BMU_2' });
    let TRdata = SocketDataALL.value.tr ?.find(x => { return x.equipment_id == 'TR' });

    let METER_MP1 = SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_MP1' });
    annM1.value = METER_MP1?.total_active_power ? (METER_MP1?.total_active_power < 0 ? 'reverse' : 'normal') : null;  //reverse=放電, normal=充電
    let useAnn1 = ![null, 0, undefined].includes(METER_MP1?.total_active_power);
    
    let METER_MP2 = SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_MP2' });
    annM2.value = METER_MP2?.total_active_power ? (METER_MP2?.total_active_power < 0 ? 'reverse' : 'normal') : null;  //reverse=放電, normal=充電
    let useAnn2 = ![null, 0, undefined].includes(METER_MP2?.total_active_power);

    let METER_SUN1 = SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_SUN1' });
    annSun1.value = METER_SUN1?.total_active_power ? (METER_SUN1?.total_active_power < 0 ? 'normal' : 'reverse') : null;
    let useAnnSun1 = ![null, 0, undefined].includes(METER_SUN1?.total_active_power);

    let METER_SUN2 = SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_SUN2' });
    annSun2.value = METER_SUN2?.total_active_power ? (METER_SUN2?.total_active_power < 0 ? 'normal' : 'reverse') : null;
    let useAnnSun2 = ![null, 0, undefined].includes(METER_SUN2?.total_active_power);

    let METER_VCB = SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_VCB' });
    annVCB.value = METER_VCB?.total_active_power ? (METER_VCB?.total_active_power < 0 ? 'reverse' : 'normal') : null;
    let useAnnVCB = ![null, 0, undefined].includes(METER_VCB?.total_active_power);

    let METER_MAIN = SocketDataALL.value.meter?.find(x => { return x.equipment_id == 'METER_MAIN' });

    const colorClass = {
      danger: 'bg-danger',
      warning: 'bg-warning',
      success: 'bg-success',
      dark: 'bg-dark',
    };

    const getRackClass = (attrBMS, attrRack) => {
      var find = SocketDataALL.value?.bms?.find(x => ( x.equipment_id == attrBMS ))?.rack.find(x => ( x.equipment_id == attrRack ));
      if (find) {
        // 取得設備的狀態顏色
        const state_color = EquipmentStatusColor.RACK.find(x => x.name === find.rack_state)?.color || '';
        
        // 檢查是否有 2 級或以上的告警
        const lv_2_alarm = find.warning?.find(ala => ala.level >= 2);
        
        // 判斷顏色邏輯
        if (lv_2_alarm || state_color.includes('danger')) {
            return 'bg-danger';
        }
        
        // 根據是否異常設定背景顏色
        return find.abnormal ? 'bg-warning' : ` ${state_color}`;
      }
      return 'bg-dark';
    };

    const getPCSClass = (attr) => {
          var find = SocketDataALL.value.pcs ?.find(x => { return x.equipment_id == attr });
          if (find) {
              // 取得設備的狀態顏色
              const state_color = EquipmentStatusColor.PCS.find(x => x.name === find.running_status)?.color || '';
              
              // 檢查是否有 2 級或以上的告警
              const lv_2_alarm = find.warning?.find(ala => ala.level >= 2);
              
              // 判斷顏色邏輯
              if (lv_2_alarm || state_color.includes('danger')) {
                  return 'bg-danger';
              }
              
              // 根據是否異常設定背景顏色
              return find.abnormal ? 'bg-warning' : `bg-${state_color}`;
          }
          return 'bg-dark';
    };

    const getBMSClass = (attr) => {
        var find = SocketDataALL.value?.bms?.find(x => { return x.equipment_id == attr });
        if (find) {
            // 取得設備的狀態顏色
            const state_color = EquipmentStatusColor.BMS.find(x => x.name === find.status)?.color || '';
            
            // 檢查是否有 2 級或以上的告警
            const lv_2_alarm = find.warning?.find(ala => ala.level >= 2);
            // 判斷顏色邏輯
            if (lv_2_alarm || state_color.includes('danger')) {
                return 'bg-danger';
            }
            
            // 根據是否異常設定背景顏色
            return find.abnormal ? 'bg-warning' : `bg-${state_color}`;
        }
        return 'bg-dark';
    };

    return [
      //以下是大框
      { id: "廠內69KV併接點", type: "input", label: "廠內69KV併接點", position: { x: 410, y: -230 }, class: "light", style: { width: "170px", height: "50px", textAlign: "center", borderColor: "black", fontSize: "18px" }, draggable: false },
      { id: "VCB-BESS盤", type: "custom", data: VCB, label: "VCB-BESS盤", class: `btn  ${VCB == null ? 'btn-secondary ' : (VCB?.abnormal ? 'btn-danger' : 'btn-success')}`, position: { x: 420, y: -60 }, draggable: false },
      { id: "BESS-TR", type: "default", label: "BESS-TR", position: { x: 450, y: 80 }, class: "light", style: { width: "90px", height: "90px", borderRadius: "50%", textAlign: "center", borderColor: "black", fontSize: "18px" }, draggable: false },
      { id: "MP-BESS盤_A", type: "custom", data: ACB_1, label: "MP-BESS盤_A", class: `btn  ${ACB_1 == null ? 'btn-secondary ' : (ACB_1?.abnormal ? 'btn-danger' : 'btn-success')}`, position: { x: -80, y: 300 }, draggable: false },
      { id: "MP-BESS盤_B", type: "custom", data: ACB_2, label: "MP-BESS盤_B", class: `btn  ${ACB_2 == null ? 'btn-secondary ' : (ACB_2?.abnormal ? 'btn-danger' : 'btn-success')}`, position: { x: 795, y: 300 }, draggable: false },
      { id: "PCS_1", type: "color", label: "PCS_1", position: { x: -75, y: 550 }, class: `${getPCSClass('PCS_1')}`, style: { width: "150px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px", color: "white" }, draggable: false },
      { id: "PCS_2", type: "color", label: "PCS_2", position: { x: 800, y: 550 }, class: `${getPCSClass('PCS_2')}`, style: { width: "150px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px", color: "white" }, draggable: false },
      //bms
      { id: "BMS_1", type: "color", label: "BMS_1", position: { x: -75, y: 760 }, class: `${getBMSClass('BMU_1')}`, style: { width: "150px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px" ,color: "white"}, draggable: false, sourcePosition: "left", targetPosition: "top" },
      { id: "BMS_2", type: "color", label: "BMS_2", position: { x: 800, y: 760 }, class: `${getBMSClass('BMU_2')}`, style: { width: "150px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px" ,color: "white"}, draggable: false, sourcePosition: "left", targetPosition: "top" },
      { id: "BMS_1Rack1", type: "color", label: "Rack1", position: { x: -60, y: 950 }, class: `${getRackClass('BMU_1','rack_1')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_1Rack2", type: "color", label: "Rack2", position: { x: -60, y: 1080 }, class: ` ${getRackClass('BMU_1','rack_2')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_1Rack3", type: "color", label: "Rack3", position: { x: -60, y: 1210 }, class: ` ${getRackClass('BMU_1','rack_3')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_1Rack4", type: "color", label: "Rack4", position: { x: -60, y: 1340 }, class: ` ${getRackClass('BMU_1','rack_4')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_1Rack5", type: "color", label: "Rack5", position: { x: -60, y: 1470 }, class: ` ${getRackClass('BMU_1','rack_5')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_1Rack6", type: "color", label: "Rack6", position: { x: -60, y: 1600 }, class: ` ${getRackClass('BMU_1','rack_6')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left"},
      { id: "BMS_2Rack1", type: "color", label: "Rack1", position: { x: 815, y: 950 }, class: ` ${getRackClass('BMU_2','rack_1')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_2Rack2", type: "color", label: "Rack2", position: { x: 815, y: 1080 }, class: ` ${getRackClass('BMU_2','rack_2')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px",color: "white" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_2Rack3", type: "color", label: "Rack3", position: { x: 815, y: 1210 }, class: ` ${getRackClass('BMU_2','rack_3')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px" ,color: "white"}, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_2Rack4", type: "color", label: "Rack4", position: { x: 815, y: 1340 }, class: ` ${getRackClass('BMU_2','rack_4')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px" ,color: "white"}, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "BMS_2Rack5", type: "color", label: "Rack5", position: { x: 815, y: 1470 }, class: ` ${getRackClass('BMU_2','rack_5')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px" ,color: "white"}, draggable: false, sourcePosition: "right", targetPosition: "left"},
      { id: "BMS_2Rack6", type: "color", label: "Rack6", position: { x: 815, y: 1600 }, class: ` ${getRackClass('BMU_2','rack_6')}`, style: { width: "120px", height: "50px", textAlign: "center", fontSize: "18px", borderRadius: "5px" ,color: "white"}, draggable: false, sourcePosition: "right", targetPosition: "left" },
      //太陽能
      { id: "PV併接點", type: "input", label: "PV併接點", position: { x: -1265, y: -230 }, class: "light", style: { width: "170px",  height: "50px",color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)",borderRadius: "5px"}, draggable: false },
      { id: "MVCB1", type: "output", label: "MVCB1", position: { x: -1225, y: 10 }, class: "light", style: { width: "90px", height: "90px", borderRadius: "50%", textAlign: "center", borderColor: "black", fontSize: "18px", display: "flex",  justifyContent: "center", alignItems: "center"}, draggable: false },
      { id: "F1併接點", type: "input", label: "F1併接點", position: { x: -965, y: -230 }, class: "light", style: { width: "170px",  height: "50px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)",borderRadius: "5px"}, draggable: false },
      { id: "MVCB2", type: "output", label: "MVCB2", position: { x: -925, y: 10 }, class: "light", style: { width: "90px", height: "90px", borderRadius: "50%", textAlign: "center", borderColor: "black", fontSize: "18px", display: "flex",  justifyContent: "center", alignItems: "center"}, draggable: false },
      //狀態標示
      { id: "設備狀態", type: "color", label: "設備狀態", position: { x: -50, y: -230 }, class: "light", style: { width: "300px", height: "100px", textAlign: "center", fontSize: "18px", borderRadius: "5px" }, draggable: false },
      { id: "正常color", type: "color", label: "", position: { x: -35, y: -160 }, class: "light", style: { width: "20px", height: "20px", textAlign: "center", fontSize: "18px", borderRadius: "3px", backgroundColor: "rgba(25, 135, 84)" }, draggable: false },
      { id: "正常", type: "color", label: "正常", position: { x: -15, y: -172 }, class: "light", style: { width: "40px", height: "40px", textAlign: "center", fontSize: "18px", color: "black", borderRadius: "3px" }, draggable: false },
      { id: "系統程序color", type: "color", label: "", position: { x: 35, y: -160 }, class: "light", style: { width: "20px", height: "20px", textAlign: "center", fontSize: "18px", borderRadius: "3px", backgroundColor: "rgba(225, 193, 7)" }, draggable: false },
      { id: "系統程序", type: "color", label: "告警", position: { x: 37, y: -172 }, class: "light", style: { width: "80px", height: "40px", textAlign: "center", fontSize: "18px", color: "black", borderRadius: "3px" }, draggable: false },
      { id: "異常color", type: "color", label: "", position: { x: 105, y: -160 }, class: "light", style: { width: "20px", height: "20px", textAlign: "center", fontSize: "18px", borderRadius: "3px", backgroundColor: "rgba(220, 53, 69)" }, draggable: false },
      { id: "異常", type: "color", label: "異常", position: { x: 107, y: -172 }, class: "light", style: { width: "80px", height: "40px", textAlign: "center", fontSize: "18px", color: "black", borderRadius: "3px" }, draggable: false },
      { id: "關閉color", type: "color", label: "", position: { x: 175, y: -160 }, class: "light", style: { width: "20px", height: "20px", textAlign: "center", fontSize: "18px", borderRadius: "3px", backgroundColor: "rgba(33, 37, 41)" }, draggable: false },
      { id: "關閉", type: "color", label: "關閉", position: { x: 177, y: -172 }, class: "light", style: { width: "80px", height: "40px", textAlign: "center", fontSize: "18px", color: "black", borderRadius: "3px" }, draggable: false },

      // 0 跟沒有值的時候不要有動畫
      // 以下是線
      { id: "廠內69KV併接點__VCB-BESS盤", type: "smoothstep", source: "廠內69KV併接點", target: "VCB-BESS盤", animated: useAnnVCB, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annVCB.value }, draggable: false },
      { id: "VCB-BESS盤__BESS-TR", type: "smoothstep", source: "VCB-BESS盤", target: "BESS-TR", animated: useAnnVCB, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annVCB.value }, draggable: false },
      { id: "BESS-TR__MP-BESS盤A", type: "smoothstep", source: "BESS-TR", target: "MP-BESS盤_A", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "MP-BESS盤A__PCS1", type: "smoothstep", source: "MP-BESS盤_A", target: "PCS_1", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "PCS1__BMS1", type: "smoothstep", source: "PCS_1", target: "BMS_1", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BMS_1__Rack1", type: "smoothstep", source: "BMS_1", target: "BMS_1Rack1", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BMS_1__Rack2", type: "smoothstep", source: "BMS_1", target: "BMS_1Rack2", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BMS_1__Rack3", type: "smoothstep", source: "BMS_1", target: "BMS_1Rack3", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BMS_1__Rack4", type: "smoothstep", source: "BMS_1", target: "BMS_1Rack4", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BMS_1__Rack5", type: "smoothstep", source: "BMS_1", target: "BMS_1Rack5", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BMS_1__Rack6", type: "smoothstep", source: "BMS_1", target: "BMS_1Rack6", animated: useAnn1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM1.value }, draggable: false },
      { id: "BESS-TR__MP-BESS盤B", type: "smoothstep", source: "BESS-TR", target: "MP-BESS盤_B", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "MP-BESS盤B__PCS2", type: "smoothstep", source: "MP-BESS盤_B", target: "PCS_2", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "PCS2__BMS2", type: "smoothstep", source: "PCS_2", target: "BMS_2", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "BMS_2__Rack1", type: "smoothstep", source: "BMS_2", target: "BMS_2Rack1", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "BMS_2__Rack2", type: "smoothstep", source: "BMS_2", target: "BMS_2Rack2", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "BMS_2__Rack3", type: "smoothstep", source: "BMS_2", target: "BMS_2Rack3", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "BMS_2__Rack4", type: "smoothstep", source: "BMS_2", target: "BMS_2Rack4", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "BMS_2__Rack5", type: "smoothstep", source: "BMS_2", target: "BMS_2Rack5", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      { id: "BMS_2__Rack6", type: "smoothstep", source: "BMS_2", target: "BMS_2Rack6", animated: useAnn2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annM2.value }, draggable: false },
      //太陽能
      { id: "PV__MVCB1", type: "smoothstep", source: "PV併接點", target: "MVCB1", animated: useAnnSun1, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annSun1.value }, draggable: false },
      { id: "F1__MVCB2", type: "smoothstep", source: "F1併接點", target: "MVCB2", animated: useAnnSun2, style: { stroke: 'DarkCyan', strokeWidth: 2, animationDirection: annSun2.value }, draggable: false },
      //以下是表格
      {
        id: "高壓併接點_INFO", type: "teleportable", position: { x: 600, y: -280 }, label: "info", class: "border-primary", draggable: false,
        data: { 'P': METER_MAIN?.total_active_power, "Q": METER_MAIN?.total_reactive_power, "S": METER_MAIN?.total_apparent_power, "V": METER_MAIN?.voltage_avg, "I": METER_MAIN?.current_avg, "frequency": METER_MAIN?.frequency, "voltage_ab": METER_MAIN?.voltage_ab, "voltage_bc": METER_MAIN?.voltage_bc, "voltage_ca": METER_MAIN?.voltage_ca, "total_power_factor": METER_MAIN?.total_power_factor }
      },
      {
        id: "VCB-BESS_INFO", type: "teleportable", position: { x: 600, y: -100 }, label: "info", class: "border-primary", draggable: false,
        data: { 'P': METER_VCB?.total_active_power, "Q": METER_VCB?.total_reactive_power, "S": METER_VCB?.total_apparent_power, "V": METER_VCB?.voltage_avg, "I": METER_VCB?.current_avg, "frequency": METER_VCB?.frequency, "voltage_ab": METER_VCB?.voltage_ab, "voltage_bc": METER_VCB?.voltage_bc, "voltage_ca": METER_VCB?.voltage_ca, "total_power_factor": METER_VCB?.total_power_factor }
      },
      {
        id: "TR_INFO", type: "TRportable", label: "info", position: { x: 580, y: 100 }, class: "border-primary", draggable: false,
        data: {
          "temperature": TRdata?.temperature,}
      },
      {
        id: "MP-BESS_1_INFO", type: "teleportable", position: { x: 100, y: 300 }, label: "info", class: "border-primary", draggable: false,
        data: { 'P': METER_MP1?.total_active_power, "Q": METER_MP1?.total_reactive_power, "S": METER_MP1?.total_apparent_power, "V": METER_MP1?.voltage_avg, "I": METER_MP1?.current_avg, "frequency": METER_MP1?.frequency, "voltage_ab": METER_MP1?.voltage_ab, "voltage_bc": METER_MP1?.voltage_bc, "voltage_ca": METER_MP1?.voltage_ca, "total_power_factor": METER_MP1?.total_power_factor }
      },
      {
        id: "MP-BESS_2_INFO", type: "teleportable", position: { x: 975, y: 300 }, label: "info", class: "border-primary", draggable: false,
        data: { 'P': METER_MP2?.total_active_power, "Q": METER_MP2?.total_reactive_power, "S": METER_MP2?.total_apparent_power, "V": METER_MP2?.voltage_avg, "I": METER_MP2?.current_avg, "frequency": METER_MP2?.frequency, "voltage_ab": METER_MP2?.voltage_ab, "voltage_bc": METER_MP2?.voltage_bc, "voltage_ca": METER_MP2?.voltage_ca, "total_power_factor": METER_MP2?.total_power_factor }
      },
      {
        id: "PCS_1_INFO", type: "PCSportable", label: "info", position: { x: 100, y: 550 }, class: "border-primary", draggable: false,
        data: { "running_status": PCS1data?.running_status, "active_power": PCS1data?.active_power, "reactive_power": PCS1data?.reactive_power, "volt_rs": PCS1data?.volt_rs, "volt_st": PCS1data?.volt_st, "volt_tr": PCS1data?.volt_tr, "battery_voltage": PCS1data?.battery_voltage, "volt_avg": PCS1data?.volt_avg, "dc_current_avg": PCS1data?.dc_current_avg }
      },
      {
        id: "PCS_2_INFO", type: "PCSportable", label: "info", position: { x: 975, y: 550 }, class: "border-primary", draggable: false,
        data: { "running_status": PCS2data?.running_status, "active_power": PCS2data?.active_power, "reactive_power": PCS2data?.reactive_power, "volt_rs": PCS2data?.volt_rs, "volt_st": PCS2data?.volt_st, "volt_tr": PCS2data?.volt_tr, "battery_voltage": PCS2data?.battery_voltage, "volt_avg": PCS2data?.volt_avg, "dc_current_avg": PCS2data?.dc_current_avg }
      },
      {
        id: "BMS_1_INFO", type: "BMSportable", label: "info", position: { x: 100, y: 750 }, class: "border-primary", draggable: false,
        data: { "status": BMS1data?.status, "voltage": BMS1data?.voltage, "current": BMS1data?.current, "soc": BMS1data?.soc, "soh": BMS1data?.soh, "max_cell_voltage": BMS1data?.max_cell_voltage, "min_cell_voltage": BMS1data?.min_cell_voltage, "max_cell_temperature": BMS1data?.max_cell_temperature, "min_cell_temperature": BMS1data?.min_cell_temperature }
      },
      {
        id: "BMS_2_INFO", type: "BMSportable", label: "info", position: { x: 975, y: 750 }, class: "border-primary", draggable: false,
        data: { "status": BMS2data?.status, "voltage": BMS2data?.voltage, "current": BMS2data?.current, "soc": BMS2data?.soc, "soh": BMS2data?.soh, "max_cell_voltage": BMS2data?.max_cell_voltage, "min_cell_voltage": BMS2data?.min_cell_voltage, "max_cell_temperature": BMS2data?.max_cell_temperature, "min_cell_temperature": BMS2data?.min_cell_temperature }
      },
      {
        id: "BMS_1_RACK1_INFO", type: "RACKportable", label: "info", position: { x: 80, y: 930 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS1data?.rack[0]?.voltage, "rack_current": BMS1data?.rack[0]?.current, "rack_soc": BMS1data?.rack[0]?.soc,}
      },
      {
        id: "BMS_1_RACK2_INFO", type: "RACKportable", label: "info", position: { x: 80, y: 1060 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS1data?.rack[1]?.voltage, "rack_current": BMS1data?.rack[1]?.current, "rack_soc": BMS1data?.rack[1]?.soc,}
      },
      {
        id: "BMS_1_RACK3_INFO", type: "RACKportable", label: "info", position: { x: 80, y: 1190 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS1data?.rack[2]?.voltage, "rack_current": BMS1data?.rack[2]?.current, "rack_soc": BMS1data?.rack[2]?.soc,}
      },
      {
        id: "BMS_1_RACK4_INFO", type: "RACKportable", label: "info", position: { x: 80, y: 1320 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS1data?.rack[3]?.voltage, "rack_current": BMS1data?.rack[3]?.current, "rack_soc": BMS1data?.rack[3]?.soc,}
      },
      {
        id: "BMS_1_RACK5_INFO", type: "RACKportable", label: "info", position: { x: 80, y: 1450 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS1data?.rack[4]?.voltage, "rack_current": BMS1data?.rack[4]?.current, "rack_soc": BMS1data?.rack[4]?.soc,}
      },
      {
        id: "BMS_1_RACK6_INFO", type: "RACKportable", label: "info", position: { x: 80, y: 1580 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS1data?.rack[5]?.voltage, "rack_current": BMS1data?.rack[5]?.current, "rack_soc": BMS1data?.rack[5]?.soc,}
      },
      {
        id: "BMS_2_RACK1_INFO", type: "RACKportable", label: "info", position: { x: 955, y: 930 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS2data?.rack[0]?.voltage, "rack_current": BMS2data?.rack[0]?.current, "rack_soc": BMS2data?.rack[0]?.soc,}
      },
      {
        id: "BMS_2_RACK2_INFO", type: "RACKportable", label: "info", position: { x: 955, y: 1060 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS2data?.rack[1]?.voltage, "rack_current": BMS2data?.rack[1]?.current, "rack_soc": BMS2data?.rack[1]?.soc,}
      },
      {
        id: "BMS_3_RACK3_INFO", type: "RACKportable", label: "info", position: { x: 955, y: 1190 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS2data?.rack[2]?.voltage, "rack_current": BMS2data?.rack[2]?.current, "rack_soc": BMS2data?.rack[2]?.soc,}
      },
      {
        id: "BMS_4_RACK4_INFO", type: "RACKportable", label: "info", position: { x: 955, y: 1320 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS2data?.rack[3]?.voltage, "rack_current": BMS2data?.rack[3]?.current, "rack_soc": BMS2data?.rack[3]?.soc,}
      },
      {
        id: "BMS_5_RACK5_INFO", type: "RACKportable", label: "info", position: { x: 955, y: 1450 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS2data?.rack[4]?.voltage, "rack_current": BMS2data?.rack[4]?.current, "rack_soc": BMS2data?.rack[4]?.soc,}
      },
      {
        id: "BMS_6_RACK6_INFO", type: "RACKportable", label: "info", position: { x: 955, y: 1580 }, class: "border-primary", draggable: false,
        data: {
          "rack_voltage": BMS2data?.rack[5]?.voltage, "rack_current": BMS2data?.rack[5]?.current, "rack_soc": BMS2data?.rack[5]?.soc,}
      },
      {
        id: "MVCB1_INFO", type: "teleportable", position: { x: -750, y: -10 }, label: "info", class: "border-primary", draggable: false,
        data: { 'P': METER_SUN1?.total_active_power, "Q": METER_SUN1?.total_reactive_power, "S": METER_SUN1?.total_apparent_power, "V": METER_SUN1?.voltage_avg, "I": METER_SUN1?.current_avg, "frequency": METER_SUN1?.frequency, "voltage_ab": METER_SUN1?.voltage_ab, "voltage_bc": METER_SUN1?.voltage_bc, "voltage_ca": METER_SUN1?.voltage_ca, "total_power_factor": METER_SUN1?.total_power_factor }
      },
      {
        id: "MVCB2_INFO", type: "teleportable", position: { x: -1850, y: -10 }, label: "info", class: "border-primary", draggable: false,
        data: { 'P': METER_SUN2?.total_active_power, "Q": METER_SUN2?.total_reactive_power, "S": METER_SUN2?.total_apparent_power, "V": METER_SUN2?.voltage_avg, "I": METER_SUN2?.current_avg, "frequency": METER_SUN2?.frequency, "voltage_ab": METER_SUN2?.voltage_ab, "voltage_bc": METER_SUN2?.voltage_bc, "voltage_ca": METER_SUN2?.voltage_ca, "total_power_factor": METER_SUN2?.total_power_factor }
      },
    ]
  });

</script>

<style>
  .container-fluid {
    height: 100%;
  }

  .vue-flow__handle.vue-flow__handle-top{
    background-color: black !important;
  }

  /* iframe {
  display: block;
  width: 100%;
  height: calc(100vh - 60px);
} */
</style>