import { createWebHistory, createRouter } from "vue-router";
const routes = [
  {
    path: "/",
    name: "root",
    component: () => import("@/views/public/login")
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/public/login")
  },
  {
    path: "/SSO",
    name: "SSO",
    component: () => import("@/views/public/SSO")
  },
  {
    path: "/Field",
    name: "Field",
    component: () => import("@/views/frame/Field"),
    children: [
      {
        path: "/FieldHome",
        name: "FieldHome",
        component: () => import("@/views/page/CoachLanding")
      },
      {
        path: "/Dashboard",
        name: "Dashboard",
        component: () => import("@/views/page/Dashboard")
      },
      {
        path: "/SunDashboard",
        name: "SunDashboard",
        component: () => import("@/views/page/SunDashboard")
      },
      {
        path: "/Alert",
        name: "Alert",
        component: () => import("@/views/page/Alert")
      },
      {
        path: "/CommunicateLine",
        name: "CommunicateLine",
        component: () => import("@/views/page/CommunicateLine")
      },
      {
        path: "/ElectricLine",
        name: "ElectricLine",
        component: () => import("@/views/page/ElectricLine")
      },

      {
        path: "/CabinetList",
        name: "CabinetList",
        component: () => import("@/views/page/CabinetList")
      },
      {
        path: "/SystemConfig",
        name: "SystemConfig",
        component: () => import("@/views/page/SystemConfig")
      },
      {
        path: "/PriceConfig",
        name: "PriceConfig",
        component: () => import("@/views/page/PriceConfig")
      },
      {
        path: "/Schedule",
        name: "Schedule",
        component: () => import("@/views/page/Schedule")
      },
      {
        path: "/ResourcesSettings",
        name: "ResourcesSettings",
        component: () => import("@/views/page/ResourcesSettings")
      },
      {
        path: "/AnalogSignal",
        name: "AnalogSignal",
        component: () => import("@/views/page/AnalogSignal")
      },
      {
        path: "/MeterChart",
        name: "MeterChart",
        component: () => import("@/views/page/MeterChart")
      },
      {
        path: "/PCSHistory",
        name: "PCSHistory",
        component: () => import("@/views/page/PCSHistory")
      },
      {
        path: "/BMSHistory",
        name: "BMSHistory",
        component: () => import("@/views/page/BMSHistory")
      },
      {
        path: "/CabinetReports",
        name: "CabinetReports",
        component: () => import("@/views/page/CabinetReports")
      },
      {
        path: "/SunCabinetReports",
        name: "SunCabinetReports",
        component: () => import("@/views/page/SunCabinetReports")
      },
      {
        path: "/admin/RoleSettings",
        name: "RoleSettings",
        component: () => import("@/views/page/RoleSettings")
      },
      {
        path: "/admin/UserSettings",
        name: "UserSettings",
        component: () => import("@/views/page/UserSettings")
      },
      {
        path: "/HolidaySettings",
        name: "HolidaySettings",
        component: () => import("@/views/page/HolidaySettings")
      },
      {
        path: "/LineSetting",
        name: "LineSetting",
        component: () => import("@/views/page/LineSetting")
      },
      {
        path: "/MsgSetting",
        name: "MsgSetting",
        component: () => import("@/views/page/MsgSetting")
      },
      {
        path: "/test",
        name: "test",
        component: () => import("@/views/page/test")
      }
      // {
      //   path: "/StepScenario",
      //   name: "StepScenario",
      //   component: () => import("@/views/page/StepScenario"),
      // },
      // {
      //   path: "/ScenarioSchedule",
      //   name: "ScenarioSchedule",
      //   component: () => import("@/views/page/ScenarioSchedule"),
      // },
      // {
      //   path: "/ReportDay",
      //   name: "ReportDay",
      //   component: () => import("@/views/page/ReportDay"),
      // },
      // {
      //   path: "/ReportMonth",
      //   name: "ReportMonth",
      //   component: () => import("@/views/page/ReportMonth"),
      // },
      // {
      //   path: "/ReportYear",
      //   name: "ReportYear",
      //   component: () => import("@/views/page/ReportYear"),
      // },
      // {
      //   path: "/WaterChart",
      //   name: "WaterChart",
      //   component: () => import("@/views/page/WaterChart"),
      // },
    ]
  },
  {
    path: "/Public",
    name: "Public",
    component: () => import("@/views/frame/Public"),
    children: [
      {
        path: "/CommunicateLinePublic",
        name: "CommunicateLinePublic",
        component: () => import("@/views/page/CommunicateLine")
      },
      {
        path: "/ElectricLinePublic",
        name: "ElectricLinePublic",
        component: () => import("@/views/page/ElectricLine")
      }
    ]
  },
  {
    path: "/:pathMatch(.*)*)",
    name: "notfound",
    component: () => import("@/views/public/login")
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
