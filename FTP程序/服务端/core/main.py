'''
    服务端
多线程
('139.199.32.236',7653)
'''
from core.serve import Server
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import queue
import socket
MAX_THREAD_SIZE = 3
server_addr = ('127.0.0.1',8080)

def accept_client(client_q): #不断的接待客户，将客户放入队列
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(server_addr)
    server.listen(5)
    print('server connected')
    while True:
        client,conn_addr = server.accept()
        print('succeed connect ', conn_addr)
        client_q.put({'client':client,'client_addr':conn_addr})
    server.close()

def run():
    client_queue = queue.Queue(MAX_THREAD_SIZE)
    executor = ThreadPoolExecutor(MAX_THREAD_SIZE)
    t = Thread(target=accept_client,args=(client_queue,))
    t.daemon = True  #主线程执行完，接待程序就结束
    t.start()
    while True:
        client_dict = client_queue.get() #不断从队列中得到客户
        server_obj = Server(client_dict['client'],client_dict['client_addr'])
        executor.submit(server_obj.connect)




