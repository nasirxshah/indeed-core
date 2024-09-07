from curl_cffi import requests
from tenacity import retry, wait_random, stop_after_attempt


class Session(requests.Session):
    def __init__(self, proxy) -> None:
        super().__init__()
        self.__post__init__(proxy)

    def __post__init__(self, proxy):
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

        if proxy:
            self.proxies.update({{"http": proxy, "https": proxy}})

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
    ) -> str | bytes | dict:
        response = super().request(
            method,
            url,
            params,
            data,
            headers,
            cookies,
            files,
            auth,
            timeout,
            allow_redirects,
            proxies,
            hooks,
            stream,
            verify,
            cert,
            json,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type")
        if "text/html" in content_type or "text/plain" in content_type:
            return response.text
        elif "application/json" in content_type:
            return response.json()
        else:
            return response.content
