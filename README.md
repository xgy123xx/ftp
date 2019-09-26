作者：徐光宇
程序介绍：
        简单的FTP程序，支持多线程，上传下载，断点续传.
程序结构：
├─客户端
│  ├─bin    #客户端执行文件目录
│  │      ftp_client.py  #执行文件
│  │      __init__.py
│  │
│  ├─core  #主程序逻辑
│  │  │  client.py  #客户端类
│  │  │  main.py    #客户端主逻辑交互程序
│  │  │  __init__.py
│  │  │
│  │  └─__pycache__
│  │          client.cpython-36.pyc
│  │          main.cpython-36.pyc
│  │          __init__.cpython-36.pyc
│  │
│  ├─db #用于数据存储的地方
│  │  │  __init__.py
│  │  │
│  │  └─down_load  #客户端下载目录
│  │          1.mp3
│  │          2.mp3
│  │          2.txt
│  │
│  └─settings  #配置文件目录
│      │  setting.py  #配置文件
│      │  __init__.py
│      │
│      └─__pycache__
│              setting.cpython-36.pyc
│              __init__.cpython-36.pyc
│
└─服务端
    ├─bin  #服务端执行文件目录
    │      ftp_server.py  #服务端执行文件
    │      __init__.py
    │
    ├─core  #主程序逻辑
    │  │  main.py  #服务端主逻辑交互程序
    │  │  serve.py  #服务端类
    │  │  __init__.py
    │  │
    │  └─__pycache__
    │          main.cpython-36.pyc
    │          serve.cpython-36.pyc
    │          __init__.cpython-36.pyc
    │
    ├─db  #用于数据存储地方
    │  │  config.ini
    │  │  __init__.py
    │  │
    │  └─home  #存储用户文件
    │      ├─alex  #alex用户目录
    │      │      1.txt
    │      │
    │      └─egon  #egon用户目录
    │          │  1.txt
    │          │  2.mp3
    │          │  2.txt
    │          │
    │          ├─test1
    │          │      3.jpg
    │          │
    │          └─test2
    │                  TV.exe
    │
    └─settings #配置文件目录
        │  setting.py #配置文件
        │  __init__.py
        │
        └─__pycache__
                setting.cpython-36.pyc
                __init__.cpython-36.pyc