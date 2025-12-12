import { get, post, del,uploadFile,download,getDownload,postDownload,getURLQueryParmater,postWithHeader , noPrefixGet} from '@/api/axiosApi'; // download, uploadFile , uploadAndParamater, postWithHeader

export const getFields = (params) => get('/fields', params);
export const postFields = (params) => post('/fields', params);
export const delFields = (params) => del('/fields', params);
export const getEquipments = (params) => get('/system/equipments', params);
export const postEquipments = (params) => post('/system/equipments', params);
export const delEquipments = (params) => del('/system/equipments', params);
export const getFieldInfo = (params) => get('/field/info', params);
export const getCabinetInfo = (params) => get('/cabinet/info', params);

export const getSystemAnnouncement=(params) => get('system/announcement',params)//公告管理，查詢

export const getAlertHistorical = (params) => get('/alert/historical', params); 
export const getAlertRealTime = (params) => get('/alert/real_time', params);
export const getAlertHistoricalExport = (params) => getDownload('/alert/historical_export', params);
export const getCabinetAirInInfo = (params) => get('/cabinet/air_in_info', params);
export const getCabinetFireInfo = (params) => get('/cabinet/fire_info', params);
export const getCabinetPCSInfo = (params) => get('/cabinet/pcs_info', params);
export const getCabinetAccessInfo = (params) => get('/cabinet/access_info', params);
export const getCabinetBMSInfo = (params) => get('/cabinet/bms_info', params);
export const getCabinetAC = (params) => get('/cabinet/ac', params);
export const getCabinetDC = (params) => get('/cabinet/dc', params);
export const getCabinetSOCCurve = (params) => get('/cabinet/soc_curve', params);
export const getCabinetSOHCurve = (params) => get('/cabinet/soc_curve', params);
export const getCabinetFieldInfo = (params) => get('/field/info', params);
export const deleteFields = (params) => del('/fields', params);
export const deleteEquipments = (params) => del('/equipments', params);
export const postFileImport = (params) => post('/file/import', params);
export const getQualitySBSPM = (params) => get('/quality/sbspm', params);
export const getSystemBidWinning = (params) => get('/system/bid/winning', params);
export const getSystemInstantFreqOutput = (params) => get('/system/instant/freq_output', params);
export const getSystemSchedulingBalanced = (params) => get('/system/scheduling/balanced', params);
export const getSystemBIDWinningCurve = (params) => get('/system/bid/winning_curve', params);
export const getSystemBIDAmount = (params) => get('/system/bid/amount', params);
export const getSystemChargeTotalTime = (params) => get('/system/charge/total_time', params);
export const getCabinetRockInfo = (params) => get('/cabinet/rack_info', params);
export const postCabinetESSCI = (params) => post('/cabinet/essci', params);
export const getEMSESSCI = (params) => get('/ems/essci', params);
export const getCabinetBMSInInfo = (params) => get('/cabinet/bms_info', params);
export const getCabinetACInfo = (params) => get('/cabinet/ac', params);
export const getCabinetDCInfo = (params) => get('/cabinet/dc', params);
export const getFieldSBSPM = (params) => get('/quality/sbspm', params);
export const getFieldFREQ = (params) => get('/system/instant/freq_output', params);
export const getFieldBIDS = (params) => get('/system/bid/winning', params);
export const getFieldBIDSCurve = (params) => get('/system/bid/winning_curve', params);
export const getFieldBIDSGantt = (params) => get('/system/bid/winning_gantt', params);
export const getFieldBIDSAmount = (params) => get('/system/bid/amount', params);
export const getFieldTotalChargeTime = (params) => get('/system/charge/total_time', params);
export const getFieldBalance = (params) => get('/system/scheduling/balanced', params);
export const getFieldAlarm = (params) => get('/alert/real_time', params);
export const uploadBIDSchedule = (params) => uploadFile('/file/import', params);
export const getSystemCapacityAmount  = (params) => get('/system/capacity/amount', params);
export const LOGIN = (params) => post('/permission/user/login', params);
export const getUsers = (params) => get('/permission/user', params);
export const postUsers = (params) => post('/permission/user', params);
export const deleteUsers = (params) => del('/permission/user', params);

export const resetUserPassword = (params) => post('/permission/user/reset', params);
export const changeUserPassword = (params) => post('/permission/user/change_password', params);
export const twoFactorAuth = (params) => post('/permission/user_two_factor_auth', params);

export const getUserFields = (params) => get('/permission/user/field', params);
export const postUserFields = (params) => post('/permission/user/field', params);
export const deleteUserFields = (params) => del('/permission/user/field', params);

export const getRoles = (params) => get('/permission/role', params);
export const postRoles = (params) => post('/permission/role', params);
export const deleteRoles = (params) => del('/permission/role', params);

export const getUserRoles = (params) => get('/permission/user/role', params);
export const postUserRoles = (params) => post('/permission/user/role', params);
export const deleteUserRoles = (params) => del('/permission/user/role', params);

export const postCabinetECI = (params) => post('/cabinet/eci', params);
export const postReportPower = (params) => post('/report/power', params);
export const postReportActual = (params) => post('/report/actual', params);
export const getFieldMeter = (params) => get('/field/meter', params);
export const postPIData = (params) => post('/pi_data', params);

// 資源管理
export const getCaseOption = (params) => get('/case_option', params); // 取得報價代碼選單
export const getResourceByCaseID = (params) => get('/resource/by_case_id', params);
export const postResourceByCaseID = (params) => post('/resource/by_case_id', params);
export const deleteResourceByCaseID = (params) => del('/resource/by_case_id', params);

export const getResourceByResourcesId = (params) => get('/resource/by_resources_id', params);
export const postResourceByResourcesId = (params) => post('/resource/by_resources_id', params);
export const deleteResourceByResourcesId = (params) => del('/resource/by_resources_id', params);
//投標
export const getOperationBID = (params) => get('/operation/bid', params);
export const getOperationBIDHistory = (params) => get('/operation/bid_history', params);
export const getOperationBIDHistoryList = (params) => get('/operation/bid_history/list', params);
export const getOperationBIDDownloadExample = (params) => getDownload('/operation/bid/download_example', params);
export const postOperationBIDUploadInformation = (params) => uploadFile('/operation/bid/upload_information', params);
export const getOperationBIDDownload = (params) => getDownload('/operation/bid/download', params);
export const postOperationBIDUploadResult = (params) => uploadFile('/operation/bid/upload_result', params);
export const postOperationBIDAddForm = (params) => post('/operation/bid/add_form', params);

// 補值
export const getOperationComplement = (params) => getDownload('/operation/complement', params);
// 對帳單
export const postOperationBankStatment = (params) => post('/operation/bank_statement', params);
export const postOperationBankStatmentDownload = (params) => download('/operation/bank_statement_download', params);


// 台電
export const getElectToday=() =>post('/pi_data', { url: 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json'})
export const getElectYesterdayCsv=() =>post('/pi_data', { url: 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadfueltype_1.csv'})
export const getElectTodayCsv=() =>post('/pi_data', { url: 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadfueltype.csv'})
export const getOperatingRes=() =>post('/pi_data', { url: 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.txt'})
// 電力交易平台
export const getNextWeek = (params) => post( '/pi_data', { url: 'https://etp.taipower.com.tw/api/infoboard/asdemand/query' + getURLQueryParmater(params) } );
export const getHistoryBid =(params) =>post('/pi_data', { url:'https://etp.taipower.com.tw/api/infoboard/offering/query'+ getURLQueryParmater(params) });
export const getHistorySettlementTrading =(params) =>post('/pi_data', { url:'https://etp.taipower.com.tw/api/infoboard/settle_value/query'+ getURLQueryParmater(params) });
export const getHistoryPriceLimit=(params) =>post('/pi_data', { url:'https://etp.taipower.com.tw/api/infoboard/price_limit/query'+ getURLQueryParmater(params) })
export const getQseList=(params) =>post('/pi_data', { url:'https://etp.taipower.com.tw/api/infoboard/qse_list'+ getURLQueryParmater(params) }) 
// 氣象局
export const getWeather=(params)=>post('/pi_data', { url: 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-091'+ getURLQueryParmater(params) })
//未來七日用電預測
export const getReserveForecast=() => post('/pi_data', { url: 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/reserve_forecast.txt'})
//今日備轉容量
export const getBackupCapacity=() => post('/pi_data', { url: 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.txt'})

export const postReportSpiningRegulation=(params) => post('/report/spinning_regulation/daily',params)//營運狀況，調頻與即時備轉
export const postReportSupplement=(params) => post('/report/supplement/daily',params)//營運狀況，補充備轉
export const getReportCapacityAndPayPlotData=(params) => get('/report/capacity_vs_capacity_pay/plot_data',params)//投/得標容量與金額(chart)
export const getReportCapacityAndElectricityPlotData=(params) => get('/report/capacity_vs_electricity_pay/plot_data',params)//投/得標容量與金額與電能費(chart)
export const getReportIncomeExacutiveRatePlotData=(params) => get('/report/income_vs_exacutive_rate/plot_data',params)//預期營收、最大營收、執行率(chart)
export const getReportSpinningSupplement=(params) => post('/report/spinning_supplement',params)//運轉分析-即時/補充
export const getReportSpinningSupplementPlotData=(params) => post('/report/spinning_supplement/plot_data',params)//運轉分析-即時/補充 ，chart data
export const postReportRegulation=(params) => post('/report/regulation',params)//運轉分析-調頻備轉
export const getReportRegulationPlotData=(params) => get('/report/regulation/plot_data',params)//運轉分析-調頻備轉，chart data

export const getOperationBidAllocation=(params) => get('/operation/bid/allocation',params)//取得得標容量分配
export const postOperationBidAllocation=(params) => post('/operation/bid/allocation',params)//更新得標容量分配

export const getDashboardToDo=(params) => get('/dashboard/to_do',params)//取得今日待辦事項{date:yyyyMMdd}
export const getDashboardHistory=(params) => get('/dashboard/history',params)//取得投標管理首頁匯總資料{date:yyyyMMdd}
export const getDashboardHistoryByCase=(params) => get('/dashboard/history/by_case',params)//取得報價代碼匯總資料{date:yyyyMMdd, case_code}
export const getDashboardFrequencyPlotData=(params) => get('/dashboard/electrical_frequency/plot_data',params)//取得報價代碼-調頻-圖型資料{date:yyyyMMddHHmmss, case_code}
export const getDashboardBidExecutionPlotData=(params) => get('/dashboard/bid_execution/plot_data',params)//取得報價代碼-非調頻-圖型資料{date:yyyyMMddHHmmss, case_code}
export const postDashboardAbortStandby=(params) => post('/dashboard/abort_standby',params)//提出中止待命{case_id,datetime,type1今天2明天}
export const getDashboardAbortStandby=(params) => get('/dashboard/abort_standby',params)//取得中止待命記錄{case_id}
export const postOperationDispatchingHistory=(params) => post('/operation/dispatching_history',params)//查詢調度記錄

export const SSO=(params,header) =>postWithHeader('/permission/user/login', params , header); // 雲地同步登入
//用電大戶
export const getSystemStorageSetting=(params) => get('/system/storage_setting',params)// 取得儲能設定
export const getSystemDemand=() => get('/system/demand', null)// 取得契約容量
export const postSystemStorageSetting=(params) => post('/system/storage_setting',params)// 更新儲能設定

export const getSystemScheduleSetting=(params) => get('/system/schedule_setting',params)// 取得排程設定
export const postSystemScheduleSetting=(params) => post('/system/schedule_setting',params)// 新增/更新排程
export const delSystemScheduleSetting=(params) => del('/system/schedule_setting',params)// 刪除排程

export const getSystemCustomProtect=(params) => get('/system/custom_protect',params)// 取得客製化系統保護
export const postSystemCustomProtect=(params) => post('/system/custom_protect',params)// 新增/更新客製化系統保護

// 排程設定 Schedule Settings (充放電腳本設定))
export const getAllSchedule=(params) => get('/electric/schedule',params)// 取得排程設定表
export const postSchedule=(params) => post('/electric/schedule',params)// 新增/更新排程設定
export const delSchedule=(params) => del('/electric/schedule',params)// 刪除單排程設定
export const getScheduleDetail=(params) => get('/electric/schedule_detail',params)// 取得單排程設定
export const postScheduleDetail=(params) => post('/electric/schedule_detail',params)// 新增/更新單排程
export const delScheduleDetail =(params) => del('/electric/schedule_detail',params)// 刪除單排程內容(刪除已存在的排程內容)
// Power Control Setting (抑低用電腳本設定)
export const getPowerSchedule=(params) => get('/power_control/schedule',params)// 取得排程設定表
// 儲能設定 > 抑低用電 > 抑低單日排程
export const getPowerOneDaySchedule=(params) => get('/power_control/settings',params)
export const postPowerOneDaySchedule=(params) => post('/power_control/settings',params)// 新增/更新排程
export const delPowerOneDaySchedule=(params) => del('/power_control/settings',params)// 刪除排程
// 電價設定
export const getSystemElectricSetting=(params) => get('/system/electric_setting',params)// 取得電價設定
export const postSystemElectricSetting=(params) => post('/system/electric_setting',params)// 電價設定更新

export const getSystemElectricReport=(params) => get('/system/electric_report',params)// 用電報表
export const getSystemElectricOperationReport=(params) => get('/system/electric_operation_report',params)// 營運日/周/月報表
export const getSystemEquipments=(params) => get('/system/equipments',params)// 資源設定查詢
export const postSystemEquipments=(params) => post('/system/equipments',params)// 資源設定新增/修戶
export const delSystemEquipments=(params) => del('/system/equipments',params)// 資源設定刪除


export const getSystemStepScenario=(params) => get('/system/step_scenario',params)// 調頻測試情境查詢
export const postSystemStepScenario=(params) => post('/system/step_scenario',params)// 調頻測試情境新增/修戶
export const getScenarioSchedule=(params) => get('/system/scenario_schedule',params)// 調頻測試排程查詢
export const postScenarioSchedule=(params) => post('/system/scenario_schedule',params)// 調頻測試排程新增/修戶
export const delScenarioSchedule=(params) => del('/system/scenario_schedule',params)// 調頻測試排程查詢刪除

export const postModbusControl=(params) => post('/modbus/control',params)// modbus指令執行
export const postModbusControlEmergency=(params) => post('/modbus/emergency',params)// modbus指令執行
export const postOperateModeChange=(params) => post('/operation_mode',params)// 控制模式切換
export const getModbusControlCheck=(params) => get('/modbus/control/check',params)// modbus指令執行
export const iecVCBControl=(params) => post('/iec61850/control',params)// relay指令(IEC)
export const getVCBControl=(params) => noPrefixGet('/relay-api/setControl',params)// relay指令
export const getVCBtestAPI=(params) => noPrefixGet('/relay-api/testAPI',params)// relay指令

export const getMeterGetData=(params) => get('/meter/get_data',params)// relay歷史數據-for chart
export const getMeterGetDataExport=(params) => get('/meter/get_data_export',params)// 周前表計資料匯出


export const getPermissionMenuItem=(params) => get("permission/menu/item",params)

// export const getBMUGetData=(params) => get("bmu/get_data",params) //水冷數據查詢
export const getBMUGetData=(params) => get('/get/rack_trand_data',params)
export const getBMUGetDataDownload=(params) => getDownload('/get/rack_trand_data/export',params)
//
export const getPCSHistoryData=(params) => get('/pcs/get_data',params, { timeout: 120000 })
export const getBMSHistoryData=(params) => get('/bms/get_data',params, { timeout: 120000 })
//
export const getPCSHistoryDataExport=(params) => download('/pcs/get_data_export',params)
export const getBMSHistoryDataExport=(params) => download('/bms/get_data_export',params)
//
export const postExportAsyncData=(params) => postDownload('/data/export_async',params)
export const getExportAsyncData=(params) => get('/data/export_async',params)
//
export const getHoildays=(params) => get('/taipower_holidays',params)
export const downTemplate=(params) => get('/system/download_template',params)
export const UpTemplate=(params) => post('/taipower_holidays',params) // # action 0: download, 1: upload
//
//notify_rule
export const getNotifyRule=(params) => get('/notify/rule',params)
export const postNotifyRule=(params) => post('/notify/rule',params)
export const delNotifyRule=(params) => del('/notify/rule',params)
//notify_token
export const getNotifyToken=(params) => get('/notify/token',params)
export const postNotifyToken=(params) => post('/notify/token',params)
export const delNotifyToken=(params) => del('/notify/token',params)
//notify_setting
export const getNotifySetting=(params) => get('/notify/setting',params)
export const postNotifySetting=(params) => post('/notify/setting',params)
//notify_log
export const getNotifyLog=(params) => get('/notify/log',params)

//
//Femc notify_rule
export const getFemcNotifyRule=(params) => get('/femc_msg/rule',params)
export const postFemcNotifyRule=(params) => post('/femc_msg/rule',params)
export const delFemcNotifyRule=(params) => del('/femc_msg/rule',params)
//Femc notify_token
export const getFemcNotifyToken=(params) => get('/femc_msg/token',params)
export const postFemcNotifyToken=(params) => post('/femc_msg/token',params)
export const delFemcNotifyToken=(params) => del('/femc_msg/token',params)
//Femc notify_setting
export const getFemcNotifySetting=(params) => get('/femc_msg/setting',params)
export const postFemcNotifySetting=(params) => post('/femc_msg/setting',params)
//Femc notify_log
export const getFemcNotifyLog=(params) => get('/femc_msg/log',params)

//system_dropdown
export const getSystemDropdown=(params) => get('/system/dropdown',params)

//CabinetReports
export const getCabinetReport=(params) => get('/report/cabinet_data',params)
export const postCabinetReportDonwload=(params) => postDownload('/report/cabinet_data',params)
export const postCabinetReportChart=(params) => post('/report/cabinet_chart_data',params)

//GetDashboardHistory
export const getChartHistory=(params) => get('/chart/history',params)
//GetSunDashboardHistory
export const getChartHistorySun=(params) => get('/chart/history_sun',params)
export const getDashboardSunData=() => get('/dashboard/sun', null)
export const getChartHistorySunDB=(params) => get('/chart/history_sun_db',params)
export const getDashboardSunDataDB=() => get('/dashboard/sun_db', null)
//SunReport
export const getSunReport=(params) => post('/inverter/get_data', params)
export const getSunReportDownload=(params) => postDownload('/inverter/get_data', params)
