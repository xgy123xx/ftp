'''
用户信息存储数据结构
[用户名]
password = ''用md5制作
home_dir = '/home/用户名'
quota= 容量数   用户磁盘配额，可以MB为单位

[alex]
password = '123'
home_dir = '/home/alex'
quota= 3   用户有3MB空间

用户示例：
name:egon
password:123

name:alex
password:abc


功能：
命令格式：
get 1.txt  下载文件
put 2.txt  上传文件
pwd  查看当前目录cur_dir
ls   查看当前目录下的文件
ls /root 切换目录   先判断目录是否存在，再赋值cur_dir = home_dir + /root
user 查看用户信息


'''
from core.client import Client

def run():#主文件

    user_obj = Client()
    user_obj.login()#用户登录验证
    while True: # 用户选项交互
        for index,opt in enumerate(user_obj.user_menu,1):
            print('%d.%s'%(index,opt[0]))
        user_choice = input('>>:').strip()
        if user_choice == 'q':#单独处理退出函数
            user_obj.quit_handle()
            break
        if not user_choice.isdigit() or int(user_choice) <= 0 or int(user_choice) > len(user_obj.user_menu):
            print('输入错误，请重新输入！！')
            continue
        cmd = getattr(user_obj,user_obj.user_menu[int(user_choice)-1][1])() # 通过用户交互得到命令
        if not cmd:
            continue
        user_obj.exec_command(cmd)  # 将命令传给处理函数
        print('-'*20)
