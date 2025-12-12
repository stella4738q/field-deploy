<template>
  <div class="p-3 card border-0 shadow-sm">
    <div class="card-body">
      <h5 class="fw-bolder mb-3">電價設定</h5>


      <el-table :data="ApiResult.getSystemElectricSetting" size="medinm" stripe border class="rounded-3"
        header-cell-class-name="tableHeaderStyle">
        <el-table-column label="版本" prop="version" align="center"></el-table-column>
        <el-table-column label="生效日" prop="effect_date" align="center"></el-table-column>
        <el-table-column label="夏月時間" align="center">
          <template #default="scope">
            {{ scope.row.summer_date_start }} ~ {{ scope.row.summer_date_end }}
          </template>
        </el-table-column>
        <el-table-column label="啟用" prop="is_set" align="center">
          <template #default="{ row }">
            {{ row.is_set === 1 ? "是" : "" }}
            <span v-if="row.is_set === 1" style="color: red;">
              ({{ row.use_name }})
            </span>
          </template>
        </el-table-column>
        <el-table-column width="120">
          <template v-slot="scope">
            <div class="text-center">
              <el-button size="small" @click="Edit(scope.row)" v-if="$store.getters.userPriviage('p_00024')">
                <font-awesome-icon icon="pen" />
              </el-button>
            </div>
          </template>

        </el-table-column>
      </el-table>
    </div>
  </div>


  <el-dialog :title="DialogType + '電價'" v-model="Dialog" width="1200px" :close-on-click-modal="false"
    :show-close="false">

    <el-form :inline="true" :model="Form" ref="FormRef" :rules="FormRule">

      <el-form-item label="版本" prop="version">
        <span class="fw-bolder text-primary">{{ Form.version }}</span>
      </el-form-item>

      <el-form-item label="生效日" prop="effect_date">
        <span class="fw-bolder text-primary">{{ Form.effect_date }}</span>
      </el-form-item>
      <br />
      <el-form-item label="夏季起始日期" prop="summer_date_start">
        <span class="fw-bolder text-primary">{{ Form.summer_date_start ? Form.summer_date_start : '尚未填寫' }}</span>
      </el-form-item>

      <el-form-item label="夏季結束日期" prop="summer_date_end">
        <span class="fw-bolder text-primary">{{ Form.summer_date_end ? Form.summer_date_end : '尚未填寫' }}</span>
      </el-form-item>
      
      <br />

      <el-form-item label="啟用" prop="is_set">
        <el-switch v-model="Form.is_set" active-text="開啟" inactive-text="關閉" :active-value="1" :inactive-value="0"
        />
      </el-form-item>


      <br />

      <el-form-item label="電壓類型" prop="volt_type">
        <el-radio-group v-model="currentSelect.volt_type">
          <el-radio-button label="高壓"></el-radio-button>
          <el-radio-button label="特高壓"></el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="時段類型" prop="time_step">

        <el-radio-group v-model="currentSelect.time_step">
          <el-radio-button label="二段式">二段式</el-radio-button>
          <el-radio-button label="三段式">三段式</el-radio-button>
          <el-radio-button label="尖峰時間可變動">尖峰時間可變動</el-radio-button>
          <el-radio-button label="批次生產">批次生產</el-radio-button>
          <el-radio-button label="表後儲能時間電價">表後儲能時間電價</el-radio-button>

        </el-radio-group>

      </el-form-item>



      <table class="table table-bordered">
        <tbody align="center">
          <tr>
            <th></th>
            <th></th>
            <th></th>
            <th>時段</th>
            <th>夏月電價</th>
            <th>非夏月電價</th>
          </tr>


          <tr v-for="(item, index) in displayForm[0].data.filter(i => i.day_start !== 7)" :key="index">
            <th v-if="showRowspan(item, index, 'day_start')" :rowspan="getRowspan(item, index, 'day_start')"
              style="width: 120px;" valign="middle">
              <span v-if="item.day_start == 1">
                週一至週五
              </span>
              <span v-else-if="item.day_start == 6">週六</span>
            </th>
            <th v-if="showRowspan(item, index, 'price_level')" :rowspan="getRowspan(item, index, 'price_level')"
              style="width: 120px;" valign="middle">
              {{ item.price_level }}
            </th>
            <th v-if="showRowspan(item, index, 'summer_type')" :rowspan="getRowspan(item, index, 'summer_type')"
              style="width: 120px;">
              {{ item.summer_type }}
            </th>

            <td class="d-flex align-items-center" valign="middle">
              <el-select v-model="item.time_start" placeholder="起始時間" filterable clearable style="width:120px" class="me-2">
                <el-option
                  v-for="timeOptionItem in TimeOption.filter(x => { return (item.time_end ? x < item.time_end : true) })"
                  :key="timeOptionItem" :label="timeOptionItem" :value="timeOptionItem">
                  {{ timeOptionItem }}
                </el-option>
              </el-select>

              <el-select v-model="item.time_end" placeholder="結束時間" filterable clearable style="width:120px">
                <el-option :key="timeOptionItem" :label="timeOptionItem" :value="timeOptionItem"
                  v-for="timeOptionItem in TimeOption.filter(x => { return (item.time_start ? x > item.time_start : true) })">
                  {{ timeOptionItem }}
                </el-option>
              </el-select>

              <el-button class="ms-1" @click="addRow(item, index)">
                <font-awesome-icon icon="add" />
              </el-button>
              <el-button class="ms-1" type="danger" :disabled="!item?.delete" @click="deleteRow(item, index)">
                <font-awesome-icon icon="trash-alt" />
              </el-button>

            </td>
            <td valign="middle">
              <el-input-number v-model="item.price" v-if="['夏月','夏月指定30天','夏月30日之外'].indexOf(item.summer_type) > -1" min="0"
                :disabled="!(item.time_start && item.time_end)" />
              <span v-else>-</span>
            </td>
            <td valign="middle">
              <el-input-number v-model="item.price" v-if="item.summer_type === '非夏月'" min="0"
                :disabled="!(item.time_start && item.time_end)" />
              <span v-else>-</span>
            </td>
          </tr>

          <tr v-for="(item, index) in displayForm[0].data.filter(i => i.day_start === 7)">

            <th v-if="!index" rowspan="2" valign="middle">週日及離峰日</th>
            <th v-if="!index" rowspan="2" valign="middle">離峰期間</th>
            <th v-if="!index" rowspan="2" valign="middle">全日</th>
            <td v-if="!index" rowspan="2" valign="middle">00:00-24:00</td>
            <td v-if="!index" rowspan="2">
              <el-input-number v-model="item.price" v-if="['夏月','夏月指定30天','夏月30日之外'].indexOf(item.summer_type) > -1" min="0" />
            </td>
            <td v-if="index" rowspan="2">
              <el-input-number v-model="item.price" v-if="item.summer_type === '非夏月'" min="0" />
            </td>

          </tr>

        </tbody>
      </table>
    </el-form>
    <div class="dialog-footer text-center mt-2">

      <el-button @click="Close">
        <font-awesome-icon icon="xmark" class="me-1" />關閉
      </el-button>
      <el-button type="primary" @click="previewDialog = true">
        <font-awesome-icon icon="table" class="me-1" />預覽
      </el-button>
      <el-button type="primary" @click="Save">
        <font-awesome-icon icon="check" class="me-1" />儲存
      </el-button>
    </div>

  </el-dialog>

  <el-dialog title="預覽" v-model="previewDialog" width="1200px" :close-on-click-modal="false">
    <el-form :inline="true">
      <el-form-item label="電壓類型" prop="volt_type">
        <el-radio-group v-model="currentSelect.volt_type" :disabled="true">
          <el-radio-button label="高壓"></el-radio-button>
          <el-radio-button label="特高壓"></el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="時段類型" prop="time_step">

        <el-radio-group v-model="currentSelect.time_step" :disabled="true">
          <el-radio-button label="二段式">二段式</el-radio-button>
          <el-radio-button label="三段式">三段式</el-radio-button>
          <el-radio-button label="尖峰時間可變動">尖峰時間可變動</el-radio-button>
          <el-radio-button label="批次生產">批次生產</el-radio-button>
          <el-radio-button label="表後儲能時間電價">表後儲能時間電價</el-radio-button>

        </el-radio-group>

      </el-form-item>


    </el-form>

    <table class="table table-bordered">
      <tbody align="center">
        <tr>
          <th></th>
          <th></th>
          <th></th>
          <th>時段</th>
          <th>夏月電價</th>
          <th>非夏月電價</th>
        </tr>


        <tr v-for="(item, index) in displayForm[0].data.filter(i => i.day_start !== 7)" :key="index">
          <th v-if="showRowspan(item, index, 'day_start')" :rowspan="getRowspan(item, index, 'day_start')"
            style="width: 120px;" valign="middle">
            <span v-if="item.day_start == 1">
              週一至週五
            </span>
            <span v-else-if="item.day_start == 6">週六</span>
          </th>
          <th v-if="showRowspan(item, index, 'price_level')" :rowspan="getRowspan(item, index, 'price_level')"
            style="width: 120px;" valign="middle">
            {{ item.price_level }}
          </th>
          <th v-if="showRowspan(item, index, 'summer_type')" :rowspan="getRowspan(item, index, 'summer_type')"
            style="width: 120px;" valign="middle">
            {{ item.summer_type }}
          </th>

          <td>
            {{ item.time_start }} - {{ item.time_end }}
          </td>

          <td v-if="showPreviewRowspan(item, index)" :rowspan="getPreviewRowspan(item, index)" valign="middle">
            <span v-if="['夏月','夏月指定30天','夏月30日之外'].indexOf(item.summer_type) > -1">{{ item.price ? item.price : '-' }}</span>
            <span v-else>-</span>
          </td>
          <td v-if="showPreviewRowspan(item, index)" :rowspan="getPreviewRowspan(item, index)" valign="middle">

            <span v-if="item.summer_type === '非夏月'">{{ item.price ? item.price : '-' }}</span>
            <span v-else>-</span>
          </td>
        </tr>

        <tr v-for="(item, index) in displayForm[0].data.filter(i => i.day_start === 7)">

          <th v-if="!index" rowspan="2">週日及離峰日</th>
          <th v-if="!index" rowspan="2">離峰期間</th>
          <th v-if="!index" rowspan="2">全日</th>
          <td v-if="!index" rowspan="2">00:00-23:59</td>
          <td v-if="!index" rowspan="2">
            <span v-if="['夏月','夏月指定30天','夏月30日之外'].indexOf(item.summer_type) > -1">{{ item.price ? item.price : '-' }}</span>
          </td>
          <td v-if="index" rowspan="2">
            <span v-if="item.summer_type === '非夏月'">{{ item.price ? item.price : '-' }}</span>
          </td>

        </tr>


      </tbody>
    </table>

    <div class="dialog-footer text-center mt-2">
      <el-button @click="previewDialog = false">
        <font-awesome-icon icon="xmark" class="me-1" />關閉
      </el-button>
    </div>
  </el-dialog>

</template>
<script setup>
  import { ref, onMounted, computed, watch, readonly } from 'vue';
  import { useStore } from 'vuex';
  const store = useStore();
  import moment from 'moment';
  import { ElMessage, ElLoading } from 'element-plus';

  import { getSystemElectricSetting, postSystemElectricSetting } from "@/api/Api.js";


  const ApiResult = ref({
    getSystemElectricSetting: []
  })

  const FormTemplate = ref({
    _id: null,
    version: 'v1',
    is_set: 0,
    effect_date: moment(new Date()).format("YYYY-MM-DD"),
    summer_date_start: '',
    summer_date_end: '',
    data: [
      {
        volt_type: '高壓',
        time_step: '二段式',
        data: [{
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '非夏月',
          price: null
        },
        ]
      },
      {
        volt_type: '高壓',
        time_step: '批次生產',
        data: [{
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '非夏月',
          price: null
        },
        ]
      },
      {
        volt_type: '高壓',
        time_step: '三段式',
        data: [
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '非夏月',
            price: null
          },
        ]
      },
      {
        volt_type: '高壓',
        time_step: '尖峰時間可變動',
        data: [
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '夏月指定30天',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月指定30天',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月30日之外',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '非夏月',
            price: null
          },
        ]
      },
      {
        volt_type: '高壓',
        time_step: '表後儲能時間電價',
        data: [
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月30日之外',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '非夏月',
            price: null
          },
        ]
      },

      {
        volt_type: '特高壓',
        time_step: '二段式',
        data: [{
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '非夏月',
          price: null
        },
        ]
      },
      {
        volt_type: '特高壓',
        time_step: '批次生產',
        data: [{
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 1,
          day_end: 5,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '半尖峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 6,
          day_end: 6,
          time_start: '',
          time_end: '',
          price_level: '離峰',
          summer_type: '非夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '夏月',
          price: null
        },
        {
          day_start: 7,
          day_end: 7,
          time_start: '',
          time_end: '',
          price_level: '離峰期間',
          summer_type: '非夏月',
          price: null
        },
        ]
      },
      {
        volt_type: '特高壓',
        time_step: '三段式',
        data: [
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '非夏月',
            price: null
          },
        ]
      },
      {
        volt_type: '特高壓',
        time_step: '尖峰時間可變動',
        data: [
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '夏月指定30天',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月指定30天',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月30日之外',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '非夏月',
            price: null
          },
        ]
      },
      {
        volt_type: '特高壓',
        time_step: '表後儲能時間電價',
        data: [
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月30日之外',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 1,
            day_end: 5,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '半尖峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 6,
            day_end: 6,
            time_start: '',
            time_end: '',
            price_level: '離峰',
            summer_type: '非夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '夏月',
            price: null
          },
          {
            day_start: 7,
            day_end: 7,
            time_start: '',
            time_end: '',
            price_level: '離峰期間',
            summer_type: '非夏月',
            price: null
          },
        ]
      }
    ]
  }
  );

  const Form = ref({});

  const currentSelect = ref({
    volt_type: '高壓',
    time_step: '二段式'
  })


  const FormRule = ref({
    version: [{ required: true, message: ' ', trigger: 'change' }],
    effect_date: [{ required: true, message: ' ', trigger: 'change' }],
    summer_date_start: [{ required: true, message: ' ', trigger: 'blur' }],
    summer_date_end: [{ required: true, message: ' ', trigger: 'blur' }],
    is_set: [{ required: true, message: ' ', trigger: 'blur' }],
  })

  const getList = () => {
    getSystemElectricSetting()
      .then((res) => {
        if (res.data.message == "Success") {
          console.log()
          ApiResult.value.getSystemElectricSetting = res.data.data;
        }
      })

  }

  const Dialog = ref(false);

  const DialogType = ref('')

  const displayForm = computed(() => {
    return Form.value.data.filter(i => i.volt_type === currentSelect.value.volt_type && i.time_step === currentSelect.value.time_step)
  })

  const Edit = (row) => {
    Form.value = structuredClone(FormTemplate.value)
    DialogType.value = '修改';
    Dialog.value = true;
    getItem(row);
  }


  const getItem = (row) => {
    const loading = ElLoading.service({
      lock: true,
      text: '',
      background: 'rgba(255, 255, 255, 0.7)',
    })
    getSystemElectricSetting({
      _id: row._id
    })
      .then((res) => {
        Form.value = res.data.data[0];
        var current_select = res.data.data[0].data.find(item => item.is_set === 1);
        if (current_select) {
          currentSelect.value.volt_type = current_select.volt_type;
          currentSelect.value.time_step = current_select.time_step;
        }
        else {
          currentSelect.value.volt_type = "高壓";
          currentSelect.value.time_step = "兩段式";
        }
      })
      .catch((err) => {
        ElMessage({ type: "error", message: err.message });
      })
      .finally(() => { loading.close(); })
  }

  const TimeOption = ref([
    "00:00", "00:30", "01:00", "01:30", "02:00", "02:30",
    "03:00", "03:30", "04:00", "04:30", "05:00", "05:30",
    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30",
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
    "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
    "24:00"
  ]);

  const showRowspan = ((row, index, key) => {
    if (index > 0) {
      if (row[key] === displayForm.value[0].data[index - 1][key]
      ) {
        return false;
      } else {
        return true;
      }

    } else {
      return true;
    }
  })

  const getRowspan = ((row, index, key) => {
    let rowspan = 1;
    for (let i = index + 1; i < displayForm.value[0].data.length; i++) {
      if (displayForm.value[0].data[i][key] === row[key]) {
        rowspan++;
      } else {
        break;
      }
    }
    return rowspan;
  })

  const getPreviewRowspan = (row, index) => {
    const count = displayForm.value[0].data.filter(item =>
      item.day_start === row.day_start &&
      item.price_level === row.price_level &&
      item.summer_type === row.summer_type &&
      Number(item.price) === Number(row.price)
    ).length;
    return count;
  }

  const showPreviewRowspan = (row, index) => {
    if (index > 0) {
      if (row.price_level === displayForm.value[0].data[index - 1].price_level && row.summer_type === displayForm.value[0].data[index - 1].summer_type && Number(row.price) == Number(displayForm.value[0].data[index - 1].price)) {
        return false; // 不顯示
      } else {
        return true;
      }
    } else {
      return true
    }
  }

  const addRow = (row, index) => {

    displayForm.value[0].data.splice(
      index + 1, 0,
      {
        day_start: row.day_start,
        day_end: row.day_end,
        time_start: '',
        time_end: '',
        price_level: row.price_level,
        summer_type: row.summer_type,
        price: null,
        delete: true
      }
    )

  }

  const deleteRow = (row, index) => {
    displayForm.value[0].data.splice(index, 1)
  }

  const previewDialog = ref(false)

  const FormRef = ref(null);

  const Close = () => {
    Dialog.value = false;
    Form.value = structuredClone(FormTemplate.value)
    refreshStartKey.value++;
    refreshEndKey.value++;
  }

  const Save = () => {
    FormRef.value.validate((valid) => {
      if (valid) {
        const loading = ElLoading.service({
          lock: true,
          text: '',
          background: 'rgba(255, 255, 255, 0.7)',
        });

        // 處理選中的項目
        Form.value.data.forEach(item => {
          if (item.volt_type === currentSelect.value.volt_type && item.time_step === currentSelect.value.time_step){
            item.is_set = 1
          }
          else {
            item.is_set = 0
          }
        });

        postSystemElectricSetting(Form.value)
          .then((res) => {
            if (res.data.message == "Success") {
              ElMessage({ type: "success", message: `${DialogType.value}成功` });
              // Form.value = structuredClone(FormTemplate.value)
              // Dialog.value = false;
              getList();

            } else {
              ElMessage({ type: "error", message: res.data.message });
            }
          })
          .catch((err) => {
            ElMessage({ type: "error", message: err.message });
          })
          .finally(() => { loading.close() })
      }
    })


  }

  onMounted(() => {
    getList();
  })

</script>
