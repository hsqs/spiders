import requests
import bs4
import urllib3


START_PAGE_NUM = 1302
MAX_PAGE_NUM = 1302

http = urllib3.PoolManager()


def get_soup():

    for index in range(START_PAGE_NUM, MAX_PAGE_NUM + 1):
        page_url = "http://wufazhuce.com/one/{}".format(index)
        response = requests.get(page_url)
        if response.status_code != 200:
            print("{}:{}".format(page_url, response.status_code))
            continue

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        divs = soup.select("div")
        for div in divs:
            try:
                if "one-cita" in div.attrs["class"]:
                    contents = ''.join(div.contents).strip()
                    img_url = soup.find_all("img")[1]['src']

                    img_request = http.request("GET", img_url)
                    with open('../downloads/{}.jpg'.format(contents), 'wb') as jpg:
                        jpg.write(img_request.data)
                        print("{}:{}".format(page_url, 'done'))
                        break
            # if div not contains a key attr, continue
            except KeyError:
                continue


if __name__ == "__main__":
    get_soup()
