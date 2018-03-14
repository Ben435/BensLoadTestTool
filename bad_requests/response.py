class Response:
    def __init__(self, status_code, status_message, proto, headers, body, init_req=None):
        self.status_code = status_code
        self.status_message = status_message
        self.proto = proto
        self.headers = headers
        self.body = body
        self.init_req = init_req

    def __str__(self):
        str_headers = "\n".join([": ".join([key, val]) for key, val in self.headers.items()])
        return "Proto: {}\nCode: {}\nMessage: {}\nHeaders: \"\n{}\"\n\nBody: \"\n{}\"".format(
            self.proto, self.status_code, self.status_message, str_headers, self.body)