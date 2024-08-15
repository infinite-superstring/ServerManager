# 面板端

Copyright © Infinite Superstring

## 编译与部署

### 使用自动安装脚本
```shell
    cd ServerManager-Panel
    sudo chmod +x setup.sh  # 给予安装脚本运行权限
    sudo ./setup.sh  # 开始安装
```

### 以Debug模式启动及调试项目
**拉取源码**

```shell
    # 克隆源码到本地
    git clone https://github.com/infinite-superstring/ServerManager-Panel.git
    cd ServerManager-Panel
    # 初始化子模块
    git submodule init
    git submodule update
```

**启动前端服务器**

```shell
    # 进入UI项目文件夹
    cd web_develop
    # 安装NodeJs依赖
    npm i
    # 运行开发服务器
    node run dev
```

**准备Python环境**

```shell
    # 回到上级目录
    cd ../
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
    python manage.py initial_data --force-init
    # ps: 忘记密码后可通过 python manage.py resetAdmin 重置密码
```

**运行后端服务器**

```shell
    python manage.py runserver 0.0.0.0:8000
```
