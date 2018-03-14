import socket
from bad_requests.response import Response

port_options = [80, 443, 8080]
buffersize = 1024


class Request:
    def __init__(self, host, message, get_body=True):
        self.host = host
        self.message = message
        self.get_body = get_body

    def send(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect and send message.
        worked = False
        for port in port_options:
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
        received = sock.recv(buffersize)
        while len(received) == buffersize:
            headers += received.decode("UTF-8")
            received = sock.recv(buffersize)
        headers += received.decode("UTF-8")

        # Parse headers.
        lines = headers.split("\n")
        status = lines[0].split(" ")
        proto = status[0]
        status_code = status[1]
        status_message = status[2]
        dict_headers = {}
        for line in lines[1:]:  # Skip "HTTP/1.1 XXX MSG" line.
            if len(line) <= 1:
                continue
            if ":" in line:
                data = line.split(": ", 1)
                key = data[0].strip()
                vals = data[1].strip()
                dict_headers[key] = vals
            else:
                dict_headers[line] = True

        if self.get_body:
            if "Content-Length" in dict_headers:
                total_body = int(dict_headers["Content-Length"])
            else:
                total_body = 0

            # Get body.
            body = ""
            received = sock.recv(buffersize)
            total_received = len(received)
            while total_received < total_body:
                body += received.decode("UTF-8")
                received = sock.recv(buffersize)
                total_received += len(received)
            body += received.decode("UTF-8")
        else:
            body = None

        return Response(status_code, status_message, proto, dict_headers, body, init_req=self)

    def __str__(self):
        return "Host: {}\nGet Body: {}\nMessage: {{\n{}\n}}".format(
            self.host, self.get_body, "\n".join(map(lambda line: "\t" + line, self.message.strip().split("\n"))))