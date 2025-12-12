import { createApp } from 'vue'
import App from './App.vue'
import 'bootstrap/dist/js/bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css';
import ElementPlus from 'element-plus'
import axios from 'axios'
import VueAxios from 'vue-axios'
import 'element-plus/theme-chalk/index.css'
import locale from 'element-plus/dist/locale/zh-tw.mjs'
import router from './router/router.js'
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { fas } from '@fortawesome/free-solid-svg-icons';
import {GGanttChart, GGanttRow} from 'vue-ganttastic'
import store from '@/store/store.js';
import 'v-calendar/dist/style.css';
import { SetupCalendar} from 'v-calendar';

library.add(fas)

createApp(App)
    .use(GGanttChart,GGanttRow)
    .use(ElementPlus, { locale })
    .use(router)
    .use(store)
    .use(VueAxios, axios)
    .use(SetupCalendar,{ screens: {
      tablet: '576px',
      laptop: '992px',
      desktop: '1200px',
    },})
    .component("font-awesome-icon", FontAwesomeIcon)
    .mount('#app')
    // .use(VCalendar, {})