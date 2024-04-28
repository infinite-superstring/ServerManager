<script>
export default {
  name: "inputDialog",
  emits: ['update', 'confirm', 'close'],
  props: {
    flag: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: false,
      default: ""
    },
    type: {
      type: String,
      required: false,
      default: "text"
    },
    value: {
      type: String,
      required: false,
      default: ""
    }
  },
  // data: () => {
  //   return {
  //     input: null,
  //   }
  // }
}
</script>

<template>
  <v-dialog
      id="inputDialog"
      :model-value="flag"
      activator="parent"
      min-width="400px"
      width="auto"
      persistent
    >
      <v-card>
        <v-card-title>{{ title }}</v-card-title>
        <v-card-text>
          <v-text-field :modelValue="value" :label="label" :type="type" @input="$emit('update', $event.target.value)"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" @click="$emit('close')">取消</v-btn>
          <v-btn color="success" @click="$emit('confirm')">确定</v-btn>
        </v-card-actions>
      </v-card>
  </v-dialog>
</template>

<style scoped>

</style>
