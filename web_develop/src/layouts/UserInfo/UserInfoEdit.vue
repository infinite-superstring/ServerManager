<script>
import ChangePassword from "@/components/UserInfo/changePassword.vue";
import EditUserInfo from "@/components/UserInfo/editUserInfo.vue";

export default {
  name: "UserInfoEdit",
  components: {EditUserInfo, ChangePassword}
}
</script>

<template>
  <v-row>
    <v-col>
      <EditUserInfo></EditUserInfo>
    </v-col>
    <v-col cols="5">
      <change-password></change-password>
    </v-col>
  </v-row>


</template>

<style scoped>
  .left {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    margin-right: 25px;
  }

</style>
