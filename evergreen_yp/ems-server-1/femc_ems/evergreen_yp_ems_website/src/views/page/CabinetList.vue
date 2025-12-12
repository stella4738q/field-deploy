<template>
   <el-tabs v-model="TabActiveName">
      <el-tab-pane v-for="item in DataList" :key="item.equipment_id" :label="item.equipment_id"
        :name="item.equipment_id" lazy>
        <div class="cabinet-wrapper">
          <CabinetInfo :BMSIndex="item.BMSIndex" :PCSIndex ="item.PCSIndex"></CabinetInfo>
        </div>
      </el-tab-pane>
    </el-tabs>
</template>

<script >
import CabinetInfo from '@/components/CabinetInfo.vue';
import { mapState } from "vuex";

export default {
  props: {
    tabname: {
      type: String,
      default: '',
    },
  },
  components: {
    CabinetInfo,
  },
  data() {
    return {
      TabActiveName: '',
      DataList: [],
    };
  },
  computed: {
    ...mapState(["SocketDataALL"])
  },
  mounted() {
    this.TabActiveName = this.$route.query.tabname ?? this.TabActiveName;
  },
  unmounted() {
  },
  created() {
    this.iniTabData();
  },
  watch: {
  },
  methods: {
    iniTabData() {
      const vm = this;
      vm.DataList = vm.SocketDataALL.bms.map((x, ind) => {
        return {
          PCSIndex:0,
          BMSIndex:ind,
          equipment_id: x.equipment_id
        }
      });
      if (!vm.TabActiveName) {
        vm.TabActiveName = vm.DataList[0]?.equipment_id;
      }
    }
  },
};
</script>
<style scoped>
.full-tab-pane {
  width: 100%;
  height: 100%;
}
.cabinet-wrapper {
  width: 100%;
  height: 100%;
}
</style>