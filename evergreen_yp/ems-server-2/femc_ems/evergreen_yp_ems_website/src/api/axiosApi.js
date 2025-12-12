import axios from 'axios';
import router from '@/router/router.js'
import store from '@/store/store.js';

const backendAPI = axios.create({
  baseURL: process.env.VUE_APP_ApiURL,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json',
  },
});

const noPrefixAPI = axios.create({
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json',
  },
});

const blobRequest = axios.create({
  baseURL: process.env.VUE_APP_ApiURL,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    "responseType": "arraybuffer"
  },
  responseType: 'blob'
});
blobRequest.interceptors.request.use((config) => {
  const token = store.getters.user.Token;
  if (token) {
    config.headers["Femc-Access-Token"] = token;
  }
  return config
}, (error) => {
  console.log(error)
  return Promise.error(error)
})

backendAPI.interceptors.request.use((config) => {
  const token = store.getters.user.Token;
  if (token) {
    config.headers["Femc-Access-Token"] = token;
  }
  return config
}, (error) => {
  console.log(error)
  return Promise.error(error)
})

backendAPI.interceptors.response.use((response) => {
  if (response.status === 200) {
    return Promise.resolve(response)
  } else {
    Promise.reject(response)
  }
}, (response) => {
  if (response.response.status === 401 || response.response.status === 403) {
    router.push({ name: 'login' });
  }
  return Promise.reject(response.response.data)
})

export function getURLQueryParmater(data) {
  const p = [];
  if (data) {
    Object.keys(data).forEach((key) => {
      p.push(`${key}=${encodeURI(data[key] || data[key] == false || data[key] == 0 ? data[key].toString() : '').replace(/#/g, '%23').replace(/&/g, '%26')}`);
    });
  }
  return p.length ? `?${p.join('&')}` : '';
}



export function noPrefixGet(url, data) {
  const parms = getURLQueryParmater(data);
  return noPrefixAPI.get(`${url}${parms}`)
}

export function get(url, data) {
  const parms = getURLQueryParmater(data);
  return backendAPI.get(`${url}${parms}`)
}

export function post(url, data) {
  return backendAPI.post(url, data)
}

export function postDownload(url, data) {
  return blobRequest.post(url, data, { responseType: 'arraybuffer' })
}

export function postWithHeader(url, data, headers) {
  return backendAPI.post(url, data, { headers: headers });
}

export function put(url, data) {
  return backendAPI.put(url, data)
}
export function del(url, data) {
  data = typeof data === 'string' ? '"' + data + '"' : data;
  return backendAPI.delete(url, { data: data })
}
// upload file only
export function uploadFile(url, file) {
  let params = new FormData();
  params.append('file', file);
  return backendAPI.post(url, params, { headers: { 'Content-Type': 'multipart/form-data' } })
}
//upload file with query string
export function uploadAndParamater(url, data) {
  return backendAPI.post(url, data, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export function getDownload(url, parmater) {
  var _url = parmater ? `${url}${getURLQueryParmater(parmater)}` : url;
  return blobRequest.get(_url, { responseType: 'arraybuffer' })
}



export function download(url, data) {

  return blobRequest.post(url, data, { responseType: 'arraybuffer' })
}
// 電力交易平台未來七日

export function getETP(url, parm) {
  let _url = '';
  const p = [];

  if (parm) {
    Object.keys(parm).forEach((key) => {
      p.push(`${key}=${encodeURI(parm[key] ? parm[key].toString() : '').replace(/#/g, '%23').replace(/&/g, '%26')}`);
    });
  }

  _url = p.length ? `${url}?${p.join('&')}` : url;

  return axios.get(_url)
}
