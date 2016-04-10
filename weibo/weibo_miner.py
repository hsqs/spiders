import os
from bs4 import BeautifulSoup
import requests
import hashlib


def get_exist_names():
    walked = list(os.walk("./downloads"))[0]
    exist = [x for x in walked[2] if str(x).endswith('.jpg')]
    return exist


exists = get_exist_names()
users = {1303132300: 2, 2663489000: 4, 5021784365: 3}
cookie_values1 = ['_T_WM=e1eadf753daa8e0eaa6a98dbd924dd89;', ' SUB=_2A256DbneDeRxGedJ6FsV9CjLzjiIHXVZ8ceWrDV6PUJb']
cookie_values2 = ['rdBeLVP8kW1LHeuE-tglgN4hADdeZV_zCKufEX1tGA..;', ' SUHB=0WGdcIcQ6fIJa7; SSOLoginState=1460259']
cookie = {"Cookie": ''.join(cookie_values1) + ''.join(cookie_values2)}


def miner():
    for user_id, page_num in users.items():
        path_img = 'downloads/{}'.format(user_id)
        if not os.path.exists(path_img):
            os.makedirs(path_img)

        for page in range(1, page_num + 1):
            url = 'http://weibo.cn/u/%s?filter=1&page=%d' % (user_id, page)
            content = requests.get(url, cookies = cookie).content
            soup = BeautifulSoup(content, "html.parser")
            download_one_page(soup, user_id)

            # more pic link, load and download again
            img_links = soup.find_all('a')
            for link in img_links:
                src = link['href']
                if 'picAll' in src:
                    content_sub = requests.get(src, cookies = cookie).content
                    soup_sub = BeautifulSoup(content_sub, "html.parser")
                    download_one_page(soup_sub, user_id)
            print('done.')


def download_one_page(soup, user_id):
    '''
    download all pictures on the website
    :param soup: web page soup
    :param user_id: the weibo user id
    :return: None
    '''
    img_urls = soup.find_all('img')
    for img_tag in img_urls:
        img_url = img_tag['src']
        if not img_url.endswith('.jpg'):
            continue

        # remove http:// in head
        img_url = img_url[7:]
        url_subs = img_url.split("/")
        if len(url_subs) != 3:
            continue
        url_subs[1] = 'mw690'
        final_url = 'http://' + '/'.join(url_subs)

        image_src = requests.get(final_url, cookies = cookie)
        # use hash value as the image name to avoid duplicate downloading
        name = get_img_name(image_src.content)
        if name not in exists:
            with open('./downloads/{}/{}.jpg'.format(user_id, name), 'wb') as jpg:
                jpg.write(image_src.content)
                exists.append(name)
                print('downloading...')
        print('one page downloaded.')


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
