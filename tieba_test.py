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

    try:
        html = urlopen(url).read().decode('UTF-8')
        soup = BeautifulSoup(html, features='html.parser')
        return soup
    except:
        return None


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


def get_time_from_string(time_str):
    return [int(time_str[0:4]), int(time_str[5: 7]), int(time_str[8:10])]


import datetime as d


def days_before(time_1, time_2, days):
    t1 = d.date(time_1[0], time_1[1], time_1[2])
    t2 = d.date(time_2[0], time_2[1], time_2[2])
    if (t1 - t2).days <= days:
        return True
    else:
        return False


def sorted_dict(analyse, axe=0):
    return sorted(analyse.items(), key=lambda item: item[axe], reverse=True)


def draw_image(sorted, path='./dataset/keyword.html', keyword='', mode='lines'):
    import plotly.graph_objs as go
    import plotly.plotly as py
    import plotly
    X = []
    Y = []
    for day in sorted:
        X.append(day[0])
        Y.append(day[1])
    aes = go.Scatter(
        x=X,
        y=Y,
        mode=mode,

    )
    layout = go.Layout(
        title='Key word: ' + keyword,

    )
    fig = go.Figure([aes], layout)
    print('plot')
    plotly.offline.plot(fig, filename=path)


def read_data(path, mask_path='./Hunan_Normal_University_logo1.jpg'):
    csvFile = open(path, "r")
    reader = csv.reader(csvFile)
    analyse = {}
    wordcount = {}
    mask = np.array(Image.open(mask_path))
    j = 0
    sorted = []
    KEY_WORD = r'物理'
    for line in reader:
        if line == []:
            continue
        name, zhuti, time = line
        # print(name, zhuti, time)
        sorted = keyword_(KEY_WORD, name, zhuti, time, analyse)
        ret = hotword_(name, zhuti, time, wordcount, j, mask)
    draw_image(sorted, keyword=KEY_WORD)
    show_cloud(wordcount)


def keyword_(KEY_WORD, name, zhuti, time, analyse):
    # print(name, zhuti, time)
    from snownlp import SnowNLP

    present_time = [d.datetime.now().year, d.datetime.now().month, d.datetime.now().day]
    if re.search(KEY_WORD, zhuti):
        tieba_time = get_time_from_string(time)
        if days_before(present_time, tieba_time, 365):
            try:
                analyse[time] += 1
            except:
                analyse[time] = 1
            s = SnowNLP(zhuti)
            print(name, ":", zhuti.strip(), '\n情绪分数:', s.sentiments)
            # print(sorted_dict(analyse))
            print('---------------')
    return sorted_dict(analyse)


def hotword_(name, zhuti, time, wordcount, j, mask):
    import jieba
    from wordcloud import WordCloud
    if re.search(r'http://pan.baidu.com/', zhuti):
        return 'useless'
    sentences = re.split(r"([.。!！?？；;，,“”\s+])", zhuti.strip())
    for sent in sentences:
        rm = remove_punctuation(sent)
        if rm != "":
            # print(rm)
            seg_list = jieba.cut(rm, cut_all=True)
            # print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
            for word in seg_list:
                # print(word)
                if len(word) < 2:
                    continue
                try:
                    wordcount[word] += 1
                except:
                    wordcount[word] = 1

                # print(sorted_dict(wordcount, 1)[:10])


def show_cloud(wordcount):
    from wordcloud import WordCloud
    wc = WordCloud(font_path="simfang.ttf",
                          background_color="white",
                          width=1500, height=950,
                          max_words=500,
                          mask=mask,
                          margin=2).generate_from_frequencies(wordcount)
    import matplotlib.pyplot as plt
    plt.figure(figsize=(15, 15))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def remove_punctuation(line):
    rule = re.compile(u'[^a-zA-Z0-9\u4e00-\u9fa5]')
    line = rule.sub('', line)
    return line


if __name__ == '__main__':
    # 贴吧是50一页
    # test()
    # 帖子是1一页
    KEY_WORD = r'学'
    page = 0
    analyse = {}
    wordcount = {}

    import jieba
    from snownlp import SnowNLP

    # seg_list = jieba.cut("转专业第一个学期期末就可以申请。如果只是对某学科感兴趣，建议辅修，如果是需要有一定的能力素养", cut_all=False)
    # print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
    # analyse['2018'] = 0
    # print(analyse['2018'])
    # days_before(get_time_from_string('2018-07-10'), [2018, 5, 10], 5)
    plt_time = 0
    j = 0
    import numpy as np
    from PIL import Image
    path = './Hunan_Normal_University_logo1.jpg'
    mask = np.array(Image.open(path))
    present_time = [d.datetime.now().year, d.datetime.now().month, d.datetime.now().day]
    import csv
    # csvfile = open('./dataset/tieba_data.csv', 'w')
    # writer = csv.writer(csvfile)
    read_data('./dataset/tieba_data.csv')
    info = []
    while(False):
        # 开启一个死循环爬去网页，当收到403 bad gate 即停止
        try:
            tieba_url = get_page(page)  # 得到网页的页码
            soup = get_soup(tieba_url)

            titles, urls = get_titles_urls(soup)  # 得到标题和对应的网页
            for index in range(len(titles)):
                # 打印输出内容：主标题、网页
                # print('<><><><><><><><><><><>')
                print(index, titles[index], urls[index])
                before = ""
                zhuti_page = 0
                while (True):

                    zhuti_url = get_zhuti_page(urls[index], zhuti_page)  # 得到网页的页码

                    soup = get_soup(zhuti_url)
                    # print(soup)
                    if soup is None:
                        print('页面读取错误', zhuti_url)
                        break
                    zhuti, name, times = get_zhuti(soup)  # 得到楼层、作者、时间
                    if zhuti[0] == before:
                        break
                    else:
                        zhuti_page += 1
                        before = zhuti[0]
                    for i in range(len(zhuti)):
                        # 打印输出内容：作者、内容、时间(格式没优化)
                        # info.append([name[i], zhuti[i], times[i]])
                        # print('writen:', [name[i], zhuti[i], times[i]])
                        try:
                            print('write')
                            # writer.writerow([name[i], zhuti[i], times[i]])
                        except:
                            print('!!!!!!!!! io error !!!!!!!!!!!!!')
                        """
                        
                        if re.search(r'http://pan.baidu.com/', zhuti[i]):
                            continue
                        sentences = re.split(r"([.。!！?？；;，,“”\s+])", zhuti[i].strip())
                        for sent in sentences:
                            rm = remove_punctuation(sent)
                            if rm != "":
                                # print(rm)
                                seg_list = jieba.cut(rm, cut_all=True)
                                # print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
                                for word in seg_list:
                                    # print(word)
                                    if len(word) < 2:
                                        continue
                                    try:
                                        wordcount[word] += 1
                                    except:
                                        wordcount[word] = 1
                                    from wordcloud import WordCloud

                                    if j % 50 == 0:
                                        # j = 0
                                        wc = wordcloud = WordCloud(font_path="simfang.ttf",
                                                                   background_color="white",
                                                                   width=1000, height=860,
                                                                   max_words=100,
                                                                   mask=mask,
                                                                   margin=2).generate_from_frequencies(wordcount)
                                        import matplotlib.pyplot as plt

                                        plt.imshow(wordcloud, interpolation='bilinear')
                                        plt.axis("off")
                                        plt.show()
                                    j += 1
                                    print(j)
                                    # print(sorted_dict(wordcount, 1)[:10])

                        # print('\t回复：', '作者', name[i], '内容', zhuti[i], '时间', times[i])
                        
                        if re.search(KEY_WORD, zhuti[i]):
                            tieba_time = get_time_from_string(times[i])
                            if days_before(present_time, tieba_time, 365):
                                try:
                                    analyse[times[i]] += 1
                                except:
                                    analyse[times[i]] = 1
                                s = SnowNLP(zhuti[i])
                                print(zhuti[i].strip(), s.sentiments)
                                # print(sorted_dict(analyse))

                                print('---------------')
                        """
            page += 1
        except:
            print('HTTP done')
            break


