<script>
export default {
  name: "Base_Settings",
  props: {
    setting_data: {
      type: Object,
      required: true
    }
  }
}
</script>

<template>
  <p class="text-h5 setting_subtitle">基础设置</p>
  <div>
    <div class="text-caption">
      服务器Token
    </div>
<!--    TODO 样式问题 继承问题-->
    <v-text-field type="text" v-model="setting_data.base.server_token" disabled density="compact">
      <template v-slot:append>
        <v-btn icon>
          <v-icon icon="mdi:mdi-refresh"/>
        </v-btn>
        <v-btn icon>
          <v-icon icon="mdi:mdi-clipboard-text-outline"/>
        </v-btn>
      </template>
    </v-text-field>

  </div>
  <div>
    <div class="text-caption">
      数据存储时间（天）
    </div>
    <v-text-field type="number" v-model="setting_data.base.data_storage_time"></v-text-field>
  </div>
  <div>
    <div>
      <div class="text-caption">
        Session到期时间(分)
      </div>
      <v-text-field type="number" v-model="setting_data.base.session_expiry"></v-text-field>
    </div>
    <v-divider></v-divider>
    <p class="text-h5 setting_subtitle">日志设置</p>
    <div>
      <div class="text-caption">
        将debug输出到文件
      </div>
      <v-checkbox></v-checkbox>
    </div>
    <div>
      <div class="text-caption">
        日志保留时长(天)
      </div>
      <v-text-field type="number"></v-text-field>
    </div>
    <v-divider></v-divider>
    <p class="text-h5 setting_subtitle">审计设置</p>
    <div>
      <div class="text-caption">
        审计日志保留时长(天)
      </div>
      <v-text-field type="number"></v-text-field>
    </div>
  </div>
</template>

<style scoped>

</style>
