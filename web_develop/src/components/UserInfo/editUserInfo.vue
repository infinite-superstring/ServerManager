<script>
import axios from "axios";
import Cropper from "cropperjs";
import SparkMD5 from "spark-md5";
import {useUserStore} from "@/store/userInfo";
import 'cropperjs/dist/cropper.css';

export default {
  name: "editUserInfo",
  data: () => {
    return {
      id: "",
      userName: "",
      realName: "",
      email: "",
      group: "",
      avatarUrl: "/userInfo/api/getAvatar",
      uploadAvatar: {
        flag: false,
        file: null,
        cropper: null
      }
    }
  },
  mounted() {
   this.getUserinfo()
  },
  methods: {
    getUserinfo() {
      axios.get("/userInfo/api/getInfo").then(res => {
        const data = res.data.data
        this.id = data.id;
        this.userName = data.userName
        this.realName = data.realName
        this.email = data.email
        this.group = data.group
      }).catch(err => {
        console.log(err)
      })
    },
    saveUserInfo() {
      axios.post("userInfo/api/editInfo", {
        data: {
          userName: this.userName,
          realName: this.realName,
          email: this.email
        }
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          const userStore = useUserStore()
          userStore.getUserInfo()
          this.$notify.create({
            text: `用户信息保存成功~`,
            level: 'success',
            location: 'bottom right',
            notifyOptions: {
              "close-delay": 3000
            }
          })
        } else {
          this.$notify.create({
            text: `API错误：${res.data.msg}(status:${apiStatus})`,
            level: 'error',
            location: 'bottom right',
            notifyOptions: {
              "close-delay": 3000
            }
          })
        }
      }).catch(err => {
        this.$notify.create({
          text: `API错误：${err.message}`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
      })
    },
    // 开启头像上传框
    openAvatarUploader() {
      document.getElementById("uploadAvatar").click()
    },
    // 头像裁剪
    avatarCut() {
      console.log('avatarCut called')
      // 检查是否为图像文件
      if (this.uploadAvatar.file && this.uploadAvatar.file.type.startsWith('image/')) {
        this.uploadAvatar.cropper = null
        this.uploadAvatar.flag = true
        this.$nextTick(() => {
          const previewImage = document.getElementById('previewImage');
          console.log(previewImage)
          previewImage.src = URL.createObjectURL(this.uploadAvatar.file);
          // 初始化 cropper.js
          this.uploadAvatar.cropper = new Cropper(previewImage, {
            aspectRatio: 1, // 固定裁剪框的宽高比
            viewMode: 1,    // 显示裁剪框，允许移动图片
            dragMode: 'move', // 设置拖动模式为移动图片
            autoCropArea: 1,  // 初始裁剪框占图像的比例
            responsive: true,  // 支持响应式布局
            cropBoxResizable: false, // 禁止用户调整裁剪框的宽高
            rotatable: false
          });
          this.uploadAvatar.cropper.setCropBoxData({
            width: 512,
            height: 512
          })
        })
      } else {
        this.uploadAvatar.flag = false
      }
    },
    // 头像上传
    async uploadAvatarImg() {

      async function calculateMD5(dataUrl) {
        // 从 base64 数据中提取文件内容
        const base64Content = dataUrl.split(',')[1];

        // 计算MD5哈希值
        const spark = new SparkMD5.ArrayBuffer();
        const buffer = Uint8Array.from(atob(base64Content), c => c.charCodeAt(0)).buffer;
        spark.append(buffer);
        const hash = spark.end();

        console.log('Image MD5 Hash:', hash);
        return hash
      }

      const imgBase64 = this.uploadAvatar.cropper.getCroppedCanvas({
        maxHeight: 512,
        maxWidth: 512
      }).toDataURL("image/webp", 0.8)

      axios.post("/userInfo/api/uploadAvatar", {
        data: {
          avatarImg: imgBase64,
          avatarHash: await calculateMD5(imgBase64)
        }
      }).then(res => {
        const apiStatus = res.data.status
        if (apiStatus === 1) {
          this.$notify.create({
            text: `头像上传成功`,
            level: 'success',
            location: 'bottom right',
            notifyOptions: {
              "close-delay": 3000
            }
          })
          this.uploadAvatar.flag = false
          this.uploadAvatar.file = null
          this.avatarUrl = "/userInfo/api/getAvatar?v" + Math.random()
        } else {
          this.$notify.create({
            text: `API错误：${res.data.msg}(status:${apiStatus})`,
            level: 'error',
            location: 'bottom right',
            notifyOptions: {
              "close-delay": 3000
            }
          })
        }
      }).catch(err => {
        this.$notify.create({
          text: `API错误：${err.message}`,
          level: 'error',
          location: 'bottom right',
          notifyOptions: {
            "close-delay": 3000
          }
        })
      })
    }
  },
  watch: {
    "uploadAvatar.file"(val) {
      console.log('flag changed:', this.uploadAvatar.flag)
      if (val !== null && val.type.startsWith('image/')) {
        this.avatarCut()
      }
    }
  }
}
</script>

<template>
  <v-card title="基础信息修改">
    <v-card-text>
      <v-container class="userInfoEdit">
        <v-row>
          <v-col class="left" cols="4">
            <v-row class="avatar">
              <v-avatar :image="avatarUrl" size="100%"></v-avatar>
              <div class="editAvatar" @click="openAvatarUploader()">
                <v-icon icon="mdi:mdi-pencil-outline"></v-icon>
                <span>更换头像</span>
                <input type="file" accept="image/*" id="uploadAvatar"
                       @change="uploadAvatar.file = $event.target.files[0]" style="display: none;">
              </div>
            </v-row>
          </v-col>
          <v-col class="editInfo">
            <v-row>
              <div>
                <div class="text-caption">
                  ID
                </div>
                <v-text-field type="number" disabled v-model="id"></v-text-field>
              </div>
            </v-row>
            <v-row>
              <div>
                <div class="text-caption">
                  用户名
                </div>
                <v-text-field type="text" v-model="userName"></v-text-field>
              </div>
            </v-row>
            <v-row>
              <div>
                <div class="text-caption">
                  真实姓名
                </div>
                <v-text-field type="text" disabled v-model="realName"></v-text-field>
              </div>
            </v-row>
            <v-row>
              <div>
                <div class="text-caption">
                  组
                </div>
                <v-text-field type="text" disabled v-model="group"></v-text-field>
              </div>
            </v-row>
            <v-row>
              <div>
                <div class="text-caption">
                  邮箱
                </div>
                <v-text-field type="email" v-model="email"></v-text-field>
              </div>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-btn block color="success" @click="saveUserInfo()">保存修改</v-btn>
    </v-card-actions>
  </v-card>
  <div>
    <v-dialog
      v-model="uploadAvatar.flag"
      activator="parent"
      min-width="400px"
      width="auto"
      persistent
    >
      <v-card>
        <v-card-title>裁剪图片</v-card-title>
        <v-card-text>
          <img id="previewImage">
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" @click="uploadAvatar.flag = false">取消</v-btn>
          <v-btn color="success" @click="uploadAvatarImg()">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.editInfo .v-row > div {
  width: 100%;
}

.userInfoEdit {
  min-width: 300px;
}

.avatar {
  width: 85%;
  position: relative;
}

.editAvatar {
  width: 100%;
  height: 100%;
  position: absolute;
  display: none;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, .3);
}

.editAvatar .v-icon {
  font-size: 30px;
}

.editAvatar span, .editAvatar .v-icon {
  color: white;
}

.avatar:hover .editAvatar {
  display: flex;
}

#previewImage {
  width: 100%;
  max-height: 70vh;
}
</style>
