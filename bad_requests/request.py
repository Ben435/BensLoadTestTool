import socket
import ssl

from bad_requests.response import Response

HTTP_STANDARD_PORTS = [80]
HTTPS_STANDARD_PORTS = [443, 8080]
BUFFERSIZE = 1024


class Request:
    def __init__(self, host, message, get_body=True):
        self.host = host
        self.message = message
        self.get_body = get_body

    def send(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        resource = self.host.split("/")

        # Enable SSL if needed.
        if "https" in resource[0].lower():
            sock = ssl.wrap_socket(sock)
            https = True
        else:
            https = False

        # Connect and send message.
        worked = False
        for port in HTTPS_STANDARD_PORTS if https else HTTP_STANDARD_PORTS:
            try:
                sock.connect((self.host, port))
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
        sock.send(self.message.encode("UTF-8"))

        # Get headers
        headers = ""
        body = ""
        received = sock.recv(BUFFERSIZE)
        while len(received) == BUFFERSIZE and "\r\n\r\n" not in received.decode("UTF-8"):
            headers += received.decode("UTF-8")
            received = sock.recv(BUFFERSIZE)
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
        for line in lines[1:]:  # Skip "HTTP/1.1 NUM MSG" line.
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
            received = sock.recv(BUFFERSIZE)
            total_received += len(received)
        body += received.decode("UTF-8")

        return Response(status_code, status_message, proto, dict_headers, body, init_req=self)

    def __str__(self):
        return "Host: {}\nGet Body: {}\nMessage: {{\n{}\n}}".format(
            self.host, self.get_body, "\n".join(map(lambda line: "\t" + line, self.message.strip().split("\n"))))
