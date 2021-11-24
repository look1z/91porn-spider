# coding=utf-8
import requests
import os
import re
import time
import random
import threading
lock = threading.Lock()
import progressbar
import requests.packages.urllib3
import sys
import base64
import urllib.parse
from pprint import pprint
import pymysql

requests.packages.urllib3.disable_warnings()

db = pymysql.connect(host='************',
                     user='*************',
                     password='**************',
                     database='************')
cursor = db.cursor()


# 是否配置代理，国内访问速度较慢
def proxy_set():

    # proxy_set = input('Do you want to use proxy?[y/n]')
    proxy_set = 'n'#默认为n，如有需要，注释此行并取消上一行注释即可。
    if proxy_set == 'y':
        global my_proxies
        proxies_set = input('input your proxy config ep:"127.0.0.1:8080"')
        my_proxies = {"http": "http://127.0.0.1:10809", "https": "https://127.0.0.1:10809"}
        if proxies_set != '':
            my_proxies['http'] = 'http://'+proxies_set
            my_proxies['https'] = 'https://'+proxies_set

    elif proxy_set == 'n':
        my_proxies = ''
    else:
        proxy_set()


# 91最新的加密，这里进行字符串解密，找到原视频地址
def strdecode( key):
    key=urllib.parse.unquote(key)
    pattern = re.compile("'(.*)' type")
    code = pattern.findall(key)
    return code[0]

def checkfileexist(id):
    global cursor
    sql="""select count(*)  from videoinfo where videoid = "{id}"  limit 1;""".format(id = id)
    lock.acquire()
    cursor.execute(sql)
    ret = cursor.fetchone()
    lock.release()
    if ret[0] == 0 :
        return True
    else:
        return False

def insertdb(videoid, videoname, videofileid, poster, imageurl, videolinktype, info, posterid):
    global cursor
    sql="""INSERT INTO `nine_one`.`videoinfo` (`videoid`, `videoname`, `videofileid`, `poster`, `imageurl`, `videolinktype`, `info`, `posterid`) VALUES ('{videoid}', '{videoname}', '{videofileid}', '{poster}', '{imageurl}', '{videolinktype}', '{info}', '{posterid}');""".format(videoid =videoid , videoname=videoname, videofileid=videofileid, poster=poster, imageurl=imageurl, videolinktype=videolinktype, info=info, posterid=posterid)

    try:
        lock.acquire()
        cursor.execute(sql)
        db.commit()
        lock.release()
        return True
    except Exception as e :
   # 错误回滚
        
        db.rollback()
        lock.release()
        print(e)
        return False

def deletedb(videoid):
    global cursor
    sql="""delete from videoinfo where videoid = "{id}"  limit 1;""".format(id =videoid)

    try:
        lock.acquire()
        cursor.execute(sql)
        db.commit()
        lock.release()
        return True
    except Exception as e :

        
        db.rollback()
        lock.release()
        print(e)
        return False




# 视频下载函数
def download_mp4_old(url,dir,my_proxies):
    # print('debug mode,skip download')
    # return 0
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://91porn.com'}
    req=requests.get(url=url, proxies=my_proxies, headers=headers)
    filename=str(dir)+'/1.mp4'
    total_length = int(req.headers.get("Content-Length"))
    print ('start to download' + url)
    if os.path.exists(filename):  # 如果文件存在
        os.remove(filename)  
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
        f.write(req.content)




def download_mp4(url,dir,my_proxies):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://91porn.com'}

    all_content = requests.get(url=url, proxies=my_proxies, headers=headers).text # 获取M3U8的文件内容
    file_line = all_content.split("\n") # 读取文件里的每一行
    filename=str(dir)+'/1.mp4'
    # 通过判断文件头来确定是否是M3U8文件
    if file_line[0] != "#EXTM3U":
        raise BaseException(u"非M3U8的链接")
    else:
        unknow = True   # 用来判断是否找到了下载的地址
        widgets = ['Progress: ', progressbar.Percentage(), ' ',progressbar.Bar(marker='#', left='[', right=']'),' ', progressbar.ETA(), ' ', progressbar.Counter()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(file_line)).start()
        for index, line in enumerate(file_line):
            if "EXTINF" in line:
                unknow = False
                    # 拼出ts片段的URL
                pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1]
                res = requests.get(pd_url, proxies=my_proxies, headers=headers)
                with open(filename, 'ab') as f:
                    f.write(res.content)
                    f.flush()
                pbar.update(index + 1)
        pbar.finish()
        if unknow:
            raise BaseException("未找到对应的下载链接")
        else:
            print("下载完成")




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
    base_url = 'https://f1020.workarea5.live/view_video.php?viewkey='
    page_url = 'https://f1020.workarea5.live/v.php?&page='+str(flag)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
        'Referer': 'https://91porn.com'}
    get_page=requests.get(url=page_url, headers=headers)
    # 利用正则匹配出特征地址
    viewkey = re.findall(
        r'viewkey=(.*?)&page',
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
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                 'X-Forwarded-For': random_ip(),
                 'referer': page_url,
                 'Content-Type': 'multipart/form-data; session_language=cn_CN',
                 'Connection': 'keep-alive',
                 'Upgrade-Insecure-Requests': '1',
                 }

        base_req = requests.get(url=base_url+key,headers=headers)
        strencodetext = re.findall(r'strencode2\(\"(.*?)\"\)', str(base_req.content))
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
        pprint(strencodetext[0])
        video_url = strdecode(key=strencodetext[0])
        if "m3u8" in video_url:
            videotype='m3u8'
            video_file_id = re.findall(r'm3u8/(.*?)/', video_url, re.S)[0]
        else:
            videotype='mp4'
            video_file_id = re.findall(r'/91porn/mp43/(.*?).mp4', video_url, re.S)
        tittle = re.findall(r'<h4 class="login_register_header" align=left>(.*?)</h4>', base_req.content.decode('utf-8'), re.S)
        if "img src" in tittle[0]:
            tittle[0]= re.findall(r'<img src=images/91.png>(.*?)$',tittle[0], re.S)[0]
        # print(tittle)
        img_url = re.findall(r'poster="(.*?)"',str(base_req.content.decode('utf-8')))[0]
        poster = re.findall(r'\(<a href="compose.php\?receiver=(.*?)"> 发送消息',str(base_req.content.decode('utf-8')))[0]
        poster_id= re.findall(r'uprofile.php\?UID=(.*?)"><span class="title">',str(base_req.content.decode('utf-8')))[0]

        info = re.findall(r'<span class="info">简介(.*?)<form id="linkForm2" name="linkForm2',str(base_req.content.decode('utf-8')), re.S)
        pattern = re.compile(r'<[^>]+>',re.S)
        info[0] = pattern.sub('', info[0])
        print(img_url)
        print(poster)
        t = 'not-find-name' + key
        try:
            tittle[0] = tittle[0].replace('\n', '')
            filename = tittle[0].replace(' ', '')
            print (filename)
            t=filename
        except IndexError:
            pass
        filename
        # 判断当前key是否已经成功抓取
        if checkfileexist(key):
            try:
                os.makedirs(t) #这里的t保留，因为可能会有空的标题
            except WindowsError  as e:
                print(e)
                print('已存在')
                time.sleep(1)
                continue

            try:
                insertdb(key, t, video_file_id, poster, img_url, videotype, info[0], poster_id)
                print('start to download:' + str(t))
                download_img(str(img_url), str(t))
                if videotype=='mp4':
                    download_mp4_old(str(video_url), str(t), my_proxies=my_proxies)
                else :
                    download_mp4(str(video_url), str(t), my_proxies=my_proxies)
                print('download complete')
            except Exception  as e:
                print(e)
                deletedb(key)
                os.remove(t)
        else:
            print('已存在')
            time.sleep(1)


# i为线程数
if __name__ == '__main__':
    proxy_set()
    if len(sys.argv) < 2:
        threads = 5
    else:
        threads = int(sys.argv[1])
    for n in range(200):
        for i in range(threads):
            # 爬取的页数在这里传入，1为1页
            t = threading.Thread(target=spider, args=(n,))
            t.start()
        t.join()
        print('join')
