<script>
import user from "@/scripts/admin/users"
import message from "@/scripts/utils/message";
import InputDialog from "@/components/dialogs/inputDialog.vue";
export default {
  name: "editUsername",
  components: {InputDialog},
  emits: ['close'],
  props: {
    flag: {
      type: Boolean,
      required: true
    },
    uid: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      value: null,
      newValue: null
    }
  },
  watch: {
    flag(val) {
      if (!val) {
        this.value = null
      } else {
        user.getUserInfo(this, this.uid).then(res=>{
          this.value = res.data.data.userName
          this.newValue = this.value
        })
      }
    },
  },
  methods: {
    submit() {
      /**
       * 提交
       */
      user.updateUserInfo(this, this.uid, {userName: this.value}).then(()=>{
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
    title="编辑用户名"
    :flag="flag"
    :value="value"
    @close="close"
    @update="args => {value = args}"
    @confirm="submit()"/>
</template>

<style scoped>

</style>
