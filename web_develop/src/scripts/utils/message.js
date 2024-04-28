function showApiErrorMsg(el, message, status = null, close_delay = 3000) {
  /**
   * 显示API错误信息
   */
  return showError(el, `API错误：${message} ${status ? '(status:' + status + ')' : ''}`, close_delay)
}

function showSuccess(el, message, close_delay = 3000) {
  /**
   * 显示成功信息
   */
  return el.$notify.create({
    text: message,
    level: 'success',
    location: 'bottom right',
    notifyOptions: {
      "close-delay": close_delay
    }
  })
}

function showInfo(el, message, close_delay = 3000) {
  /**
   * 显示信息
   */
  return el.$notify.create({
    text: message,
    level: 'info',
    location: 'bottom right',
    notifyOptions: {
      "close-delay": close_delay
    }
  })
}

function showWarning(el, message, close_delay = 3000) {
  /**
   * 显示警告信息
   */
  return el.$notify.create({
    text: message,
    level: 'warning',
    location: 'bottom right',
    notifyOptions: {
      "close-delay": close_delay
    }
  })
}

function showError(el, message, close_delay = 3000) {
  /**
   * 显示错误信息
   */
  return el.$notify.create({
    text: message,
    level: 'error',
    location: 'bottom right',
    notifyOptions: {
      "close-delay": close_delay
    }
  })
}

export default {
  showApiErrorMsg,
  showSuccess,
  showInfo,
  showWarning,
  showError
}
