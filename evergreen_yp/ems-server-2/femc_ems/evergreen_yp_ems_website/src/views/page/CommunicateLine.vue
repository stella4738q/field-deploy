<template>

  <VueFlow v-model="elements" fit-view-on-init class="basicflow" :zoomOnScroll="true" :min-zoom="0.2" :max-zoom="4"
    ref="myVueFlow" style="height:100vh; width:100%">
    <template #edge-customLine="props">
      <CustomLine v-bind="props" :data="props" />
    </template>
    <template #node-color="props">
      <ColorNode v-bind="props" :data="props" />
    </template>
    <template #node-communicate="props">
      <CommunicateNode v-bind="props" :data="props" />
    </template>

    <Controls :showInteractive="false" />

  </VueFlow>
</template>

<script setup>
  //debugger;
  import { ref, computed, watch } from 'vue';
  import { useStore, mapState } from 'vuex';
  import { Controls, VueFlow, useVueFlow } from '@braks/vue-flow'

  // import CommunData from '@/JSON/CommunData.json'
  // import CustomNode from '@/components/CustomNode.vue';
  import ColorNode from '@/components/CustomColorNode.vue';
  import CommunicateNode from '@/components/CommunicateNode.vue';
  import CustomLine from '@/components/CustomLine.vue';
  import { h } from 'vue'
  import { reactive } from 'vue'



  const { onPaneReady, onNodeDragStop, onConnect, addEdges, setTransform, toObject, nodes, addNodes, setNodes, setEdges, dimensions, fitView, setInteractive } = useVueFlow();
  const store = useStore();

  const storeState = mapState(["SocketDataALL"]);
  const resultStoreState = {};
  Object.keys(storeState).map((item) => {
    const resFuc = storeState[item];
    resultStoreState[item] = computed(resFuc.bind({ $store: store }));
  });
  const { SocketDataALL } = { ...resultStoreState };


  const elements = computed(() => {
    const statusMap = {};

    let socketObject = SocketDataALL.value ? SocketDataALL.value : {};
    let alarmData = SocketDataALL.value?.alarm ?? [];
    alarmData.forEach(alarmItem => {
      if (!statusMap[alarmItem.equipment_id]) statusMap[alarmItem.equipment_id] = {};

      statusMap[alarmItem.equipment_id]["abnormal"] = true;
      if (alarmItem.message.includes('通訊異常')) {
        statusMap[alarmItem.equipment_id]["comm"] = true;
      }
    });
    // console.log(statusMap);

    const switchAndHubComm1 = statusMap['DCP']?.comm || statusMap['DCP_DEHU']?.comm  || statusMap['METER_CABINET']?.comm || statusMap['BMU_1']?.comm || statusMap['BMU_2']?.comm || statusMap['PCS_1']?.comm || statusMap['VDF_1']?.comm || statusMap['VDF_2']?.comm  || statusMap['TR']?.comm ;
    const switchAndHubComm2 = statusMap['VCB']?.comm || statusMap['IO_TCP']?.comm || statusMap['IO_INTERNET']?.comm || statusMap['METER_VCB']?.comm || statusMap['METER_FACTORY']?.comm || statusMap['METER_MAIN']?.comm || statusMap['METER_SUN']?.comm || statusMap['EXPOSURE']?.comm || statusMap['UPS']?.comm;
    const switchAbnormal = switchAndHubComm1 || switchAndHubComm2;
    const mgetUpsideComm = statusMap['VDF_1']?.comm || statusMap['VDF_2']?.comm ||  statusMap['DCP_DEHU']?.comm;

    const color_cat6 = "#0057A0";
    const color_fiber = "#008000";
    const color_rs485 = "#000000";
    const color_vga = "#A0A0A0";
    const color_dio = "#DDA0DD";
    // const color_signal = "#A04040";


    return [
      //以下Element是為了增加node的handle，用來連接線
      { id: "SwitchElement_1", type: "color", label: "01", position: { x: 640, y: 615 }, class: "light", style: { width: "40px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "left" },
      { id: "SwitchElement_2", type: "color", label: "02", position: { x: 600, y: 605 }, class: "light", style: { width: "40px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "SwitchElement_3", type: "color", label: "03", position: { x: 600, y: 530 }, class: "light", style: { width: "80px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_4", type: "color", label: "04", position: { x: 600, y: 475 }, class: "light", style: { width: "80px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_5", type: "color", label: "05", position: { x: 600, y: 395 }, class: "light", style: { width: "40px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_6", type: "color", label: "06", position: { x: 600, y: 315 }, class: "light", style: { width: "80px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_7", type: "color", label: "07", position: { x: 600, y: 235 }, class: "light", style: { width: "80px", height: "40px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_8", type: "color", label: "08", position: { x: 640, y: 165 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "SwitchElement_9", type: "color", label: "09", position: { x: 640, y: 150 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "SwitchElement_10", type: "color", label: "10", position: { x: 600, y: 165 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_11", type: "color", label: "11", position: { x: 600, y: 85 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_12", type: "color", label: "12", position: { x: 640, y: 115 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "SwitchElement_13", type: "color", label: "13", position: { x: 640, y: 180 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "SwitchElement_14", type: "color", label: "14", position: { x: 640, y: 195 }, class: "light", style: { width: "40px", height: "20px", color: "", border: "none", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "MgateElement_01", type: "color", label: "01", position: { x: 880, y: 480 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "top" },
      { id: "光電HubElement_01", type: "color", label: "", position: { x: 1800, y: -30 }, class: "light", style: { width: "20px", height: "50px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
      { id: "光電HubElement_02", type: "color", label: "", position: { x: 1775, y: -30 }, class: "light", style: { width: "20px", height: "50px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
      { id: "光電HubElement_03", type: "color", label: "", position: { x: 1855, y: -30 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
      { id: "光電HubElement_04", type: "color", label: "", position: { x: 1875, y: -30 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
      { id: "光電HubElement_05", type: "color", label: "", position: { x: 1875, y: 0 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "right" },
      { id: "DataCollectionElement_01", type: "color", label: "", position: { x: 290, y: 350 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "DataCollectionElement_02", type: "color", label: "", position: { x: 250, y: 359.5 }, class: "light", style: { width: "1px", height: "1px", color: "", border: "none", backgroundColor: "transparent" }, draggable: false, sourcePosition: "left", targetPosition: "left" },

      { id: "MP-BESS盤Element_02", type: "color", label: "", position: { x: 2480, y: -450 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_02-1", type: "color", label: "", position: { x: 2508, y: -450 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_03", type: "color", label: "", position: { x: 1600, y: -450 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_03-1", type: "color", label: "", position: { x: 1580, y: -450 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_04", type: "color", label: "", position: { x: 1480, y: -450 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },

      // {id: "MP-BESS盤Element_05", type: "color", label: "", position: {x: 2600, y: -157}, class: "light", style: {width: "20px",  height: "20px",color: "",border: "none", backgroundColor: "transparent",borderRadius: "5px"}, draggable: false, sourcePosition: "bottom", targetPosition: "top"},
      { id: "MP-BESS盤Element_06", type: "color", label: "", position: { x: 2520, y: -470 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_06-1", type: "color", label: "", position: { x: 2548, y: -470 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_07", type: "color", label: "", position: { x: 1550, y: -460 }, class: "light", style: { width: "1px", height: "1px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "MP-BESS盤Element_07-1", type: "color", label: "", position: { x: 1528, y: -460 }, class: "light", style: { width: "1px", height: "1px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },

      { id: "MP-BESS盤Element_08", type: "color", label: "", position: { x: 1480, y: -470 }, class: "light", style: { width: "20px", height: "20px", color: "", border: "none", backgroundColor: "transparent", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },

      //ems機櫃
      { id: "EMS機櫃_外框", type: "color", label: "", position: { x: 210, y: -60 }, class: "light", style: { width: "790px", height: "975px", color: "black", border: "1px solid #002379", borderRadius: "5px", backgroundColor: "rgba(33, 255, 255, 0.1)" }, draggable: false },
      { id: "EMS機櫃", type: "color", label: "EMS機櫃", position: { x: 220, y: -60 }, class: "light", style: { width: "100px", height: "50px", color: "black", border: "none", backgroundColor: "transparent", borderRadius: "5px", fontWeight: "bold" }, draggable: false },
      { id: "1U 機架型LCD KVM", type: "color", label: "1U 機架型LCD KVM", position: { x: 290, y: -10 }, class: "light", style: { width: "220px", height: "50px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      { id: "EMS主機1", type: "color", label: "EMS主機1", position: { x: 290, y: 60 }, class: 'light', style: { width: "180px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "EMS主機2", type: "color", label: "EMS主機2", position: { x: 290, y: 140 }, class: "light", style: { width: "180px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "DBServer1", type: "color", label: "DB Server1", position: { x: 290, y: 220 }, class: "light", style: { width: "180px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "DataCollection", type: "color", label: "Data Collection", position: { x: 290, y: 300 }, class: "light", style: { width: "180px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "3DServer/Client", type: "color", label: "3D Server/Client", position: { x: 290, y: 380 }, class: "light", style: { width: "180px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "ups", type: "color", label: "UPS", position: { x: 290, y: 460 }, class: statusMap['UPS']?.abnormal ? 'bg-danger' : "light", style: { width: "180px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "I/O Logik_left", type: "color", label: "I/O Logik", position: { x: 290, y: 585 }, class: `${statusMap['IO_INTERNET']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "60px", height: "80px", color: "White", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      { id: "I/O Logik_right", type: "color", label: "I/O Logik", position: { x: 420, y: 585 }, class: `${statusMap['IO_TCP']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "60px", height: "80px", color: "White", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "right" },
      { id: "Fortinet", type: "communicate", label: "Fortinet", position: { x: 750, y: 830 }, class: `${statusMap['FORTI']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "Switch", type: "communicate", label: "Switch", position: { x: 600, y: 60 }, class: `${switchAbnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "80px", height: "595px", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
      { id: "Mgate", type: "communicate", label: "Mgate", position: { x: 800, y: 460 }, class: `${statusMap['EXPOSURE']?.comm ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      //ems機櫃_ip
      { id: "EMS主機1_ip", type: "color", label: "192.168.100.101", position: { x: 290, y: 85 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "EMS主機2_ip", type: "color", label: "192.168.100.102", position: { x: 290, y: 165 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "DBServer1_ip", type: "color", label: "192.168.100.105", position: { x: 290, y: 245 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "DataCollection_ip", type: "color", label: "192.168.100.103", position: { x: 290, y: 325 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "3DServer/Client_ip", type: "color", label: "192.168.100.104", position: { x: 290, y: 405 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "ups_ip", type: "color", label: "192.168.100.170", position: { x: 290, y: 485 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "Mgate_ip", type: "color", label: "192.168.100.161", position: { x: 800, y: 490 }, class: "light", style: { width: "180px", height: "50px", color: "white", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "Fortinet_ip", type: "color", label: "192.168.100.254", position: { x: 750, y: 855 }, class: "light", style: { width: "180px", height: "50px", color: "white", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "I/O Logik_left_ip", type: "color", label: "192.168.100.162", position: { x: 225, y: 695 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "I/O Logik_right_ip", type: "color", label: "192.168.100.163", position: { x: 355, y: 655 }, class: "light", style: { width: "180px", height: "50px", color: "grey", border: "none", backgroundColor: "transparent" }, draggable: false },
      // pcs
      { id: "Fimer PCS_外框", type: "color", label: "", position: { x: 1100, y: -135 }, class: "light", style: { width: "320px", height: "190px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "Fimer PCS", type: "color", label: "Fimer PCS 1696kVA", position: { x: 1100, y: -135 }, class: "light", style: { width: "90px", height: "190px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "PCS_RJ 45埠", type: "communicate", label: "RJ 45埠", position: { x: 1215, y: -120 }, class: `${statusMap['PCS_1']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      //pcs_ip
      { id: "PCS_RJ 45埠_ip", type: "color", label: "192.168.100.111", position: { x: 1215, y: -90 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      // dcp
      { id: "DCP_外框", type: "color", label: "", position: { x: 1030, y: -600 }, class: "light", style: { width: "490px", height: "340px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "DCP", type: "color", label: "DCP", position: { x: 1030, y: -600 }, class: "light", style: { width: "70px", height: "340px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "DCP_RJ 45埠", type: "communicate", label: "RJ 45埠", position: { x: 1120, y: -350 }, class: `${statusMap['DCP']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
      { id: "DCP_Mgate", type: "communicate", label: "Mgate", position: { x: 1320, y: -480 }, class: `${ mgetUpsideComm ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      { id: "除濕機", type: "communicate", label: "除濕機", position: { x: 1360, y: -580 }, class: `${statusMap['DCP_DEHU']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "60px", borderRadius: "5px" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      // dcp_ip
      { id: "DCP_RJ 45埠_ip", type: "color", label: "192.168.100.112", position: { x: 1120, y: -320 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "DCP_Mgate_ip", type: "color", label: "192.168.100.160", position: { x: 1320, y: -450 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //電池櫃_A
      { id: "電池櫃_A_外框", type: "color", label: "", position: { x: 1660, y: -135 }, class: "light", style: { width: "520px", height: "190px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "電池櫃_A", type: "color", label: "電池櫃_A", position: { x: 1660, y: -135 }, class: "light", style: { width: "80px", height: "190px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "電池櫃RJ 45埠_1", type: "communicate", label: "RJ 45埠", position: { x: 1970, y: -120 }, class: `${statusMap['BMU_1']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "bottom", targetPosition: "left" },
      { id: "光電Hub", type: "color", label: "光電Hub", position: { x: 1765, y: -30 }, class: `${ switchAndHubComm1 ? 'bg-danger' : 'bg-success'}`, style: { width: "130px", height: "60px", color: "white", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      //電池櫃_A_ip
      { id: "電池櫃RJ 45埠A_ip", type: "color", label: "192.168.100.121", position: { x: 1970, y: -90 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //電池櫃_B
      { id: "電池櫃_B_外框", type: "color", label: "", position: { x: 1660, y: -415 }, class: "light", style: { width: "520px", height: "190px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "電池櫃_B", type: "color", label: "電池櫃_B", position: { x: 1660, y: -415 }, class: "light", style: { width: "80px", height: "190px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "電池櫃RJ 45埠_2", type: "communicate", label: "RJ 45埠", position: { x: 1970, y: -350 }, class: `${statusMap['BMU_2']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "left", targetPosition: "right" },
      //電池櫃_B_ip
      { id: "電池櫃RJ 45埠B_ip", type: "color", label: "192.168.100.122", position: { x: 1970, y: -320 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //MP-BESS盤
      { id: "MP-BESS盤_外框", type: "color", label: "", position: { x: 2250, y: -135 }, class: "light", style: { width: "300px", height: "260px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "MP-BESS盤", type: "color", label: "MP-BESS盤", position: { x: 2250, y: -135 }, class: "light", style: { width: "80px", height: "260px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "MP-BESS_Meter", type: "communicate", label: "Meter", position: { x: 2400, y: -120 }, class: `${statusMap["METER_CABINET"]?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "70px", height: "70px", borderRadius: "50%", textAlign: "center" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      // {id: "變頻器通訊RS485*2", type: "color", label: "(變頻器通訊RS485*2)", position: {x: 2340, y: 40}, class: "light", style: {width: "200px",  height: "50px",color: "red", border: "none", backgroundColor: "transparent",borderRadius: "5px"}, draggable: false, sourcePosition: "left", targetPosition: "right"},
      { id: "變頻器1", type: "communicate", label: "變頻器1", position: { x: 2390, y: 10 }, class: `${statusMap["VDF_1"]?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "50px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "right" },
      { id: "變頻器2", type: "communicate", label: "變頻器2", position: { x: 2390, y: 60 }, class: `${statusMap["VDF_2"]?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "50px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "right" },



      //MP-BESS盤_ip
      { id: "MP-BESS_Meter_ip", type: "color", label: "192.168.100.155", position: { x: 2350, y: -60 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //晉瑜電氣室高壓盤
      { id: "晉瑜電氣室高壓盤_外框", type: "color", label: "", position: { x: 1050, y: 215 }, class: "light", style: { width: "280px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "晉瑜電氣室高壓盤", type: "color", label: "晉瑜電氣室高壓盤HP Panel", position: { x: 1050, y: 215 }, class: "light", style: { width: "90px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "高壓盤_Meter", type: "communicate", label: "Meter", position: { x: 1200, y: 270 }, class: `${statusMap['METER_MAIN']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "70px", height: "70px", borderRadius: "50%", textAlign: "center" }, draggable: false, sourcePosition: "right", targetPosition: "top" },
      //晉瑜電氣室高壓盤_ip
      { id: "高壓盤_Meter_ip", type: "color", label: "192.168.100.150", position: { x: 1145, y: 330 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //晉瑜電氣室低壓盤
      { id: "晉瑜電氣室低壓盤_外框", type: "color", label: "", position: { x: 1350, y: 215 }, class: "light", style: { width: "280px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "晉瑜電氣室低壓盤", type: "color", label: "晉瑜電氣室低壓盤MP1 Panel", position: { x: 1350, y: 215 }, class: "light", style: { width: "90px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "低壓盤_Meter", type: "communicate", label: "Meter", position: { x: 1500, y: 270 }, class: `${statusMap['METER_FACTORY']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "70px", height: "70px", borderRadius: "50%", textAlign: "center" }, draggable: false, sourcePosition: "right", targetPosition: "top" },
      //晉瑜電氣室低壓盤_ip
      { id: "低壓盤_Meter_ip", type: "color", label: "192.168.100.151", position: { x: 1445, y: 330 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //VCB-BESS
      { id: "VCB-BESS_外框", type: "color", label: "", position: { x: 1660, y: 215 }, class: "light", style: { width: "300px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "VCB-BESS", type: "color", label: "VCB-BESS", position: { x: 1660, y: 215 }, class: "light", style: { width: "90px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "VCB_Meter", type: "communicate", label: "Meter", position: { x: 1815, y: 225 }, class: `${statusMap['METER_VCB']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "70px", height: "70px", borderRadius: "50%", textAlign: "center" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      { id: "VCB_Relay", type: "communicate", label: "Relay", position: { x: 1765, y: 370 }, class: `${statusMap['VCB']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      //VCB-BESS_ip
      { id: "VCB_Meter_ip", type: "color", label: "192.168.100.153", position: { x: 1765, y: 285 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "VCB_Relay_ip", type: "color", label: "192.168.100.154", position: { x: 1765, y: 400 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //TR-BESS
      { id: "TR-BESS_外框", type: "color", label: "", position: { x: 2030, y: 215 }, class: "light", style: { width: "300px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "TR-BESS", type: "color", label: "TR-BESS", position: { x: 2030, y: 215 }, class: "light", style: { width: "70px", height: "240px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "溫度告警", type: "communicate", label: "溫度告警", position: { x: 2125, y: 260 }, class: `${statusMap['TR']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "70px", borderRadius: "5px" }, draggable: false, sourcePosition: "top", targetPosition: "bottom" },
      //TR-BESS_ip
      { id: "溫度告警_ip", type: "color", label: "192.168.100.130", position: { x: 2125, y: 290 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //太陽能
      { id: "太陽能_外框", type: "color", label: "", position: { x: 1100, y: 570 }, class: "light", style: { width: "1070px", height: "150px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "太陽能", type: "color", label: "太陽能", position: { x: 1100, y: 570 }, class: "light", style: { width: "40px", height: "150px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "太陽能_Meter", type: "communicate", label: "Meter", position: { x: 1230, y: 600 }, class: `${statusMap['METER_SUN']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "70px", height: "70px", borderRadius: "50%", textAlign: "center" }, draggable: false, sourcePosition: "bottom", targetPosition: "top" },
 
      { id: "日照計", type: "color", label: "日照計", position: { x: 1370, y: 635 }, class: `${statusMap['EXPOSURE']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "50px", color: "White", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "top" },
 
      { id: "DCU-1", type: "communicate", label: "DCU-1", position: { x: 1520, y: 610 }, class: `${statusMap['DCU_1']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "180px", height: "100px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "bottom" },
      { id: "INV-1", type: "communicate", label: "INV-1", position: { x: 1750, y: 635 }, class: `${statusMap['INVERTER_1']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "50px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "INV-2", type: "communicate", label: "INV-2", position: { x: 1900, y: 635 }, class: `${statusMap['INVERTER_2']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "50px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      { id: "INV-3", type: "communicate", label: "INV-3", position: { x: 2050, y: 635 }, class: `${statusMap['INVERTER_3']?.abnormal ? 'bg-danger' : 'bg-success'}`, style: { width: "100px", height: "50px", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      //太陽能_ip
      { id: "太陽能_Meter_ip", type: "color", label: "192.168.100.152", position: { x: 1175, y: 660 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "DCU-1_ip", type: "color", label: "192.168.100.180", position: { x: 1520, y: 650 }, class: "light", style: { width: "180px", height: "50px", color: "white", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //中華電信
      { id: "辦公大樓1F辦公室", type: "color", label: "辦公大樓1F辦公室", position: { x: 1150, y: 750 }, class: "light", style: { width: "300px", height: "50px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false },
      { id: "辦公大樓1F辦公室_外框", type: "color", label: "", position: { x: 1150, y: 800 }, class: "light", style: { width: "300px", height: "150px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false },
      { id: "中華電信", type: "color", label: "中華電信", position: { x: 1175, y: 820 }, class: "light", style: { width: "250px", height: "90px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "left" },
      //中華電信_ip
      { id: "中華電信_ip", type: "color", label: "211.75.160.130", position: { x: 1210, y: 845 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      { id: "中華電信即時備轉_ip", type: "color", label: "211.75.160.128", position: { x: 1180, y: 870 }, class: "light", style: { width: "240px", height: "50px", color: "black", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },
      //2F圖控室
      { id: "2F圖控室", type: "color", data: {}, label: "2F圖控室", position: { x: 705, y: 940 }, class: "light", style: { width: "220px", height: "50px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 1)", fontWeight: "bold" }, draggable: false, sourcePosition: "left", targetPosition: "bottom", },
      { id: "即時備轉廠內PLC接點", type: "color", data: {}, label: "即時備轉廠內PLC接點", position: { x: 705, y: 990 }, class: "light", style: { width: "220px", height: "80px", color: "black", border: "1px solid #002379", borderRadius: "0px", backgroundColor: "rgba(255, 255, 255, 0.1)" }, draggable: false, sourcePosition: "bottom", targetPosition: "left", },
      //晉瑜內網switch
      { id: "晉瑜內網switch", type: "color", label: "晉瑜內網switch", position: { x: 1175, y: 1020 }, class: "light", style: { width: "250px", height: "70px", color: "black", border: "1px solid black", backgroundColor: "rgb(255, 255, 255)", borderRadius: "5px" }, draggable: false, sourcePosition: "right", targetPosition: "bottom" },
      //晉瑜內網switch_ip
      { id: "晉瑜內網switch_ip", type: "color", label: "192.168.91.35", position: { x: 1210, y: 1050 }, class: "light", style: { width: "180px", height: "50px", color: "grey", borderRadius: "5px", border: "none", backgroundColor: "transparent" }, draggable: false },

      //以下是線路顏色標示
      { id: "Cat6", type: "color", label: "Cat6", position: { x: 60, y: -60 }, class: "light", style: { width: "115px", height: "45px", color: "white", borderRadius: "3px", backgroundColor: color_cat6 }, draggable: false },
      { id: "多模光纖", type: "color", label: "多模光纖", position: { x: 60, y: 0 }, class: "light", style: { width: "115px", height: "45px", color: "white", borderRadius: "3px", backgroundColor: color_fiber }, draggable: false },
      { id: "RS485", type: "color", label: "RS485", position: { x: 60, y: 60 }, class: "light", style: { width: "115px", height: "45px", color: "white", borderRadius: "3px", backgroundColor: color_rs485 }, draggable: false },
      { id: "VGA+PS/2", type: "color", label: "VGA+PS/2", position: { x: 60, y: 120 }, class: "light", style: { width: "115px", height: "45px", color: "white", borderRadius: "3px", backgroundColor: color_vga }, draggable: false },
      { id: "DO/DI", type: "color", label: "DO/DI", position: { x: 60, y: 180 }, class: "light", style: { width: "115px", height: "45px", color: "white", borderRadius: "3px", backgroundColor: color_dio }, draggable: false },
      // {id: "訊號線", type: "color", label: "訊號線", position: {x: 60, y: 180}, class: "light", style: {width: "115px",height: "45px", color: "white", borderRadius: "3px", backgroundColor: color_signal}, draggable: false},
      { id: "通訊異常", type: "color", label: "通訊異常", position: { x: 60, y: 240 }, class: "light", style: { width: "115px", height: "45px", color: "white", borderRadius: "3px", backgroundColor: "#CC0000" }, draggable: false },

      //以下是線 //type: "customLine"代表有接資料
      //RS485
      { id: "1U 機架型LCD KVM__3DServer/Client", type: "smoothstep", source: "1U 機架型LCD KVM", target: "3DServer/Client", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "1U 機架型LCD KVM__DataCollection", type: "smoothstep", source: "1U 機架型LCD KVM", target: "DataCollection", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "1U 機架型LCD KVM__DBServer1", type: "smoothstep", source: "1U 機架型LCD KVM", target: "DBServer1", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "1U 機架型LCD KVM__EMS主機2", type: "smoothstep", source: "1U 機架型LCD KVM", target: "EMS主機2", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "1U 機架型LCD KVM__EMS主機2", type: "smoothstep", source: "1U 機架型LCD KVM", target: "EMS主機2", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "DCU-1__INV-1", type: "customLine", source: "DCU-1", target: "INV-1", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['INVERTER_1']?.comm || false, } },
      { id: "INV-1__2", type: "customLine", source: "INV-1", target: "INV-2", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['INVERTER_2']?.comm || false, } },
      { id: "INV-2__INV-3", type: "customLine", source: "INV-2", target: "INV-3", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['INVERTER_3']?.comm || false, } },
      { id: "MgateElement_01__日照計", type: "customLine", source: "MgateElement_01", target: "日照計", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false , data: { defaultColor: color_rs485, isAbnormal: statusMap['EXPOSURE']?.comm || false, } },
      { id: "DataCollectionElement_01__DataCollectionElement_02", type: "straight", source: "DataCollectionElement_01", target: "DataCollectionElement_02", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "DataCollectionElement_02__晉瑜內網switch", type: "smoothstep", source: "DataCollectionElement_02", target: "晉瑜內網switch", style: { strokeWidth: "3px", stroke: color_rs485, }, draggable: false },
      { id: "變頻1連接__MP-BESS盤Element_02", type: "customLine", source: "變頻器1", target: "MP-BESS盤Element_02", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['VDF_1']?.comm } },
      { id: "MP-BESS盤Element_02-1__MP-BESS盤Element_03", type: "customLine", source: "MP-BESS盤Element_02-1", target: "MP-BESS盤Element_03", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['VDF_1']?.comm } },
      { id: "MP-BESS盤Element_03-1__MP-BESS盤Element_04", type: "customLine", source: "MP-BESS盤Element_04", target: "MP-BESS盤Element_03-1", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['VDF_1']?.comm } },
      { id: "變頻器2__MP-BESS盤Element_06", type: "customLine", source: "變頻器2", target: "MP-BESS盤Element_06", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['VDF_2']?.comm } },
      { id: "MP-BESS盤Element_06-1__MP-BESS盤Element_07", type: "customLine", source: "MP-BESS盤Element_06-1", target: "MP-BESS盤Element_07", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['VDF_2']?.comm } },
      { id: "MP-BESS盤Element_07-1__MP-BESS盤Element_08", type: "customLine", source: "MP-BESS盤Element_08", target: "MP-BESS盤Element_07-1", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['VDF_2']?.comm } },
      { id: "DCP_Mgate__除濕機", type: "customLine", source: "DCP_Mgate", target: "除濕機", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_rs485, isAbnormal: statusMap['DCP_DEHU']?.comm } },
      //VGA+PS/2
      { id: "1U 機架型LCD KVM__EMS主機1", type: "smoothstep", source: "1U 機架型LCD KVM", target: "EMS主機1", style: { strokeWidth: "3px" }, draggable: false },
      //DO/DI
      { id: "即時備轉廠內PLC接點__I/O Logik_left", type: "customLine", source: "即時備轉廠內PLC接點", target: "I/O Logik_left", draggable: false, style: { strokeWidth: "3px" }, data: { defaultColor: color_dio, isAbnormal: statusMap['IO_INTERNET']?.comm || false, } },
      { id: "I/O Logik_right__即時備轉廠內PLC接點", type: "customLine", source: "I/O Logik_right", target: "即時備轉廠內PLC接點", draggable: false, style: { strokeWidth: "3px" }, data: { defaultColor: color_dio, isAbnormal: statusMap['IO_TCP']?.comm || false, } },
      { id: "Switch__Fortinet", type: "customLine", source: "Switch", target: "Fortinet", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['FORTI']?.comm || false, } },
      { id: "Fortinet__中華電信", type: "smoothstep", source: "Fortinet", target: "中華電信", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false },
      { id: "溫度告警__光電Hub", type: "customLine", source: "溫度告警", target: "光電Hub", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['TR']?.comm } },
      { id: "光電Hub__DCP_Mgate", type: "customLine", source: "光電Hub", target: "DCP_Mgate", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: mgetUpsideComm } },
      { id: "SwitchElement_1__DCU-1", type: "customLine", source: "SwitchElement_1", target: "DCU-1", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['DCU_1']?.comm || false, } },
      { id: "SwitchElement_2__I/O Logik_right", type: "customLine", source: "SwitchElement_2", target: "I/O Logik_right", draggable: false, style: { strokeWidth: "3px" }, data: { defaultColor: color_dio, isAbnormal: statusMap['IO_TCP']?.comm || false, } },
      { id: "I/O Logik_left__SwitchElement_3", type: "customLine", source: "I/O Logik_left", target: "SwitchElement_3", draggable: false, style: { strokeWidth: "3px" }, data: { defaultColor: color_dio, isAbnormal: statusMap['IO_INTERNET']?.comm || false, } },
      { id: "SwitchElement_3__太陽能_Meter", type: "customLine", source: "SwitchElement_3", target: "太陽能_Meter", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['METER_SUN']?.comm || false, } },
      { id: "ups__SwitchElement_4", type: "customLine", source: "ups", target: "SwitchElement_4", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false , data: { defaultColor: color_cat6, isAbnormal: statusMap['UPS']?.comm || false, } },
      { id: "SwitchElement_4__Mgate", type: "customLine", source: "SwitchElement_4", target: "Mgate", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false , data: { defaultColor: color_cat6, isAbnormal: statusMap['EXPOSURE']?.comm || false, } },
      { id: "3DServer/Client__SwitchElement_5", type: "smoothstep", source: "3DServer/Client", target: "SwitchElement_5", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false },
      { id: "DataCollection__SwitchElement_6", type: "smoothstep", source: "DataCollection", target: "SwitchElement_6", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false },
      { id: "SwitchElement_14__高壓盤_Meter", type: "customLine", source: "SwitchElement_14", target: "高壓盤_Meter", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['METER_MAIN']?.comm || false, } },
      { id: "DBServer1__SwitchElement_7", type: "smoothstep", source: "DBServer1", target: "SwitchElement_7", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false },
      { id: "SwitchElement_13__低壓盤_Meter", type: "customLine", source: "SwitchElement_13", target: "低壓盤_Meter", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['METER_FACTORY']?.comm || false, } },
      { id: "VCB_Meter__SwitchElement_8", type: "customLine", source: "VCB_Meter", target: "SwitchElement_8", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['METER_VCB']?.comm || false, } },
      { id: "VCB_Relay__SwitchElement_9", type: "customLine", source: "VCB_Relay", target: "SwitchElement_9", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['VCB']?.comm || false, } },
      { id: "EMS主機2__SwitchElement_10", type: "smoothstep", source: "EMS主機2", target: "SwitchElement_10", style: { strokeWidth: "3px", stroke: color_cat6, }, draggable: false },
      { id: "EMS主機1__SwitchElement_11", type: "customLine", source: "EMS主機1", target: "SwitchElement_11", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['SWITCH']?.comm || false, } },
      { id: "DCP_RJ 45埠__光電HubElement_01", type: "customLine", source: "DCP_RJ 45埠", target: "光電HubElement_01", style: { strokeWidth: "3px", }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['DCP']?.comm } },
      { id: "PCS_RJ 45埠__光電HubElement_02", type: "customLine", source: "PCS_RJ 45埠", target: "光電HubElement_02", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['PCS_1']?.comm } },
      { id: "電池櫃RJ 45埠_2__光電HubElement_03", type: "customLine", source: "電池櫃RJ 45埠_2", target: "光電HubElement_03", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['BMU_2']?.comm } },
      { id: "MP-BESS_Meter__光電HubElement_04", type: "customLine", source: "MP-BESS_Meter", target: "光電HubElement_04", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['METER_CABINET']?.comm  } },
      { id: "電池櫃RJ 45埠_1__光電HubElement_05", type: "customLine", source: "電池櫃RJ 45埠_1", target: "光電HubElement_05", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_cat6, isAbnormal: statusMap['BMU_1']?.comm || false, } },
      //多模光纖
      { id: "光電HubElement_01__SwitchElement_12", type: "customLine", source: "光電HubElement_01", target: "SwitchElement_12", style: { strokeWidth: "3px" }, draggable: false, data: { defaultColor: color_fiber, isAbnormal: switchAndHubComm1 } },




    ]
  });

</script>

<style>
  .container-fluid {
    height: 100%;
  }

  .vertical-line {
    white-space: pre;
    /* 保留換行與空白 */
    text-align: center;
    /* 文字水平置中 */
    line-height: 1.2;
    /* 行高適中 */
  }

  .vue-flow__edge-path {
    shape-rendering: geometricPrecision;
  }
</style>