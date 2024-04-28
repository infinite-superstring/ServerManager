<script>
import axios from "axios";
import message from "@/scripts/utils/message";

export default {
  name: "permissionGroupTable",
  emits: ['update'],
  props: {
    select: {
      type: Number,
      required: false,
      default: null
    }
  },
  data() {
    return {
      select_copy: null,
      search: "",
      list: [],
      currentPage: 1,
      maxPage: 1
    }
  },
  mounted() {
    this.loadPermissionGroups()
    this.select_copy = this.select
  },
  methods: {
    loadPermissionGroups(search = "", page = 1, pageSize = 20) {
      /**
       * 加载权限组列表
       */
      axios.post("/admin/api/getPermissionGroups", {search: search, page: page, pageSize: pageSize}).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.maxPage = res.data.data.maxPage
          this.currentPage = res.data.data.currentPage
          this.list = []
          for (let i = 0; i < res.data.data.PageContent.length; i++) {
            const item = res.data.data.PageContent[i]
            this.list.push({
              id: item.id,
              name: item.name
            })
          }
        } else {
          message.showApiErrorMsg(this, res.data.msg, apiStatus)
        }
      }).catch(err => {
        console.error(err)
        message.showApiErrorMsg(this, err.message)
      })
    },
  },
  watch: {
    search(val) {
      console.log(val)
      this.loadPermissionGroups(val)
    }
  }
}
</script>

<template>
  <div class="toolsBar">
    <v-text-field
      id="searchUser"
      class="search"
      density="compact"
      label="搜索权限组名"
      variant="solo-filled"
      single-line
      hide-details
      v-model="search">
    </v-text-field>
  </div>
  <v-table>
    <thead>
    <tr>
      <th class="text-left">
        选择
      </th>
      <th class="text-left">
        权限ID
      </th>
      <th class="text-left">
        权限组名
      </th>
    </tr>
    </thead>
    <tbody>
      <tr
        v-for="item in list"
        :key="item.id"
      >
        <td>
          <input
            type="radio"
            name="editUserPermission"
            :value="item.id"
            @input="$emit('update', $event.target.value)"
            v-model="select_copy">
        </td>
        <td>{{ item.id }}</td>
        <td>{{ item.name }}</td>
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
</template>

<style scoped>

</style>
