import os
import re
from bs4 import BeautifulSoup
import requests
import datetime


def get_exist_names():
    walked = list(os.walk("./downloads"))[0]
    exist = [x for x in walked[2] if str(x).endswith('.jpg')]
    return exist


exists = get_exist_names()
users = {1303132300: 10, 2663489000: 10, 5021784365: 10}
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

        print('done.')


def download_one_page(soup, user_id):
    '''
    download all pictures on the website
    :param soup: web page soup
    :param user_id: the weibo user id
    :return: None
    '''

    div_c = [div for div in soup.find_all('div') if div.get('class', 'null') == ['c']]
    divs = [div for div in div_c if div.get('id') is not None]

    for div in divs:
        spans = div.find_all('span')

        wb_post_time = get_weibo_post_time(spans[1].text)

        all_img = div.find_all('img')
        img_link = filter(lambda x: x.endswith('.jpg'), [all_img[0].get('src')] if all_img else [])

        more_links = [link['href'] for link in div.find_all('a') if link.get('href') is not None]
        more_links_real = [x for x in more_links if 'picAll' in x]
        if more_links_real:
            more_content = requests.get(more_links_real[0], cookies = cookie)
            more_soup = BeautifulSoup(more_content.content, 'html.parser')
            more_soup_urls = get_more_page_image_url(more_soup)
            img_link = more_soup_urls if more_soup_urls else img_link

        for idx, link in enumerate(img_link):
            image_name = wb_post_time + '>' + str(idx)
            if image_name not in exists:
                large_link = replace_part2_in_link(link)
                image_content = requests.get(large_link, cookies = cookie)
                with open('./downloads/{}/{}.jpg'.format(user_id, image_name), 'wb') as jpg:
                    jpg.write(image_content.content)

                    exists.append(image_name)
                    print('download ', large_link, image_name)
            else:
                print('jump over:', image_name)


def get_more_page_image_url(soup):
    all_img = soup.find_all('img')
    all_img_link = (x.get('src') for x in all_img)
    return [x for x in all_img_link if x.endswith('jpg')]


def replace_part2_in_link(link):
    link = link[7:]
    all_parts = link.split('/')
    all_parts[1] = 'large'
    return 'http://' + '/'.join(all_parts)

_h_M = re.compile('\d{2}:\d{2}')
_y_m_d_H_M_S = re.compile('(\d{4})\-(\d{2})\-(\d{2}) (\d{2}):(\d{2}):(\d{2})')
_2_num = re.compile('(\d{2})')


def get_weibo_post_time(wb_time):

    if '今天' in wb_time:
        hhmm = _h_M.findall(wb_time)[0].split(':')
        hour, minute = int(hhmm[0]), int(hhmm[-1])
        today = datetime.datetime.now().replace(hour = hour, minute = minute)
        return today.strftime('%Y-%m-%d-%H-%M-xx')

    elif wb_time.count('-') == 2:
        y_2_s = _y_m_d_H_M_S.findall(wb_time)[0]
        return '-'.join(y_2_s)

    elif '分钟前' in wb_time:
        m_before = int(_2_num.findall(wb_time)[0])
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
    miner()
