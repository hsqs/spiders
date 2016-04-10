import re, os
from bs4 import BeautifulSoup
import requests
import random
import hashlib


def get_exist_names():
    walked = list(os.walk("./downloads"))[0]
    exist = [x for x in walked[2] if str(x).endswith('.jpg')]
    return exist


def miner():
    user_id = '2663489000'
    cookie = {"Cookie": "_T_WM=e1eadf753daa8e0eaa6a98dbd924dd89; SUB=_2A256DbneDeRxGedJ6FsV9CjLzjiIHXVZ8ceWrDV6PUJbrdBeLVP8kW1LHeuE-tglgN4hADdeZV_zCKufEX1tGA..; SUHB=0WGdcIcQ6fIJa7; SSOLoginState=1460259214"}
    exists = get_exist_names()

    page_num = 1
    for page in range(1, page_num + 1):
        url = 'http://weibo.cn/u/%s?filter=1&page=%d' % (user_id, page)
        content = requests.get(url, cookies = cookie).content

        soup = BeautifulSoup(content, "html.parser")
        urls = soup.find_all('a', href=re.compile(r'^http://weibo.cn/mblog/oripic', re.I))
        for img_url in urls:
            image_src = requests.get(img_url['href'], cookies = cookie)

            # use hash value as the image name to avoid duplicate downloading
            name = get_img_name(image_src.content)
            if name not in exists:
                with open('./downloads/%s.jpg' % name, 'wb') as jpg:
                    jpg.write(image_src.content)
                    print('downloading...')
        print('done.')


def get_img_name(content):
    '''
    return the hash value of the content
    :param content: image binary content
    :return: hashed value
    '''
    md5obj = hashlib.md5()
    md5obj.update(content)
    return md5obj.hexdigest()


if __name__ == '__main__':
    miner()
