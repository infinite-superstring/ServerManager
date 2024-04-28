<script>
// import {ref} from 'vue';
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/mode-json'
// import 'ace-builds/src-noconflict/mode-mysql'
import 'ace-builds/src-noconflict/mode-text'
import 'ace-builds/src-noconflict/theme-monokai'
import 'ace-builds/src-min-noconflict/ext-language_tools'

export default {
  name: "AceEdit",
  emits: ["edit-event"],
  props: {
    theme: {
      type: String,
      default: "monokai",
      required: false
    },
    language: {
      type: String,
      required: true
    },
    readOnly: {
      type: Boolean,
      default: false,
      required: false
    },
    fontSize: {
      type: Number,
      default: 16,
      required: false
    },
    autoWrap: {
      type: Boolean,
      default: false,
      required: false
    },
    value: {
      type: String,
      required: true
    },
    webSocket: {
      type: Object,
      required: false
    },
    fileId: {
      type: String,
      required: false
    }
  },
  data:() => {
    return {
      // display: null, //显示对象
      editor: null, // 编辑器对象
    }
  },
  mounted() {
    // this.display = ref("aceEdit")
    if (this.editor) {
      //实例销毁
      this.editor.destroy()
    }
    const options = { // 编辑器设置
      theme: `ace/theme/${this.theme}`, // 主题
      mode: `ace/mode/${this.language}`, // 代码匹配模式
      tabSize: 2, //标签大小
      fontSize: this.fontSize, //设置字号
      wrap: this.autoWrap, // 用户输入的sql语句，自动换行
      readOnly: this.readOnly, // 只读模式
      enableSnippets: true, // 启用代码段
      showLineNumbers: true, // 显示行号
      enableLiveAutocompletion: true, // 启用实时自动完成功能 （比如：智能代码提示）
      enableBasicAutocompletion: true, // 启用基本自动完成功能
      scrollPastEnd: true, // 滚动位置
      highlightActiveLine: true, // 高亮当前行
    }
    this.editor = ace.edit(document.getElementById("aceEdit"), options)
    this.editor.setValue(this.value ? this.value : '') // 设置内容
    this.editor.on('change', () => { // 当文件改动时
      if (this.$props.webSocket) {
        this.webSocket.send(JSON.stringify({
          action: "saveFile",
          data: {
            value: this.editor.getValue()
          }
        }))
      }
      console.log(this.editor.getValue())
      this.$emit('edit-event', this.editor.getValue())
    })
  },
  unmounted() {
    if (this.editor) {
      //实例销毁
      this.editor.destroy()
      this.websocket = null
    }
  }
}
</script>

<template>
  <div
    ref="aceEdit"
    id="aceEdit"
    class="bi-ace-editor"
    style="width: 100%;height: 100%"
  >
  </div>
</template>

<style scoped>
</style>
