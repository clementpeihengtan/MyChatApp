from socket import *
import select
import threading
import sys
import re

thread_array = []   # all threads
client_info = {}    # client information
client_name = {}    #associate client name and address
connection_list = []
active_client = [] #active client
list_filenames = {}

def p2p_put(filename, clientID):
    list_filenames[clientID+"?"+filename] = filename

def file_list():
    s = "\n";
    for file in list_filenames:
        s+=(list_filenames[file]+"------"+file+"\n")
    return s

def getpeerinfo(fileID):
    res = []
    for file in list_filenames:
        if(file == fileID):
            clientID = fileID.split('?', 1)[0]
            for conn in client_name:
                if (client_name[conn] == clientID):
                    res.append(conn[0])
                    res.append(conn[1])
                    res.append(list_filenames[fileID])
                    return res
    return res


def clist_active():
    temp = ""
    for client in active_client:
        temp+=client+","
    return temp+"\n"

def loaduser(userlists):    # load all the user information from the file
    with open(userlists) as fp:
        for line in fp:
            user = line.strip().split(',')
            client_info[user[0]] = user[1]

def broadcast(soc, msg):
    for sock in connection_list:
        if sock != serversocket and sock != soc:
            try:
                sock.send(msg)
            except:
                sock.close()
                connection_list.remove(sock)

def checkuser(register, username, password):
    if (register == "REGISTER"):
        for key in client_info:
            if key == username:
                return 0x02 #duplucate ID
        client_info[username] = password
        f = open("UserDetails.txt","a")
        f.write(username+","+password+"\n")
        f.close()
        return 0x00     #success
    elif (register == "LOGIN"):
        for key in client_info:
            if key == username:
                if client_info[key] == password:
                    return 0x00 #success
                else:
                    return 0x01 #access denied, invalid password
        return 0x01
    else:
        return 0x01

def run_thread(conn, addr):
    while(1):
        try:
            data = conn.recv(recv_buf)
            if "".join(data.strip()) == "CLIST":
                msg = clist_active()
                try:
                    conn.send(msg)
                except:
                    conn.close()
            elif "".join(data.strip()) == "DISCONNECT":
                broadcast(conn, "%s is offline\n" % client_name[addr])
                print "Client (%s %s) is offline" % addr
                connection_list.remove(conn)
                active_client.remove(client_name[addr])
                conn.close()
            elif "".join(data.strip()) == "FPUT":
                filename = ""
                try:
                    filename = conn.recv(4096);
                    # list_filename.append(filename)
                    conn.send("ACK")
                    p2p_put(filename, client_name[addr])
                except:
                    print "fail to write"

            elif "".join(data.strip()) == "FLIST":
                msg = file_list()
                try:
                    conn.send(msg)
                except:
                    conn.close()
            elif data.split(' ', 1)[0] == "MSG":
                broadcast(conn, "\r" + client_name[addr] + ':'+ data.split(' ', 1)[1])
            elif "".join(data.strip()) == "FGET":
                fileID = ""
                try:
                    fileID = conn.recv(4096)
                    if fileID:
                        info = getpeerinfo(fileID.strip())
                        if not info:
                            conn.send("0x03")
                        else:
                            s = " ".join(str(x) for x in info)
                            print s
                            conn.send(s)
                            # THIS IS THE PROBLEM , regarding converting info to string
                            print "0x00 send successfully"
                except:
                    print "fail to write"
        except:
            conn.close()
            break


if __name__ == "__main__":
    recv_buf = 4096
    PORT = 8080

    if(len(sys.argv) < 2):
        print "User list is not included"
        sys.exit()
    loaduser(sys.argv[1]) # call loaduser information

    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversocket.bind(('localhost', PORT))
    serversocket.listen(5)

    connection_list.append(serversocket)

    print "Char server is starting up" + str(PORT)

    while(1):
        # read_sockets, write_socket, error_socket = select.select(connection_list,[],[])
        # for sock in read_sockets:
        #     if sock == serversocket:
                conn, addr = serversocket.accept()
                if conn not in connection_list:
                    try:
                        userinfo = conn.recv(4096)
                        userinfo = userinfo.split(',')
                        if not userinfo:
                            break
                        elif checkuser(userinfo[0], userinfo[1], userinfo[2]) == 0x00:
                            active_client.append(userinfo[1])
                            client_name[addr] = userinfo[1];
                            conn.send("SUCCESS")
                            print "Client (%s, %s) connected" % addr
                            broadcast(conn, "[%s] entered room\n" % client_name[addr])
                        elif checkuser(userinfo[0], userinfo[1], userinfo[2]) == 0x01:
                            conn.send("INVALID")
                            conn.close()
                            # continue
                        elif checkuser(userinfo[0], userinfo[1], userinfo[2]) == 0x02:
                            conn.send("DUPLICATE")
                            conn.close()
                            # continue

                    except KeyboardInterrupt:
                        # sys.exit()
                        # conn.send("false")
                        conn.close()

                connection_list.append(conn)

                thread_array.append(threading.Thread(target = run_thread, args=(conn,addr)).start())

    for thread in thread_array:
        thread.join()
    serversocket.close()
