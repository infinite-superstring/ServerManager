import os
import re
import base64
import shutil
import hashlib
import zipfile

import chardet
from datetime import datetime
from util.logger import Log
from audit.util.auditTools import write_file_change_log


def mergePaths(homePath: str, path: list):
    """
    合并目标路径
    :param homePath: Home路径
    :param path: 路径列表
    :return:
    """
    pathBuilder = None
    if homePath and path:
        for index, item in enumerate(path[1:]):
            if os.path.isabs(item):
                Log.warning("路径列表中有绝对路径")
                break
            if re.match(r".{1,2}[/\\]", item):
                Log.warning("路径列表中有返回上一级命令")
                break

            if index == 0:
                pathBuilder = os.path.join(homePath, item)
            else:
                pathBuilder = os.path.join(pathBuilder, item)
    # 如果没有，返回homePath
    else:
        pathBuilder = os.path.join(homePath)

    if pathBuilder is None:
        pathBuilder = os.path.join(homePath)

    return pathBuilder


# 获取文件列表
def getFileList(homePath: str, path: list = None) -> dict:
    """
    获取文件列表
    :param homePath: Home路径
    :param path: 路径列表
    :return:
    """
    pathBuilder = None
    pathList = []
    # 当data中有指定路径时
    if path:
        for index, item in enumerate(path[1:]):
            if os.path.isabs(item) or re.match(r".{1,2}[/\\]", item):
                Log.warning(f"非法的路径列表：{path}")
                break
            if index == 0:
                pathBuilder = os.path.join(homePath, item)
                pathList.append("/")
            else:
                pathBuilder = os.path.join(pathBuilder, item)
            pathList.append(item)
    # 如果没有，返回homePath
    else:
        pathBuilder = os.path.join(homePath)
        pathList.append("/")

    if pathBuilder is None:
        pathBuilder = os.path.join(homePath)
        pathList.append("/")

    listdir = os.listdir(pathBuilder)

    dirs = []
    files = []
    for item in listdir:
        itemPath = os.path.join(pathBuilder, item)
        ctime = datetime.fromtimestamp(os.path.getctime(itemPath)).strftime('%Y-%m-%d %H:%M:%S')
        mtime = datetime.fromtimestamp(os.path.getmtime(itemPath)).strftime('%Y-%m-%d %H:%M:%S')
        size = os.path.getsize(itemPath)
        if os.path.isdir(itemPath):
            dirs.append({"dirName": item, "dirSize": size, "ctime": ctime, "mtime": mtime})
        elif os.path.isfile(itemPath):
            files.append({"fileName": item, "fileSize": size, "ctime": ctime, "mtime": mtime})

    return {"action": "returnFileList", "data": {"path": pathList, "dirs": dirs, "files": files}}


# 新建文件
def createFile(file_path: str) -> bool:
    """
    新建文件
    :param file_path: 文件路径
    :return:
    """
    if not os.path.exists(file_path):
        try:
            with open(file_path, 'w'):
                Log.info("文件创建成功")
                return True
        except OSError as e:
            Log.error(f"文件创建失败\n{e}")
            return False
    else:
        Log.error("文件已存在")
        return False


# 删除文件与目录
def delFile(path: str) -> bool:
    """
    删除文件或目录
    :param path: 路径
    :return:
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            Log.info("目录删除成功")
            return True
        elif os.path.isfile(path):
            os.remove(path)
            Log.info("文件删除成功")
            return True
    else:
        Log.error("文件或目录不存在")
        return False


# 解码base64并保存
def receiveFiles(data: str, hash: str, base64Mode: bool = False):
    if not os.path.exists("temp"):
        os.mkdir("temp")

    if os.path.exists(os.path.join("temp", f"{hash}.temp")):
        Log.debug("文件已存在，跳过写入")
        return True

    if base64Mode:
        dataBytes = base64.b64decode(data.split(",")[1])
    else:
        dataBytes = data

    with open(os.path.join("temp", f"{hash}.temp"), "wb+") as f:
        md5 = hashlib.md5()
        md5.update(dataBytes)

        saveFileMd5 = md5.hexdigest()

        if saveFileMd5 == hash:
            Log.debug("文件块Md5验证成功")
            f.write(dataBytes)
            return True
        else:
            Log.warning(f"文件块Md5验证失败(发送时：{hash} 接收时：{saveFileMd5})")
            return False


def mergeFiles(homePath, path, filename, fileHash, chunksHash, refresh=None):
    """
    合并文件
    :param homePath: Home路径
    :param path: 路径列表
    :param filename: 输出文件名
    :param fileHash: 文件哈希
    :param chunksHash: 块哈希列表
    :param refresh: 刷新文件目录回调函数
    :return:
    """
    Log.debug("文件合并开始")
    md5 = hashlib.md5()
    saveFilePath = os.path.join(mergePaths(homePath, path), filename)
    with open(saveFilePath, "wb+") as saveFile:
        for chunkHash in chunksHash:
            tempFile = os.path.join("temp", f"{chunkHash}.temp")
            if not os.path.exists(tempFile):
                os.remove(saveFilePath)
                raise RuntimeError(f"文件合并失败，缺少块:{chunkHash}")
            with open(tempFile, "rb") as tempFileBytes:
                while True:
                    chunkBytes = tempFileBytes.read(8192)
                    if not chunkBytes:
                        break
                    md5.update(chunkBytes)
                    saveFile.write(chunkBytes)
            os.remove(tempFile)
    saveFileMd5 = md5.hexdigest()
    if saveFileMd5 == fileHash:
        Log.success(f"文件{filename}合并成功")
        if refresh:
            print("刷新文件列表")
            return refresh()
        else:
            return True
    else:
        Log.error(f"文件{filename}合并失败（MD5不一致 发送时：{fileHash} 接收时：{saveFileMd5}）")
        os.remove(saveFilePath)
        return False


# 获取文件编码
def getFileEncoding(path):
    with open(path, 'rb') as f:
        text = f.read()
    file_encoding = chardet.detect(text)['encoding']
    return file_encoding


# 移动文件或文件夹
def move(user_id, homePath, sourceFileDirectory, selectFiles, toDirectory):
    sourceFileDirectory = mergePaths(homePath, sourceFileDirectory)
    toDirectory = mergePaths(homePath, toDirectory)
    Log.debug(f"源文件目录：{sourceFileDirectory}\t目标文件：{selectFiles}\t目标目录：{toDirectory}")
    for item in selectFiles:
        if not os.path.exists(os.path.join(sourceFileDirectory, item)):
            Log.warning(f"文件{item}不存在，已跳过")
            continue
        if os.path.exists(os.path.join(toDirectory, item)):
            Log.warning(f"文件{item}在目标目录已存在，已跳过")
            continue
        shutil.move(os.path.join(sourceFileDirectory, item), toDirectory)
        write_file_change_log(user_id, "Move File", os.path.join(sourceFileDirectory, item)+"-->"+toDirectory)


# 复制文件或目录
def copy(user_id, homePath, sourceFileDirectory, selectFiles, toDirectory):
    sourceFileDirectory = mergePaths(homePath, sourceFileDirectory)
    toDirectory = mergePaths(homePath, toDirectory)
    Log.debug(f"源文件目录：{sourceFileDirectory}\t目标文件：{selectFiles}\t目标目录：{toDirectory}")
    for item in selectFiles:
        if not os.path.exists(os.path.join(sourceFileDirectory, item)):
            Log.warning(f"文件{item}不存在，已跳过")
            continue
        if os.path.exists(os.path.join(toDirectory, item)):
            Log.warning(f"文件{item}在目标目录已存在，已跳过")
            continue
        if os.path.isfile(os.path.join(sourceFileDirectory, item)):
            shutil.copy2(os.path.join(sourceFileDirectory, item), toDirectory)
            write_file_change_log(user_id, "Copy File", os.path.join(sourceFileDirectory, item)+"-->"+toDirectory)
        elif os.path.isdir(os.path.join(sourceFileDirectory, item)):
            shutil.copytree(os.path.join(sourceFileDirectory, item), os.path.join(toDirectory, item))
            write_file_change_log(user_id, "Copy Dir", os.path.join(sourceFileDirectory, item) + "-->" + toDirectory)


# 压缩
def compression(user_id, homePath, path, files, output, callback=None):
    def compress_item(zip_filename, item_path):
        """
        将文件或目录添加到zip文件中

        Parameters:
            zip_filename (str): zip文件名
            item_path (str): 要添加的文件或目录路径
        """
        with zipfile.ZipFile(zip_filename, 'a', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(item_path):
                zipf.write(item_path, os.path.basename(item_path))
            elif os.path.isdir(item_path):
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, item_path)
                        zipf.write(file_path, arcname)

    inputFilePath = mergePaths(homePath, path)
    outputFilePath = os.path.join(mergePaths(homePath, path), output)
    outputFilePath = outputFilePath if outputFilePath[-4:] == '.zip' else f'{outputFilePath}.zip'
    if os.path.exists(outputFilePath):
        Log.error("压缩文件已存在")
        return False
    for filename in files:
        if not os.path.exists(os.path.join(inputFilePath, filename)):
            Log.error(f"文件{filename}不存在，压缩被取消")
            return False
        else:
            compress_item(outputFilePath, os.path.join(inputFilePath,  filename))
            write_file_change_log(user_id, "Compression File", os.path.join(inputFilePath,  filename)+"-->"+outputFilePath)

    Log.success(f"文件{outputFilePath}压缩完成")
    if callback:
        callback()


# 解压
def decompress(user_id, homePath, path, files, outputPath=None, callback=None):
    inputFilePath = mergePaths(homePath, path)
    outputPath = mergePaths(homePath, [outputPath])
    Log.debug(outputPath)
    if outputPath is not None and not os.path.exists(outputPath):
        os.mkdir(outputPath)
        Log.info(f"输出文件夹{outputPath}不存在，已自动创建")

    # 如果输入
    for archiveName in files:
        if not os.path.exists(os.path.join(inputFilePath, archiveName)):
            Log.error(f"压缩包{archiveName}不存在，已取消解压任务")
            break
        if archiveName[-4:] != ".zip":
            Log.warning(f"文件{archiveName}不是支持的压缩包，已跳过")
        shutil.unpack_archive(os.path.join(inputFilePath, archiveName), outputPath)
        write_file_change_log(user_id, "Decompress File", os.path.join(inputFilePath, archiveName)+"-->"+outputPath)
        if callback:
            callback()