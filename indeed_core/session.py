from curl_cffi import requests
from tenacity import retry, wait_random, stop_after_attempt


class Session(requests.Session):
    def __init__(self, proxy) -> None:
        super().__init__()
        self.__post__init__()
        self.proxy = proxy
        self.verify = False

    def __post__init__(self):
        self.headers.update(
            {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "priority": "u=0, i",
                "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            }
        )            

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        json = None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects = None,
        max_redirects= None,
        proxies=None,
        proxy=None,
        proxy_auth=None,
        verify = None,
        referer=None,
        accept_encoding="gzip, deflate, br",
        content_callback=None,
        impersonate=None,
        ja3=None,
        akamai=None,
        extra_fp=None,
        default_headers = None,
        default_encoding="utf-8",
        http_version=None,
        interface=None,
        cert=None,
        stream = False,
        max_recv_speed = 0,
        multipart=None,
    ) -> requests.Response:
        proxy = proxy or self.proxy
        verify = verify or self.verify
        response =  super().request(
            method,
            url,
            params,
            data,
            json,
            headers,
            cookies,
            files,
            auth,
            timeout,
            allow_redirects,
            max_redirects,
            proxies,
            proxy,
            proxy_auth,
            verify,
            referer,
            accept_encoding,
            content_callback,
            impersonate,
            ja3,
            akamai,
            extra_fp,
            default_headers,
            default_encoding,
            http_version,
            interface,
            cert,
            stream,
            max_recv_speed,
            multipart,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type")
        if "text/html" in content_type or "text/plain" in content_type:
            return response.text
        elif "application/json" in content_type:
            return response.json()
        else:
            return response.content
