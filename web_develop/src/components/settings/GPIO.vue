<script>

export default {
  name: "GPIO_Settings",
  props: {
    setting_data: {
      type: Object,
      required: true
    }
  }
}
</script>

<template>

  <v-alert title="警告" text="本页面内容仅供开发人员调试时使用，如不理解其中内容请勿随意更改" color="error"></v-alert>

  <div>
    <div class="text-caption">
      GPIO系统选择
    </div>
    <v-select
      :items="['Linux GPIO Subsystem','OrangePi GPIO']"
      v-model="setting_data.gpio.mode"
    ></v-select>
  </div>

  <p class="text-h5 setting_subtitle">按钮</p>
  <div>
    <div class="text-caption">
      电源
    </div>
    <v-text-field type="number" v-model="setting_data.gpio.Power_Btn"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      重启
    </div>
    <v-text-field type="number" v-model="setting_data.gpio.Restart_Btn"></v-text-field>
  </div>
  <v-divider></v-divider>
  <p class="text-h5 setting_subtitle">LED</p>
  <div>
    <div class="text-caption">
      电源
    </div>
    <v-text-field type="number" v-model="setting_data.gpio.Power_LED"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      硬盘
    </div>
    <v-text-field type="number" v-model="setting_data.gpio.Restart_Btn"></v-text-field>
  </div>
  <v-divider></v-divider>
  <p class="text-h5 setting_subtitle">其他设备</p>
  <div>
    <div class="text-caption">
      USB使能
    </div>
    <v-text-field type="number" v-model="setting_data.gpio.UsbDisk_EN"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      USB切换
    </div>
    <v-text-field type="number" v-model="setting_data.gpio.UsbDisk_Switch"></v-text-field>
  </div>
</template>

<style scoped>
.v-alert {
  margin-bottom: 35px;
}
</style>
