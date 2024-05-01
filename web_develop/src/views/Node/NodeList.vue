<script>
import list from '@/components/nodeList/list.vue';
import toolsBar from "@/components/nodeList/toolsBar.vue";
import GroupList from "@/layouts/admin/PermissionGroup/PermissionGroup.vue";
export default {
  name: "MachineList",
  components: {GroupList, list, toolsBar},
}
</script>

<template>
  <v-card title="节点列表" class="pageMain-card">
    <v-card-text>
      <tools-bar/>
      <list/>
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>
