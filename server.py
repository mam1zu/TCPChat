import socket
import threading
import sys
import __main__

PORT = 56564
BUFSIZE = 4096
clist = []
cnamedic = {}
threadflag = True

print("ソケット作成")
srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("ソケットバインド")
srvsock.bind(("", PORT))

print("ソケット listen状態")
srvsock.listen()


def srv_commandline():
    # サーバーのコマンド入力を処理する関数　Thread化する
    while threadflag:

        cmd = input()

        if cmd == "stop":
            if not srvsock.fileno() == -1 :
                srvsock.close()
            if not len(clist) == 0:

                for c in clist:
                    c.send("SRVCLS".encode("utf-8"))
                    c.close()
                    cnamedic.pop(c)

                clist.clear()

            __main__.threadflag = False
            sys.exit()
        elif cmd.startswith("/msg"):
            if cmd == "/msg" :
                print("/msg 内容 で発言")
                continue
            cmd = cmd.removeprefix("/msg")
            for c in clist:
                c.send(("MSG:|ServerAdmin| "+cmd).encode("utf-8"))

def logout(client, address) :

    clist.remove(client)
    cnamedic.pop(address)



def broadcast(client, address):
    print("broadcast スレッド開始")
    # クライアントからのメッセージを受け取ってほかの人に送信するプログラム Thread化する

    while threadflag:

        msg = client.recv(BUFSIZE).decode("utf-8")

        if msg.startswith('MSG:'):

            msg = msg.removeprefix("MSG:")

            print("<" + str(cnamedic[address]) + ">" +msg)

            for c in clist:
                sendmsg = "MSG:<"+str(cnamedic[address])+">"+msg
                sendmsg = sendmsg.encode("utf-8")
                c.send(sendmsg)
        elif msg == "QUIT":
            clist.remove(client)
            print(cnamedic[address] + "がログアウトしました")
            cnamedic.pop(address)
            client.send("CONCLS".encode("utf-8"))
            client.close()
        else:
            client.send("Message Refused - Something went wrong with your message\n".encode("utf-8"))


cmdlinethread = threading.Thread(target=srv_commandline, daemon=True, name="cmdline")
cmdlinethread.start()
print("コマンドライン起動")
while True:

    print("受付待機中")

    client, address = srvsock.accept()
    print("受付 - ", client)

    msg = client.recv(BUFSIZE).decode("utf-8")
    print("受信")

    if msg == "QUIT":
        clist.remove(client)
        client.close()
        continue

    client.send("OK\n".encode("utf-8"))
    username = client.recv(BUFSIZE).decode("utf-8")

    if not username.startswith("USERNAME:"):

        client.send(
            "Connection will be continued - You didn't send your USERNAME, so join as anonymous\n".encode("utf-8"))
        cnamedic[address] = "Anonymous"

    else:
        username = username.removeprefix("USERNAME:")
        print(username)
        client.send(("USERNAME OK - " + username + "\n").encode("utf-8"))

        cnamedic[address] = username
        print(cnamedic[address])

    clist.append(client)

    # threading_processに情報をわたし、それ以降の処理は非同期処理を行う。引数はclient,addressを渡す。
    # closeをしないうちにプログラムが終了してはいけないので、Daemon=Falseとして非デーモンプロセスとする。
    # 同一IPからのアクセスを想定せずに設計するため、スレッドの識別としてのスレッド名に接続先のIPアドレスを利用する。
    bcthread = threading.Thread(target=broadcast, args=(client, address,), daemon=True, name=address)

    bcthread.start()
