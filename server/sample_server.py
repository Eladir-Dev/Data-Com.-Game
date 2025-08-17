import socket

# Standard loopback interface address (localhost).
# 127.0.0.1 makes it so that the server is only accesible from the same machine.
# 0.0.0.0 allows connections from other machines.
HOST = "127.0.0.1"  
PORT = 3000        # Port to listen on (non-privileged ports are > 1023)

def read_sample_client_conn():
        # AF_INET: socket family is IPv4
    # SOCK_STREAM: socket type is TCP (lossless)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"LOG: Server listening on {HOST}:{PORT}")

        conn, addr = s.accept() # Accepts a new connection

        with conn:
            print(f"Connected by {addr}")

            while True:
                data = conn.recv(1024) # Receives up to 1024 bytes of data
                if not data:
                    break # If no data, the connection is closed

                print(f"LOG: Received from client: {data.decode()}")
                conn.sendall(data) # Echoes the received data back to the client
                print(f"LOG: Sent back to client: {data.decode()}")