import os
import re
from bs4 import BeautifulSoup
import requests
import datetime
import hashlib
import random
import time


def get_exist_names(user_id):
    """
    返回已存在的图片名字
    :param user_id 被爬取的用户id
    :return: 图片名字
    """
    for parent, dirnames, filenames in os.walk('./downloads'):
        for dirname in dirnames:
            if dirname == str(user_id):
                exist_names = os.listdir(os.path.join(parent, dirname))
                md5s_jpg = (x.split('_')[1] for x in exist_names if '_' in x)
                md5s = [x[:-4] for x in md5s_jpg]
                return md5s


def get_cookie():
    """
    返回请求cookie,用来登录页面用.应对微博的反爬虫系统,在cookie末尾加上随机数
    :return: cookie
    """
    cookie_values1 = ['_T_WM=e1eadf753daa8e0eaa6a98dbd924dd89;', ' SUB=_2A256DbneDeRxGedJ6FsV9CjLzjiIHXVZ8ceWrDV6PUJb']
    cookie_values2 = ['rdBeLVP8kW1LHeuE-tglgN4hADdeZV_zCKufEX1tGA..;', ' SUHB=0WGdcIcQ6fIJa7; SSOLoginState=1460259']

    cookie = ''.join(cookie_values1) + ''.join(cookie_values2) + str(random.randint(0, 50))
    return {"Cookie": cookie}


def miner(users):

    with requests.Session() as s:
        for user_id, page_num in users.items():
            exists = get_exist_names(user_id)

            path_img = 'downloads/{}'.format(user_id)
            if not os.path.exists(path_img):
                os.makedirs(path_img)

            if page_num <= 0:
                print(user_id, 'has error page num', page_num, 'it must be positive')
                continue

            for page in range(1, page_num + 1):
                url = 'http://weibo.cn/u/%s?filter=1&page=%d' % (user_id, page)
                content = s.get(url, cookies = get_cookie(), headers = get_header()).content
                soup = BeautifulSoup(content, "html.parser")
                ret = download_one_page(soup, user_id, exists)

                if not ret:
                    break

        print('done.')


def get_header():
    """
    返回自定义请求头,伪装成浏览器
    :return: 请求头参数
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
    }
    return header


def div_filter_func(tag):
    """
    页面微博节点过滤器
    :param tag: 节点
    :return: 过滤条件
    """
    return tag.name == 'div' and tag.has_attr('id') and tag.get('class', 'null') == ['c']


def download_one_page(soup, user_id, exists):
    """
    download all pictures on the website
    :param soup: web page soup
    :param user_id: the weibo user id
    :param exists exists pic names
    :return: find weibo divs, return True, else False
    """

    # ten weibo div in every page
    divs = soup.find_all(div_filter_func)

    if not divs:
        return False

    for div in divs:
        spans = div.find_all('span')
        wb_post_time = get_weibo_post_time(spans[1].text)

        # abstract a link
        all_img = div.find_all('img')
        img_link = filter(lambda x: x.endswith('.jpg'), [all_img[0].get('src')] if all_img else [])

        # abstract more links
        more_links = [link['href'] for link in div.find_all('a') if link.get('href') is not None]
        more_links_real = [x for x in more_links if 'picAll' in x]
        if more_links_real:
            more_content = requests.get(more_links_real[0], cookies = get_cookie())
            more_soup = BeautifulSoup(more_content.content, 'html.parser')
            more_soup_urls = get_more_page_image_url(more_soup)
            img_link = more_soup_urls if more_soup_urls else img_link

        # download
        for idx, link in enumerate(img_link):
            md5 = calculate_md5(link)
            if md5 not in exists:
                large_link = replace_part2_in_link(link)
                image_content = requests.get(large_link, cookies = get_cookie())

                image_name = "{}>{}_{}".format(wb_post_time, str(idx), md5)
                with open('./downloads/{}/{}.jpg'.format(user_id, image_name), 'wb') as jpg:
                    jpg.write(image_content.content)

                    exists.append(image_name)
                    print('download', large_link, image_name, datetime.datetime.now())
                    time.sleep(random.random())
            else:
                print('jump over:', link)

    sleep = 8 * random.random()
    print('sleep', sleep, 'seconds')
    time.sleep(sleep)
    return True


def calculate_md5(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def get_more_page_image_url(soup):
    """
    获取'更多'链接里的图片链接
    :param soup: '更多'链接对应的soup
    :return: 图片链接
    """
    all_img_link = (x.get('src') for x in soup.find_all('img'))
    return [x for x in all_img_link if x.endswith('jpg')]


def replace_part2_in_link(link):
    """
    替换第二部分为large,下载对应大图
    :param link: 原始链接
    :return: 处理后的链接
    """
    indexes = [i for i, v in enumerate(link) if v == '/']
    slash_start, slash_end = indexes[2], indexes[3]
    url = link[:slash_start] + '/large' + link[slash_end:]
    return url


_h_M = re.compile('\d{2}:\d{2}')
_y_m_d_H_M_S = re.compile('(\d{4})\-(\d{2})\-(\d{2}) (\d{2}):(\d{2}):(\d{2})')
_2_num = re.compile('(\d{2})')
_nums = re.compile('(\d+)')


def get_weibo_post_time(wb_time):
    """
    解析微博的时间,作为文件名一部分保存
    :param wb_time: 微博上显示的时间
    :return: 处理后的时间
    """

    if '今天' in wb_time:
        hhmm = _h_M.findall(wb_time)[0].split(':')
        hour, minute = int(hhmm[0]), int(hhmm[-1])
        today = datetime.datetime.now().replace(hour = hour, minute = minute)
        return today.strftime('%Y-%m-%d-%H-%M-xx')

    elif wb_time.count('-') == 2:
        y_2_s = _y_m_d_H_M_S.findall(wb_time)[0]
        return '-'.join(y_2_s)

    elif '分钟前' in wb_time:
        m_before = int(_nums.findall(wb_time)[0])
        m_now = datetime.datetime.now() - datetime.timedelta(minutes = m_before)
        return m_now.strftime('%Y-%m-%d-%H-%M-%S')

    else:
        year = datetime.datetime.today().year
        ret = _2_num.findall(wb_time)
        ret.insert(0, year)
        ret.append('00')
        ret = map(lambda x: str(x), ret)
        return '-'.join(ret)


if __name__ == '__main__':
    target = {
        # user_id : page_num
        2663489000: 80
        # 2811699412: 7
    }
    miner(target)
