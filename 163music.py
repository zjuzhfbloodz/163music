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



def get_music(id,name,folder,headers):
    """爬取一首歌曲，输入网易云网页版id后面的数字编号"""

    """发送请求，得到响应，因为我们找到了下载url，所以直接得到了byte音乐数据，直接写入mp3文件，记得要去掉命名中的标点之类的，不然不能创建"""
    base_url = 'http://music.163.com/song/media/outer/url?id=' + id + '.mp3'
    response = requests.get(url = base_url, headers = headers)
    response.raise_for_status()
    html = response.content
    name = "".join([x for x in name if x.isalpha() or x == " " or x.isalnum()])
    with open('Music Library/{}/{}.mp3'.format(folder,name),'wb') as f:
        f.write(html)
    """加入三秒休息时间反反爬虫"""
    time.sleep(3)


def get_list(base_url,id,headers):
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


def download_list(music_dict, folder_name,headers):
    """下载歌单"""

    """通过获取的歌单歌曲名称和id批量下载歌曲"""
    for music_name,id in music_dict.items():
        get_music(id, music_name, folder_name,headers)
        print("歌曲 {} 下载完毕...".format(music_name))


def singer_to_id(headers):

    """爬取歌手对应id，写入csv文件"""
    singerid = {}
    for p in [1,2,4,6,7]:
        for i in range(3):
            for j in range(26):
                singer_url = 'https://music.163.com/discover/artist/cat?id={}&initial={}'
                html = requests.get(url = singer_url.format(p * 1000 + i + 1,65 + j),headers = headers).content.decode("utf-8")
                soup = BeautifulSoup(html, 'lxml')
                """网易云热门歌手，歌手页有图片的，和普通的分开不在一块儿，单独爬"""
                top_list = soup.find_all('div', {'class': 'u-cover u-cover-5'})
                for top in top_list:
                    singerid[top.find('a').get('title')[:-3]] = top.find('a').get('href')[11:]
                """普通歌手，没图片，没牌面"""
                singer_list = soup.find_all('li', {'class': 'sml'})
                for singer in singer_list:
                    singerid[singer.text.strip()] = singer.find('a').get('href')[11:]
    with open("singer-id.txt",'w',encoding = 'utf-8') as f:
        f.write(str(singerid))

    """曾经使用过的pandas创建csv版本，速度慢一些，而且打包成exe容量太大"""
    #https://blog.csdn.net/zhuzuwei/article/details/80890007 解决乱码
    # with open('singer-id.csv', 'w', encoding='utf_8_sig',newline='') as f:
    #     df = pd.DataFrame(singerid, index=[0])
    #     df.to_csv(f, index=None,encoding='utf_8_sig')


def get_singer_id(singer_name):
    """得到歌手id"""
    """通过用户输入的歌手名称得到该歌手id"""
    with open("singer-id.txt",'r',encoding = 'utf-8') as f:
        singerid = eval(f.read())
        return str(singerid[singer_name])

    #曾经使用过的pandas创建csv版本，速度慢一些，而且打包成exe容量太大
    # singerid = pd.read_csv('singer-id.csv')
    # return str(singerid[singer_name].values[0])


def main(headers):
    """主程序"""

    """目前支持三种模式的爬取，单首音乐、整个歌单或根据歌手下载，分别用012表示"""

    pattern = input("请输入您想爬取的内容类型，目前有歌曲、歌单和歌手三种，分别用0，1，2来代表： ")

    """创建存放MP3文件主文件夹，以及存放单首歌曲的次级文件夹"""

    try:
        os.mkdir("Music Library")
        os.mkdir("Music Library/Single Music")
    except:
        pass


    if pattern == "0":
        id = input("请输入下载音乐id，即网易云网页版音乐链接id后面的数字编号： ")
        get_music(id,id,"Single Music",headers)
        print("===========================================================")
        print("歌曲下载完成")


    elif pattern == "1":
        list_id = input("请输入歌单id，即网易云歌单链接id后面的数字编号： ")
        music_dict,list_name = get_list('https://music.163.com/playlist?id=',list_id,headers)
        print("歌单信息读取完毕！")
        folder_name = "".join([x for x in list_name if x.isalpha() or x == " " or x.isalnum()])
        try:
            os.mkdir("Music Library/{}".format(folder_name))
        except:
            pass
        print("为了防止网易云官方限制ip，本程序加入了三秒的下载间隔，请耐心等待...")
        download_list(music_dict,folder_name,headers)
        print("===========================================================")
        print("歌单 {} 下载完成".format(list_name))


    else:
        """如果是第一次使用该功能，爬取下载歌手id数据库"""
        if not os.path.exists('singer-id.txt'):
            print('\n')
            print('===============================更新后台歌手数据中====================================')
            print('\n')
            print('系统检测到您是第一次使用歌手下载功能，正在初始化后台数据中，这个过程可能需要数分钟，请您耐心等待')
            print('\n')
            print('===============================更新后台歌手数据中====================================')
            singer_to_id(headers)
            print('\n')
            print('===============================歌手数据更新完毕！====================================')
            print('\n')
        """转化歌手名称为id"""
        singer_id = get_singer_id(input("请输入歌手名称，如李健： "))
        music_dict,singer_name = get_list('https://music.163.com/artist?id=',singer_id,headers)
        print('歌手信息读取完毕！')
        folder_name = "".join([x for x in singer_name if x.isalpha() or x == " " or x.isalnum()])
        try:
            os.mkdir("Music Library/{}".format(folder_name))
        except:
            pass
        print("为了防止网易云官方限制ip，本程序加入了三秒的下载间隔，请耐心等待...")
        download_list(music_dict,folder_name,headers)
        print("===========================================================")
        print("歌手 {} 热门歌曲下载完成".format(singer_name))


"""运行主程序"""
if __name__ == "__main__":

    """我的请求头，用的是Chrome浏览器"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }

    """运行主程序"""
    main(headers)


