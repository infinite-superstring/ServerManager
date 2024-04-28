import json
import os

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer

from threading import Thread

from django.apps import apps

from util.logger import Log
import file_manager.util.FileTools as FT
from file_manager.models import Temporary_link
from user_manager.util.userUtils import get_user_by_id
from audit.util.auditTools import write_access_log, write_file_change_log

links = {}


class fileManagerPageWebSocket(WebsocketConsumer):
    __homePath = None
    __currentEditor = None
    __userID = None
    __clientIP = None

    def connect(self):
        # 在建立连接时执行的操作
        user = self.scope["session"].get("user")
        self.__userID = self.scope["session"].get("userID")
        self.__clientIP = self.scope["client"][0]
        if user:
            from setting.entity.Config import config
            config: config = apps.get_app_config('setting').get_config()
            self.__homePath = config.base.USB_MountDirectory
            self.accept()
            # links.update({user: self})
            Log.success(f"用户{user}已连接")
            write_access_log(self.__userID, self.__clientIP, "FileManager Websocket Connect")
        else:
            self.close(-1)

    def disconnect(self, close_code):
        # 在断开连接时执行的操作
        user = self.scope["session"].get("user")
        # links.pop(user)
        Log.success(f"用户{user}已断开({close_code})")
        write_access_log(self.__userID, self.__clientIP, f"FileManager Websocket Disconnect(Code:{close_code})")
        raise StopConsumer

    @Log.catch
    def receive(self, text_data=None, bytes_data=None):
        # 处理接收到的消息
        if bytes_data:
            fileHeader = bytes_data[0:63]
            fileHash = fileHeader[0:32]
            flag = fileHeader[-31:]
            if flag == "   LoongArch-ServerManager_FileUploadData   ".encode():
                fileData = bytes_data[63:]
                Log.debug("收到一个文件包")
                Log.debug("fileHash:" + str(fileHash))
                FT.receiveFiles(fileData, fileHash.decode())
                write_file_change_log(self.__userID, "Upload File Chunk(Bytes)", f"temp/{fileHash}")

        if text_data:
            try:
                jsonData = json.loads(text_data)
            except Exception as e:
                Log.error(f"解析Websocket消息时发生错误：\n{e}")
            else:
                action = jsonData.get("action")
                data = jsonData.get("data")
                path = data.get("path")
                Log.debug(action)
                match action:
                    # 获取文件列表
                    case "getFileList":
                        return self.sendJson(FT.getFileList(self.__homePath, path))
                    # 新建目录
                    case "newDir":
                        dirName = data.get("dirName")
                        if path and dirName:
                            targetPath = FT.mergePaths(self.__homePath, path)
                            if not os.path.exists(os.path.join(targetPath, dirName)):
                                os.mkdir(os.path.join(targetPath, dirName))
                                Log.debug("目录已创建")
                                self.sendSuccessMessage("目录创建成功")
                                self.sendJson(FT.getFileList(self.__homePath, path))
                                write_file_change_log(self.__userID, "New Dir", os.path.join(targetPath, dirName))
                            else:
                                self.sendErrorMessage("目录已存在")
                                Log.debug("目录已存在")
                        else:
                            self.sendErrorMessage("[新建目录]参数不完整")
                            Log.warning("参数不完整")
                    # 新建文件
                    case "newFile":
                        fileName = data.get("fileName")
                        if path and fileName:
                            targetPath = FT.mergePaths(self.__homePath, path)
                            if FT.createFile(os.path.join(targetPath, fileName)):
                                self.sendJson(FT.getFileList(self.__homePath, path))
                                write_file_change_log(self.__userID, "New File", os.path.join(targetPath, fileName))
                                self.sendSuccessMessage("文件创建成功")
                            else:
                                self.sendErrorMessage("文件创建失败")
                        else:
                            self.sendErrorMessage("[新建文件]参数不完整")
                            Log.warning("参数不完整")
                    # 重命名文件
                    case "reName":
                        oldFileName = data.get("oldFileName")
                        newFileName = data.get("newFileName")
                        if oldFileName and newFileName:
                            old = os.path.join(FT.mergePaths(self.__homePath, path), oldFileName)
                            new = os.path.join(FT.mergePaths(self.__homePath, path), newFileName)
                            if os.path.exists(old) and not os.path.exists(new):
                                os.rename(old, new)
                                self.sendJson(FT.getFileList(self.__homePath, path))
                                write_file_change_log(self.__userID, "ReName", f"{old}-->{new}")
                            elif not os.path.exists(old):
                                self.sendErrorMessage("找不到目标文件")
                                Log.info("目标文件缺失")
                            elif os.path.exists(new):
                                self.sendErrorMessage("要更改的文件名与当前已有的文件名冲突")
                                Log.info("要更改的文件名与当前已有的文件名冲突")
                        else:
                            self.sendErrorMessage("[重命名]参数不完整")
                            Log.warning("参数不完整")
                    # 删除
                    case "del":
                        path = data.get("path")
                        fileName = data.get("filename")
                        if path and fileName:
                            targetPath = FT.mergePaths(self.__homePath, path)
                            if isinstance(fileName, list):
                                for item in fileName:
                                    if FT.delFile(os.path.join(targetPath, item)):
                                        self.sendSuccessMessage("目录或文件删除成功")
                                        write_file_change_log(self.__userID, "Del files", os.path.join(targetPath, item))
                                    else:
                                        self.sendErrorMessage("目录或文件删除失败")
                                        Log.debug("文件或目录已删除")
                            else:
                                if FT.delFile(os.path.join(targetPath, fileName)):
                                    write_file_change_log(self.__userID, "Del file", os.path.join(targetPath, fileName))
                                    self.sendSuccessMessage("目录或文件删除成功")
                                else:
                                    self.sendErrorMessage("目录或文件删除失败")
                                    Log.debug("文件或目录已删除")
                            self.sendJson(FT.getFileList(self.__homePath, path))
                        else:
                            self.sendErrorMessage("[删除]参数不完整")
                            Log.warning("参数不完整")
                    # 弃用的上传文件方法（效率过低）
                    case "uploadFile":
                        chunkHash = data.get("chunkHash")
                        base64 = data.get("base64")
                        if path and chunkHash and base64:
                            FT.receiveFiles(base64, chunkHash, True)
                            write_file_change_log(self.__userID, "Upload file chunk(base64)", f"temp/{chunkHash}")
                        else:
                            self.sendErrorMessage("[上传]参数不完整")
                            Log.warning("参数不完整")
                    # 合并文件
                    case "mergeFile":
                        filename = data.get("filename")
                        fileHash = data.get("fileHash")
                        chunksHash = data.get("chunksHash")
                        if path and filename and fileHash and chunksHash:
                            Thread(target=FT.mergeFiles,
                                   args=(self.__homePath, path, filename, fileHash, chunksHash)).start()
                            self.sendJson(FT.getFileList(self.__homePath, path))
                            write_file_change_log(self.__userID, "Merge File", os.path.join(FT.mergePaths(self.__homePath, path), filename))
                        else:
                            self.sendErrorMessage("[上传]参数不完整")
                            Log.warning("参数不完整")
                    # 新建临时链接
                    case "newTemporaryLink":
                        filename = data.get("filename")
                        if path and filename:
                            User_Model = get_user_by_id(self.__userID)
                            TL_Model = Temporary_link.objects.create(userID=User_Model, filePath=os.path.join(
                                FT.mergePaths(self.__homePath, path), filename))
                            self.sendJson({
                                "action": "returnTemporaryLink",
                                "data": {
                                    "path": path,
                                    "filename": filename,
                                    "token": str(TL_Model.token)
                                }
                            })
                            write_file_change_log(self.__userID, "New temporary link", os.path.join(FT.mergePaths(self.__homePath, path), filename))
                        else:
                            self.sendErrorMessage("[下载]参数不完整")
                            Log.warning("参数不完整")
                    # 编辑文件
                    case "editFile":
                        filename = data.get("filename")
                        if filename and not self.__currentEditor:
                            self.__currentEditor = os.path.join(FT.mergePaths(self.__homePath, path), filename)
                            if os.path.exists(self.__currentEditor) and os.path.getsize(
                                    self.__currentEditor) <= 10 * 1024 * 1024:
                                with open(self.__currentEditor, "r",
                                          encoding=FT.getFileEncoding(self.__currentEditor)) as file:
                                    self.sendJson({
                                        "action": "returnEditFileValue",
                                        "data": {
                                            "path": path,
                                            "filename": filename,
                                            "value": file.read()
                                        }
                                    })
                                    write_file_change_log(self.__userID, "Start edit file", self.__currentEditor)
                                    Log.debug(f"正在编辑文件：{self.__currentEditor}")
                            else:
                                self.sendErrorMessage("[打开文件]文件大小超出可编辑范围")
                                Log.error("文件过大，不可在线编辑")
                                self.__currentEditor = None
                        else:
                            self.sendErrorMessage("[打开文件]参数不完整或当前已有正在编辑的文件")
                            Log.warning("参数不完整或当前已有正在编辑的文件")
                    # 取消编辑文件
                    case "cancelEdit":
                        write_file_change_log(self.__userID, "Cancel edit file", self.__currentEditor)
                        self.__currentEditor = None
                        self.sendInfoMessage("已取消编辑")
                        Log.debug("已取消编辑文件")
                    # 保存文件
                    case "saveFile":
                        value: str = data.get("value")
                        if value and self.__currentEditor:
                            Log.debug("正在保存编辑")
                            Log.debug(value)
                            with open(self.__currentEditor, "w", encoding=FT.getFileEncoding(self.__currentEditor)) as editFile:
                                editFile.write(value)
                            write_file_change_log(self.__userID, "Save edit file", self.__currentEditor)
                            self.sendSuccessMessage("编辑的文件已保存")
                            Log.success("编辑的文件已保存")
                        elif not value:
                            self.sendErrorMessage("[保存编辑]参数不完整")
                            Log.warning("参数不完整")
                        elif not self.__currentEditor:
                            self.sendErrorMessage("[保存编辑]该文件未处于编辑状态")
                            Log.warning("未开启编辑")
                    # 压缩
                    case "compress":
                        files = data.get("files")
                        outputName = data.get("outputName")
                        if path and files and outputName:
                            Thread(target=FT.compression, args=(self.__userID, self.__homePath, path, files, outputName)).start()
                        else:
                            self.sendErrorMessage("[压缩文件]参数不完整")
                            Log.warning("参数不完整")
                    # 解压缩
                    case "decompress":
                        files = data.get("files")
                        decompressToPath = data.get("decompressToPath")
                        if path and files:
                            Thread(target=FT.decompress, args=(self.__userID, self.__homePath, path, files, decompressToPath)).start()
                        else:
                            self.sendErrorMessage("[解压文件]参数不完整")
                            Log.warning("参数不完整")
                    # 复制
                    case "copy":
                        sourceFileDirectory = data.get("sourceFileDirectory")
                        selectFiles = data.get("selectFiles")
                        toDirectory = data.get("toDirectory")
                        if sourceFileDirectory and selectFiles and toDirectory:
                            FT.copy(self.__userID, self.__homePath, sourceFileDirectory, selectFiles, toDirectory)
                            self.sendJson(FT.getFileList(self.__homePath, toDirectory))
                        else:
                            self.sendErrorMessage("[复制]参数不完整")
                            Log.warning("参数不完整")
                    # 移动
                    case "move":
                        sourceFileDirectory = data.get("sourceFileDirectory")
                        selectFiles = data.get("selectFiles")
                        toDirectory = data.get("toDirectory")
                        if sourceFileDirectory and selectFiles and toDirectory:
                            FT.move(self.__homePath, self.__homePath, sourceFileDirectory, selectFiles, toDirectory)
                            self.sendJson(FT.getFileList(self.__homePath, toDirectory))
                        else:
                            self.sendErrorMessage("[移动]参数不完整")
                            Log.warning("参数不完整")
                        pass
                    case _:
                        Log.warning(f"未定义的操作：{action}")

    # 发送Json消息
    @Log.catch
    def sendJson(self, data):
        self.send(json.dumps(data))

    # 发送信息到客户端
    def sendInfoMessage(self, message):
        self.sendJson({
            "action": "info",
            "data": {
                "msg": message
            }
        })

    # 发送操作成功信息到客户端
    def sendSuccessMessage(self, message):
        self.sendJson({
            "action": "success",
            "data": {
                "msg": message
            }
        })

    # 发送警告信息到客户端
    def sendWarningMessage(self, message):
        self.sendJson({
            "action": "Warning",
            "data": {
                "msg": message
            }
        })

    # 发送错误信息到客户端
    def sendErrorMessage(self, message):
        self.sendJson({
            "action": "error",
            "data": {
                "msg": message
            }
        })
