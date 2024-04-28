<script>
import Settings from "@/layouts/admin/Settings.vue";

export default {
  name: "Config",
  components: {Settings},
}
</script>

<template>
  <v-card title="LoongArch-Server-Manager 设置" class="pageMain-card">
    <v-card-text>
      <settings></settings>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.v-card-text {
  display: flex;
  min-height: 90%;
  width: 95%;
  margin: 0 auto;
  border: rgba(0,0,0,0.2) solid 0.5px;
  border-radius: 15px;
}
</style>
