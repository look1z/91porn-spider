# 91spider
you can input the number of the posts of 91porn.
Then 91spider can download the picture automatically from the post in 91porn.

可以用来批量下载91视频，图片。

## 使用说明

代码编写于python2.7环境下，依赖于requests库，自行下载安装环境文件。

## test.py
test.py是91视频爬虫，源代码来自**91_spider**，7月31日优化了链接，代理（主要解决速度问题），多线程。

使用：
python test.py 线程数
如：
python test.py 10 将指定线程数为10

## test2.py
test2.py是91论坛图片爬虫，输入id区间即可批量下载图片

## 8月1日更新

更新了网站地址链接；

添加了代理功能，不使用代理的话，把requests.get中的proxy去掉即可；

添加了多线程下载，可以综合自己网络速度进行调试；

## 8月2日更新

对test.py的模块进行了备注；

## 9月22日更新

更新了代理判断，现在进入的时候可以自由选择是否开启代理与配置代理；

添加了进度条模块，视频下载时会有进度显示，并提供当前下载速度，预计完成时间等信息；

添加了线程参数，默认第一个参数为线程数（默认线程为5）；



# **本代码仅限于python学习使用，勿用于其他用途**

