# -*- coding:gbk -*-
# by look1z
import requests
import time
import re
import threading
import os
from Queue import Queue


class spider91(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._queue = queue

    def run(self):
        while not self._queue.empty():
            page_url = self._queue.get_nowait()
            print page_url
            self.spider(url=page_url)

    def spider(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0',}
        # 伪造http头部
        r = requests.get(url=url, headers=headers)
        print r.status_code, len(r.content), time.ctime().split(' ')[3]  # 返回状态码，长度，时间
        if r.status_code != 404:
            # 创建标题名的文件夹
            name91 = re.findall('<h1>(.*?)</h1>', r.content)
            fileName =  'img/'+name91[0].decode('utf-8').encode('gbk', 'replace')

            if not os.path.exists(fileName):
                os.mkdir(fileName)

        img_urls1 = re.findall('file="attachments(.*?)"', r.content)
        img_urls2 = re.findall('attachments(.*?)"', r.content)
        img_urls = img_urls1+img_urls2
        for img_url in img_urls:
            # 获取真实图片地址
            img_url = 'http://g.91p35.space/attachments'+img_url
            #opener = urllib2.build_opener() #python 3可以采用的方法
            #opener.addheaders = headers
            response = requests.get(img_url,headers=headers)
            with open(fileName+'/'+img_url.split('/')[-1],'wb') as f: #打印图片到本地
                f.write(response.content)
                f.flush()
            #urllib.urlretrieve(url=img_url,filename=fileName+'/'+img_url.split('/')[-1])
            print img_url
        #time.sleep(2)


def main():
    queue = Queue()

    for i in range(285599, 285799): #256805
        queue.put('http://g.91p35.space/viewthread.php?tid='+str(i))

    threads = []
    thread_count = 10

    for i in xrange(thread_count):
        threads.append(spider91(queue))

    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()


