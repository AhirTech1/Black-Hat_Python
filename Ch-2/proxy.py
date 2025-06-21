import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to listen on {local_host}:{local_port} : {e}")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"[==>] Received incoming connection from {addr[0]}:{addr[1]}")
            proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
            proxy_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
        server.close()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if local_buffer:
            print("[==>] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)

        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)

        if not local_buffer and not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def hexdump(src, length=16):
    result = []
    if isinstance(src, bytes):
        for i in range(0, len(src), length):
            chunk = src[i:i+length]
            hexa = ' '.join(f"{b:02X}" for b in chunk)
            text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
            result.append(f"{i:04X}   {hexa:<{length*3}}   {text}")
        print('\n'.join(result))

def receive_from(connection):
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def request_handler(buffer):
    # modify packet if needed
    return buffer

def response_handler(buffer):
    # modify packet if needed
    return buffer

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: python3 proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: python3 proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() == "true"

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()
