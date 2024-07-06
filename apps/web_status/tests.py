from django.db.models import QuerySet
from django.test import TestCase

from apps.web_status.models import Web_Site
from apps.web_status.utils.webUtil import is_valid_host
from util import pageUtils


# Create your tests here.

class Test(TestCase):

    def test(self):
        hosts = [
            "example.com",  # 常见的域名
            "http://example.com",  # 带有 http 协议的 URL
            "https://example.com",  # 带有 https 协议的 URL
            "192.168.1.1",  # 本地 IP 地址
            "localhost",  # 本地主机名
            "ftp://example.com",  # 带有 ftp 协议的 URL
            "invalid_host",  # 无效的主机名
            "http://localhost",  # 带有 http 协议的本地主机名
            "127.0.0.1:8080",  # 带有端口号的本地 IP 地址
            "0.0.0.0:80",  # 带有端口号的任意 IP 地址
            "www.baidu.com",  # 常见的中文网站域名
            "http://bilibili.com",  # 带有 http 协议的中文网站 URL
            "https://www.google.com",  # 带有 https 协议的常见搜索引擎域名
            "http://www.github.com",  # 带有 http 协议的常见开发者网站域名
            "https://news.ycombinator.com",  # 带有 https 协议的新闻网站域名
            "ftp://ftp.example.com",  # 带有 ftp 协议的域名
            "http://subdomain.example.com",  # 带有子域名的 URL
            "https://example.org",  # 另一个顶级域名
            "http://example.net",  # 常见的顶级域名
            "http://xn--fiq228c.com",  # 带有 punycode 编码的国际化域名
            "https://example.edu",  # 教育机构域名
            "http://example.gov",  # 政府网站域名
            "http://example.museum",  # 博物馆域名
            "http://example.travel",  # 旅游网站域名
            'https://127.0.0.1:8080',
            "http://baidu",
            "http://localhost:8080"
        ]

        for host in hosts:
            print(f"{host}: {is_valid_host(host)}")

    def test2(self):
        for i in range(5):
            Web_Site.objects.create(title=f"title{i}", host=f"host{i}", description=f"description{i}")
        print(Web_Site.objects.all().count())
        content = pageUtils.get_page_content(Web_Site.objects.all(), 2, 5)
        print(content.count())
        print(type(content))
