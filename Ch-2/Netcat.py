import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = ""
execute = ""
target = ""
port = 0

def usage():
    print("Netcat Replacement Tool")
    print()
    print("Usage: Netcat.py -t target_host -p port")
    print("-l --listen             - listen on [host]:[port] for incoming connections")
    print("-e --execute=file       - execute given file upon connection")
    print("-c --command            - initialize a command shell")
    print("-u --upload=destination - upload file and save to [destination]")
    print()
    print("Examples:")
    print("Netcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("Netcat.py -t 192.168.0.1 -p 5555 -l -u=/tmp/file")
    print("Netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'test' | Netcat.py -t 192.168.0.1 -p 5555")
    sys.exit(0)

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode())

        while True:
            response = ""
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data.decode()
                if len(data) < 4096:
                    break
            if response:
                print(response, end='')

            buffer = input("> ")
            buffer += "\n"
            client.send(buffer.encode())

    except Exception as e:
        print(f"[*] Exception! Exiting. {e}")
        client.close()

def server_loop():
    global target
    if not target:
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    print(f"[*] Listening on {target}:{port}")
    try:
        while True:
            client_socket, addr = server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
        server.close()

def run_command(command):
    command = command.strip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = b"Failed to execute command.\r\n"
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if upload:
        file_buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data
        try:
            with open(upload, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Successfully saved file to {upload}\r\n".encode())
        except:
            client_socket.send(f"Failed to save file to {upload}\r\n".encode())

    if execute:
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send(b"<NC:#> ")
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer.decode())
            client_socket.send(response)

def main():
    global listen, port, execute, command, target, upload

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                ["help", "listen", "execute=", "target=", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled option"

    if not listen and target and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

if __name__ == "__main__":
    main()
