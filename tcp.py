import socket

TCP_IP = 'localhost'
TCP_PORT = 5555
BUFFER_SIZE = 16
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Fix 'Address already in use' error
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def server():
    print('Start server on {}:{}...'.format(TCP_IP, TCP_PORT))
    s.bind((TCP_IP, TCP_PORT))
    s.listen(5)
    
    while True:
        # now our endpiont knows about the OTHER endpoint
        client_socket, address = s.accept()
        print('Connection from {} has been established'.format(address))
        
        msg = client_socket.recv(BUFFER_SIZE)
        print(msg.decode())
        client_socket.close()
        
def client():
    s.connect((TCP_IP, TCP_PORT))
    msg = 'HELLO WORLD'.encode()
    s.send(msg)
    s.close()
        
        
