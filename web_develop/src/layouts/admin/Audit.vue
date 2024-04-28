<script>
import operationLog from "@/components/tables/auditPage/operationLog.vue";
import systemLog from "@/components/tables/auditPage/systemLog.vue";
import accessLog from "@/components/tables/auditPage/accessLog.vue";
import fileChangeLog from "@/components/tables/auditPage/fileChangeLog.vue";

export default {
  name: "audit_layout",
  components: {fileChangeLog, accessLog, systemLog, operationLog},
  data: () => {
    return {
      tab: null
    }
  }
}
</script>

<template>
  <v-card>
    <v-tabs
      v-model="tab"
    >
      <v-tab value="operation_log">操作日志</v-tab>
      <v-tab value="System_log">系统日志</v-tab>
      <v-tab value="Access_log">访问日志</v-tab>
      <v-tab value="File_change_log">文件修改日志</v-tab>
    </v-tabs>
    <v-card-text>
      <v-window v-model="tab">
        <v-window-item value="operation_log">
          <operation-log/>
        </v-window-item>
        <v-window-item value="System_log">
          <system-log/>
        </v-window-item>
        <v-window-item value="Access_log">
          <access-log/>
        </v-window-item>
        <v-window-item value="File_change_log">
          <file-change-log/>
        </v-window-item>
      </v-window>
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>
