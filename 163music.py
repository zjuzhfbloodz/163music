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
import time


"""
网易云很坏，反爬虫就是在url里面加了个#，记得去掉

经过抓包发现网易云歌曲下载页面在这里: http://music.163.com/song/media/outer/url?id=1417900311.mp3

歌单的url为： http://music.163.com/playlist?id=2182968685

歌手的url为：https://music.163.com/artist?id=3695

"""


"""我的请求头，用的是Chrome浏览器"""
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',}


def get_music(id,name,folder):
    """爬取一首歌曲，输入网易云网页版id后面的数字编号"""

    """发送请求，得到响应，因为我们找到了下载url，所以直接得到了byte音乐数据，直接写入mp3文件，记得要去掉命名中的标点之类的，不然不能创建"""
    current_path = os.getcwd()
    try:
        os.mkdir("Music Library")
        os.mkdir("Music Library\\{}".format(folder))
    except:
        pass
    base_url = 'http://music.163.com/song/media/outer/url?id=' + id + '.mp3'
    response = requests.get(url = base_url, headers = headers)
    response.raise_for_status()
    html = response.content
    name = "".join([x for x in name if x.isalpha() or x == " " or x.isalnum()])
    with open('Music Library\\{}\\{}.mp3'.format(folder,name),'wb') as f:
        f.write(html)
    time.sleep(3)


def get_list(base_url,id):
    """爬取歌单里的歌曲，输入网易云网页版歌单后面id的数字编号"""

    """发送请求，得到响应"""
    complete_url = base_url + id
    response = requests.get(url=complete_url, headers=headers)
    response.raise_for_status()
    html = response.content
    """利用BeautifulSoup找到歌单中歌曲名称和对应编号id"""
    soup = BeautifulSoup(html, 'lxml')
    music_list = soup.find('ul', {'class': 'f-hide'})
    name = soup.find('h2').text
    music_dict = {}
    """利用find_all找到所有<a>里的内容，写入字典"""
    for music in music_list.find_all("a"):
        music_id = music['href'][9:]
        music_name = music.text
        music_dict[music_name] = music_id
    return music_dict,name


def download_list(music_dict, folder_name):
    """下载歌单"""

    """通过获取的歌单歌曲名称和id批量下载歌曲"""
    for music_name,id in music_dict.items():
        get_music(id, music_name, folder_name)
        print("歌曲 {} 下载完毕...".format(music_name))


def main():
    """主程序"""

    """目前支持三种模式的爬取，单首音乐、整个歌单或根据歌手下载"""

    pattern = input("请输入您想爬取的内容类型，目前有歌曲、歌单和歌手三种，分别用0，1，2来代表： ")


    if pattern == "0":
        id = input("请输入下载音乐id，即网易云网页版音乐链接id后面的数字编号： ")
        get_music(id,id,"Single Music")
        print("===========================================================")
        print("歌曲下载完成")


    elif pattern == "1":
        list_id = input("请输入歌单id，即网易云歌单链接id后面的数字编号： ")
        music_dict,list_name = get_list('https://music.163.com/playlist?id=',list_id)
        folder_name = "".join([x for x in list_name if x.isalpha() or x == " " or x.isalnum()])
        download_list(music_dict,folder_name)
        print("===========================================================")
        print("歌单 {} 下载完成".format(list_name))


    else:
        singer_id = input("请输入歌手id，即网易云歌手链接id后面的数字编号： ")
        music_dict,singer_name = get_list('https://music.163.com/artist?id=',singer_id)
        folder_name = "".join([x for x in singer_name if x.isalpha() or x == " " or x.isalnum()])
        download_list(music_dict,folder_name)
        print("===========================================================")
        print("歌手 {} 热门歌曲下载完成".format(singer_name))


"""运行主程序"""
if __name__ == "__main__":
    main()


