# coding=utf-8
import requests
import os
import re
import time
import random
import threading
import progressbar
import requests.packages.urllib3
import sys
import base64

requests.packages.urllib3.disable_warnings()

# 是否配置代理，国内访问速度较慢
def proxy_set():
    proxy_set = raw_input('Do you want to use proxy?[y/n]')
    if proxy_set == 'y':
        global my_proxies
        proxies_set = raw_input('input your proxy config ep:"127.0.0.1:8080"')
        my_proxies = {"http": "http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}
        if proxies_set != '':
            my_proxies['http'] = 'http://'+proxies_set
            my_proxies['https'] = 'https://'+proxies_set

    elif proxy_set == 'n':
        my_proxies = ''
    else:
        proxy_set()


# 91最新的加密，这里进行字符串解密，找到原视频地址
def strdecode(input, key):
    input = base64.b64decode(input).decode("utf-8")
    str_len = len(key)
    code = ''
    for i in range(0, str_len):
        k = i % str_len
        input_i_unicode = ord(input[i])
        key_k_unicode = ord(key[k])
        code += chr(input_i_unicode ^ key_k_unicode)
    missing_padding = 4 - len(code) % 4
    if missing_padding:
        code = code + '='*missing_padding
    code = base64.b64decode(code).decode("utf-8")
    pattern = re.compile("'(.*)' type")
    code = pattern.findall(code)
    return code[0]


# 视频下载函数
def download_mp4(url,dir,my_proxies):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://91porn.com'}
    req=requests.get(url=url, proxies=my_proxies, headers=headers)
    filename=str(dir)+'/1.mp4'
    total_length = int(req.headers.get("Content-Length"))
    print ('start to download' + url)
    with open(filename, 'wb') as f:
        widgets = ['Progress: ', progressbar.Percentage(), ' ',
                   progressbar.Bar(marker='#', left='[', right=']'),
                   ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_length).start()
        for chunk in req.iter_content(chunk_size=1):
            if chunk:
                f.write(chunk)
                f.flush()
            pbar.update(len(chunk) + 1)
        pbar.finish()
        #f.write(req.content)


# 视频页中，预览图下载函数
def download_img(url,dir):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://91porn.com'}
    req=requests.get(url=url, proxies=my_proxies, headers=headers)
    with open(str(dir)+'/thumb.png','wb') as f:
        f.write(req.content)


# 定义随机ip地址
def random_ip():
    a=random.randint(1, 255)
    b=random.randint(1, 255)
    c=random.randint(1, 255)
    d=random.randint(1, 255)
    return (str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d))


# 爬虫主体，flag为页码
def spider(flag):
    tittle = []
    # 如果连接访问不了，在这里把base_url替换成你知道的标准地址
    base_url = 'http://0314.91p47.com/view_video.php?viewkey='
    page_url = 'http://0314.91p47.com/v.php?category=top&viewtype=basic&page='+str(flag)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
        'Referer': 'http://91porn.com'}
    get_page=requests.get(url=page_url, headers=headers)
    # 利用正则匹配出特征地址
    viewkey = re.findall(
        r'<a target=blank href="http://0314.91p47.com/view_video.php\?viewkey=(.*)&page=.*&viewtype=basic&category=.*?">',
        str(get_page.content))
    for eachkey in viewkey:
        print ('find:'+eachkey)
    # 遍历每个特征地址，并进行爬取
    for key in viewkey:
        headers={'Accept-Language':'zh-CN,zh;q=0.9',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0',
                 'X-Forwarded-For': random_ip(),
                 'referer': page_url,
                 'Content-Type': 'multipart/form-data; session_language=cn_CN',
                 'Connection': 'keep-alive',
                 'Upgrade-Insecure-Requests': '1',
                 }
        base_req = requests.get(url=base_url+key,headers=headers)
        pattern_video = re.compile('document.write\(strencode\("(.*)"')
        a = pattern_video.findall(base_req.content)
        a = a[0].split(',')
        input = a[0].replace('"', '')
        encode_key = a[1].replace('"', '')
        video_url = strdecode(input=input, key=encode_key)
        tittle = re.findall(r'<h4 class="login_register_header" align=left>(.*?)</h4>', base_req.content, re.S)
        img_url = re.findall(r'poster="(.*?)"',str(base_req.content))
        t = 'not-find-name' + key
        try:
            t = tittle[0]
            tittle[0] = t.replace('\n', '')
            t = tittle[0].replace(' ', '').decode('utf-8').encode('gbk', 'replace')
            print t
        except IndexError:
            pass
        # 判断当前目录是否已存在相同文件夹
        if not os.path.exists(t):
            try:
                os.makedirs(t)
                print('start to download:' + str(t))
                download_img(str(img_url[0]), str(t))
                download_mp4(str(video_url[0]), str(t), my_proxies=my_proxies)
                print('download complete')
            except:
                pass
        else:
            print('已存在文件夹,跳过')
            time.sleep(1)


# i为线程数
if __name__ == '__main__':
    proxy_set()
    if len(sys.argv) < 2:
        threads = 5
    else:
        threads = int(sys.argv[1])
    for i in range(threads):
        # 爬取的页数在这里传入，1为1页
        t = threading.Thread(target=spider, args=(1,))
        t.start()


