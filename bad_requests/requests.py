import urllib.parse
from bad_requests.request import Request

# Kinda Firefox.
standard_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept-Language": "en,en-US",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Encoding": 'deflate'
}


def get(uri, args=None, headers=None):
    host, resource = parse_uri(uri)

    if headers is None:
        headers = standard_headers
    header_str = serialize_headers(headers)

    args_str = url_encode_dict(args)
    if args_str:
        resource += "?" + args_str
    message = "GET {} HTTP/1.1\nHost: {}\n{}\n\n".format(resource, host, header_str)
    return Request(host, message)


def head(uri, args=None, headers=None):
    host, resource = parse_uri(uri)

    if headers is None:
        headers = standard_headers
    header_str = serialize_headers(headers)

    args_str = url_encode_dict(args)
    if args_str:
        resource += "?" + args_str

    message = "HEAD {} HTTP/1.1\nHost: {}\n{}\n\n".format(resource, host, header_str)
    return Request(host, message, get_body=False)


def post(uri, args=None, headers=None, content_type=None, boundary=None):
    host, resource = parse_uri(uri)

    if content_type is None:
        if "Content-Type" in headers:
            if headers['Content-Type'] == "application/x-www-form-urlencoded":
                content_type = "application/x-www-form-urlencoded"
            elif "multipart/form-data" in headers['Content-Type'] and :
                pass
            pass


    raise Exception("NOT IMPLEMENTED")


def parse_uri(uri):
    resource = uri.split("/")
    # ['http:', '', 'www.example.com', 'what_we_want.html']
    host = resource[2]
    if len(resource) < 4:
        resource = "/".join(resource)
    else:
        resource = "/" + "/".join(resource[3:])
    return host, resource


def serialize_headers(headers):
    # Join headers.
    header_str = ""
    for key, val in headers.items():
        header_str += key + ": " + val + "\n"
    return header_str


def url_encode_dict(args):
    if args is not None and isinstance(args, dict):
        all_args = []
        for k, v in args.items():
            print(k, v)
            cur_k = urllib.parse.quote(k)
            cur_v = urllib.parse.quote(v)
            all_args.append(cur_k + "=" + cur_v)
        return "&".join(all_args)
    else:
        return None


if __name__ == "__main__":
    test_url = "http://www.theuselessweb.com"

    resp_head = head(test_url)
    print(resp_head)

    req_get = get(test_url, args={"hello": "world"})
    print(req_get)
    resp_get = req_get.send()
    print(resp_get)