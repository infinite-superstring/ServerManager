<script>
import user from "@/scripts/admin/users"
import InputDialog from "@/components/dialogs/inputDialog.vue";

export default {
  name: "resetPassword",
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
  mounted() {
    this.newValue = this.value
  },
  watch: {
    flag(val) {
      if (!val) {
        this.value = null
      }
    }
  },
  methods: {
    submit() {
      /**
       * 提交
       */
      user.updateUserInfo(this, this.uid, {password: this.value}).then(()=>{
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
    title="重置用户密码"
    label="至少6字符，必须含有数字，小写字母，大写字母，特殊字符"
    type="password"
    :flag="flag"
    :value="value"
    @close="close"
    @update="args => {value = args}"
    @confirm="submit()"/>
</template>

<style scoped>

</style>
