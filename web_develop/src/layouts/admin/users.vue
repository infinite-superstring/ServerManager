<script>
import userList from "@/components/tables/users/userList.vue";
import axios from "axios";
import message from "@/scripts/utils/message";

import EditUserPermission from "@/components/dialogs/users/editUserPermission.vue";
import NewUser from "@/components/dialogs/users/newUser.vue";
import EditEmail from "@/components/dialogs/users/editEmail.vue";
import EditRealName from "@/components/dialogs/users/editRealName.vue";
import EditUsername from "@/components/dialogs/users/editUsername.vue";
import ResetPassword from "@/components/dialogs/users/resetPassword.vue"

export default {
  name: "users",
  components: {EditUsername, EditRealName, EditEmail, NewUser, EditUserPermission, ResetPassword, userList},
  data() {
    return {
      search: "",
      userList: [],
      currentPage: 1,
      maxPage: null,
      newUser: {
        flag: false,
      },
      editUserName: {
        flag: false,
        uid: null
      },
      editUserRealName: {
        flag: false,
        uid: null
      },
      editUserPermission: {
        flag: false,
        uid: null
      },
      editUserEmail: {
        flag: false,
        uid: null
      },
      resetPassword: {
        flag: false,
        uid: null
      }
    }
  },
  methods: {
    getUserList(search = "", page = 1, pageSize = 20) {
      axios.post("/admin/api/getUserList", {
        page: page,
        pageSize: pageSize,
        search: search
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          const data = res.data.data
          const PageContent = data.PageContent
          this.userList = []
          this.maxPage = data.maxPage
          this.currentPage = data.currentPage
          for (const item of PageContent) {
            this.userList.push({
              uid: item.id,
              userName: item.userName,
              realName: item.realName,
              email: item.email,
              createdAt: item.createdAt,
              lastLoginTime: item.lastLoginTime,
              lastLoginIP: item.lastLoginIP,
              permission_id: item.permissionGroupID,
              permission_name: item.permissionGroupName,
              disable: item.disable
            })
          }
          console.log(this.userList)
        } else {
          message.showApiErrorMsg(this, res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        message.showApiErrorMsg(this, err.message)
      })
    },
    editUser(uid, action) {
      /**
       * 编辑用户
       */
      switch (action) {
        // 编辑用户名
        case "editUsername":
          this.editUserName.uid = uid
          this.editUserName.flag = true
          break
        // 编辑真实姓名
        case "editRealName":
          this.editUserRealName.uid = uid
          this.editUserRealName.flag = true
          break
        // 编辑邮箱
        case "editEmail":
          this.editUserEmail.uid = uid
          this.editUserEmail.flag = true
          break
        // 编辑权限
        case "editPermission":
          this.editUserPermission.uid = uid
          this.editUserPermission.flag = true
          break
        // 重置密码
        case "resetPassword":
          this.resetPassword.uid = uid
          this.resetPassword.flag = true
          break
      }
    },
    closeEditUserPermissionWindow() {
      /**
       * 关闭编辑用户权限组窗口
       */
      this.editUserPermission.uid = null
      this.editUserPermission.flag = false
      this.getUserList()
    },
    closeEditUserEmailWindow() {
      /**
       * 关闭编辑用户邮箱窗口
       * @type {null}
       */
      this.editUserEmail.uid = null
      this.editUserEmail.flag = false
      this.getUserList()
    },
    closeEditUserNameWindow() {
      /**
       * 关闭编辑用户名窗口
       * @type {null}
       */
      this.editUserName.uid = null
      this.editUserName.flag = false
      this.getUserList()
    },
    closeEditUserRealNameWindow() {
      /**
       * 关闭编辑用户真实姓名窗口
       * @type {null}
       */
      this.editUserRealName.uid = null
      this.editUserRealName.flag = false
      this.getUserList()
    },
    closeResetPasswordWindow() {
      /**
       * 关闭重置密码窗口
       * @type {null}
       */
      this.resetPassword.uid = null
      this.resetPassword.flag = false
    },
    closeNewUserWindow() {
      /**
       * 关闭新建用户窗口
       * @type {boolean}
       */
      this.newUser.flag = false
      this.getUserList()
    }
  },
  mounted() {
    this.getUserList()
  },
  watch: {
    currentPage(val) {
      this.getUserList(this.search, val)
    },
    search(val) {
      this.getUserList(val)
      this.currentPage = 1
    },
  }
}
</script>

<template>
  <div class="toolsBar">
    <v-btn
      id="addUser"
      color="success"
      @click="newUser.flag = true">
      新增用户
    </v-btn>
    <v-text-field
      id="searchUser"
      class="search"
      density="compact"
      label="搜索"
      variant="solo-filled"
      single-line
      hide-details
      v-model="search">
    </v-text-field>
  </div>
  <user-List :user-list="userList" @action="editUser"/>
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
    <edit-user-permission
    :uid="editUserPermission.uid"
    :flag="editUserPermission.flag"
    @close="closeEditUserPermissionWindow()"/>
    <edit-email
      :uid="editUserEmail.uid"
      :flag="editUserEmail.flag"
      @close="closeEditUserEmailWindow()" />
    <edit-real-name
      :uid="editUserRealName.uid"
      :flag="editUserRealName.flag"
      @close="closeEditUserRealNameWindow()"/>
    <edit-username
      :uid="editUserName.uid"
      :flag="editUserName.flag"
      @close="closeEditUserNameWindow()"/>
    <reset-password
      :uid="resetPassword.uid"
      :flag="resetPassword.flag"
      @close="closeResetPasswordWindow()"/>
    <new-user
      :flag="newUser.flag"
      @close="closeNewUserWindow()"/>
  </div>

</template>

<style scoped>

</style>
