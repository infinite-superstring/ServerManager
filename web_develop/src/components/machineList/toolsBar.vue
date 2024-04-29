<script>
export default {
  name: "toolsBar",
  data() {
    return {
      search: ""
    }
  }
}
</script>

<template>
  <div class="toolsBar">
    <v-btn
      id="addUser"
      color="success"
      @click="">
      添加机器
    </v-btn>
    <v-text-field
      id="searchUser"
      class="search"
      density="compact"
      label="按机器名搜索"
      variant="solo-filled"
      single-line
      hide-details
      v-model="search">
    </v-text-field>
  </div>
</template>

<style scoped>

</style>
