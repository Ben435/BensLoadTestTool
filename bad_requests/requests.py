import socket
import ssl

port_options = [80, 443, 8080]
buffersize = 1024
standard_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept-Language": "en,en-US",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Encoding": 'deflate'
}


class Response:
    def __init__(self, status_code, status_message, proto, headers, body):
        self.status_code = status_code
        self.status_message = status_message
        self.proto = proto
        self.headers = headers
        self.body = body

    def __str__(self):
        str_headers = "\n".join([": ".join([key, val]) for key, val in self.headers.items()])
        return "Proto: {}\nCode: {}\nMessage: {}\nHeaders: \"\n{}\"\n\nBody: \"\n{}\"".format(
            self.proto, self.status_code, self.status_message, str_headers, self.body)

def get(uri, headers=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if uri[-1] == "/":
        # Strip.
        url = uri
        uri = uri[:-1]
    else:
        url = uri
    resource = uri.split("/")
    # ['http:', '', 'www.example.com', 'what_we_want.html']
    host = resource[2]
    if len(resource) < 4:
        resource = "/".join(resource)
    else:
        resource = "/" + "/".join(resource[3:])

    # Enable SSL if needed.
    print(uri)
    if "https" in resource[0].lower():
        sock = ssl.wrap_socket(sock)
        proto = "HTTPS"
    else:
        proto = "HTTP"

    # Join headers.
    if headers is None:
        headers = standard_headers
    header_str = ""
    for key, val in headers.items():
        header_str += key + ": " + val + "\n"

    message = "GET {} {}/1.1\nHost: {}\n{}\r\n\r\n".format(resource, proto, host, header_str)

    # Connect and send message.
    worked = False
    for port in port_options:
        try:
            sock.connect((host, port))
            worked = True
        except socket.error as e:
            print(e)
            print("Failed on port: " + str(port))
            raise e
        finally:
            if worked:
                break
    if not worked:
        print("Failed all ports.")
        return None

    # Send message.
    sock.send(message.encode("UTF-8"))

    # Get headers
    headers = ""
    body = ""
    received = sock.recv(buffersize)
    while len(received) == buffersize and "\r\n\r\n" not in received.decode("UTF-8"):
        headers += received.decode("UTF-8")
        received = sock.recv(buffersize)
    snip = received.decode("UTF-8").split("\r\n\r\n")
    if len(snip) >= 2:
        headers += snip[0]
        body += "\r\n\r\n".join(snip[1:])
    else:
        headers += "\r\n\r\n".join(snip)

    # Parse headers.
    lines = headers.split("\r\n")
    status = lines[0].split(" ")
    proto = status[0]
    status_code = status[1]
    status_message = status[2]
    dict_headers = {}
    for line in lines[1:]:        # Skip HTTP/1.1 200 OK line.
        if len(line) <= 1:
            continue
        data = line.split(": ", 1)
        key = data[0]
        vals = data[1].strip()
        dict_headers[key] = vals

    if "Content-Length" in dict_headers:
        total_body = int(dict_headers["Content-Length"])
    else:
        total_body = 0

    # Get body.
    total_received = len(body)
    while total_received < total_body:
        body += received.decode("UTF-8")
        received = sock.recv(buffersize)
        total_received += len(received)
    body += received.decode("UTF-8")

    return Response(status_code, status_message, proto, dict_headers, body)


if __name__ == "__main__":
    response = get("http://www.theuselessweb.com")
    print(response)