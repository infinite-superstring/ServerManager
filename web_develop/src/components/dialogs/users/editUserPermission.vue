<script>
import axios from "axios";
import user from "@/scripts/admin/users"
import message from "@/scripts/utils/message";
import PermissionGroupTable from "@/components/tables/users/permissionGroupTable.vue";

export default {
  name: "editUserPermission",
  components: {PermissionGroupTable},
  emits: ['close'],
  props: {
    uid: {
      type: Number,
      required: true
    },
    flag: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      search: null,
      select: null,
    }
  },
  methods: {

    submit() {
      /**
       * 提交
       */
      user.updateUserInfo(this, this.uid, {permission: this.select}).then(()=>{
        this.close()
      })
    },
    close() {
      /**
       * 触发关闭事件
       */
      this.$emit('close')
    }
  },
  watch: {
    flag(val) {
      if (val) {
        user.getUserInfo(this, this.uid).then(res => {
          const apiStatus = res.data.status
          if (apiStatus != 1) {
            message.showApiErrorMsg(this, res.data.msg)
            return
          }
          this.select = res.data.data.permissionId
        })
      } else {
        this.search = null
      }
    },
  }
}
</script>

<template>
  <v-dialog
    :model-value="flag"
    activator="parent"
    min-width="400px"
    width="auto"
    persistent
  >
    <v-card>
      <v-card-title>修改用户权限</v-card-title>
      <v-card-text>
        <permission-group-table :select="select" @update="(val)=>{select = val;console.log(val)}"/>
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
