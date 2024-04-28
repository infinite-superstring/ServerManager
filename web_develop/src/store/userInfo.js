import { defineStore } from 'pinia'
import axios from "axios";
// 1. 创建store
// 参数1：store的唯一表示
// 参数2：对象，可以提供state actions getters
export const useUserStore = defineStore('UserInfo', {
  state: () => ({
    email: null,
    group: null,
    id: null,
    realName: null,
    userName: null,
    permissions: {
      all: false,
      viewDevice: false,
      controllingDevice: false,
      changeDevicePowerState: false,
      changeSettings: false,
      manageUsers: false,
      managePermissionGroups: false,
      viewAudit: false,
      editAudit: false,
    }
  }),
  actions: {
    getUserInfo() {
      return new Promise((resolve)=>{
        axios.get("/userInfo/api/getInfo").then(res=>{
          const data = res.data.data
          this.id = data.id
          this.userName = data.userName
          this.realName = data.realName
          this.group = data.group
          this.email = data.email
          this.permissions = data.permissions
          resolve()
        }).catch(err=>{
          console.log(err)
        })
      })
    }
  },
  persist: true,
})
