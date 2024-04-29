<script>
import group_list from "@/components/tables/permissionGroup/groupList"
import axios from "axios";
import NewGroup from "@/components/dialogs/permissionGroup/newGroup";
import EditGroupInfo from "@/components/dialogs/permissionGroup/editGroupInfo.vue";
import EditGroupName from "@/components/dialogs/permissionGroup/editGroupName.vue";

export default {
  name: "PermissionGroup",
  components: {EditGroupName, EditGroupInfo, NewGroup, group_list},
  data: () => {
    return {
      currentPage: 1,
      maxPage: null,
      search: "",
      permissionGroups: [],
      flag: {
        newGroup: false
      },
      editGroupPermission: {
        flag: false,
        gid: null
      },
      editGroupName: {
        flag: false,
        gid: null,
      }
    }
  },
  methods: {
    showApiErrorMsg(message, status = null) {
      /**
       * 显示API错误信息
       */
      this.$notify.create({
        text: `API错误：${message} ${status ? '(status:' + status + ')' : ''}`,
        level: 'error',
        location: 'bottom right',
        notifyOptions: {
          "close-delay": 3000
        }
      })
    },
    // 获取用户列表
    getPermissionGroupList(search = "", page = 1, pageSize = 20) {
      /**
       * 获取用户列表
       */
      axios.post("/admin/api/getPermissionGroups", {
        page: page,
        pageSize: pageSize,
        search: search
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          const data = res.data.data
          const PageContent = data.PageContent
          this.permissionGroups = []
          this.maxPage = data.maxPage
          this.currentPage = data.currentPage
          for (const item of PageContent) {
            console.log(item)
            this.permissionGroups.push({
              id: item.id,
              name: item.name,
              creator: item.creator,
              createdAt: item.createdAt,
              disable: item.disable,
            })
          }
          console.log(this.permissionGroups)
        } else {
          this.showApiErrorMsg(res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
    // 打开输入框
    openInputDialog(id, title, label, defaultValue, callback = null, type = "text") {
      if (!this.inputDialog.flag) {
        this.inputDialog.flag = true
        this.inputDialog.uid = id
        this.inputDialog.title = title
        this.inputDialog.label = label
        this.inputDialog.input = defaultValue
        this.inputDialog.type = type
        this.inputDialog.callback = callback
      } else {
        console.warn("当前已有开启中的输入框")
      }
    },
    // 动作
    action(action, groupId = null) {
      /**
       * 操作
       */
      switch (action) {
        case "newPermissionGroup":
          /**
           * 新建组
           */
          this.getPermissionList().then(res => {
            const apiStatus = res.data.status
            if (apiStatus === 1) {
              this.restore_init("newPermissionGroupDialog")
              this.newPermissionGroupDialog.permissionList = res.data.data
              this.newPermissionGroupDialog.flag = true
            } else {
              this.showApiErrorMsg(res.data.msg, apiStatus)
            }
          })
          break
        case "rename":
          /**
           * 重命名
           */
          this.editGroupName.gid = groupId
          this.editGroupName.flag = true
          break
        case "update_status":
          /**
           * 更新状态
           */
          this.getPermissionGroupInfo(groupId).then(res => {
            const apiStatus = res.data.status
            if (apiStatus === 1) {
              this.updateGroupStatusDialog.value = !res.data.data.disable
              this.updateGroupStatusDialog.gid = groupId
              this.updateGroupStatusDialog.flag = true
            } else {
              this.showApiErrorMsg(res.data.msg, apiStatus)
            }
          })
          break
        case "edit":
          /**
           * 编辑权限组
           */
          this.editGroupPermission.gid = groupId
          console.log(this.editGroupPermission.gid)
          this.editGroupPermission.flag = true
          break
        case "del":
          /**
           * 删除权限组
           */
          this.$dialog.confirm("操作确认", "确定要删除这个组吗", 'warning', '否', '是')
            .then((anwser) => {
              if (anwser) {
                axios.post('/admin/api/delPermissionGroup', {id: groupId}).then(res => {
                  const apiStatus = res.data.status
                  if (apiStatus === 1) {
                    this.getPermissionGroupList(this.search, this.currentPage)
                  } else {
                    this.showApiErrorMsg(res.data.msg, apiStatus)
                  }
                }).catch(err => {
                  this.showApiErrorMsg(err.message)
                })
              }
            })
          break
      }
    },
    // 恢复初始值
    restore_init(dialogName) {
      switch (dialogName) {
        case "updateGroupStatusDialog":
          this.updateGroupStatusDialog.flag = false
          this.updateGroupStatusDialog.value = null
          break
        case "editPermissionGroupDialog":
          this.editPermissionGroupDialog.flag = false
          this.editPermissionGroupDialog.gid = null
          this.editPermissionGroupDialog.name = null
          this.editPermissionGroupDialog.status = true
          this.editPermissionGroupDialog.permissionList = []
          this.editPermissionGroupDialog.selected = []
          break
      }
    },
    // 重命名组
    rename(groupId, newName) {
      axios.post("/admin/api/setPermissionGroup", {
        id: groupId,
        data: {
          newName: newName
        }
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.getPermissionGroupList(this.search, this.currentPage)
        } else {
          this.showApiErrorMsg(res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
    // 更新权限组状态
    updateStatus(groupId, value) {
      axios.post("/admin/api/setPermissionGroup", {
        id: groupId,
        data: {
          disable: !value
        }
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.getPermissionGroupList(this.search, this.currentPage)
          this.restore_init('updateGroupStatusDialog')
        } else {
          this.showApiErrorMsg(res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
    closeEditGroupPermission() {
      this.editGroupPermission.gid = null
      this.editGroupPermission.flag = false
      this.getPermissionGroupList(this.search, this.currentPage)
    },
    closeEditGroupName() {
      this.editGroupName.gid = null
      this.editGroupName.flag = false
      this.getPermissionGroupList(this.search, this.currentPage)
    }
  },
  created() {
    this.getPermissionGroupList()
  },
  watch: {
    currentPage(val) {
      this.getPermissionGroupList(this.search ,val)
    },
    "search"(val) {
      console.log(val)
      this.getPermissionGroupList(val)
      this.currentPage = 1
    }
  },
}
</script>

<template>
  <div class="toolsBar">
    <v-btn
      id="addUser"
      color="success"
      @click="flag.newGroup = true"
    >
      新增权限组
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
  <group_list
    @action="action"
    @updateData="getPermissionGroupList(search, currentPage)"
    :permission-group-list="permissionGroups"
  />
  <div class="dialogs">
    <new-group
      :open-window="flag.newGroup"
      @success="getPermissionGroupList();flag.newGroup = false"
      @exit="flag.newGroup = false"
    />
    <edit-group-info
      :gid="editGroupPermission.gid"
      :flag="editGroupPermission.flag"
      @close="closeEditGroupPermission()"
    />
    <edit-group-name
      :gid="editGroupName.gid"
      :flag="editGroupName.flag"
      @close="closeEditGroupName()"
    />
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
</template>

<style scoped>

</style>
