<template>

  <v-sheet
    class="d-flex align-content-start mb-6 flex-wrap"
    min-height="200"
  >
    <v-sheet class="ma-3 pa-3">
      <v-card>
        <v-img
          src="@/assets/images/Machine1.png"
          class="align-end"
          gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
          height="200px"
          min-width="30vw"
          cover
        >
          <v-card-title class="text-white" v-text="text"></v-card-title>
        </v-img>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn size="small" color="surface-variant" variant="text" prepend-icon="mdi:mdi-play">控制</v-btn>

          <v-btn size="small" color="surface-variant" variant="text" prepend-icon="mdi:mdi-tune">设置</v-btn>

          <v-btn size="small" color="surface-variant" variant="text" icon="mdi-share-variant"></v-btn>
        </v-card-actions>
      </v-card>
    </v-sheet>


  </v-sheet>
</template>

<script>
export default {
  name: 'MachineList',
  data() {
    return {
      text:"测试文本"
    }
  }
}
</script>
