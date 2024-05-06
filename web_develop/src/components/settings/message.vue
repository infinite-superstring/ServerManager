<script>
export default {
  name: "message",
  props: {
    setting_data: {
      type: Object,
      required: true
    }
  }
}
</script>

<template>
  <p class="text-h5 setting_subtitle">消息设置</p>
  <!--  TODO 发件方式-->
  <div class="msg_email">
     <!--  TODO 邮件发件方式-->
    <div>
      <div class="text-caption">
        邮件服务器地址
      </div>
      <v-text-field type="text" v-model="setting_data.message.email_host"></v-text-field>
    </div>
    <div>
      <div class="text-caption">
        邮件服务器端口
      </div>
      <v-text-field type="number" v-model="setting_data.message.email_port"></v-text-field>
    </div>
    <div>
      <div class="text-caption">
        邮件服务用户名
      </div>
      <v-text-field type="text" v-model="setting_data.message.email_username"></v-text-field>
    </div>
    <div>
      <div class="text-caption">
        邮件服务密码
      </div>
      <v-text-field type="password" v-model="setting_data.message.email_password"></v-text-field>
    </div>
    <!--  TODO SSL设置 -->
    <div>
      <div class="text-caption">
        邮件发件地址
      </div>
      <v-text-field type="text" v-model="setting_data.message.email_from_address"></v-text-field>
    </div>
    <div>
      <div class="text-caption">
        邮件发件人
      </div>
      <v-text-field type="text" v-model="setting_data.message.email_from_name"></v-text-field>
    </div>
  </div>
</template>

<style scoped>

</style>
