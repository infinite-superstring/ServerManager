<script>
import message from "@/scripts/utils/message"
import user from "@/scripts/admin/users"
import axios from "axios";
import EditUserStatus from "@/components/dialogs/users/editUserStatus.vue";

import('@/styles/Admin/UserList.scss')
export default {
  name: "UserList",
  components: {EditUserStatus},
  data: () => {
    return {
      maxPage: null,
      currentPage: null,
      search: "",
      userList: [],
      permissionGroupsList: [],
      inputDialog: {
        flag: false,
        input: null,
        uid: null,
        title: null,
        label: null,
        type: null,
        callback: null
      },
      newUserDialog: {
        flag: false,
        userName: null,
        realName: null,
        email: null,
        password: null,
        disable: false
      },
      editUserPermission: {
        flag: false,
        userId: null,
        maxPage: null,
        currentPage: 1,
        search: "",
        selected: null
      },
      editUserStatus: {
        flag: false,
        userId: null,
        value: null
      }
    }
  },
  methods: {
    // 打开输入框
    openInputDialog(uid, title, label, defaultValue, callback=null, type="text") {
      if (!this.inputDialog.flag) {
        this.inputDialog.flag = true
        this.inputDialog.uid = uid
        this.inputDialog.title = title
        this.inputDialog.label = label
        this.inputDialog.input = defaultValue
        this.inputDialog.type = type
        this.inputDialog.callback = callback
      } else {
        console.warn("当前已有开启中的输入框")
      }
    },
    getUserInfo(uid) {
      /**
       * 获取用户信息
       */
      return axios.post("/admin/api/getUserInfo",{id:uid}).catch(err=>{
        message.showApiErrorMsg(this, err.message)
      })
    },
    updateUserInfo(uid, data) {
      /**
       * 更新用户信息
       * @type {{data, id}}
       */
      data = {id: uid, data: data}
      axios.post("/admin/api/setUserInfo",data).then(res=>{
        const status = res.data.status
        if (status !== 1) {
         message.showApiErrorMsg(this, res.data.msg, status)
         return false
        } else {
          return true
        }
      }).catch(err=>{
        console.error(err)
        message.showApiErrorMsg(this, err.message)
        return false
      })
    },
    // 新增用户
    newUser() {

    },

    editPermission(uid) {
      /**
       * 编辑权限
       */
      this.updateUserInfo(uid,{permission: this.editUserPermission.selected})
      this.editUserPermission.flag = false
      this.getUserList(this.search, this.maxPage)
    },

    // 编辑用户

  },
  watch: {

    "editUserPermission.currentPage"(val) {
      this.loadPermissionGroups(this.editUserPermission.search, val)
    },
    "editUserPermission.search"(val) {
      this.loadPermissionGroups(val, 1)
      this.editUserPermission.currentPage = 1
    }
  },
  created() {
    this.getUserList()
  },
}
</script>

<template>
  <div class="toolsBar">
    <v-btn id="addUser" color="success" @click="newUserDialog.flag = true">新增用户</v-btn>
    <v-text-field id="searchUser" class="search" density="compact" label="搜索" variant="solo-filled" single-line hide-details v-model="search"></v-text-field>
  </div>

  <v-pagination
    v-model="currentPage"
    v-if="!maxPage <= 1"
    :length="maxPage"
    :total-visible="6"
    prev-icon="mdi:mdi-menu-left"
    next-icon="mdi:mdi-menu-right"
    rounded="circle"
  ></v-pagination>
  <div class="dialogs">
<!--    通用输入框-->
    <v-dialog
      id="inputDialog"
      v-model="inputDialog.flag"
      activator="parent"
      min-width="400px"
      width="auto"
      persistent
    >
      <v-card>
        <v-card-title>{{ inputDialog.title }}</v-card-title>
        <v-card-text>
          <v-text-field v-model="inputDialog.input" :label="inputDialog.label" :type="inputDialog.type"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" @click="inputDialog.flag = false;inputDialog.input = null">取消</v-btn>
          <v-btn color="success" @click="inputDialog.callback ? inputDialog.callback(inputDialog.uid, inputDialog.input) : null;inputDialog.flag = false;inputDialog.input = null">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
<!--    新增用户-->

  </div>
</template>

<style scoped>

</style>
