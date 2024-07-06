# Uncomment this to pass the first stage
import socket
import re

DEFAULT_HTTP_VERSION = 'HTTP/1.1'
CRLF = '\r\n'
def parse_request_line(request_line):
    request_parts = request_line.split(' ')
    method = request_parts[0]
    url = request_parts[1]
    protocol = request_parts[2] if len(request_parts) > 2 else DEFAULT_HTTP_VERSION
    return method, url, protocol

def get_after_echo(str):
    match = re.search(r'/echo/(.*)', str)
    if match:
        return match.group(1)
    else:
        return ''
    
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
            request = conn.recv(1024).decode('utf-8')
            if not request:
                break
            req_lines = request.split(CRLF,1)
            # _, headers = request.decode('utf-8').split('\r\n', 1)
            method, url, protocol=parse_request_line(req_lines[0])
            echo_string = get_after_echo(url) if get_after_echo(url)!='' else ''
            echo_length = len(echo_string) if echo_string!='' else 0
            # print(echo_length)
            status_line = f'{protocol} 200 OK\r\n' if echo_string!='' else f'{protocol} 404 Not Found\r\n'
            content_type = 'Content-Type: text/plain\r\n'
            content_length = f'Content-Length: {echo_length}\r\n\r\n'
            if echo_string=='':
                if url=='/':
                    status_line=f'{protocol} 200 OK\r\n'
                conn.sendall((status_line+content_type+content_length+echo_string).encode())
            else:  
                conn.sendall((status_line+content_type+content_length+echo_string).encode())
            # match url:
            #     case '/':
            #         conn.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
            #     case 
            #     case _:
            #         conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
            
if __name__ == "__main__":
    main()
