import socket
import sys


def start_tcp_server(ip, port):
    print('web server start')
    #create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    #bind port
    sock.bind(server_address)
    #starting listening, allow only one connection
    try:
        sock.listen(1)
    except:
        sys.exit(1)
    while True:
        client, addr = sock.accept()
        print('get new sock')
        client_data = client.recv(1024)
        print(client_data.decode('utf-8'))
        client.close()

if __name__ == '__main__':
    start_tcp_server('127.0.0.1', 2002)
