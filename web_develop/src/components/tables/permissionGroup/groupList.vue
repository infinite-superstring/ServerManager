<script>
import axios from "axios";
import message from "@/scripts/utils/message.js"

/**
 * 权限组列表
 */

export default {
  name: "List",
  emits: [
    /**
     * 动作
     */
    "action",
    /**
     * 列表更新
     */
    "updateData"
  ],
  props: {
    permissionGroupList: {
      /**
       * 权限组列表数据
       */
      type: Array,
      required: true
    }
  },
  methods: {
    delGroup(groupId) {
      /**
       * 删除权限组
       */
      this.$dialog.confirm("操作确认", "确定要删除这个组吗", 'warning', '否', '是')
        .then((anwser) => {
          if (anwser) {
            axios.post('/admin/api/delPermissionGroup', {id: groupId}).then(res => {
              const apiStatus = res.data.status
              if (apiStatus === 1) {
                this.$emit("updateData")
              } else {
                message.showApiErrorMsg(this, res.data.msg, apiStatus)
              }
            }).catch(err => {
              message.showApiErrorMsg(this, err.message)
            })
          }
        })
    }
  }
}
</script>

<template>
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
      v-for="item in permissionGroupList"
      :key="item.id"
    >
      <td>{{ item.id }}</td>
      <td>{{ item.name }}
        <v-icon
          icon="mdi:mdi-square-edit-outline"
          size="x-small"
          @click="$emit('action','rename', item.id)"/>
      </td>
      <td>{{ item.creator ? item.creator : "未知" }}</td>
      <td>{{ item.createdAt ? item.createdAt : "未知" }}</td>
      <td>{{ item.disable ? "已禁用" : "已启用" }}
        <v-icon
          icon="mdi:mdi-square-edit-outline"
          size="x-small"
          @click="$emit('action','update_status', item.id)"/>
      </td>
      <td>
        <v-btn
          size="small"
          @click="$emit('action','edit', item.id)">
          编辑
        </v-btn>
        <v-btn
          color="error"
          size="small"
          @click="delGroup(item.id)">
          删除
        </v-btn>
      </td>
    </tr>
    </tbody>
  </v-table>
</template>

<style scoped>

</style>
