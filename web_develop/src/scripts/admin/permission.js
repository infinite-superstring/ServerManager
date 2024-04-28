import axios from "axios";
import message from "@/scripts/utils/message";

function editGroup(el, gid, data) {
  return new Promise((resolve, reject) => {
    axios.post("/admin/api/setPermissionGroup", {
      id: gid,
      data: data
    }).then(res => {
      const apiStatus = res.data.status
      if (apiStatus !== 1) {
        message.showApiErrorMsg(el, res.data.msg, apiStatus)
        reject(apiStatus)
      }
      resolve()
    }).catch(err => {
      console.error(err)
      message.showApiErrorMsg(el, err.message)
      reject()
    })
  })
}

function getGroupInfo(el, gid) {
   return axios.post("/admin/api/getPermissionGroupInfo", {id: gid}).catch(err => {
    console.error(err)
    message.showApiErrorMsg(el, err.message)
  })
}

export default {
  editGroup,
  getGroupInfo
}
