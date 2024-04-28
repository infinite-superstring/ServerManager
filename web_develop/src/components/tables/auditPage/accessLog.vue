<script>
import axios from "axios";
import message from "@/scripts/utils/message.js"

export default {
  name: "accessLog_table",
  data:()=>{
    return {
      currentPage: 1,
      maxPage: null,
      table: [],
    }
  },
  methods: {
    // 获取用户列表
    getTable(page=1, pageSize=20) {
      axios.post("/admin/api/auditAndLogger/accessLog",{
        page: page,
        pageSize: pageSize,
      }).then(res=>{
        const apiStatus = res.data.status
          if (apiStatus === 1) {
            const data = res.data.data
            const PageContent = data.PageContent
            this.table = []
            this.maxPage = data.maxPage
            this.currentPage = data.currentPage
            for (const item of PageContent) {
              console.log(item)
              this.table.push({
                id: item.id,
                user: item.user,
                time: item.time,
                ip: item.ip,
                module: item.module,
              })
            }
          } else {
            message.showApiErrorMsg(this, res.data.msg, apiStatus)
          }
      }).catch(err=>{
        console.error(err)
        message.showApiErrorMsg(this, err.message)
      })
    },
  },
  created() {
    this.getTable()
  },
  watch: {
    currentPage(val) {
      this.getTable(val)
    },
  },
}
</script>

<template>
  <v-table density="compact">
    <thead>
    <tr>
      <th class="text-left">
        用户
      </th>
      <th class="text-left">
        时间
      </th>
      <th class="text-left">
        ip
      </th>
      <th class="text-left">
        模块
      </th>
    </tr>
    </thead>
    <tbody>
    <tr
      v-for="item in table"
      :key="item.id"
    >
      <td>{{ item.user }}</td>
      <td>{{ item.time }}</td>
      <td>{{ item.ip }}</td>
      <td>{{ item.module }}</td>
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
