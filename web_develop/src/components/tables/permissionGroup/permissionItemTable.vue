<script>
import axios from "axios";

export default {
  name: "permissionItemTable",
  props: {
    select: {
      type: Array,
      required: false
    }
  },
  emits: ['update'],
  data() {
    return {
      permissionItemList: null,
      select_copy: null
    }
  },
  mounted() {
    this.getPermissionList()
    this.select_copy = this.select
  },
  methods: {
    getPermissionList() {
      /**
       * 获取权限列表
       */
      axios.get("/admin/api/getPermissionList").then(res=>{
        this.permissionItemList = res.data.data
      }).catch(err => {
        console.error(err)
        this.showApiErrorMsg(err.message)
      })
    },
  },
  watch: {
    select_copy(val) {
      this.$emit('update', val)
    }
  }
}
</script>

<template>
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
      v-for="(value, key) in permissionItemList"
      :key="key"
    >
      <td><input type="checkbox" :value="key" v-model="select_copy"></td>
      <td>{{ key }}</td>
      <td>{{ value }}</td>
    </tr>
    </tbody>
  </v-table>
</template>

<style scoped>

</style>
