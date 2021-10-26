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
        my_proxies = {"http": "http://127.0.0.1:10809", "https": "https://127.0.0.1:10809"}
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
    base_url = 'http://f1020.workarea5.live/view_video.php?viewkey='
    page_url = 'http://f1020.workarea5.live/v.php?category=top&viewtype=basic&page='+str(flag)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
        'Referer': 'http://91porn.com'}
    get_page=requests.get(url=page_url, headers=headers)
    # 利用正则匹配出特征地址
    viewkey = re.findall(
        r'viewkey=(.*)&page',
        str(get_page.content))
    for eachkey in viewkey:
        print ('find:'+eachkey)
    ################################
    # 遍历每个特征地址，并进行爬取
    #
    # 强烈建议在这里调试通了，viewkey就是当前页面下所有视频的url地址变量
    #####################################
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
        strencode = re.findall(r'strencode2\(\"(.*)\"\)', str(base_req.content))
        ##################################################
        # 目前修复到这里，strencode是可以正常爬取到的，
        # 举个例子：
        # 返回值类似：“%3c%73%6f%75%72%63%65%20%73%72%63%3d%27%68%74%74%70%73%3a%2f%2f%63%64%6e%2e%
        # 77%6f%72%6b%67%72%65%61%74%31%34%2e%6c%69%76%65%2f%2f%6d%33%75%38%2f%35%33%31%30%38%35%2f%3
        # 5%33%31%30%38%35%2e%6d%33%75%38%3f%73%74%3d%5a%38%4a%32%38%79%4e%32%5a%78%6b%33%61%4b%4b%35
        # %5a%61%37%73%71%77%26%65%3d%31%36%33%35%32%34%36%33%31%39%27%20%74%79%70%65%3d%27%61%70%70%6
        # c%69%63%61%74%69%6f%6e%2f%78%2d%6d%70%65%67%55%52%4c%27%3e”
        # url解码后，可以看到关于m3u8的，所以后面的下载方式要有重大变化了
        ##################################################
        video_url = strdecode(input=input, key=strencode[0])
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


