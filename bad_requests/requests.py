from bad_requests.request import Request

STANDARD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept-Language": "en,en-US",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Encoding": 'deflate'
}

DEFAULT_BOUNDARY = "=="


def get(uri, args=None, headers=None):
    host, resource = parse_uri(uri)

    if headers is None:
        headers = STANDARD_HEADERS
    header_str = serialize_headers(headers)

    args_str = url_encode_dict(args)
    if args_str:
        resource += "?" + args_str
    message = "GET {} HTTP/1.1\nHost: {}\n{}\n\n".format(resource, host, header_str)
    return Request(host, message)


def head(uri, args=None, headers=None):
    host, resource = parse_uri(uri)

    if headers is None:
        headers = STANDARD_HEADERS
    header_str = serialize_headers(headers)

    args_str = url_encode_dict(args)
    if args_str:
        resource += "?" + args_str

    message = "HEAD {} HTTP/1.1\nHost: {}\n{}\n\n".format(resource, host, header_str)
    return Request(host, message, get_body=False)


def post(uri, args=None, headers=None):
    host, resource = parse_uri(uri)

    if "Content-Type" in headers:
        if headers['Content-Type'] == "application/x-www-form-urlencoded":
            return urlencoded_post(host, resource, args=args, headers=headers)
        elif "multipart/form-data" in headers['Content-Type']:
            parts = headers['Content-Type'].split(";")
            if len(parts) >= 2:
                boundary_parts = parts[1].strip().split("=")
                if boundary_parts[0].lower() == "boundary":
                    boundary = boundary_parts[1]
                else:
                    # Default boundary.
                    boundary = DEFAULT_BOUNDARY
                return multipart_post(host, resource, boundary, args=args, headers=headers)
            else:
                return multipart_post(host, resource, DEFAULT_BOUNDARY, args=args, headers=headers)
        else:
            raise Exception("Invalid Content-Type: {}".format(headers['Content-Type']))
    else:
        # Default.
        return urlencoded_post(host, resource, args=args, headers=headers)


def urlencoded_post(host, resource, args=None, headers=None):
    pass


def multipart_post(host, resource, boundary, args=None, headers=None):
    pass


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
            cur_k = percent_encode_string(k)
            cur_v = percent_encode_string(v)
            all_args.append(cur_k + "=" + cur_v)
        return "&".join(all_args)
    else:
        return None


def percent_encode_string(string):
    safe_chars = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
    end_str = ""
    for char in string:
        if char not in safe_chars:
            num = ord(char)
            print(num, hex(num), len(str(hex(num)).split("x")[-1])*8)

            if num <= 255:
                end_str += "%" + str(hex(num).split("x")[-1]).upper()
            else:
                tmp = str(hex(num).split("x")[-1]).upper()
                if len(tmp) % 2 == 1:
                    tmp = "0" + tmp
                for i in range(2, len(tmp)+1, 2):
                    end_str += "%" + tmp[i-2:i]
        else:
            end_str += char

    return end_str



if __name__ == "__main__":
    #test.
    import urllib.parse
    test_str = "♥"
    print(test_str)
    print(urllib.parse.quote(test_str))
    print(percent_encode_string(test_str))

    # test_url = "http://www.theuselessweb.com"
    #
    # resp_head = head(test_url)
    # print(resp_head)
    #
    # req_get = get(test_url, args={"hello": "world"})
    # print(req_get)
    # resp_get = req_get.send()
    # print(resp_get)
