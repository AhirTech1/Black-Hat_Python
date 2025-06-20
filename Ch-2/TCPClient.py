import socket

target_host = "0.0.0.0"
target_port = 9999

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.AF_INET means IPv4 will be used, socket.AF_INET6 for IPv6
# socket.SOCK_STREAM for using TCP, socket.SOCK_DGRAM for UDP

# connect the client
client.connect((target_host, target_port))

# send some data
client.send(b"ACK?")
# GET - to retrieve some kind of resource
# / - root path of the website (maybe home page)
# HTTP/1.1 - version of HTTP
#\r\n - return + newline

# receive some data
response = client.recv(4096)

print(response)

'''Assumptions in this code - 
 - our connection will always succeed
 - server is always expecting us to send data first
 - server will always send us data back in a timely fashion
'''