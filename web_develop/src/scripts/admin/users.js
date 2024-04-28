import axios from "axios";
import message from "@/scripts/utils/message";

function updateUserInfo(el, uid, data) {
  /**
   * 更新用户信息
   * @type {{data, id}}
   * @param uid 用户UID
   * @param data 更新的数据
   */
  return axios.post("/admin/api/setUserInfo", {id: uid, data: data}).then(res => {
    const status = res.data.status
    if (status !== 1) {
      message.showApiErrorMsg(el, res.data.msg, status)
    }
  }).catch(err => {
    console.error(err)
    message.showApiErrorMsg(el, err.message)
  })
}

function getUserInfo(el, uid) {
  /**
   * 获取用户信息
   * @param uid 用户ID
   */
  return axios.post("/admin/api/getUserInfo", {id: uid}).catch(err => {
    message.showApiErrorMsg(this, err.message)
  })
}

export default {
  updateUserInfo,
  getUserInfo,
}
