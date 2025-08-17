import socket

# The server's hostname or IP address.
# Since the server is being ran on the same machine, the loopback address is used.
HOST = "127.0.0.1"  
PORT = 3000        # The port used by the server

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # Send data to the server.
        message = "Hello, world!"
        print(f"LOG: Sending to server: {message}")
        s.sendall(message.encode())
        
        # Receive the echoed data from the server.
        data = s.recv(1024)

    print(f"LOG: Received from server: {data.decode()}")

if __name__ == "__main__":
    main()