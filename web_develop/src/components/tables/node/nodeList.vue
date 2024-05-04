<template>

  <v-container class="machine-list">
    <v-card
      class="machine-item"
      v-for="item in nodeList"
      :key="item.uuid"
      @click=""
    >
      <v-card-title class="machine-name">
        {{ item.name }}
        <div class="machine-action">
          <v-btn size="x-small" @click="$emit('action:reset_token', item.uuid)">重置Token</v-btn>
          <v-btn size="x-small" color="red" @click="$emit('action:del_node', item.uuid)">删除节点</v-btn>
        </div>
      </v-card-title>
      <v-card-text>
        <v-row>
          <node-base-info/>
        </v-row>
        <p class="description" v-if="item.description">
          <v-divider/>
          {{ item.description }}
        </p>
        <div class="tags" v-if="item.tags">
          <v-divider/>
          <v-chip
            color="secondary"
            v-for="tag in item.tags"
            :key="tag"
            @click="$emit('action:click_tag', tag)"
          >
            {{ tag }}
          </v-chip>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import NodeBaseInfo from "@/components/nodeList/nodeBaseInfo.vue";

export default {
  name: 'NodeList',
  components: {NodeBaseInfo},
  props: {
    nodeList: {
      type: Array,
      required: true
    }
  },
  emits: ['action:del_node', 'action:reset_token', 'action:click_tag'],
}
</script>

<style>
.machine-name {
  display: flex;
  justify-content: space-between;
}

.machine-list {
  max-width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.machine-item {
  width: 32%;
}

@media screen and (max-width: 1000px) {
  .machine-item {
    width: 49%;
  }

}

@media screen and (max-width: 570px) {
  .machine-item {
    width: 100%;
  }
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
</style>
