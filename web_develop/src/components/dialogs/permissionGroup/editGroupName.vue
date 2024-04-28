<script>
import InputDialog from "@/components/dialogs/inputDialog.vue";
import permission from "@/scripts/admin/permission";
import message from "@/scripts/utils/message";

export default {
  name: "EditGroupName",
  components: {InputDialog},
  emits: ['close'],
  props: {
    flag: {
      type: Boolean,
      required: true
    },
    gid: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      value: null,
    }
  },
  watch: {
    flag(val) {
      if (!val) {
        this.value = null
      } else {
        permission.getGroupInfo(this, this.gid).then(res => {
          const apiStatus = res.data.status
          if (apiStatus === 1) {
            const groupInfo = res.data.data
            this.value = groupInfo.name
          } else {
            message.showApiErrorMsg(this, res.data.msg, apiStatus)
          }
        })
      }
    },
  },
  methods: {
    submit() {
      /**
       * 提交
       */
      permission.editGroup(this, this.gid, {newName: this.value}).then(() => {
        this.close()
      })
    },
    close() {
      this.$emit('close')
    }
  }
}
</script>

<template>
  <input-dialog
    title="编辑权限组名"
    :flag="flag"
    :value="value"
    @close="close"
    @update="args => {this.value = args}"
    @confirm="submit()"
  />
</template>

<style scoped>

</style>
