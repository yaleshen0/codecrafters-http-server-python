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
def get_body(url, protocol):
    echo_string = get_after_echo(url)
    echo_length = len(echo_string) if echo_string!='' else 0
    # print(echo_length)
    status_line = f'{protocol} 200 OK\r\n' if (echo_string!='' or url=='/') else f'{protocol} 404 Not Found\r\n'
    content_type = 'Content-Type: text/plain\r\n'
    content_length = f'Content-Length: {echo_length}\r\n\r\n'
    return (status_line+content_type+content_length+echo_string).encode()
def get_after_user_agent(str):
    match=re.search(r'User-Agent: (.*)\r' ,str)
    if match:
        return match.group(1)
    else:
        return ''
def get_user_agent(user_agent, url, protocol):
    # user_agent_string = get_after_user_agent(user_agent)
    user_agent_length = len(user_agent) if user_agent!='' else 0
    # print(user_agent_length)
    status_line = f'{protocol} 200 OK\r\n'
    content_type = 'Content-Type: text/plain\r\n'
    content_length = f'Content-Length: {user_agent_length}\r\n\r\n'
    return (status_line+content_type+content_length+user_agent).encode()

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
            # get body response 
            body = get_body(url, protocol)
            # read header
            user_agent_string = req_lines[1].split('\n')[1]
            if get_after_user_agent(user_agent_string)!='':
                body=get_user_agent(get_after_user_agent(user_agent_string), url, protocol)
                conn.sendall(body)
            #     conn.sendall(body)
            else:
                conn.sendall(body)
            # conn.sendall(body)
            # match url:
            #     case '/':
            #         conn.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
            #     case 
            #     case _:
            #         conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
            
if __name__ == "__main__":
    main()
