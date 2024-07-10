# Uncomment this to pass the first stage
import socket
import re
import selectors
import types
import sys

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

def accept_wrapper(sock, sel):
    conn,addr = sock.accept()
    print(f"Accepted connection from {addr}")

    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def get_file(directory, file_name):
    try:
        body = ""
        with open(f"/{directory}/{file_name}", "r") as file:
            body = file.read()
        status_line = 'HTTP/1.1 200 OK\r\n'
        content_type = 'Content-Type: application/octet-stream\r\n'
        content_length = f'Content-Length: {len(body)}\r\n\r\n'
        return (status_line + content_type + content_length + body).encode()
    except Exception as e:
        return "HTTP/1.1 404 Not Found\r\n\r\n".encode()

def service_connection(key, mask, sel):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            recv_data = recv_data.decode('utf-8')
            req_lines = recv_data.split(CRLF,1)
            # _, headers = request.decode('utf-8').split('\r\n', 1)
            method, url, protocol=parse_request_line(req_lines[0])
            # get body response 
            body = get_body(url, protocol)
            # read header
            user_agent_string = req_lines[1].split('\n')[1]
            if url.startswith('/files'):
                directory = sys.argv[2]
                file_name = url[7:]
                # print(directory,file_name)
                response = get_file(directory, file_name)
                sock.sendall(response)

            if get_after_user_agent(user_agent_string)!='':
                body=get_user_agent(get_after_user_agent(user_agent_string), url, protocol)
                sock.sendall(body)
            else:
                sock.sendall(body)
            
            data.outb += recv_data.encode('utf-8')
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    # if mask & selectors.EVENT_WRITE:
    #     if data.outb:
    #         sent = sock.sendall(data.outb)
    #         data.outb = data.outb[sent:]

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    # server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    sel = selectors.DefaultSelector()
    host, port = "localhost", 4221
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    # conn, addr=server_socket.accept() # wait for client
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj, sel)
                else:
                    service_connection(key, mask, sel)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()
            
if __name__ == "__main__":
    main()
