<script>
import axios from "axios";

export default {
  name: "userInfoCard",
  data() {
    return {
      username: "UserName",
      group: "未知",
      avatar: "/userInfo/api/getAvatar"
    }
  },
  created() {
    axios.get("/userInfo/api/getInfo").then(res=>{
      const data = res.data.data
      this.username = data.userName
      this.group = data.group
    }).catch(err=>{
      console.log(err)
    })
  }
}
</script>

<template>
  <v-list-item :to="{name: 'userInfo'}" :title="username" :subtitle="group" :prepend-avatar="avatar"></v-list-item>
</template>

<style scoped>

</style>
