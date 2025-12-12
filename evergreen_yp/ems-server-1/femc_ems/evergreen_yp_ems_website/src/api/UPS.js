import { get, post   } from '@/api/axiosApi';

const getEquipments = (params) => get('/ups/equipments', params);
const getUPSRackInfo = (params) => get('/ups/ups/rack_info', params);
const getUPSRackDetailInfo = (params) => get('/ups/ups/rack/detail_info', params);
const postUPSECI = (params) => post('/ups/ups/eci', params);

 export default {
    getEquipments,
    getUPSRackInfo,
    getUPSRackDetailInfo,
    postUPSECI,
 }