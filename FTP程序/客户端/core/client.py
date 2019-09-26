import socket
import json
import struct
import hashlib
import os
from settings.setting import *
class Client:
    """
因为传给服务端只通过命令形式
两个接口

命令接口：
用户交互接口：

测试用户
alex    abc

    """
    user_menu = [('查看个人信息','interact_userinfo'),('查看目录下所有文件','interact_ls'),
                 ('查看当前位置','interact_pwd'),('切换目录','interact_cd'),('上传文件','interact_put'),
                 ('下载文件','interact_get')]
    server_addr = ('127.0.0.1',8080)
    down_load_dir = DOWNLOAD_DIR
    cmd_dict = {'get': 'get_handle', 'put': 'put_handle', 'pwd': 'pwd_handle', 'ls': 'ls_handle',
                'userinfo': 'userinfo_handle','cd': 'cd_handle'}

    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect(self.server_addr)
        print('Connected server ')

    def __del__(self):
        self.client.close()

    def exec_command(self, cmd):  # 语句分析函数
        cmd_name = cmd.split()[0]
        cmd_args = cmd.split()[1:]
        if cmd_name in self.cmd_dict.keys():
            self.client.send(cmd.encode('utf-8'))  # 发送命令给服务器
            getattr(self, self.cmd_dict[cmd_name])(*cmd_args)  # 执行cmd_dict命令
        else:
            print('命令不存在')
            return False

    # 处理函数
    def receive_header(self):  # 接受报头函数
        #  1.接受4字节报头长度
        #  2.接受报头
        header_length = self.client.recv(4)
        header_json_length = struct.unpack('i',header_length)[0]
        header_json = self.client.recv(header_json_length)
        header = json.loads(header_json.decode('utf-8'))
        return header

    def send_header(self,header_dic):  # 发送报头函数
        #  1.发送4字节报头长度
        #  2.发送报头
        header_json = json.dumps(header_dic)
        header_json_length = struct.pack('i',len(header_json.encode('utf-8')))
        self.client.send(header_json_length)
        self.client.send(header_json.encode('utf-8'))

    def print_process(self,total_size,process_info):#用来打印进度信息
        #  传入总大小，当前进度
        #  一共有10个*  进度按百分比显示
        process_str = '*'*int(process_info/10)
        print('总大小：%s,当前进度：%s %s%%' % (total_size,process_str.ljust(10),process_info))

    # 命令处理函数
    def get_handle(self, filename):  # 下载文件
        header = self.receive_header()
        if header['exist_flag']:                                # 判断服务端文件是否存在
            file_mode = 'wb'
            file_size = header['file_size']                     # 服务端文件大小
            file_dir = '%s\\%s'% (self.down_load_dir, filename)  # 客户端文件下载位置
            file_pos = 0                                           # 文件光标位置
            file_md5 = hashlib.md5()
            # 断点续传
            if os.path.exists(file_dir) and os.path.getsize(file_dir) <= file_size:
                #  查看本地是否有该文件,且小于服务端大小
                choice = input('文件已存在，是否继续原来的下载(yes,no)>>:').strip()
                if choice == 'yes':
                    file_mode = 'ab'
                    with open(file_dir,'rb') as f:
                        for line in f:
                            file_md5.update(line)
                        file_pos = f.tell()

            self.send_header({'file_pos': file_pos})        # 制作报头，告诉服务器是否要断点续传
            with open(file_dir,file_mode) as f:
                date_size = file_pos                        # 记录传输过程中总文件大小
                process_info = int(date_size*100/file_size)  # 记录进度
                self.print_process(file_size,process_info)
                while date_size < file_size:                # 开始传输文件
                    date = self.client.recv(1024)
                    f.write(date)
                    date_size += len(date)
                    file_md5.update(date)
                    # 进度信息
                    if process_info != int(date_size*100/file_size):
                        process_info = int(date_size*100/file_size)
                        self.print_process(file_size, process_info)
                # 验证md5
                if file_md5.hexdigest() != header['md5']:
                    print('文件md5错误！')
                    os.remove(file_dir)
            print('%s 文件下载成功'% filename)
        else:
            print('文件不存在')

    def put_handle(self,filename):  # 上传文件
        # 将文件信息发给服务端
        file_dir = '%s\\%s' % (self.down_load_dir, filename)
        file_size = os.path.getsize(file_dir)
        with open(file_dir,'rb') as f:
            file_md5 = hashlib.md5()
            for line in f:
                file_md5.update(line)
        header_dic = { 'md5': file_md5.hexdigest(), 'file_size': file_size}
        self.send_header(header_dic)
        file_pos = self.receive_header()['file_pos']  # 接受文件的位置

        if self.receive_header()['quota_flag']:  # 接受服务器检查用户配额结果
            with open(file_dir,'rb') as f:
                f.seek(file_pos)
                date_size = file_pos
                process_info = int(date_size*100/file_size)  # 记录进度
                self.print_process(file_size,process_info)
                for line in f:
                    self.client.send(line)
                    date_size += len(line)
                    if process_info != int(date_size*100/file_size):
                        process_info = int(date_size*100/file_size)
                        self.print_process(file_size,process_info)
            if self.receive_header()['md5_flag']:
                print('%s 文件上传成功'% filename)
            else:
                print('文件md5错误！')
        else:
            print('用户配额不够')

    def pwd_handle(self):  # 查看当前位置
        # pwd     查看当前目录cur_dir
        pwd_dic = self.receive_header()
        print('当前位置为',pwd_dic['cur_dir'])
        return True

    def quit_handle(self):#退出
        self.client.send('exit'.encode('utf-8'))

    def ls_handle(self,*args):  # 查看当前目录下的文件  非固定参数
        # ls        查看当前目录下的文件
        # ls test1  查看家目录下test1
        ls_dic = self.receive_header()
        if ls_dic['result_flag']:  # 判断命令是否执行成功
            list_dir = ls_dic['listdir']
            for content in list_dir:
                print(content)
        else:
            print('输入的路径不存在')

    def userinfo_handle(self):  # 查看用户信息
        user_str = '''
                用户信息
    用户姓名：%s
    用户当前容量：%.2f MB
    用户剩余容量：%.2f MB
    用户家目录：%s
    当前用户所在目录：%s
        '''
        # user 查看用户信息
        userinfo = self.receive_header()
        # 打印用户信息
        #userinfo字典 {'name':'egon','cur_dir':'hone/egon','quota':500,'type':'userinfo}
        print(user_str % (userinfo['name'],userinfo['quota'],userinfo['leave_space'],userinfo['home_dir'],userinfo['cur_dir']))
        return True

    def cd_handle(self,*args):  # 切换用户目录
        # cd 切换到家目录
        # cd test1   切换到用户目录下test1目录
        cd_dic = self.receive_header()
        if cd_dic['result_flag']:  # 判断命令是否执行成功
            print('切换成功')
            print('当前位置为',cd_dic['cur_dir'])
        else:
            print('输入的路径不存在')

    # 用户交互函数 将交互得到的信息转换成命令，以方面发送给服务端
    def interact_get(self):#下载文件
        print('当前操作：下载文件')
        filename = input('filename>>:').strip()
        if not filename:
            print('文件名不能为空')
            return False
        cmd = 'get %s' % filename
        return cmd

    def interact_put(self):
        print('当前操作：上传文件')
        filename = input('filename>>:').strip()
        if not filename:
            print('文件名不能为空')
            return False
        file_dir = '%s\\%s' % (self.down_load_dir, filename)
        if os.path.exists(file_dir) or os.path.isfile(file_dir):
            return 'put %s' % filename
        else:
            print('文件不存在')
            return False

    def interact_pwd(self):
        print('当前操作：查看当前位置')
        return 'pwd'

    def interact_ls(self):
        print('当前操作：查看指定目录下所有文件')
        print('(直接敲回车则查看当前目录)')
        file_path = input('path>>:').strip() # 目录可以为空
        if file_path and file_path[0] != '\\': # 自动补全反斜杠
            file_path = '\\' + file_path
        return 'ls %s' % file_path

    def interact_userinfo(self):
        print('当前操作：查看用户信息')
        return 'userinfo'

    def interact_cd(self):  # 切换目录
        print('当前操作：切换目录')
        print('(直接敲回车则回到家目录)')
        file_path = input('path>>:').strip() # 目录可以为空
        if file_path and file_path[0] != '\\': # 自动补全反斜杠
            file_path = '\\' + file_path
        return 'cd %s' % file_path

# 客户端登陆程序
    def login(self):#用户登录
        '''
        用户登录过程：
        1.先写一个三次登录
        2.然后登录时，将用户名和密码发送给服务器，服务器处理
        3。收到服务器的回应，然后判断用户是否登录成功
            3.1 登录成功退出循环
            3.2 登录失败，判断是否超过次数

        发送报头-》发送用户名密码字典
        :return:
        '''
        print('欢迎登录FTP客户端')
        count = 0
        while count < 3:
            name = input('name:').strip()
            password = input('password:').strip()
            if not name or not password:
                print('用户名或密码不能为空')
                continue
            #将用户名，密码md5的字典发给服务器
            password_md5 = hashlib.md5()
            password_md5.update(password.encode('utf-8'))
            user_info = {'name': name,'password': password_md5.hexdigest()}
            self.send_header(user_info) # 发送用户信息报头
            result_dict = self.receive_header()  # 接收服务器结果
            if result_dict['name'] == name and result_dict['login_result']:
                print('欢迎登录',name)
                return name
            else:
                print('用户名或密码错误,请重试')
                count += 1
        else:
            print('错误次数过多')
            exit()


