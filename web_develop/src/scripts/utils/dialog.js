import editUserStatus from "@/components/dialogs/users/editUserStatus.vue";
import {createApp} from "vue";

function showEditUserStatusDialog(el, uid, default_value) {
  /**
   * 显示编辑用户状态弹窗
   */
  const app = createApp(editUserStatus, value)
  app.mount(document.body)
}

export default {
  showEditUserStatusDialog
}
