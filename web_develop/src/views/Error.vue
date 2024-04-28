<script>
export default {
  name: "errorPage",
  data() {
    return {
      errorMessage: '',
      errorCode: null
    };
  },
  created() {
    // 从路由参数中获取错误代码
    this.errorCode = Number(this.$route.params.errorCode);
      if (isNaN(this.errorCode)) {
        this.errorCode = "Unknown Error"
      }


    // 根据错误代码设置相应的错误消息
    switch (this.errorCode) {
      case 403:
        this.errorMessage = 'Forbidden';
        break;
      case 404:
        this.errorMessage = 'Page not found';
        break;
      case 500:
        this.errorMessage = 'Internal Server Error';
        break;
      case 502:
        this.errorMessage = 'Bad Gateway';
        break;
      case 504:
        this.errorMessage = 'Gateway Timeout';
        break;
      // 添加其他错误代码的处理逻辑...
      default:
        this.errorMessage = 'An error occurred';
    }
  }
}
</script>

<template>
  <div class="error">
    <h1>{{errorCode}}</h1>
    <p>{{ errorMessage }}</p>
  </div>
</template>

<style scoped>
  .error {
    height: 100%;
    display: flex;
    flex-wrap: wrap;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .error h1 {
    margin-bottom: 15px;
  }
</style>
