# coding=utf-8
import requests
import os,re,time,random


def download_mp4(url,dir):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://91porn.com'}
    req=requests.get(url=url)
    filename=str(dir)+'/1.mp4'
    with open(filename,'wb') as f:
        f.write(req.content)
def download_img(url,dir):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://91porn.com'}
    req=requests.get(url=url)
    with open(str(dir)+'/thumb.png','wb') as f:
        f.write(req.content)


flag = 1
tittle = []
base_url = 'http://91.91p27.space/view_video.php?viewkey='
page_url = 'http://91.91p27.space/v.php?next=watch&page='+str(flag)
get_page=requests.get(url=page_url)
print get_page.content
viewkey=re.findall(r'<a target=blank href="http://91.91p27.space/view_video.php\?viewkey=(.*)&page=.*&viewtype=basic&category=.*?">\n                    <img ',str(get_page.content))
print viewkey


def random_ip():
    a=random.randint(1,255)
    b=random.randint(1,255)
    c=random.randint(1,255)
    d=random.randint(1,255)
    return(str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d))


for key in viewkey:
    headers={'Accept-Language':'zh-CN,zh;q=0.9','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36','X-Forwarded-For':random_ip(),'referer':page_url,'Content-Type': 'multipart/form-data; session_language=cn_CN'}
    video_url=[]
    img_url=[]
    base_req=requests.get(url=base_url+key,headers=headers)
    video_url=re.findall(r'<source src="(.*?)" type=\'video/mp4\'>',str(base_req.content))
    tittle=re.findall(r'<div id="viewvideo-title">(.*?)</div>', str(base_req.content),re.S)
    img_url=re.findall(r'poster="(.*?)"',str(base_req.content))
    try:
        t = tittle[0]
        tittle[0] = t.replace('\n', '')
        t = tittle[0].replace(' ', '').decode('utf-8').encode('gbk', 'replace')
        print t
    except IndexError:
        pass
    if not os.path.exists(t):
        try:
            os.makedirs(t)
            print('开始下载:' + str(t))
            download_img(str(img_url[0]), str(t))
            download_mp4(str(video_url[0]), str(t))
            print('下载完成')
        except:
            pass
    else:
        print('已存在文件夹,跳过')
        time.sleep(2)

