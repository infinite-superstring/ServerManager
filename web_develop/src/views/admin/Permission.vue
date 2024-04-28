<script>
import GroupList from "@/layouts/admin/PermissionGroup/PermissionGroup.vue";

export default {
  name: "Permission",
  components: {GroupList}
}
</script>

<template>
  <v-card title="权限管理" class="pageMain-card">
    <v-card-text>
      <group-list></group-list>
    </v-card-text>
  </v-card>
</template>

<style scoped>
</style>
