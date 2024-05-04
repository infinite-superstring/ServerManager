<script>

export default {
  name: "toolsBar",
  emits: ['action:search', 'action:addNode'],
  props: {
    search: {
      type: String,
      required: true
    }
  },
  data() {
    return {
    }
  }
}
</script>

<template>
  <div class="toolsBar">
    <v-btn
      id="addUser"
      color="success"
      @click="$emit('action:addNode')">
      添加节点
    </v-btn>
    <v-text-field
      id="searchUser"
      class="search"
      density="compact"
      label="按节点名搜索"
      variant="solo-filled"
      single-line
      hide-details
      :model-value="search"
      @input="$emit('action:search', $event.target.value)"
    >
    </v-text-field>
  </div>

</template>

<style scoped>

</style>
