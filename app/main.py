# Uncomment this to pass the first stage
import socket
DEFAULT_HTTP_VERSION = 'HTTP/1.1'
CRLF = '\r\n'
def parse_request_line(request_line):
    request_parts = request_line.split(' ')
    method = request_parts[0]
    url = request_parts[1]
    protocol = request_parts[2] if len(request_parts) > 2 else DEFAULT_HTTP_VERSION
    return method, url, protocol
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr=server_socket.accept() # wait for client
    # conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    with conn:
        while True:
            request = conn.recv(1024)
            if not request:
                break
            req_lines = request.decode('utf-8').split(CRLF,1)
            # _, headers = request.decode('utf-8').split('\r\n', 1)
            method, url, protocol=parse_request_line(req_lines[0])
            if (url!='/'):
                conn.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
            else:
                conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
            
if __name__ == "__main__":
    main()
