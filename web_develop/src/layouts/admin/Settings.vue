<script>

import base_settings from "@/components/settings/base";
import display_settings from "@/components/settings/display";
import gpio_settings from "@/components/settings/GPIO";
import message from "@/scripts/utils/message.js"
import axios from "axios";

export default {
  name: "Settings",
  components: {gpio_settings, display_settings, base_settings},
  data: () => {
    return {
      openWindow: "Base_Settings",
      settings: null,
    }
  },
  created() {
    this.getSettings()
  },
  methods: {
    getSettings() {
      /**
       * 获取设置数据
       */
      axios.get('/admin/api/settings/getSettings').then(res => {
        this.settings = res.data
      }).catch(err => {
        console.error(err)
      })
    },
    save() {
      /**
       * 保存设置信息
       */
      axios.post('/admin/api/settings/editSettings', this.settings).then(res => {
        message.showSuccess(this, "设置已保存")
      }).catch(err => {
        console.error(err)
        message.showApiErrorMsg(this, err.message)
      })
    }
  }
}
</script>

<template>
  <div class="workspace">
    <v-window v-model="openWindow" v-if="settings">
      <v-window-item value="Base_Settings">
        <base_settings :setting_data="settings"/>
      </v-window-item>
      <v-window-item value="Display_Settings">
        <display_settings :setting_data="settings"/>
      </v-window-item>
      <v-window-item value="GPIO_Settings">
        <gpio_settings :setting_data="settings"/>
      </v-window-item>
    </v-window>
    <div class="actionButton">
      <v-btn @click="save()" color="green">保存</v-btn>
    </div>
  </div>
  <v-list>
    <v-list-subheader>设置项</v-list-subheader>
    <v-list-item
      color="primary"
      value="baseSettings"
      @click="openWindow = 'Base_Settings'">
      基础设置
    </v-list-item>
    <v-list-item
      color="primary"
      value="displaySettings"
      @click="openWindow = 'Display_Settings'">
      录制与显示
    </v-list-item>
    <v-list-item
      color="primary"
      value="GPIO_Settings"
      @click="openWindow = 'GPIO_Settings'">
      GPIO
    </v-list-item>
  </v-list>
</template>

<style scoped>
.v-main {
  padding: 15px;
}

.workspace {
  width: 80%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.workspace .v-window {
  padding: 15px 35px 0 15px;
}

.workspace .actionButton {
  padding: 15px 0 15px 15px
}

.workspace .actionButton .v-btn {
  margin-right: 15px;
}

.v-list {
  width: 30%;
  min-width: 150px;
  height: min-content;
  border: rgba(0, 0, 0, 0.3) solid 0.3px;
  border-radius: 10px;
  margin-right: 15px;
  margin-top: 15px;
}

.v-list .v-list-item {
  white-space: nowrap
}
</style>
