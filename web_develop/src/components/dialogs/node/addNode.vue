<script>
import InputTag from "@/components/inputTag.vue";
import axios from "axios";
import message from "@/scripts/utils/message";
import {el} from "vuetify/locale";

export default {
  name: "addNode",
  components: {InputTag},
  props: {
    flag: {
      type: Boolean,
      required: true,
    }
  },
  emits: ['close'],
  data() {
    return {
      nodeName: null,
      description: null,
      tags: [],
      tag_items: [],
      group: null
    }
  },
  methods: {
    search_tag(tag_name) {
      if(tag_name) {
        axios.post("/node_tag/search_tag", {tag: tag_name}).then(res=>{
          const apiStatus = res.data.status
          if (apiStatus === 1) {
            this.tag_items = res.data.data.tags
          } else {
            message.showError(this, res.data.msg)
          }
        }).catch(err=>{
          console.log(err)
          message.showApiErrorMsg(this, err.message)
        })
      }
    },
    close() {
      this.nodeName = null
      this.description = null
      this.tags = []
      this.group = null
      this.$emit('close')
    },
    submit() {
      if (!this.nodeName) {
        message.showError(this, "节点名未填写")
      }
      axios.post('/node_manager/addNode', {
        node_name: this.nodeName,
        node_description: this.description,
        node_tags: this.tags,
        node_group: this.group
      }).then(res=>{
        const status = res.data.status
        if (status !== 1) {
          message.showError(this, res.data.msg)
        } else {
          message.showSuccess(this, `节点添加成功,Token:${res.data.data.token}`, 10000)
          this.close()
        }
      }).catch(err=>{
        console.error(err)
        message.showApiErrorMsg(this, err.message)
      })
    }
  }
}
</script>

<template>
  <v-dialog
    id="inputDialog"
    activator="parent"
    min-width="600px"
    width="auto"
    persistent
    :modelValue="flag"
  >
    <v-card>
      <v-card-title>添加节点</v-card-title>
      <v-card-text>
        <div>
          <div class="text-caption">
            节点名
          </div>
          <v-text-field type="text" v-model="nodeName"></v-text-field>
        </div>
        <div>
          <div class="text-caption">
            节点标签
          </div>
          <input-tag label="" :items="tag_items" @update:chips="args => {tags = args}" @input="args => {search_tag(args)}"/>
        </div>
        <div>
          <div class="text-caption">
            节点分组
          </div>
          <v-select
            :items="['默认组', 'Colorado', 'Florida', 'Georgia', 'Texas', 'Wyoming']"
            v-model="group"
          >
            <template v-slot:append>
              <v-btn icon variant="plain">
                <v-icon icon="mdi:mdi-plus"/>
              </v-btn>
            </template>
          </v-select>
        </div>
        <div>
          <div class="text-caption">
            节点备注
          </div>
          <v-textarea v-model="description"></v-textarea>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn color="error" @click="close">取消</v-btn>
        <v-btn color="success" @click="submit">确定</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>
