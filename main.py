import cloudscraper
import os
import time
import imghdr
from bs4 import BeautifulSoup
import re
import random, string

# Windowsフォルダ名の禁則処理用
trans_tone = {
    u':': u'：',
    u'/': u'／',
    u'\¥': u'',
    u'\?': u'？',
    u'\"': u'”',
    u'\<': u'＜',
    u'\>': u'＞',
    u'\*': u'＊',
    u'\|': u'｜'
}


# Windowsフォルダ名の禁則処理
# https://qiita.com/kusunamisuna/items/a32679874afedc032158
def multiple_replace(text, adict):
    """ 一度に複数のパターンを置換する関数
    - text中からディクショナリのキーに合致する文字列を探し、対応の値で置換して返す
    - キーでは、正規表現を置換前文字列とできる
    """

    rx = re.compile('|'.join(adict))

    def dedictkey(_text):
        """ マッチした文字列の元であるkeyを返す
        """
        for key in adict.keys():
            print(key)
            if re.search(key, _text):
                return key

    def one_xlat(match):
        return adict[dedictkey(match.group(0))]

    return rx.sub(one_xlat, text)


# Story ViewerのURLを取得する
def search_story_url(url):
    story_url = url.replace('/image/', '/story/')
    # print(story_url)
    return story_url


# cloudscraperを利用してページをダウンロードし，soupにして返す
def get_soup(url):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    html = scraper.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def random_name(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


# フォルダ名にするためにタイトルを取得する
def get_title(url):
    title = None
    count = 0

    print("######################################################")
    print("get_title")

    while title is None:
        title = get_soup(url).find('meta', attrs={'name': 'description'})
        count += 1
        print(count)
        time.sleep(1)

    # print(title.get('content'))
    return title.get('content')


# Story Viewerのページから全画像のURLを取得する
def get_image_urls(story_url):
    soup = None
    a = None
    count = 0

    print("######################################################")
    print("get_image_urls")

    while a is None:
        soup = get_soup(story_url)
        # a = soup.find('a', attrs={'class': 'left'})
        a = soup.find('amp-img')
        count += 1
        print(count)
        time.sleep(1)

    print("######################################################")
    print("download_images")

    image_url_list = []
    for a_tag in soup.find_all('amp-img'):
        image_url = a_tag.get('src')
        # print(image_url)
        image_url_list.append(image_url)

    return image_url_list


# image_urlの画像を指定フォルダに実際にダウンロードする
def download_image(path, image_url):
    image_type = None
    count = 0

    # 画像として一旦保存してみて，画像でなかった場合はtype=Noneとなるので再ダウンロードする
    while image_type is None:
        if os.path.exists(path):
            image_type = imghdr.what(path)
            if image_type is not None:
                break

        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        html = scraper.get(image_url).content
        with open(path, 'wb') as f:
            f.write(html)

        image_type = imghdr.what(path)
        count += 1
        print(count)
        time.sleep(0.5)


# image_url_listに含まれる画像URLの画像を1つずつダウンロードする
def download_images(title, image_url_list):
    save_directory = multiple_replace(title, trans_tone)
    save_path = os.path.join("images", save_directory)
    if save_directory not in os.listdir("./images/"):
        os.mkdir(save_path)

    count = 0

    for image_url in image_url_list:
        count += 1
        print(count, " ", end="")
        print(image_url)

        name = str(count)

        if count <= 9:
            name = "0" + name

        name += ".jpg"

        download_image(os.path.join(save_path, name), image_url)
        # time.sleep(1)


def main_function(url):
    story_url = search_story_url(url)
    title = get_title(url)
    image_url_list = get_image_urls(story_url)
    download_images(title, image_url_list)


if __name__ == '__main__':
    file_name = './input_url_list.txt'
    file = open(file_name)
    input_url_list = file.readlines()

    for input_url in input_url_list:
        input_url = input_url.replace('\n','')
        print('input_url: ' + input_url)
        main_function(input_url)
