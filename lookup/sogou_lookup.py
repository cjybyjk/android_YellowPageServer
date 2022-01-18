import requests
import re
from .lookup_base import LookupBase

class SogouLookup(LookupBase):
    def query(self, number, region):
        headers = {'Accept': 'text/html, application/xhtml+xml, */*',
                   'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                   'Accept-Encoding': 'deflate',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        get = requests.get("https://www.sogou.com/web?query=" + number, headers = headers)
        if get.ok:
            usertags = re.findall(r'号码通用户数据：(.+)：', get.text)
            if len(usertags) > 0:
                result = dict()
                result["number"] = number
                result["region"] = region
                result["tagstr"] = usertags[0]
                result["type"] = 1
                result["tag_count"] = 5
                for spam_str in ("骚扰", "诈骗", "金融", "广告", "违法", "保险", "推销"):
                    if spam_str in usertags[0]:
                        result["type"] = -1
                        break

                return result
        return None

    def is_supported_region(self, region):
        return 'cn' == region
