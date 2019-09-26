import socket
import json
import struct
import hashlib
import os
import configparser
from settings.setting import *
class Server:
    """
    服务端
为了多线程，不要记录客户端套接字，以传入参数的形式


上传文件
查看当前位置
查看文件
查看用户信息
切换路径
    """
    home_dir = ''           # 用户家目录
    cur_dir = ''            # 用户当前目录
    name = ''               # 记录用户姓名  方面查找数据库用
    cmd_dict = {'get': 'get_handle', 'put': 'put_handle', 'pwd': 'pwd_handle', 'ls': 'ls_handle',
                'userinfo': 'userinfo_handle','cd': 'cd_handle'}

    def __init__(self,client,addr):
        self.client = client  #记录客户端套接字
        self.client_addr = addr

    def exec_command(self,cmd):  # 语句分析函数
        print(cmd)
        cmd_name = cmd.split()[0]
        cmd_args = cmd.split()[1:]
        if cmd_name in self.cmd_dict.keys():
            getattr(self, self.cmd_dict[cmd_name])(*cmd_args)
        else:
            return False

# 报头处理函数

    def receive_header(self):  # 接受报头
        header_length = self.client.recv(4)
        header_json_length = struct.unpack('i',header_length)[0]
        header_json = self.client.recv(header_json_length)
        header = json.loads(header_json.decode('utf-8'))
        return header

    def send_header(self, header_dic):  # 发送报头
        header_json = json.dumps(header_dic)
        header_json_length = struct.pack('i', len(header_json.encode('utf-8')))
        self.client.send(header_json_length)
        self.client.send(header_json.encode('utf-8'))

# 命令处理函数
    def get_handle(self, filename):  # 下载文件
        # header_dic = {'filename': filename, 'md5': file_md5.hexdigest(), 'file_size': file_size,exidt_flag:true}
        # 制作报头
        file_dir = '%s\\%s' % (self.cur_dir,filename)
        if os.path.exists(file_dir) and os.path.isfile(file_dir):  # 判断文件是否存在  且不能为路径名
            file_size = os.path.getsize(file_dir)
            with open(file_dir,'rb') as f:
                file_md5 = hashlib.md5()
                for line in f:
                    file_md5.update(line)
            header_dic = {'filename': filename, 'md5': file_md5.hexdigest(), 'file_size': file_size,
                          'exist_flag': True}
            self.send_header(header_dic)
            # 接受客户端信息,确定文件从哪个位置开始传
            file_pos = self.receive_header()['file_pos']
            with open(file_dir,'rb') as f:
                f.seek(file_pos)
                for line in f:
                    self.client.send(line)
            print('%s 文件下载成功' % filename)
        else:
            header_dic = {'filename': filename,'exist_flag': False}
            self.send_header(header_dic)

    def put_handle(self,filename):  # 上传文件
        header = self.receive_header()
        file_size = header['file_size']
        file_dir = '%s\\%s' % (self.cur_dir, filename)
        file_pos = 0                            #文件光标的初始位置
        file_md5 = hashlib.md5()
        file_mode = 'wb'
        if os.path.exists(file_dir) and os.path.isfile(file_dir) and os.path.getsize(file_dir) <= file_size:
            with open(file_dir,'rb') as f:
                file_mode = 'ab'
                for line in f:
                    file_md5.update(line)
                file_pos = f.tell()
        self.send_header({'file_pos': file_pos})  # 将文件位置发送给客户端

        if (file_size-file_pos)/1024/1024 + self.home_dir_size > self.quota :  # 检查用户配额够不够
            self.send_header({'quota_flag': False})
            return False
        else:
            self.send_header({'quota_flag': True})

        with open(file_dir,file_mode) as f:  # 传输文件
            date_size = file_pos
            while date_size < file_size:
                date = self.client.recv(1024)
                f.write(date)
                date_size += len(date)
                file_md5.update(date)

        if file_md5.hexdigest() != header['md5']:  # 验证md5
            print('文件md5错误！')
            os.remove(file_dir)
            self.send_header({'md5_flag':False})
        else:
            print('%s 文件上传成功' % file_dir)
            self.send_header({'md5_flag':True})

    def pwd_handle(self):  # 查看当前位置
        pwd_dic = {'cur_dir':self.cur_dir}
        self.send_header(pwd_dic)

    def ls_handle(self,*args):  # 查看当前目录下的文件  非固定参数
        # ls        查看当前目录下的文件
        # ls test1  查看当前目录test1
        # 字典格式 {'result_flag':'true','listdir':[....]}
        ls_dir = self.cur_dir
        if len(args):
            ls_dir += args[0]
        if os.path.exists(ls_dir) and os.path.isdir(ls_dir):  # 判断文件是否存在
            list_dir = os.listdir(ls_dir)
            result_flag = True
        else:
            list_dir = []
            result_flag = False
        ls_dic = {'result_flag': result_flag,'listdir': list_dir}  # 制作数据
        self.send_header(ls_dic)  # 发送数据

    def userinfo_handle(self):  # 查看用户信息
        #user 查看用户信息
        userinfo_dic = {'name':self.name,'cur_dir':self.cur_dir,'quota':self.quota,
                        'leave_space': self.quota-self.home_dir_size,'home_dir':self.home_dir}  # 制作用户信息字典
        self.send_header(userinfo_dic)  # 将字典发送给客户端

    def cd_handle(self,*args):  # 切换用户目录
        # cd 切换到家目录
        # cd test1   切换到用户目录下test1目录
        if len(args):
            cd_dir = self.cur_dir + args[0]
        else:
            cd_dir = self.home_dir
        if os.path.exists(cd_dir) and os.path.isdir(cd_dir):  # 判断文件是否存在
            self.cur_dir = cd_dir
            result_flag = True
        else:
            result_flag = False
        cd_dic = {'result_flag': result_flag, 'cur_dir': self.cur_dir}  # 制作数据
        self.send_header(cd_dic)  # 发送数据

#获取文件夹大小
    @property
    def home_dir_size(self):
        #  遍历文件夹使用os.walk函数
        size = 0
        user_dir = self.home_dir
        for root, dirs, files in os.walk(user_dir):
          size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size/1024/1024

# 服务器接受登陆程序
    def login(self):
        '''
        返回客户端 {'name':name,'login_result':False}
        :return:
        '''
        count = 0
        user_config = configparser.ConfigParser()
        user_config.read(DB_DIR)
        while count < 3:
            # 接受报头
            user_account = self.receive_header()
            user_name = user_account['name']
            user_password = user_account['password']
            # 读取数据库信息
            if user_name in user_config and user_config[user_name]['password'] == user_password:
                result_dict = {'name': user_name,'login_result': True}
                self.send_header(result_dict)
                self.home_dir = user_config[user_name]['home_dir']
                self.cur_dir = self.home_dir
                self.name = user_name
                self.quota = int(user_config[user_name]['quota'])
                return True
            else:  # 用户名或密码错误，返回错误信息
                result_dict = {'name': user_name,'login_result': False}
                self.send_header(result_dict)
                count += 1
        else:
            return False

# 服务器与客户端连接程序
    def connect(self):
        client_exit_flag = False  # 客户端退出标志
        while not client_exit_flag:
            try:
                # 处理用户登录
                logined_flag = self.login()
                if not logined_flag:
                        client_exit_flag = True
                else:
                    # 处理客户端传来的命令
                    cmd = ''
                    while cmd != 'exit':
                        cmd = self.client.recv(1024).decode('utf-8')
                        print(self.client_addr,'收到命令：',cmd)
                        if cmd == 'exit':  # 处理退出函数
                            client_exit_flag = True
                            break
                        self.exec_command(cmd)
            except ConnectionResetError:
                break
            except ConnectionAbortedError:
                break
        print('connect out ', self.client_addr)
        self.client.close()