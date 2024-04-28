<script>
import axios from "axios";
import message from "@/scripts/utils/message.js"

export default {
  name: "NewGroup",
  emits: ["success", "exit"],
  props: {
    openWindow: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      newGroupName: "",
      newGroupStatus: "",
      permissionList: [],
      permissionSelect: [],
    }
  },
  // created() {
  //   this.getPermissionList()
  // },
  watch: {
    openWindow(val) {
      if (val) {
        this.getPermissionList()
      }
    }
  },
  methods: {
    getPermissionList() {
      /**
       * 获取权限列表
       */
      axios.get("/admin/api/getPermissionList").then(res => {
        if (res.data.status === 1) {
          this.permissionList = res.data.data
        } else {
          message.showApiErrorMsg(this, res.data.msg, res.data.status)
        }
      }).catch(err => {
        console.error(err)
        message.showApiErrorMsg(this, err.messages)
      })
    },
    reset() {
      /**
       * 重置
       * @type {string}
       */
      this.newGroupName = ""
      this.newGroupStatus = ""
      // this.permissionList = []
      this.permissionSelect = []
    },
    submitNewGroup() {
      /**
       * 提交新增组
       */
      if (this.newGroupName.length < 3 && this.newGroupName.length > 20) {
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
      if (this.permissionSelect.length < 1) {
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
      for (const permissionKey in this.permissionList) {
        permission[permissionKey] = this.permissionSelect.includes(permissionKey)
      }
      console.log(permission)
      axios.post("/admin/api/addPermissionGroup", {
        name: this.newGroupName,
        disable: !this.newGroupStatus,
        permissions: permission
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.reset()
          this.$emit('success')
        } else {
          this.$notify.create({
            text: `${res.data.msg} (${apiStatus})`,
            level: 'error',
            location: 'bottom right',
            notifyOptions: {
              "close-delay": 3000
            }
          })
        }
      }).catch(err => {
        console.error(err)
        this.$notify.create({
          text: `API错误：${err.message}`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
      })
    },
  }
}
</script>

<template>
  <v-dialog
    id="inputDialog"
    activator="parent"
    min-width="400px"
    width="auto"
    persistent
    :modelValue="openWindow"
  >
    <v-card>
      <v-card-title>新建权限组</v-card-title>
      <v-card-text>
        <v-text-field type="text" label="请输入要创建的权限组名" v-model="newGroupName"></v-text-field>
        <v-switch label="是否启用" v-model="newGroupStatus" color="primary"></v-switch>
        <v-card class="pa-1">
          <v-card-title>选择该组可使用的权限</v-card-title>
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
                v-for="(value, key) in permissionList"
                :key="key"
              >
                <td><input type="checkbox" :value="key" v-model="permissionSelect"></td>
                <td>{{ key }}</td>
                <td>{{ value }}</td>
              </tr>
              </tbody>
            </v-table>
          </v-card-text>
          <v-card-actions>
            <v-btn color="warning" :disabled="permissionSelect.length < 1" @click="permissionSelect = []">
              清空已选择
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-card-text>
      <v-card-actions>
        <v-btn color="error" @click="reset(); $emit('exit')">取消</v-btn>
        <v-btn color="success" @click="submitNewGroup()">确定</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>
