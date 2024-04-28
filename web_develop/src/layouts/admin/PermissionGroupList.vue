<script>
import axios from "axios";

export default {
  name: "GroupList",
  data: () => {
    return {
      currentPage: 1,
      maxPage: null,
      search: "",
      permissionGroups: [],
      newPermissionGroupDialog: {
        flag: false,
        permissionList: {},
        newGroupName: null,
        newGroupStatus: true,
        selected: []
      },
      editPermissionGroupDialog: {
        flag: false,
        gid: null,
        name: null,
        status: true,
        permissionList: {},
        selected: []
      },
      updateGroupStatusDialog: {
        flag: false,
        gid: null,
        value: null
      },
      inputDialog: {
        flag: false,
        input: null,
        uid: null,
        title: null,
        label: null,
        type: null,
        callback: null
      },
    }
  },
  methods: {
    // 显示APi错误
    showApiErrorMsg(message, status = null) {
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
    // 获取权限列表
    getPermissionList() {
      return axios.get("/admin/api/getPermissionList").catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
    // 获取权限组信息
    getPermissionGroupInfo(groupId) {
      return axios.post("/admin/api/getPermissionGroupInfo", {id: groupId}).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
    // 动作
    action(action, groupId = null) {
      switch (action) {
        case "newPermissionGroup":
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
          this.getPermissionGroupInfo(groupId).then(res => {
            const apiStatus = res.data.status
            if (apiStatus === 1) {
              this.openInputDialog(groupId, "更改权限组组名", "请输入新组名", res.data.data.name, this.rename)
            } else {
              this.showApiErrorMsg(res.data.msg, apiStatus)
            }
          })
          break
        case "update_status":
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
          this.getPermissionGroupInfo(groupId).then(res => {
            const apiStatus = res.data.status
            if (apiStatus === 1) {
              this.restore_init("editPermissionGroupDialog")
              const groupInfo = res.data.data
              this.editPermissionGroupDialog.gid = groupId
              this.editPermissionGroupDialog.name = groupInfo.name
              this.editPermissionGroupDialog.status = !groupInfo.disable
              for (const item in groupInfo.Permission) {
                if (groupInfo.Permission[item] === true) {
                  this.editPermissionGroupDialog.selected.push(item)
                }
              }
              this.getPermissionList().then(res => {
                const apiStatus = res.data.status
                if (apiStatus === 1) {
                  this.editPermissionGroupDialog.permissionList = res.data.data
                  this.editPermissionGroupDialog.flag = true
                  console.log(this.editPermissionGroupDialog)
                } else {
                  this.showApiErrorMsg(res.data.msg, apiStatus)
                  this.restore_init("editPermissionGroupDialog")
                }
              })
            } else {
              this.showApiErrorMsg(res.data.msg, apiStatus)
            }
          })
          break
        case "del":
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
    // 新建权限组
    newPermissionGroup() {
      if (this.newPermissionGroupDialog.newGroupName.length < 3 && this.newPermissionGroupDialog.newGroupName.length > 20) {
        this.$notify.create({
          text: `权限组名长度应在3-20个字符`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
        return
      }
      if (this.newPermissionGroupDialog.selected === []) {
        this.$notify.create({
          text: `你好像啥权限都没选择呢~`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
        return
      }
      let permission = {}
      for (const permissionKey in this.newPermissionGroupDialog.permissionList) {
        permission[permissionKey] = this.newPermissionGroupDialog.selected.includes(permissionKey)
      }
      console.log(permission)
      axios.post("/admin/api/addPermissionGroup", {
        name: this.newPermissionGroupDialog.newGroupName,
        disable: !this.newPermissionGroupDialog.newGroupStatus,
        permissions: permission
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.restore_init("newPermissionGroupDialog")
          this.getPermissionGroupList()
        } else {
          this.showApiErrorMsg(res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
    // 恢复初始值
    restore_init(dialogName) {
      switch (dialogName) {
        case "newPermissionGroupDialog":
          this.newPermissionGroupDialog.flag = false
          this.newPermissionGroupDialog.permissionList = []
          this.newPermissionGroupDialog.selected = []
          this.newPermissionGroupDialog.newGroupName = ""
          this.newPermissionGroupDialog.newGroupStatus = true
          break
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
    //编辑权限组
    editPermissionGroup() {
      if (this.editPermissionGroupDialog.name.length < 3 && this.editPermissionGroupDialog.name.length > 20) {
        this.$notify.create({
          text: `权限组名长度应在3-20个字符`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
        return
      }
      if (this.editPermissionGroupDialog.selected === []) {
        this.$notify.create({
          text: `你好像啥权限都没选择呢~`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
        return
      }
      let permission = {}
      console.log(this.editPermissionGroupDialog.permissionList)
      for (const permissionKey in this.editPermissionGroupDialog.permissionList) {
        permission[permissionKey] = this.editPermissionGroupDialog.selected.includes(permissionKey)
        console.log(permissionKey, this.editPermissionGroupDialog.selected.includes(permissionKey))
      }
      axios.post("/admin/api/setPermissionGroup", {
        id: this.editPermissionGroupDialog.gid,
        data: {
          newName: this.editPermissionGroupDialog.name,
          disable: !this.editPermissionGroupDialog.status,
          permissions: permission
        }
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.restore_init("editPermissionGroupDialog")
          this.getPermissionGroupList()
        } else {
          this.showApiErrorMsg(res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    }
  },
  created() {
    this.getPermissionGroupList()
  },
  watch: {
    currentPage(val) {
      this.getPermissionGroupList(this.search, val)
    },
    search(val) {
      this.getPermissionGroupList(val)
      this.currentPage = 1
    }
  },
}
</script>

<template>
  <div class="toolsBar">
    <v-btn id="addUser" color="success" @click="action('newPermissionGroup')">新增权限组</v-btn>
    <v-text-field id="searchUser" class="search" density="compact" label="搜索" variant="solo-filled" single-line
                  hide-details v-model="search"></v-text-field>
  </div>
  <v-table>
    <thead>
    <tr>
      <th class="text-left">
        ID
      </th>
      <th class="text-left">
        权限组名
      </th>
      <th class="text-left">
        创建者
      </th>
      <th class="text-left">
        创建时间
      </th>
      <th class="text-left">
        状态
      </th>
      <th class="text-left">
        操作
      </th>
    </tr>
    </thead>
    <tbody>
    <tr
      v-for="item in permissionGroups"
      :key="item.id"
    >
      <td>{{ item.id }}</td>
      <td>{{ item.name }}
        <v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="action('rename', item.id)"></v-icon>
      </td>
      <td>{{ item.creator ? item.creator : "未知" }}</td>
      <td>{{ item.createdAt ? item.createdAt : "未知" }}</td>
      <td>{{ item.disable ? "已禁用" : "已启用" }}
        <v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="action('update_status', item.id)"></v-icon>
      </td>
      <td>
        <v-btn size="small" @click="action('edit', item.id)">编辑</v-btn>
        <v-btn color="error" size="small" @click="action('del', item.id)">删除</v-btn>
      </td>
    </tr>
    </tbody>
  </v-table>
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
          <v-btn color="success"
                 @click="inputDialog.callback(inputDialog.uid, inputDialog.input);inputDialog.flag = false;inputDialog.input = null">
            确定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!--    新建权限组-->
    <v-dialog
      id="inputDialog"
      v-model="newPermissionGroupDialog.flag"
      activator="parent"
      min-width="400px"
      width="auto"
      persistent
    >
      <v-card>
        <v-card-title>新建权限组</v-card-title>
        <v-card-text>
          <v-text-field type="text" label="请输入要创建的权限组名"
                        v-model="newPermissionGroupDialog.newGroupName"></v-text-field>
          <v-switch label="是否启用" v-model="newPermissionGroupDialog.newGroupStatus" color="primary"></v-switch>
          <v-card class="pa-1">
            <v-card-title>选择该组可使用的权限</v-card-title>
            <v-card-text>
              <v-table density="compact">
                <thead>
                <tr>
                  <th class="text-left">
                    选择
                  </th>
                  <th class="text-left"> fSj权限原名
                  </th>
                  <th class="text-left">
                    权限译名
                  </th>
                </tr>
                </thead>
                <tbody>
                <tr
                  v-for="(value, key) in newPermissionGroupDialog.permissionList"
                  :key="key"
                >
                  <td><input type="checkbox" :value="key" v-model="newPermissionGroupDialog.selected"></td>
                  <td>{{ key }}</td>
                  <td>{{ value }}</td>
                </tr>
                </tbody>
              </v-table>
            </v-card-text>
            <v-card-actions>
              <v-btn color="warning" :disabled="newPermissionGroupDialog.selected.length < 1"
                     @click="newPermissionGroupDialog.selected = []">清空已选择
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" @click="restore_init('newPermissionGroupDialog')">取消</v-btn>
          <v-btn color="success" @click="newPermissionGroup()">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!--    修改权限组状态-->
    <v-dialog
      id="inputDialog"
      v-model="updateGroupStatusDialog.flag"
      activator="parent"
      min-width="400px"
      width="auto"
      persistent
    >
      <v-card>
        <v-card-title>修改权限组状态</v-card-title>
        <v-card-text>
          <v-switch label="是否启用" v-model="updateGroupStatusDialog.value" color="primary"></v-switch>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" @click="restore_init('updateGroupStatusDialog')">取消</v-btn>
          <v-btn color="success" @click="updateStatus(updateGroupStatusDialog.gid,updateGroupStatusDialog.value)">确定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!--    修改权限组信息-->
    <v-dialog
      id="inputDialog"
      v-model="editPermissionGroupDialog.flag"
      activator="parent"
      min-width="400px"
      width="auto"
      persistent
    >
      <v-card>
        <v-card-title>编辑权限组--{{ editPermissionGroupDialog.name }}</v-card-title>
        <v-card-text>
          <v-text-field type="text" label="权限组名" v-model="editPermissionGroupDialog.name"></v-text-field>
          <v-switch label="是否启用" v-model="editPermissionGroupDialog.status" color="primary"></v-switch>
          <v-card class="pa-1">
            <v-card-title>请选择该组可使用的权限</v-card-title>
            <v-card-text>
              <v-table density="compact">
                <thead>
                <tr>
                  <th class="text-left">
                    选择
                  </th>
                  <th class="text-left">
                    权限原名
                  </th>
                  <th class="text-left">
                    权限译名
                  </th>
                </tr>
                </thead>
                <tbody>
                <tr
                  v-for="(value, key) in editPermissionGroupDialog.permissionList"
                  :key="key"
                >
                  <td><input type="checkbox" :value="key" v-model="editPermissionGroupDialog.selected"></td>
                  <td>{{ key }}</td>
                  <td>{{ value }}</td>
                </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" @click="restore_init('editPermissionGroupDialog')">取消</v-btn>
          <v-btn color="success" @click="editPermissionGroup()">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>

</style>
