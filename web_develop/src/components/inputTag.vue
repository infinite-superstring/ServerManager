<script>
export default {
  name: "inputTag",
  props: {
    label: {
      type: String,
      required: true,
    },
    items: {
      type: Array,
      required: false
    },
    tags: {
      type: Array,
      required: false
    }
  },
  emits: ["input", 'update:chips'],
  data() {
    return {
      chips: [],
    }
  },
  mounted() {
    this.chips = this.tags
  },
  methods: {
    remove(item) {
      this.chips.splice(this.chips.indexOf(item), 1)
    },
  },
  watch: {
    chips(val) {
      this.$emit('update:chips', val)
    }
  }
}
</script>

<template>
  <v-combobox
    clearable
    chips
    multiple
    :label="label"
    v-model="chips"
    :items="items"
    @input="$event => {this.$emit('input', $event.target.value)}"
  ></v-combobox>
</template>

<style scoped>

</style>
