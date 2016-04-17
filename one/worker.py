import bs4
import urllib3


START_PAGE_NUM = 1300
MAX_PAGE_NUM = 1309

http = urllib3.PoolManager()


def spider():

    for index in range(START_PAGE_NUM, MAX_PAGE_NUM + 1):
        response = get_response(index)
        if response.status != 200:
            print("{}:{}".format(index, response.status))
            continue

        soup = bs4.BeautifulSoup(response.data, "html.parser")
        divs = get_page_node(soup, "div")
        for div in divs:
            try:
                if "one-cita" in div.attrs["class"]:
                    contents = ''.join(div.contents).strip()

                    img_url = soup.find_all("img")[1]['src']
                    img_request = http.request("GET", img_url)
                    with open('./downloads/{}.jpg'.format(contents), 'wb') as jpg:
                        jpg.write(img_request.data)
                        print("{}:{}".format(index, 'done'))
                        break
            # if div doesn't contains key of 'class', continue
            except KeyError:
                continue


def get_response(page_index):
    page_url = "http://wufazhuce.com/one/{}".format(page_index)
    return http.request("GET", page_url, timeout=urllib3.Timeout(total = 15))


def get_page_node(soup, node_name):
    return soup.select(node_name)

if __name__ == "__main__":
    spider()
