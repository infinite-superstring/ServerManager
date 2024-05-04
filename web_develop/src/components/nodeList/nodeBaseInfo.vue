<script>
export default {
  name: "nodeBaseInfo",
  props: {
    data: {
      type: Array
    }
  }
}
</script>

<template>
  <v-col
    cols="16"
    sm="4"
  >
    <div class="status">
      <div class="status-name">
        平台
      </div>
      <div class="status-value">
        Linux
      </div>
    </div>
  </v-col>
  <v-col
    cols="16"
    sm="4"
  >
    <div class="status">
      <div class="status-name">
        CPU
      </div>
      <div class="status-value">
        10%
      </div>
    </div>
  </v-col>
  <v-col
    cols="16"
    sm="4"
  >
    <div class="status">
      <div class="status-name">
        内存
      </div>
      <div class="status-value">
        10%
      </div>
    </div>
  </v-col>
  <v-col
    cols="16"
    sm="4"
  >
    <div class="status">
      <div class="status-name">
        在线状态
      </div>
      <div class="status-value">
        在线
      </div>
    </div>
  </v-col>
  <v-col
    cols="16"
    sm="4"
  >
    <div class="status">
      <div class="status-name">
        节点版本
      </div>
      <div class="status-value">
        v0.1
      </div>
    </div>
  </v-col>
  <v-col
    cols="16"
    sm="3"
  >
    <div class="status">
      <div class="status-name">
        节点ID
      </div>
      <div class="status-value">
        <v-icon icon="mdi:mdi-clipboard-text-outline" size="small"/>
      </div>
    </div>
  </v-col>

</template>

<style scoped>

</style>
