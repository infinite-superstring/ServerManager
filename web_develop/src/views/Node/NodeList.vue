<script>
import Node_list_layout from "@/layouts/Node/node_list_layout.vue";

export default {
  name: "MachineList",
  components: {Node_list_layout},
  data() {
    return {
      show_msg: {
        flag: false,
        msg: null
      }
    }
  },
  unmounted() {
    this.show_msg.flag = true
    this.show_msg.msg = null
  },
  methods: {
    show_token(type, token) {
      switch (type) {
        case "new_node":
          this.show_msg.msg = `节点添加成功！Token已生成(Token只会显示一次，请妥善保存)：${token}`
          this.show_msg.flag = true
          break
        case "reset_token":
          this.show_msg.msg = `节点Token重置成功：${token}`
          this.show_msg.flag = true
          break
      }
    }
  }
}
</script>

<template>
  <v-card title="节点列表" class="pageMain-card">
    <v-alert
      variant="tonal"
      v-if="show_msg.flag"
      :text="show_msg.msg"
      type="success"
      closable
    ></v-alert>
    <v-card-text>
      <node_list_layout @show_token="show_token"/>
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>
