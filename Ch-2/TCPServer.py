#### Use - sudo lsof -i :9999 when the server is not closed properly ####

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# pass in the ip and port we want the server to listen on
server.bind((bind_ip, bind_port))

#start listening with max backlog of 5 connections
server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

# client handling thread
def handle_client(client_socket):
    # print out what the client sends
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)

    # send back a packet
    client_socket.send(b"ACK!")

    client_socket.close()

try:
    while True:
        client, addr = server.accept()
        print(client)
        print(addr)

        print("[*] Accepted connection from %s:%d" % (addr[0], addr[1]))

        # spin up our client thread to handle incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
except KeyboardInterrupt:
    print("\n[*] Shutting down server...")
    server.close()