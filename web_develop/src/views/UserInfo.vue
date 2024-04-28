<script>

import UserInfoEdit from "@/layouts/UserInfo/UserInfoEdit.vue";

export default {
  name: "UserInfo",
  components: {UserInfoEdit},
}
</script>

<template>
  <v-card title="个人信息" class="pageMain-card">
    <v-card-text>
      <user-info-edit></user-info-edit>
    </v-card-text>
  </v-card>
</template>

<style scoped>
</style>
