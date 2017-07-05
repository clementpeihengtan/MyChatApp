from socket import *
import select
import sys
import string
import errno
import threading

def getinfo():
    regis_or_signin = raw_input("REGISTER OR SIGN_IN::\n")
    if(regis_or_signin == "REGISTER") :
        sys.stdout.write("---REGISTER---\n")
        user_name = raw_input("Username: ")
        password = raw_input("Password: ")
    elif(regis_or_signin == "LOGIN"):
        sys.stdout.write("---SIGN IN---\n")
        user_name = raw_input("Username: ")
        password = raw_input("Password: ")
    else:
        user_name = "notusername"
        password = "nopassword"
        sys.stdout.write("0xFF INVALID COMMAND\n")

    userinfo = regis_or_signin + ',' +user_name+','+password
    return userinfo

def getfileID():
    fileID = raw_input("Enter filename: ")
    return fileID

def p2pget(conn, port, filename):
    soc = socket.socket()
    soc.connect((conn, port))
    msg = "GET "+filename
    soc.send(msg)
    print "reach here successfully to other client"
    with open("testing_send.txt", 'rb') as filename:
        while(1):
            data = soc.recv(4096)
            if not data:
                break
            filename.write(data)
    filename.close()
    print "0x00 Get successfully"
    soc.close()

def handle_p2p_request(s):
    data = ""
    while(1):
        data = s.recv(4096)
        if not data:
            continue
        else:
            break
    if data.split(' ',1)[0] == "GET":
        with open(data.split(' ',1)[1], 'rb') as filename:
            for data in filename:
                s.send(data)
        print "0x00 Send successfully"

def waitthread(s):
    addr = s[0]
    PORT = s[1]
    file_tran_soc = socket(AF_INET, SOCK_STREAM)
    file_tran_soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # print s
    file_tran_soc.bind( (addr, PORT) )
    file_tran_soc.listen(5)
    # s.listen(5)
    while(1):
        conn, addr = file_tran_soc.accept()
        if conn != file_tran_soc:
            continue
        handle_thread = threading.Thread(target = handle_p2p_request, args=(conn,)).start()

def getfilename():
    filename = raw_input("Enter file name: ")
    return filename

def listoutclient(msg):
    msg = msg.strip().split(',')
    for client in msg:
        print sys.stdout.write(client)

def prompt():
    sys.stdout.write('You: ')
    sys.stdout.flush()

if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print 'usage : python telnet.py hostname'
        sys.exit()
    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(2)

    try:
        s.connect((host,port))
    except:
        print "Failed to connect"
        sys.exit()

    user_info = getinfo()
    s.send(user_info)
    while(1):
        try:
            reply = s.recv(4096)
            if not reply:
                break
            elif reply.strip() == "SUCCESS":
                print "0x00 Login Successfully"
                break
            elif reply.strip() == "DUPLICATE":
                print "0x02 User name already exist"
                s.close()
                sys.exit()
            elif reply.strip() == "INVALID":
                print "0xFF Incorrect information"
                s.close()
                sys.exit()
        except:
                print "0x04 Failed to login"
                sys.exit()
                s.close()
                break

    print "0x00 Connected to remote host, proceed to send message"
    prompt()

    while(1):
        socketlist = [sys.stdin, s]
        read_sockets, write_socket, error_socket = select.select(socketlist, [], [])

        for sock in read_sockets:
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print "Disconnected from server"
                    sys.exit()
                elif data.strip() == "ACK":
                    prompt()
                else:
                    sys.stdout.write(data)
                    prompt()
            else:
                msg = sys.stdin.readline()
                s.send(msg)
                if msg.strip() == "DISCONNECT":
                    print "Disconnected from the chat"
                    sys.exit()
                elif msg.strip() == "FPUT":
                    filename = getfilename()
                    s.send(filename)
                    print "0x00 Send successfully"
                    t = threading.Thread(target = waitthread, args = (s.getpeername(),))
                    t.start()
                elif msg.split(' ', 1)[0] == "MSG":
                    sys.stdout.write("You: "+msg.split(' ', 1)[1])
                    prompt()
                elif msg.strip() == "FGET":
                    fileID = getfileID()
                    s.send(fileID)
                    try:
                        data = s.recv(4096)
                        if not data:
                            print "error receiving info of client"
                        elif data.strip() == "0x03":
                            print "0x03 Invalid file ID"
                            prompt()
                        else:
                            info = data.split(' ')
                            p2pget(info[0], int(info[1]), info[2])
                            prompt()
                    except:
                        print "fail to receive data"
                else:
                    prompt()
