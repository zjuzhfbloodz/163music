#!/usr/bin/env python

# -*- coding: utf-8 -*- 

"""
@File: 163music.py

Created on 02 08 13:00 2020

@Authr: zhf12341 from Mr.Zhao

"""

import requests
from bs4 import BeautifulSoup
import os

"""

经过抓包发现网易云歌曲下载页面在这里: http://music.163.com/song/media/outer/url?id=1417900311.mp3

歌单的url为： http://music.163.com/playlist?id=2182968685

"""


"""我的请求头，用的是Chrome浏览器"""
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',}


def get_music(id,name):
    """爬取一首歌曲，输入网易云网页版id后面的数字编号"""

    """发送请求，得到响应，因为我们找到了下载url，所以直接得到了byte音乐数据，直接写入mp3文件，记得要去掉命名中的标点之类的，不然不能创建"""
    try:
        os.mkdir("Music Library")
    except:
        pass
    base_url = 'http://music.163.com/song/media/outer/url?id=' + id + '.mp3'
    response = requests.get(url = base_url, headers = headers)
    response.raise_for_status()
    html = response.content
    name = "".join([x for x in name if x.isalpha() or x == " " or x.isalnum()])
    with open('Music Library/{}.mp3'.format(name),'wb') as f:
        f.write(html)


def get_list(list_id):
    """爬取歌单里的歌曲，输入网易云网页版歌单后面id的数字编号"""

    """发送请求，得到响应"""
    list_url = 'http://music.163.com/playlist?id=' + list_id
    response = requests.get(url=list_url, headers=headers)
    response.raise_for_status()
    html = response.content
    """利用BeautifulSoup找到歌单中歌曲名称和对应编号id"""
    soup = BeautifulSoup(html, 'lxml')
    music_list = soup.find('ul', {'class': 'f-hide'})
    music_dict = {}
    """利用find_all找到所有<a>里的内容，写入字典"""
    for music in music_list.find_all("a"):
        music_id = music['href'][9:]
        music_name = music.text
        music_dict[music_name] = music_id
    return music_dict


def download_list(music_dict):
    """下载歌单"""

    """通过获取的歌单歌曲名称和id批量下载歌曲"""
    for name,id in music_dict.items():
        get_music(id,name)
        print("歌曲 {} 下载完毕...".format(name))


def main():
    """主程序"""

    """目前支持两种模式的爬取，单首音乐或整个歌单"""
    pattern = input("请输入您想爬取的内容类型，目前有歌曲和歌单两种，分别用0和1来代表： ")
    if pattern == "0":
        id = input("请输入下载音乐id，即网易云网页版音乐id后面的数字编号： ")
        get_music(id,id)
        print("歌曲下载完成")
    else:
        list_id = input("请输入下载歌单id，即网易云网页版歌单id后面的数字编号： ")
        download_list(get_list(list_id))
        print("歌单下载完成")


"""运行主程序"""
if __name__ == "__main__":
    main()



