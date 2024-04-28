<script>
import list from '@/components/machineList/list.vue';
import toolsBar from "@/components/machineList/toolsBar.vue";
export default {
  name: "MachineList",
  components: {list, toolsBar},
}
</script>

<template>
  <tools-bar/>
  <list/>
</template>

<style scoped>

</style>
