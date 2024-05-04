<script>
import ToolsBar from "@/components/nodeList/toolsBar.vue";
import nodeList from "@/components/tables/node/nodeList.vue";
import addNode from "@/components/dialogs/node/addNode.vue";
import axios from "axios";
import message from "@/scripts/utils/message";

export default {
  name: "node_list_layout",
  components: {ToolsBar, nodeList, addNode},
  emits: ['show_token'],
  data() {
    return {
      add_node: false,
      token_alert: false,
      search: "",
      currentPage: 1,
      maxPage: null,
      nodeListData: []
    }
  },
  watch: {
    search(val) {
      this.getNodeList(1, val)
    },
    currentPage(val) {
      this.getNodeList(val, this.search)
    }
  },
  mounted() {
    this.getNodeList()
  },
  methods: {
    getNodeList(page = 1, search = "") {
      axios.post('/node_manager/getNodeList',{
        page: page,
        search: search
      }).then((res) => {
        if (res.data.status === 1) {
          this.maxPage = res.data.data.maxPage
          this.currentPage = res.data.data.currentPage
          this.nodeListData = res.data.data.PageContent
        } else {
         message.error(res.data.msg)
        }
      }).catch(err=>{
        console.log(err)
        message.showApiErrorMsg(this, err.message)
      })
    }
  }
}
</script>

<template>
  <tools-bar
    @action:addNode="add_node=true"
    @action:search="args => {search=args}"
    :search="search"
  />
  <node-list
    :nodeList="nodeListData"
    @action:click_tag="args => search = `tag:${args}`"
    @action:del_node=""
    @action:reset_token=""
  />
  <div class="dialogs">
    <add-node
      :flag="add_node"
      @close="add_node = false"
      @success="args => $emit('show_token', 'new_node', args)"
    />
  </div>
  <v-pagination
    v-model="currentPage"
    v-if="!maxPage <= 1"
    :length="maxPage"
    :total-visible="6"
    prev-icon="mdi:mdi-menu-left"
    next-icon="mdi:mdi-menu-right"
    rounded="circle"
  ></v-pagination>
</template>

<style scoped>

</style>
