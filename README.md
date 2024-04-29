## 编译与部署

**拉取源码**

```shell
    # 克隆源码到本地
    git clone https://github.com/Pigeon-Server/PigeonKVM.git
    cd PigeonKVM
```

**编译用户界面**

```shell
    # 进入UI项目文件夹
    cd web_develop
    # 安装NodeJs依赖
    npm i
    # 将静态文件编译到指定文件夹
    npm run buildToStatic
    # 返回主目录
    cd ../
```

**准备Python环境**

```shell
    # 新建虚拟环境
    python -m venv venv
    # 进入虚拟环境
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate  # Linux
    # 安装依赖
    pip3 install -r requirements.txt
```

**初始化数据库**
```shell
    # 生成数据表
    python manage.py makemigrations
    # 创建数据库文件 
    python manage.py migrate
    # 初始化数据库数据
    python manage.py initial_data
```

### 以Debug模式启动项目
```shell
    python manage.py runserver 0.0.0.0:8080 --noreload
```
