<script>
import {NULL} from "sass";
import AddNode from "@/components/dialogs/node/addNode.vue";

export default {
  name: "toolsBar",
  components: {AddNode},
  data() {
    return {
      search: null,
      add_node: false
    }
  },
  watch: {
    search(val) {
      // TODO 搜索节点
    }
  }
}
</script>

<template>
  <div class="toolsBar">
    <v-btn
      id="addUser"
      color="success"
      @click="add_node = true">
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
      v-model="search">
    </v-text-field>
  </div>
  <div class="dialogs">
    <add-node :flag="add_node" @close="add_node = false"/>
  </div>
</template>

<style scoped>

</style>
