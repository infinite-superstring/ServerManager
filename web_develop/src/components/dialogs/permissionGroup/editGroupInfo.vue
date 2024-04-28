<script>
import PermissionItemTable from "@/components/tables/permissionGroup/permissionItemTable.vue";
import message from "@/scripts/utils/message.js"
import permission from "@/scripts/admin/permission";
import axios from "axios";

export default {
  name: "EditGroupInfo",
  components: {PermissionItemTable},
  emits: ["close"],
  props: {
    flag: {
      type: Boolean,
      required: true
    },
    gid: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      name: null,
      new_name: null,
      status: null,
      select: []
    }
  },
  methods: {
    getPermissionGroupInfo() {
      /**
       * 获取权限组数据
       */
      permission.getGroupInfo(this, this.gid).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          const groupInfo = res.data.data
          this.name = groupInfo.name
          this.new_name = groupInfo.name
          this.status = !groupInfo.disable
          for (const item in groupInfo.Permission) {
            if (groupInfo.Permission[item] === true) {
              this.select.push(item)
            }
          }
        } else {
          message.showApiErrorMsg(this, res.data.msg, apiStatus)
        }
      })
    },
    submit() {
      if (this.new_name.length < 3 && this.new_name.length > 20) {
        message.showWarning(this, "权限组名长度应在3-20个字符")
        return
      }
      if (!this.select) {
        message.showWarning(this, "你好像啥权限都没选择呢~")
        return
      }
      permission.editGroup(
        this,
        this.gid,
        {newName: this.new_name, disable: !this.status, permissions: this.select}
      ).then(() => {
        this.close()
      })
    },
    close() {
      this.name = null
      this.new_name = null
      this.status = null
      this.select = []
      this.$emit('close')
    }
  },
  watch: {
    flag(val) {
      if (val) {
        this.getPermissionGroupInfo()
      } else {
        this.name = null
        this.new_name = null
        this.status = null
        this.select = []
      }
    }
  }
}
</script>

<template>
  <!--    修改权限组信息-->
  <v-dialog
    id="inputDialog"
    :model-value="flag"
    activator="parent"
    min-width="400px"
    width="auto"
    persistent
  >
    <v-card>
      <v-card-title>编辑权限组--{{ name }}</v-card-title>
      <v-card-text>
        <v-text-field type="text" label="权限组名" v-model="new_name"></v-text-field>
        <v-switch label="是否启用" v-model="status" color="primary"></v-switch>
        <v-card class="pa-1">
          <v-card-title>请选择该组可使用的权限</v-card-title>
          <v-card-text>
            <permission-item-table :select="select" @update="args => {select = args; console.log(select)}"/>
          </v-card-text>
        </v-card>
      </v-card-text>
      <v-card-actions>
        <v-btn color="error" @click="close()">取消</v-btn>
        <v-btn color="success" @click="submit()">确定</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>
