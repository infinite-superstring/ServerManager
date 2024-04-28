<script>
export default {
  name: "Display_Settings",
  props: {
    setting_data: {
      type: Object,
      required: true
    }
  }
}
</script>

<template>
  <p class="text-h5 setting_subtitle">采集卡设置</p>
  <div class="text-caption">
    屏幕分辨率
  </div>
  <v-row>
    <v-col
      cols="12"
      md="6"
    >
      <v-text-field
        label="宽"
        hint="例如：1920"
        type="number"
        v-model="setting_data.camera.width"
      ></v-text-field>
    </v-col>
    <v-col
      cols="12"
      md="6"
    >
      <v-text-field
        label="高"
        hint="例如：1080"
        type="number"
        v-model="setting_data.camera.height"
      ></v-text-field>
    </v-col>
  </v-row>
  <div>
    <div class="text-caption">
      帧率
    </div>
    <v-slider
      thumb-label="always"
      max="60"
      min="24"
      step="1"
      v-model="setting_data.camera.fps"
    >
      <template v-slot:append>
        <v-text-field
          type="number"
          style="width: 80px"
          density="compact"
          hide-details
          variant="outlined"
          v-model="setting_data.camera.fps"
        ></v-text-field>
      </template>
    </v-slider>
  </div>
  <div>
    <div class="text-caption">
      图像更新阈值
    </div>
    <v-slider
      thumb-label="always"
      max="5"
      min="0.01"
      step="0.01"
      v-model="setting_data.camera.updateDisplayChange"
    >
      <template v-slot:append>
        <v-text-field
          type="number"
          style="width: 80px"
          density="compact"
          hide-details
          variant="outlined"
          v-model="setting_data.camera.updateDisplayChange"
        ></v-text-field>
      </template>
    </v-slider>
  </div>
  <div>
    <div class="text-caption">
      亮度
    </div>
    <v-text-field type="number" v-model="setting_data.camera.brightness"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      曝光
    </div>
    <v-text-field type="number" v-model="setting_data.camera.exposure"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      饱和度
    </div>
    <v-text-field type="number" v-model="setting_data.camera.colorfulness"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      色调
    </div>
    <v-text-field type="number" v-model="setting_data.camera.tonal"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      控制时添加水印到画面中
    </div>
    <v-checkbox></v-checkbox>
  </div>
  <v-divider></v-divider>
  <p class="text-h5 setting_subtitle">录制设置</p>
  <div>
    <div class="text-caption">
      录制帧率
    </div>
    <v-text-field type="number" v-model="setting_data.record.fps"></v-text-field>
  </div>
  <div>
    <div class="text-caption">
      录制时添加信息水印到画面中
    </div>
    <v-checkbox></v-checkbox>
  </div>
</template>

<style scoped>

</style>
