import socket
import threading
import sys

import main

PORT = 56564
BUFSIZE = 4096
threadflag = True
USERNAME = "Mamizu"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("localhost", PORT))

sock.send('HELO\n'.encode("utf-8"))
print("send : HELO")
print("recv : ", sock.recv(BUFSIZE).decode("utf-8"))

print("send: USERNAME:", USERNAME)
sock.send(("USERNAME:"+USERNAME).encode())
print("recv:", sock.recv(BUFSIZE).decode("utf-8"))



#サーバーからのメッセージを受付する部分
def threading_process() :

    print("分岐プロセス:受信側 開始")

    while threadflag:

        msgfromsrv = sock.recv(BUFSIZE).decode("utf-8")

        if msgfromsrv == "SRVCLS":

            print("サーバーはクローズしました")

            main.threadflag = False
            sock.close()
        elif msgfromsrv == "CONCLS":

            print("切断されました")

            main.threadflag = False


        elif msgfromsrv.startswith("MSG:") :

            print(msgfromsrv.removeprefix("MSG:"))

        else :
            print("AN ERROR HAS OCCURRED")

    if not threadflag: sys.exit()

t = threading.Thread(target=threading_process, daemon=True)
t.start()

print("メインプロセス:送信側 開始")

while True:

    msg = input()
    if sock.fileno() == -1:
        print("サーバーは既にクローズしています")
        print("プログラムを終了します")
        sys.exit()
    if msg == "" : continue

    if msg == "QUIT" :

        if sock.fileno() == -1 :

            #ソケットはすでに閉じられている
            print("サーバーとの接続はすでに切断されています")
            threadflag = False
            sys.exit()

        else :
            sock.send(msg.encode("utf-8"))
            print(sock.recv(BUFSIZE).decode("utf-8"))
            sock.close()
            threadflag = False
            sys.exit()

    sendmsg = "MSG:" + msg
    sock.send(sendmsg.encode('utf-8'))
