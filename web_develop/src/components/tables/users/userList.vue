<script>
import axios from "axios";
import user from "@/scripts/admin/users"
import message from "@/scripts/utils/message";

export default {
  name: "userList",
  emits: ['action', 'update'],
  props: {
    userList: {
      type: Array,
      required: true
    }
  },
  methods: {
    delUser(uid) {
      /**
       * 删除用户
       */
      this.$dialog.confirm("操作确认", "确定要删除这个用户吗", 'warning', '否', '是')
      .then((anwser) => {
        if (anwser) {
          axios.post("/admin/api/delUser", {id:uid}).then(res=>{
            const status = res.data.status
            if (status !== 1) {
              message.showApiErrorMsg(this, res.data.msg, status)
            } else {
              // this.getUserList("", this.maxPage)
              this.$emit('update')
            }
          }).catch(err=>{
            message.showApiErrorMsg(this, err.message)
          })
        }
      })
    },
    updateUserStatus(uid, status) {
      user.updateUserInfo(this, uid, {disable: status})
    }
  }
}
</script>

<template>
  <v-table>
    <thead>
      <tr>
        <th class="text-left">
          UID
        </th>
        <th class="text-left">
          用户名
        </th>
        <th class="text-left">
          真实姓名
        </th>
        <th class="text-left">
          邮箱
        </th>
        <th class="text-left">
          权限
        </th>
        <th class="text-left">
          启用
        </th>
        <th class="text-left">
          创建时间
        </th>
        <th class="text-left">
          上次登录时间
        </th>
        <th class="text-left">
          操作
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="item in userList"
        :key="item.name"
      >
        <td>{{ item.uid }}</td>
        <td>{{ item.userName }}<v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="$emit('action', item.uid, 'editUsername')"></v-icon></td>
        <td>{{ item.realName ? item.realName : "未设置" }}<v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="$emit('action', item.uid, 'editRealName')"></v-icon></td>
        <td>{{item.email ? item.email : "未设置"}}<v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="$emit('action', item.uid, 'editEmail')"></v-icon></td>
        <td>{{ item.permission_name ? item.permission_name : "无权限" }}<v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="$emit('action', item.uid, 'editPermission')"></v-icon></td>
        <td>
          <input type='checkbox' :checked="!item.disable" @change="updateUserStatus(item.uid, !$event.target.checked)">
<!--          {{ item.disable ? "" : "<input type='checkbox' checked>" }}<v-icon icon="mdi:mdi-square-edit-outline" size="x-small" @click="$emit('action', item.uid, 'editStatus')"></v-icon>-->
        </td>
        <td>{{ item.createdAt ? item.createdAt : "未知" }}</td>
        <td>{{ item.lastLoginTime ? `${item.lastLoginTime}（ip:${item.lastLoginIP}）` : "未登录" }} </td>
        <td>
          <v-btn size="small" @click="$emit('action', item.uid, 'resetPassword')">重置密码</v-btn>
          <v-btn size="small" color="error" @click="delUser(item.uid)">删除</v-btn>
        </td>
      </tr>
    </tbody>
  </v-table>
</template>

<style scoped>

</style>
