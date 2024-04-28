// Composables
import { createRouter, createWebHistory } from 'vue-router'
import login from "@/views/Login.vue";
import UserInfo from "@/views/UserInfo.vue";
import Dashboard from "@/views/Dashboard.vue"
import MachineList from "@/views/machine/MachineList.vue";
import NodeControl from "@/views/machine/NodeControl.vue";
import userManagementPage from "@/views/admin/User.vue"
import permissionManagementPage from "@/views/admin/Permission.vue"
import auditAndLoggerPage from "@/views/admin/Audit.vue"
import configPage from "@/views/admin/Config.vue"
import aboutPage from "@/views/About.vue"
import errorPage from "@/views/Error.vue"
import appbar_default from "@/components/header/AppBar_Btn/default.vue"


const routes = [
  // 登录
  {
    path: '/login',
    name: "login",
    component: login,
  },
  // 仪表板
  {
    path: '/',
    name: "dashboard",
    components: {
      default: Dashboard
    }
  },
  // 机器列表
  {
    path: '/machineList',
    name: "machineList",
    components: {
      default: MachineList
    }
  },
  // 节点控制（暂定名）
  {
    path: '/nodeControl',
    name: "nodeControl",
    components: {
      default: NodeControl
    }
  },
  // 网站可用性监控
  // {
  //
  // },
  // 个人信息设置
  {
    path: '/userInfo',
    name: "userInfo",
    components: {
      default: UserInfo,
    }
  },
  // 管理 - 用户管理
  {
    path: "/admin/users",
    name: "userManagement",
    components: {
      default: userManagementPage,
    }
  },
  // 管理 - 权限管理
  {
    path: "/admin/permission",
    name: "permissionManagement",
    components: {
      default: permissionManagementPage,
    }
  },
  // 管理 - 审计与日志
  {
    path: "/admin/audit",
    name: "audit",
    components: {
      default: auditAndLoggerPage,
      appBarBtn: appbar_default
    }
  },
  // 配置文件编辑
  {
    path: "/admin/settings",
    name: "settings",
    components: {
      default: configPage,
      // appBarBtn: appbar_default
    }
  },
  // 关于
  {
    path: "/about/",
    name: "about",
    component:aboutPage
  },
  // 错误
  { path: '/error/:errorCode', component: errorPage },
  { path: '/:pathMatch(.*)*', redirect: '/error/404' } // 重定向到404页
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
