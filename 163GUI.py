#!/usr/bin/env python

# -*- coding: utf-8 -*- 

"""
@File: 163GUI.py

Created on 02 11 20:45 2020

@Authr: zhf12341 from Mr.Zhao

"""

import PySimpleGUI as sg
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
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}



def get_music(id,name,folder,headers,path,mode):
    """爬取一首歌曲，输入网易云网页版id后面的数字编号"""

    """发送请求，得到响应，因为我们找到了下载url，所以直接得到了byte音乐数据，直接写入mp3文件，记得要去掉命名中的标点之类的，不然不能创建"""
    base_url = 'http://music.163.com/song/media/outer/url?id=' + id + '.mp3'
    response = requests.get(url = base_url, headers = headers)
    response.raise_for_status()
    html = response.content
    name = "".join([x for x in name if x.isalpha() or x == " " or x.isalnum()])
    with open(path+'/Music Library/{}/{}.mp3'.format(folder,name),'wb') as f:
        f.write(html)
    """加入三秒休息时间反反爬虫"""
    if mode == '反反爬虫模式':
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


def download_list(music_dict, folder_name,headers,path,mode):
    """下载歌单"""

    """通过获取的歌单歌曲名称和id批量下载歌曲"""
    layout1 = [[sg.Text('正在下载 {} 歌曲中...,可以想想今晚吃什么，也可以想想我'.format(folder_name))],
               [sg.Text('', size=(5, 1), font=('Helvetica', 15), justification='center', key='text')],
               [sg.ProgressBar(len(music_dict), orientation='h', size=(50, 20), key='progressbar')],
               [sg.Button('中止下载程序')]]
    window1 = sg.Window('{} 歌曲下载进度'.format(folder_name), layout=layout1)
    progress_bar = window1['progressbar']
    i = 0
    for music_name, id in music_dict.items():
        event, values = window1.read(timeout=10)
        if event == '中止下载程序' or event is None:
            break
        get_music(id, music_name, folder_name, headers, path, mode)
        print("歌曲 {} 下载完毕...".format(music_name))
        i += 1
        progress_bar.UpdateBar(i + 1)
        window1['text'].update('{}%'.format(int(i / len(music_dict) * 100)))
    window1.close()


def singer_to_id(headers):

    """爬取歌手对应id，写入csv文件"""

    """设置字典变量singerid来保存歌手id信息"""
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



def get_singer_id(singer_name):
    """得到歌手id"""

    """通过用户输入的歌手名称得到该歌手id"""
    with open("singer-id.txt",'r',encoding = 'utf-8') as f:
        singerid = eval(f.read())
        return str(singerid[singer_name])




def music_gui(headers):

    """GUI用户界面"""

    """设置风格，可以百度"""
    sg.ChangeLookAndFeel('TealMono')

    """界面上的内容，用layout装载"""
    layout = [
        [sg.Text('欢迎来到网易云音乐下载管理器')],
        [sg.Text('选择要保存的文件夹', size=(15, 1), auto_size_text=False),
         sg.InputText(os.getcwd(),key = 'PATH'), sg.FolderBrowse()],
        [sg.Text('请选择您要爬取的歌曲类型'), sg.InputCombo(('单首歌曲下载', '歌单下载', '歌手热门歌曲下载'), size=(20, 3),key = 'PATTERN'),],
        [sg.Text('请输入您要爬取的歌曲id或歌手名称'), sg.InputText('歌曲和歌单下载填写id，歌手下载输入歌手名称',key = 'ID')],
        [sg.Text('请选择爬取模式'), sg.InputCombo(('极速爬取', '反反爬虫模式'), size=(20, 3),key = "MODE"), ],
        [sg.Button('开始爬取'), sg.Button('退出')],

    ]

    """创建GUI窗口"""
    window = sg.Window('126 Music Download Manager', layout=layout)

    while True:

        """读取用户输入"""
        event,values = window.read()
        pattern,id,path,mode = values['PATTERN'],values['ID'],values['PATH'],values['MODE']
        if event in (None,'退出'):
            break
        """运行主程序"""
        """创建存放MP3文件主文件夹，以及存放单首歌曲的次级文件夹"""

        try:
            os.mkdir(path + "/Music Library")
            os.mkdir(path + "/Music Library/Single Music")
        except:
            pass

        if pattern == "单首歌曲下载":
            get_music(id, id, "Single Music", headers, path, mode)
            print("===========================================================")
            print("歌曲下载完成")

        elif pattern == "歌单下载":
            music_dict, list_name = get_list('https://music.163.com/playlist?id=', id, headers)
            print("歌单信息读取完毕！")
            folder_name = "".join([x for x in list_name if x.isalpha() or x == " " or x.isalnum()])
            try:
                os.mkdir(path + "/Music Library/{}".format(folder_name))
            except:
                pass
            if mode == "反反爬虫模式":
                print("===========================================================")
                print("您已进入更安全的反反爬虫模式，为了防止网易云官方限制ip，本程序加入了三秒的下载间隔，请耐心等待...")
                print("===========================================================")
            else:
                print("===========================================================")
                print("您已进入极速模式，下载速度快的飞起，但是不推荐经常使用哦，zhfbloodz官方推荐使用反反爬虫模式，更安全...")
                print("===========================================================")
            download_list(music_dict,folder_name,headers,path,mode)
            print("===========================================================")
            print("歌单 {} 下载完成".format(list_name))

        elif pattern == '歌手热门歌曲下载':
            id = get_singer_id(id)
            music_dict, singer_name = get_list('https://music.163.com/artist?id=', id, headers)
            print('歌手信息读取完毕！')
            folder_name = "".join([x for x in singer_name if x.isalpha() or x == " " or x.isalnum()])
            try:
                os.mkdir(path + "/Music Library/{}".format(folder_name))
            except:
                pass
            if mode == "反反爬虫模式":
                print("===========================================================")
                print("您已进入更安全的反反爬虫模式，为了防止网易云官方限制ip，本程序加入了三秒的下载间隔，请耐心等待...")
                print("===========================================================")
            else:
                print("===========================================================")
                print("您已进入极速模式，下载速度快的飞起，但是不推荐经常使用哦，zhfbloodz官方推荐使用反反爬虫模式，更安全...")
                print("===========================================================")
            download_list(music_dict, folder_name, headers, path, mode)
            print("===========================================================")
            print("歌手 {} 热门歌曲下载完成".format(singer_name))
        else:
            pass

    window.close()

if __name__ == "__main__":

    """启动GUI界面"""
    music_gui(headers)