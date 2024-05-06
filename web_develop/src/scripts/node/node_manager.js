import axios from "axios";
import message from "@/scripts/utils/message";

function del_node(el, node_uuid) {
  /**
   * 删除节点
   */
  axios.post('/node_manager/delNode', {
    uuid: node_uuid
  }).then(res=>{
    const apiStatus = res.data.status;
    if (apiStatus !== 1) {
      message.showApiErrorMsg(el, res.data.msg, apiStatus)
    } else {
      message.showSuccess(el, res.data.msg)
    }
  }).catch(err=>{
    console.log(err)
    message.showApiErrorMsg(el, err.msg)
  })
}

function reset_token(el, node_uuid) {
  axios.post('/node_manager/delNode', {
    uuid: node_uuid
  }).then(res=>{
    const apiStatus = res.data.status;
    if (apiStatus !== 1) {
      message.showApiErrorMsg(el, res.data.msg, apiStatus)
    } else {
      message.showSuccess(el, res.data.msg)
    }
  }).catch(err=>{
    console.log(err)
    message.showApiErrorMsg(el, err.msg)
  })
}

export default {
  del_node,
  reset_token
}
