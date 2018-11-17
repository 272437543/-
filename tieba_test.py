from bs4 import BeautifulSoup
from urllib.request import urlopen
import re


def get_titles_urls(soup):
    all_titles = soup.find_all('li')
    titles = []
    urls = []
    for t in all_titles:
        try:

            if ['', 'j_thread_list', 'clearfix'] == t['class']:
                all_a = t.find_all('a')
                for a in all_a:

                    if ['j_th_tit', ''] == a['class']:
                        titles.append(a.get_text())
                        urls.append("http://tieba.baidu.com" + a['href'])
                        # print(a)
                        # print(a.get_text(), "http://tieba.baidu.com" + a['href'])
        except:
            todo = 0
    return titles, urls


def get_zhuti(soup):
    divs = soup.find_all('div')
    times = []
    for div in divs:
        try:
            # print(len(divs))
            all_str = div['data-field'].split(':')
            for index in range(0, len(all_str)):
                s = all_str[index]
                # print(s)
                if re.search(r'date', s):
                    # print(all_str[index + 1][1: 11])
                    times.append(all_str[index + 1][1: 11])
        except:
            todo = 0
    index = 0
    zhuti = []
    for div in divs:
        try:
            if ['d_post_content', 'j_d_post_content', 'clearfix'] == div['class']:
                index += 1
                zhuti.append(div.get_text())

        except:
            todo = 0

    all_names = []
    lis = soup.find_all('li')
    for li in lis:
        try:
            if ['d_name'] == li['class']:
                all_names.append(li.get_text())
        except:
            todo = 0

    return zhuti, all_names, times


def get_soup(url):
    html = urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, features='html.parser')
    return soup


def get_page(page=0):
    return 'http://tieba.baidu.com/f?kw=%E6%B9%96%E5%8D%97%E5%B8%88%E8%8C%83%E5%A4%A7%E5%AD%A6&ie=utf-8&pn=' + str(50 * page)


def get_zhuti_page(url, page=0):
    return url + '?pn=' + str(page + 1)


def test():
    url = 'http://tieba.baidu.com/p/2957706439'
    soup = get_soup(url)
    divs = soup.find_all('div')
    times = []
    for div in divs:
        try:
            all_str = div['data-field'].split(':')
            for index in range(0, len(all_str)):
                s = all_str[index]
                if re.search(r'date', s):
                    times.append(all_str[index + 1][1: 11])
        except:
            todo = 0
    all_names = []
    lis = soup.find_all('li')
    for li in lis:
        try:
            if ['d_name'] == li['class']:
                all_names.append(li.get_text())
        except:
            todo=0

    index = 0
    zhuti = []
    for div in divs:
        try:
            if ['d_post_content', 'j_d_post_content', 'clearfix'] == div['class']:
                index += 1
                zhuti.append(div.get_text())

        except:
            todo = 0
    print(len(all_names), len(zhuti), len(times))


if __name__ == '__main__':
    # 贴吧是50一页
    # test()
    # 帖子是1一页
    page = 0
    while(True):
        # 开启一个死循环爬去网页，当收到403 bad gate 即停止
        try:
            tieba_url = get_page(page)  # 得到网页的页码
            titles, urls = get_titles_urls(get_soup(tieba_url))  # 得到标题和对应的网页
            for index in range(len(titles)):
                # 打印输出内容：主标题、网页
                print(index, titles[index], urls[index])
                before = ""
                zhuti_page = 0
                while (True):

                    zhuti_url = get_zhuti_page(urls[index], zhuti_page)  # 得到网页的页码
                    zhuti, name, times = get_zhuti(get_soup(zhuti_url))  # 得到楼层、作者、时间
                    if zhuti[0] == before:
                        break
                    else:
                        zhuti_page += 1
                        before = zhuti[0]
                    for i in range(len(zhuti)):
                        # 打印输出内容：作者、内容、时间(格式没优化)
                        print('\t回复：', '作者', name[i], '内容', zhuti[i], '时间', times[i])
            page += 1
        except:
            break
