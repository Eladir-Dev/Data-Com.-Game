from socket import socket

# Re-export Python's `socket` type under a different name so that it doesn't conflict with
# the name of the module, which is also named `socket`.
Connection = socket

# The size of the socket's buffer for receiving and sending messages 
# between the server and the client.
BUF_SIZE = 1024