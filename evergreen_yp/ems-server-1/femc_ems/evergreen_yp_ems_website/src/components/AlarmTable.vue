<template>

  <el-table  id="exTable" :data="SocketDataALL.alarm" stripe border class="rounded-3" header-cell-class-name="tableHeaderStyle">
        <el-table-column  label="時間" prop="time" width="180" align="center"></el-table-column>
        <el-table-column  label="等級" prop="level" width="100" align="center"></el-table-column>
        <!-- <el-table-column  label="案場" prop="field_id" >
          <template #default="scope">
            {{
              ApiResult.getFields.find(x=> {return x._id == scope.row.field_id})?.name
            }}
          </template>
        </el-table-column> -->
        <el-table-column  label="設備" prop="equipment_id" width="150" align="center"></el-table-column>
        <el-table-column  label="訊息" prop="message" align="left"></el-table-column>
  </el-table>
</template>

<script > 
 
import { mapState } from "vuex"; 
export default {
  props: {
     
  },
  components: {
  },
  data() {
    return {
      ApiResult: {
        getFields: [],
      }
    };
  },
  computed: { 
    ...mapState(["SocketDataALL"])
  },
  mounted() {
  },
  unmounted() {
  },
  created() { 
  },
  watch: {},
  
  methods: { 
  },
};
</script>