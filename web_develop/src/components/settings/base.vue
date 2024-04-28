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
  <p class="text-h5 setting_subtitle">设备设置</p>
  <div>
    <div class="text-caption">
      采集卡设备ID/路径
    </div>
    <v-text-field type="text" v-model="setting_data.base.camera"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      HID串口设备
    </div>
    <v-text-field type="text" v-model="setting_data.base.HID_Serial"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      Session到期时间(分)
    </div>
    <v-text-field type="number" v-model="setting_data.base.sessionExpiry"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      USB设备路径/挂载路径
    </div>
    <v-row>
      <v-col
      cols="12"
      md="6">
        <v-text-field type="text" v-model="setting_data.base.USB_Device"></v-text-field>
      </v-col>
      <v-col
      cols="12"
      md="6">
        <v-text-field type="text" v-model="setting_data.base.USB_MountDirectory"></v-text-field>
      </v-col>
    </v-row>
  </div>
  <div>
    <div class="text-caption">
      设备被控制时启动视频录制
    </div>
    <v-checkbox v-model="setting_data.base.record"></v-checkbox>
  </div>
  <div>
    <div class="text-caption">
      最大保留录制数
    </div>
    <v-text-field type="number" v-model="setting_data.record.maxFile"></v-text-field>
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
</template>

<style scoped>

</style>
