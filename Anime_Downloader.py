import subprocess

'''def importmodules(packages):
    for i in packages:
        try:
            globals()[i] = __import__(i)
        except:
            subprocess.call('python -m pip install --upgrade pip', stdout=subprocess.PIPE)
            pip.main(['install', i])
        finally:
            globals()[i] = __import__(i)
packages = ['selenium', 'time', 'bs4', 'gtts', 'playsound', 'os', 'shutil', 'requests', 'datetime', 'zipfile',
            'psutil','tkinter','threading']
importmodules(packages)'''
from gtts import gTTS
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from tkinter import messagebox
from tkinter.ttk import Progressbar,Style
import os, playsound, shutil, requests, pyperclip, datetime, zipfile, psutil, tkinter as tk, threading, webbrowser, \
    string, sys,time as ttime

chrome = ""
if psutil.WINDOWS:
    c = 0
    for i in ['C:\Program Files\Google\Chrome\Application', 'C:\Program Files (x86)\Google\Chrome\Application']:
        if os.path.exists(i):
            c = 1
            chrome = i
            break
    if c == 0:
        print('Google Chrome must be installed.')
        messagebox.showwarning('Warning', 'Google Chrome must be installed.')
        exit(0)
else:
    print('Operating System must be Windows.')
    messagebox.showwarning('Warning', 'Operating System must be Windows.')
    sleep(5)
    exit(0)
import sqlite3

con = sqlite3.connect('Anime_Downloader.db', check_same_thread=False)
global sema
sema = 0


def exec(query):
    while True:
        global sema
        if sema == 0: break
    sema = 1
    result_query = con.execute(query).fetchall()
    try:
        con.commit()
    except:
        pass
    sema = 0
    return result_query


def curpath():
    return os.getcwd()


exec(
    '''create table if not exists anime(animename text primary key,total text not null,episodes text,status text,processing text);''')
exec('''create table if not exists history(animename text ,episode_num text ,date_down text,time_down text);''')
exec('''create table if not exists transfer(animename text ,folder_name text ,season_name text,anime_type text);''')
exec('''create table if not exists temp(animename text ,episode_num text ,quality text,time_down text);''')
exec('''create table if not exists setting(variable text ,"value" text );''')
exec('delete from temp;')
# for i in ['anime','history','transfer','temp','setting']:print(i, exec(f'PRAGMA table_info({i});'))
# for i in exec('select * from history ;'):print(i)
p1 = curpath()
url = "https://gogoanime.sh/"
url2 = 'https://www.kiss-anime.ws/Anime/'
SYS = os.path.join(p1, 'Anime')
if not os.path.exists(SYS): os.makedirs(SYS)
start = "1"  # input("enter starting episoide(default=1): ")
stop = "999999"  # input("enter stoping episoide(default= Till Last Episoide): ")
queue = "1"  # input("Enter the number of simultaneous download you want (default=1): ")
dont = []
driverpath = os.path.join(p1, 'chromedriver')
if len(exec('select * from setting;')) < 3:
    exec('delete from setting;')
    query = ['insert into setting values("HDD"," ")', 'insert into setting values("quality","highest")',
             'insert into setting values("Minimum Storage","30")']
    for i in query: exec(i)


def rethdd(): return exec('select value from setting where variable="HDD"')[0][0]


def retpath():
    global canimename
    return os.path.join(SYS, canimename.replace('-', ' ').strip().title())


def main(anime):
    while True:
        start = "1"  # input("enter starting episoide(default=1): ")
        stop = "1"  # input("enter stoping episoide(default= Till Last Episoide): ")
        queue = "1"  # input("Enter the number of simultaneous download you want (default=1): ")
        if not start: start = "1"
        if not queue: queue = "1"
        if not stop: stop = "999999"
        if start.isnumeric() and stop.isnumeric() and queue.isnumeric(): break
    print("\rChecking network status!!!", end="")
    while True:
        try:
            requests.get('http://www.google.com')
            print("\r", end="")
            break
        except:
            print("\rChecking network status!!! : False", end="")
    print('\r' + ' ' * 50, end="")
    getting_anime_title()
    transfer()


def failedcheck(path):
    li = []
    os.chdir(path)
    for i in os.listdir():
        if str(i).endswith('crdownload'):
            li.append([i, os.stat(i).st_size])
    if li: sleep(10)
    cou = 0
    for i in os.listdir():
        if str(i).endswith('crdownload'):
            for j in li:
                if i == j[0]:
                    if os.stat(i).st_size == j[1]:
                        cou += 1
    return cou


def totalep_update():
    print('\rUpdating Anime Episodes...', end="")
    srt = ""
    f = []
    for i in exec('select * from anime;'):
        f.append(i)
    for i in f:
        try:
            a = i[0]
            res = anime_exists(a)
            if not res[0]:
                a += '-'
                res = anime_exists(a)
            tota = str(res[1])
            if int(res[1]) != int(i[1]):
                exec(f'update anime set total= {tota} where animename ="{a}";')
            if i[3].lower() != res[2].lower().strip("\n"):
                status = res[2].lower().strip('\n')
                exec(f'update anime set status= "{status}" where animename ="{a}";')
            if tota == i[2].split(',')[-1] or int(tota) == len(i[2].split(',')):
                exec(f'update anime set processing= "n" where animename ="{a}";')
            else:
                exec(f'update anime set processing= "y" where animename ="{a}";')
        except:
            pass


def getting_anime_title():
    anime = list(map(lambda x: x[0], con.execute('select animename from anime where processing="y";').fetchall()))
    for animename in anime:
        remove_empty_folders()
        if not stroage_check_2():
            break
        a = ""
        for i in animename.split():
            i.strip(') ( :')
            if str(i) != '-': z = str(i).strip('):(- ')
            if z: a += z + '-'
        a = a[:-1].title().strip()
        res = anime_exists(a)
        if not res[0]:
            a += '-'
            res = anime_exists(a)
        if res[0]:
            print(f'\r\t{anime.index(animename) + 1}/{len(anime)}', end="")
            if animename.lower() in dont: continue
            getting_anime_episode(a, res[1])
        else:
            print(
                f'\r\t{anime.index(animename) + 1}/{len(anime)}\tAnime \'%s\' doesn\'t extsts...' % a.replace('-', ' '))
        closedriver()
        transfer()
        remove_empty_folders()
    animecheck()


def download_driver():
    page = requesturl("https://chromedriver.chromium.org/downloads")
    soup = BeautifulSoup(page.content, "html.parser")
    link = soup.findAll('a', {'style': "background-color:transparent"})
    for i in link:
        ver = get_version_number(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')

        if ver[:ver.find('.')] in i.text:
            a = str(i.text)
            link = str(i.attrs['href'])
            link = link[:link.find('/index')]
            link += "/" + a[a.find(' ') + 1:] + '/chromedriver_win32.zip'
            download(link, os.path.join(p1, 'chromedriver_win32.zip'))
            with zipfile.ZipFile(os.path.join(p1, 'chromedriver_win32.zip'),
                                 "r") as zip_ref:
                zip_ref.extractall(p1)
            zip_ref.close()
            os.remove(os.path.join(p1, 'chromedriver_win32.zip'))


def download(url, name):
    r = requests.get(url, stream=True,timeout=120)
    total=int(r.headers['content-length'])/1024#1024*1024
    try:
        s1.geometry('715x528')
        progress['maximum']=total
        progress.pack()
        currentdown()
    except:pass
    with open(name, 'wb')as f:
        c=0
        dl=0
        start=ttime.perf_counter()
        for data in r.iter_content(chunk_size = 1024):
            if data:
                c+=1
                dl+=len(data)
                f.write(data)
                try:
                    speed=dl//(ttime.perf_counter() - start)
                    speed='%.3f'%(speed/1024)
                    tleft=(total-c)/float(speed)/60
                    ttleft=str('%.1f'%tleft)+' min(s) left'
                    if tleft>60:
                        ttleft=str(int(tleft/60)) +' hours '+str(int(tleft%60)) +'min(s) left'
                    progress['value']=c
                    per=c/total
                    per*=100
                    per='%.2f' % per
                    style.configure("LabeledProgressbar", text=per+f'%     {"%.2f"%(c/1024)}/{"%.2f"%(total/(1024))} MB   {speed} KBps  {ttleft}  ')
                    s1.update_idletasks()
                except:pass
    try:
        progress.pack_forget()
        s1.geometry('715x501')
    except:pass
    return f'Download Complete for {name}'


while True:
    if not os.path.exists('Anime_Downloader.png'): download(
        'https://gogoanime.so/img/icon/logo.png',
        os.path.join(p1, 'Anime_Downloader.png'))
    break


def get_version_number(filename):
    try:
        ver = []
        for i in os.listdir(chrome):
            if i[:2].isnumeric(): ver.append(i)
        ver = sorted(ver)
        return (ver[-1][:3])
    except:
        return "Unknown version"


def opendriver(a):
    global driverpath
    if not os.path.exists(os.path.join(driverpath + '.exe')):
        download_driver()
        driverpath = os.path.join(p1, 'chromedriver')
    if os.path.exists((os.path.join(p1, 'chromedriver_win32.zip'))): os.remove(
        os.path.join(p1, 'chromedriver_win32.zip'))
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": os.path.join(SYS, a.replace('-', ' ').strip())}
    chromeOptions.add_experimental_option("prefs", prefs)
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-logging"])
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument("--proxy-bypass-list=*")
    chromeOptions.add_argument("--disable-web-security")
    chromeOptions.add_argument("--log-level=3")
    chromeOptions.add_argument("--proxy-server='direct://'")
    chromeOptions.add_argument("--hide-scrollbars")
    global driver
    try:
        driver = webdriver.Chrome(driverpath, options=chromeOptions)
    except:
        download_driver()
        driverpath = os.path.join(p1, 'chromedriver')
        print(driverpath)
        driver = webdriver.Chrome(driverpath, options=chromeOptions)
    # did=driver.service.process.pid


def getting_anime_episode(a, total):
    animelist, alreadydownloaded = already_downloaded(a, total)
    global sizetotal
    sizetotal = len(str(total))
    on = 0
    for i in range(1, total + 1):
        if os.path.exists(os.path.join(p1, 'waste')): os.remove(os.path.join(p1, 'waste'))
        if a.replace('-', ' ').lower().strip() not in animelistmain(): return
        if str(i).zfill(sizetotal) in alreadydownloaded: continue
        if not stroage_check_2(): break
        try:
            driver.window_handles
        except:
            quality = exec('select value from setting where variable="quality";')[0][0]
            if on == 0: print(
                f'\tDownloading {a.replace("-", " ").strip()}...   list of episoides 1-{total}, at {str(datetime.datetime.now())[:-7]},\
                \n\t\t\t Saving in [{os.path.join(SYS, a.replace("-", " ").strip())}], at [{quality.title()}] Quality')
            on = 1
            system_check(a)
            os.chdir(os.path.join(SYS, a.replace('-', ' ').strip()))
            # opendriver(a)
        global cepno, canimename
        cepno = i
        canimename = a
        get_anime_download_link()
        totalep_update()
        if i == total + 1: print()
    path = os.path.join(SYS, a.replace('-', ' ').strip())
    while True:
        c = 0
        if os.path.exists(path):
            for i in os.listdir(path):
                if os.path.splitext(i)[1] == ".crdownload": c += 1
            if c == 0 and queuecheck(path, queue): break
        else:
            break
    try:
        driver.close()
    except:
        pass


def downstarted(a, no):
    sleep(10)
    for i in os.listdir(os.path.join(SYS, a)):
        if i.startswith('EP') and i.endswith('crdownload'):
            no1 = str(i[i.find('.') + 1:])
            no1 = no1[:no1.find('.')]
            if no1 == str(no):
                return True
    # print(f' Failed  at {str(datetime.datetime.now().time())[:-7]}')
    return False


def get_anime_download_link():
    a = canimename
    i = cepno
    for loop in range(2):
        soup = BeautifulSoup(requesturl(url + '/' + a.lower() + f'-episode-{i}').content, "html.parser").find('div', {
            'class': 'anime_video_body_cate'})
        if not soup:
            soup = BeautifulSoup(requesturl(url + '/' + a.lower() + f'-episode-{i}-{i}').content, "html.parser").find(
                'div',
                {
                    'class': 'anime_video_body_cate'})
        if not soup:
            soup = BeautifulSoup(requesturl(url + '/' + a.lower() + f'episode-{i}').content, "html.parser").find('div',
                                                                                                                 {
                                                                                                                     'class': 'anime_video_body_cate'})
        if not soup:
            soup = BeautifulSoup(requesturl(url + '/' + a.lower()[:-3] + f'episode-{i}').content, "html.parser").find(
                'div',
                {
                    'class': 'anime_video_body_cate'})
        if not soup:
            soup = BeautifulSoup(requesturl(url + '/' + a.lower()[:-11] + f'-episode-{i}').content, "html.parser").find(
                'div', {
                    'class': 'anime_video_body_cate'})
        try:
            downlink = (soup.find('a', {'target': '_blank'}).attrs['href'])
            break
        except:
            pass
    qualitystarted = ""
    system_check(a)
    '''try:startdown(a,downlink,i)
    except:'''
    quality='0'
    dlink=''
    for link in BeautifulSoup(requesturl(downlink).content, "html.parser").find('div', {'class', 'mirror_link'}).contents[4:]:

        if str(link).strip():
            try:qualit = (str(BeautifulSoup(str(link), "html.parser").find('a').text).split('\n')[1].strip())
            except:pass
            qualit = qualit[1:qualit.find('P')]
            if qualit=='HD':continue
            if int(qualit)>int(quality):
                quality=qualit
                dlink=str(BeautifulSoup(str(link), "html.parser").find('a').attrs['href'])
    if quality != 'HD' or True:
        print(f"\r\t\t\tDownloading Episode {i}", end="")
        r = requests.get(dlink, stream=True)
        if r.headers['content-type']=='video/mp4':
            named=f'EP.{i}.{quality}p.mp4'
            name=os.path.join(SYS, a.replace("-", " ").strip(),named)
            q = quality
            an = a.replace("-", " ").strip().title()
            while True:
                tim = str(datetime.datetime.now().time())[:-7]
                exec('delete from temp;')
                exec(f'insert into temp values("{an}","{str(i)}","{str(q)}","{tim}");')
                print(
                    f"\r\t\t\tDownloading Episode {i} at {q}P Quality started at {str(datetime.datetime.now().time())[:-7]}")
                try:
                    download(dlink,name)
                    break
                except:os.remove(name)
            exec('delete from temp;')
            currentdown()
            progress.pack_forget()
            s1.geometry('715x501')

        download_update(a, sizetotal, os.path.join(SYS, a.replace('-', ' ').strip()))


def startdown(a, link, i):
    page = requesturl(link)
    link = str(
        BeautifulSoup(requesturl(link).content, "html.parser").find('div', {'class', 'mirror_link'}).contents[-2])
    quality = (str(BeautifulSoup(link, "html.parser").find('a').text).split('\n')[1].strip())
    quality = quality[1:quality.find('P')]
    if quality == 'HD':
        print(f'\r\t\t\tDownloading Episode {i} skipped and not started at {str(datetime.datetime.now().time())[:-7]}')
        return
    link = BeautifulSoup(link, "html.parser").find('a').attrs['href']
    '''r = requests.get(link, stream=True).headers['Content-length']
    print(float(int(r)/8)/325.82)'''
    if (requests.get(link, stream=True).headers['Content-type'].lower()) == 'video/mp4':
        print(
            f"\r\t\t\tDownloading Episode {i} at {quality}P Quality started at {str(datetime.datetime.now().time())[:-7]}")
        name = os.path.join(SYS, a.replace('-', ' ').strip(), (f'EP.{i}.{quality}p.mp4'))
        an = a.replace("-", " ").strip().title()
        tim = str(datetime.datetime.now().time())[:-7]
        exec('delete from temp;')
        exec(f'insert into temp values("{an}","{str(i)}","{str(quality)}","{tim}");')
        currentdown()
        download(link, name)


def getting_anime_episode_download(downlink):
    global driver
    driver.get(downlink)
    if driver.title == 'Attention Required! | Cloudflare': print(' Authenticating...', end="")
    while True:
        if driver.title == 'Attention Required! | Cloudflare':
            driver.refresh()
            bypassAuth()
            # volume(100)
            # audio('Authentication Required')
        if driver.title != 'Attention Required! | Cloudflare': break
    # download('https://vidstreaming.io/goto.php?url=aHR0cHM6LyAawehyfcghysfdsDGDYdgdsfsdfwstdgdsgtert9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL250aC1idWNrc2F3LTI3ODkxMS9mb2xkZXI4LzIzYV8xNTkyNjA2NDY3MTQxMzkwLm1wNA==&title=(HDP%20-%20mp4)%20Plunderer+Episode+23','try555.mp4')
    list1 = []
    list2 = []
    if len(driver.window_handles) == 0: exit(0)
    sleep(1)
    for i in driver.find_elements_by_tag_name("div"):
        if 'DOWNLOAD' in i.text and 'P - MP4' in i.text and len(i.text) <= 32:  # and 'HDP' not in i.text:
            list1.append(i)
            z = str(i.text)
            z = z[z.find('(') + 1:z.find('P')]
            list2.append(z)
    if len(list2) > 1:
        for i in list2:
            if 'HD' in i: list2.remove(i)
    elif len(list2) == 1 and 'HD' == list2[0] or len(list2) == 0:
        list1[0].click()
        return ' HDP Quality'
    z = list2[0]

    if len(list2) > 0: pass
    z = list2[0]
    for i in range(len(list2)):
        if str(list2[i]).isnumeric():
            if exec('select value from setting where variable="quality"')[0][0] == 'highest':
                if int(list2[i]) > int(z):
                    z = list2[i]
            else:
                if int(list2[i]) < int(z):
                    z = list2[i]
    list2 = z
    if len(driver.window_handles) == 0: exit(0)
    title = driver.title
    for i in list1:
        if list2 in i.text:
            i.click()
            sleep(5)
    for i in range(1, len(driver.window_handles)):
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
    if driver.title != title: raise ZeroDivisionError
    return f'at {list2}P Quality '


def bypassAuth():
    try:
        global driver
        driver.switch_to.default_content()
        d = datetime.datetime.now()
        try:
            driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/div/div[1]/div/form/div[4]/input').click()
        except:
            pass
        while True:
            try:
                if driver.title != 'Attention Required! | Cloudflare': return
                try:
                    driver.find_element_by_xpath(
                        '/html/body/div/div[2]/div[2]/div/div/div[1]/div/form/div[4]/input').click()
                except:
                    pass
                d2 = datetime.datetime.now()
                d3 = d2 - d
                driver.switch_to.frame(0)
                driver.find_element_by_tag_name('div').click()
                driver.switch_to.default_content()
                break
            except:
                if int(d3.seconds) > 180:
                    driver.refresh()
                    d = datetime.datetime.now()
                sleep(10)
        try:
            driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/div/div[1]/div/form/div[4]/input').click()
        except:
            pass
        sleep(5)
        if driver.title != 'Attention Required! | Cloudflare': return
        driver.switch_to.frame(1)
        for i in range(0, 2):
            sleep(2)
            for i in driver.find_elements_by_class_name('border'):
                i.click()
                sleep(1)
            driver.find_element_by_class_name('button-submit').click()
        sleep(3)
        driver.switch_to.default_content()
        try:
            driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/div/div[1]/div/form/div[4]/input').click()
        except:
            pass
        sleep(20)
        if driver.title != 'Attention Required! | Cloudflare': return
        try:
            driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/div/div[1]/div/form/div[4]/input').click()
        except:
            pass
    except:
        driver.switch_to.default_content()
        driver.refresh()


def requesturl(urllink):
    while True:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
            page = requests.get(urllink, headers=headers)
            return page
        except:
            pass


def animecheck():
    exec('delete from anime where status="completed" and processing="n";')
    dele = []
    for i in exec('select animename from transfer where animename not in (select animename from anime);'):
        delete = 'y'
        if os.path.exists(os.path.join(SYS, i[0].title())):
            for j in os.listdir(os.path.join(SYS, i[0].title())):
                if j.endswith('.mp4'): delete = 'n'
        if delete == 'y':
            dele.append(i[0])
    for i in dele:
        exec(f'delete from transfer where animename="{i}";')


def anime_exists(a):
    page = requesturl(url + '/category/' + a.replace(' ', '-'))
    soup = BeautifulSoup(page.content, "html.parser")
    end_ep = soup.find('a', {'class': 'active'})
    p = soup.findAll('p', {'class': 'type'})
    for i in p:
        if 'Status' in (i.text):
            status = str(i.text)
            status = status[status.find(":") + 2:]
        if 'Type' in i.text:
            atype = str(i.text)
            atype = atype[atype.find(':') + 2:].strip()
    if end_ep:
        try:
            end_ep = end_ep.text.split('-')[1]
        except:
            end_ep = end_ep.text.split('-')[0]
        return [True, int(end_ep), status, atype]
    return [False, 0]


def system_check(a):
    if os.path.exists(os.path.join(SYS, a.replace('-', ' ').strip())):
        for i in os.listdir(os.path.join(SYS, a.replace('-', ' ').strip())):
            if os.path.splitext(i)[1] == '.crdownload' or os.path.splitext(i)[1] == '' or i.startswith('EP.'):
                while True:
                    os.remove(os.path.join(SYS, a.replace('-', ' '), i))
                    break
            if os.path.splitext(i)[1] == '.log':
                try:
                    os.remove(os.path.join(SYS, a.replace('-', ' '), i))
                except:
                    pass
    else:
        os.mkdir(os.path.join(SYS, a.replace('-', ' ')))


def stroage_check_2():
    total, used, free = shutil.disk_usage(SYS)
    if (free // (2 ** 30)) < int(exec('select value from setting where variable= "Minimum Storage";')[0][0]):
        HDD = exec('select value from setting where variable= "HDD"')[0][0]
        total, used, free = shutil.disk_usage(HDD)
        if (free // (2 ** 30)) > int(exec('select value from setting where variable= "Minimum Storage";')[0][0]):
            print(f'\r\nInsufficient Storage!!!    Trying to move to {HDD}...\n')
            return transfer()
        return False
    return True


def transfer():
    global transferbtn
    HDD = exec('select value from setting where variable= "HDD"')[0][0]
    if HDD == "": return False
    if HDD == SYS: return False
    files1 = []
    for root, folders, files in os.walk(SYS):
        for i in files:
            if i.endswith('mp4'):
                files1.append(i)
    if not files1: return False
    '''if not os.path.exists(HDD):
        #volume(100)
        try:
            audio('Insert harddrive and press enter to start tranfering  files')
        except:
            pass
        #input('Insert harddrive and press enter to start tranfering  files')'''
    sleep(2)
    if os.path.exists(HDD):
        total, used, free = shutil.disk_usage(HDD)
        # if (free // (2 ** 30)) <= minstorage:return False
        try:
            transferbtn['state'] = tk.DISABLED
            transferbtn['bg'] = 'green'
            f = []
            for i in exec('select * from transfer;'):
                f.append(list(i))
            season = {}
            for s in f:
                season[s[0].lower()] = s[1:]
            for i in (os.listdir(SYS)):
                if i.lower() in list(season.keys()):
                    if season[i.lower()][2] != 'movie':
                        path111 = os.path.join(HDD, season[i.lower()][2].title(), season[i.lower()][0].title(),
                                               season[i.lower()][1].title())
                    else:
                        path111 = os.path.join(HDD, 'Anime ' + season[i.lower()][2].strip() + 's'.title(), i.title())
                    if not os.path.exists(path111): os.makedirs(path111)
                    for j in os.listdir(os.path.join(SYS, i)):
                        if os.path.splitext(j)[1] == '.mp4' and not j.startswith('EP.'):
                            try:
                                shutil.copy(os.path.join(SYS, i, j), path111)
                                if season[i.lower()][2] == 'movie': os.rename(os.path.join(path111, j),
                                                                              os.path.join(path111, i.title() + '.mp4'))
                                os.remove(os.path.join(SYS, i, j))
                            except Exception as e:
                                print(os.path.join(SYS, i, j), path111)
                        else:
                            if j.startswith('EP.'):
                                try:
                                    os.remove(os.path.join(SYS, i, j))
                                except:
                                    pass
                    try:
                        if os.path.isdir(os.path.join(SYS, i)) and os.stat(
                                os.path.join(SYS, i)).st_size == 0: os.remove(
                            os.path.join(SYS, i))
                    except:
                        pass
                else:
                    pass
                # print(f'Error!!!! {i.title()} not in animeseason.txt file')
            print('\r', end="")
            transferbtn['bg'] = 'gray'
            transferbtn['state'] = tk.NORMAL
            return True
        except Exception as e:
            print('\r', e, end="")
            transferbtn['bg'] = 'gray'
            transferbtn['state'] = tk.NORMAL
            return False
    else:
        print('\r', end="")
        return False


def already_downloaded(a, total=0):
    animelist = animelistmain()
    alreadydownloaded = []
    a = a.lower().replace('-', ' ').strip()
    for i in str(exec(f'select episodes from anime where animename="{a}"')[0][0]).split(','):
        if i.strip() != "": alreadydownloaded.append(str(int(i)).zfill(len(str(total))))
    return [animelist, alreadydownloaded]


def download_update(a, nodigit, path):
    global cepno
    ep = str(cepno)
    for i in os.listdir(path):
        if os.path.splitext(i)[1] == '' and not os.path.isdir(i):
            z = os.path.splitext(i)[0]
            a1 = z[z.find(')') + 2:]
            z1 = ""
            animestr = ""
            for j in a1.split('+'):
                if str(j).isnumeric():
                    j = j.zfill(nodigit)
                    animestr += f',{j}'
                z1 += j + " "
            rename(i, z1, animestr, a)
        elif i.startswith('EP') and i.endswith('mp4'):
            epno = i[i.find('.') + 1:]
            epno = epno[:epno.find('.')].zfill(nodigit)

            z1 = a.replace('-', " ") + ' Episode ' + epno + ' '
            if int(epno) != 1: epno = ',' + epno
            rename(i, z1, epno, a)
        elif not i.startswith('EP') and i[:2].isnumeric() and i.endswith('mp4'):
            z1 = a.replace('-', " ") + ' Episode ' + (ep) + ' '
            if ',' not in ep and int(ep) != 1: ep = ',' + ep
            rename(i, z1, ep, a)


def rename(i, z1, animestr, a):
    try:
        animestr = animestr
        anime = a.lower().replace('-', ' ').strip()
        os.rename(i, z1[:-1] + '.mp4')
        episodes = str(exec(f'select episodes from anime where animename="{anime}"')[0][0]) + f'{animestr}'
        exec(f'update anime set episodes="{episodes}" where animename="{anime}";')
        if ',' not in animestr: animestr = ',' + animestr
        if int(str(exec(f'select total from anime where animename="{anime}"')[0][0])) < int(animestr[1:]):
            exec(f'update anime set processing="n" where animename="{anime}";')
        else:
            exec(f'update anime set processing="y" where animename="{anime}";')
        datetime1 = datetime.datetime.now()
        exec(
            f'insert into history values ("{anime}","{animestr[1:]}","{datetime1.date()}","{str(datetime1.time())[:-7]}");')
    except Exception as e:
        os.remove(i)
        print(e)
        print(
            f'insert into history values ("{anime}","{animestr[1:]}","{datetime1.date()}","{str(datetime1.time())[:-7]}");')


def queuecheck(path, no):
    c = 0
    sleep(2)
    for i in os.listdir(path):
        if os.path.splitext(i)[1] == '.crdownload': c += 1
    f = failedcheck(path)
    if f == int(no):
        try:
            system_check(os.path.split(path)[1].lower())
            get_anime_download_link()
        except:
            pass
    if c < int(no):
        return True
    else:
        return False


def closedriver():
    try:
        global driver
        for i in range(len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[0])
            driver.quit()
            if driver.switch_to.alert:
                driver.switch_to.alert.dismiss()
    except:
        pass
    try:
        for i in psutil.process_iter():
            a = i.name()
            if a == 'chromedriver.exe':
                try:
                    os.kill(i.pid, 9)
                except Exception as e:
                    print(e)
    except:
        pass


def remove_empty_folders():
    os.chdir(SYS)
    for i in os.listdir():
        if os.path.isdir(i) and os.stat(i).st_size == 0:
            try:
                os.rmdir(i)
            except:
                pass


def animelistmain():
    anime = []
    for i in (exec('select animename from anime;')):
        for j in i:
            anime.append(j.strip())
    return anime


def searchanime(a):
    page = requesturl(url + '//search.html?keyword=' + a.lower().replace(' ', '%20'))
    soup = BeautifulSoup(page.content, "html.parser")
    anime = soup.find('div', {'class': 'last_episodes'}).findAll('li')
    list = []
    for i in anime:
        b = (str(i.text))
        link = str(i.find('a').attrs['href'][10:]).replace('-', ' ')
        b1 = b[:b.find('Released')].strip()
        b2 = b[b.find('Released'):].strip()
        b3 = anime_exists(link)
        b4 = b3[3]
        b3 = b3[1]
        list.append([b1, b2, link, f'Total Episodes: {b3}', b4])
    return list


def clear_unfinished_download():
    for i in os.walk(SYS):
        if i:
            for j in i[2]:
                if j.endswith('.crdownload') or j.endswith('.log'):
                    try:
                        os.remove(os.path.join(i[0], j))
                    except:
                        pass


def main1():
    tries = 1
    closedriver()
    clear_unfinished_download()
    remove_empty_folders()
    # startup()
    c = 0  # input("Do you want menu to come again(1/0): ")
    print(f'\rNo of tries: {tries} \t\t\tat {str(datetime.datetime.now())[:-7]} ')
    while True:
        try:
            clear_unfinished_download()
            transfer()
            closedriver()
            remove_empty_folders()
            if datetime.datetime.now().minute == 0 :
                totalep_update()
                anime = animelistmain()
                closedriver()
                remove_empty_folders()
                main(anime)
                if c == '1':
                    print()
                    # startup()
                    c = input("Do you want menu to come again(1/0): ")
            else:
                timewait = 60 - (datetime.datetime.now().minute % 60)
                print(
                    f"\r\twait for {timewait} minutes for the program to run, current time: {str(datetime.datetime.now().time())[:-7]} ",
                    end="")
                if timewait > 2:
                    sleep((timewait - 2) * 60)
                else:
                    sleep(1)
        # break
        # os.system('shutdown -s -t 10')
        except Exception as ex:
            tries += 1
            print('\nNo of tries: {} \t\t\tat {}: {}'.format(tries, str(datetime.datetime.now()))[:-7])  # ,ex)
            try:
                closedriver()
            except:
                pass
            sleep(2)


def audio(text):
    out = gTTS(text=text, lang='en', slow=False)
    out.save(os.path.join(p1, "try.mp3"))
    playsound.playsound(os.path.join(p1, "try.mp3"))
    os.remove(os.path.join(p1, "try.mp3"))


def systemtray():
    global trayicon

    def opena():
        trayicon.hide()
        window()

    app = QApplication(sys.argv)
    trayicon = QSystemTrayIcon(QIcon('Anime_Downloader.png'), app)
    trayicon.setToolTip('Anime Downloader')
    menu = QMenu()
    max = menu.addAction('Maximise')
    max.triggered.connect(opena)
    exit = menu.addAction('Exit')
    exit.triggered.connect(app.exit)

    trayicon.setContextMenu(menu)
    sys.exit(app.exec_())


x = threading.Thread(target=(main1))
x.daemon = True



def window():
    global animelist, totalep, transferbtn, currentdown,progress,s1,style
    animelist = []

    def s1animeadd1(event):
        s1animeadd()

    def s1animeadd():
        def search():
            if e1.get() != "" and f2['text'] != 'History':
                global animelist
                animelist = searchanime(str(e1.get()).lower())
                butn1['bg'] = 'grey'
                butn4['bg'] = 'grey'
                f2.grid_forget()
                f4.grid_forget()
                f3.grid_forget()
                f3.grid(row=1, column=0)
                addbtn.grid_forget()
                f2.grid(row=1, column=0)
                f2['text'] = 'Search Result'
                f3.grid_forget()
                f3.grid(row=2, column=0, sticky=tk.W)
                f4.grid_forget()
                l1.delete(0, tk.END)
                e1.delete(0, tk.END)
                height = l1['height']
                l1['height'] = 8
                c = 0
                size = len(str(len(animelist)))
                for i in animelist:
                    c += 1
                    text = f'{str(c).zfill(size)}. {i[0]} ; {i[3]} ;  {i[1]} ; Type: {i[4]}'
                    l1.insert(tk.END, text)
                addbtn.grid(row=0, column=0, sticky=tk.W)
            elif e1.get() != "" and f2['text'] == 'History':
                butn1['bg'] = 'grey'
                butn4['bg'] = 'grey'
                anime = e1.get()
                li = exec(f'select * from history where animename LIKE "%{anime.lower()}%" order by animename;')
                li = list(dict.fromkeys(li))
                # li=sorted(li, key=lambda x: x[1])
                if len(li) != 0:
                    l1.delete(0, tk.END)
                    e1.delete(0, tk.END)
                    for i in li:
                        text = str(li.index(i) + 1).zfill(len(str(len(li)))) + '.  ' + i[
                            0].title() + ', Episode No = ' + i[1] + f' at Date= {i[2]} Time= {i[3]}'
                        l1.insert(tk.END, text)

        x2 = threading.Thread(target=search)
        x2.start()

    def s1animeadd2():
        global totalep
        item = str(l1.get(tk.ANCHOR))
        if item.strip() == "": return
        totalep = item[item.find('s:') + 3:].strip()
        totalep = totalep[:totalep.find(' ')]
        if item[item.rfind(':') + 2:].lower() == 'movie':
            movie = animelist[int(str(item[:item.find(".")].strip())) - 1][2]
            exec(f'insert into anime values("{movie}","1","","completed","y");')
            exec(f'insert into transfer values("{movie}","","","movie");')

        else:
            animename['text'] = animelist[int(str(item[:item.find('.')].strip())) - 1][2]
            animename.grid(row=0, column=1)
            seasonno.grid_forget()
            seasonof.grid_forget()
            seasonnol.grid_forget()
            seasonofl.grid_forget()
            seasonof.grid(row=1, column=1)
            aname = item[item.find('.') + 1:item.find(';')].strip()
            if len(aname) > 30:
                aname = aname[:30]
                aname = aname[:aname.rfind(' ')] + '...'
            animename['text'] = aname
            seasonofl['text'] = f"Enter the name of anime whose part is {aname} :"
            seasonof['text'] = ""
            seasonno['text'] = ""
            seasonofl.grid(row=1, column=0)
            seasonno.grid(row=2, column=1)
            seasonno.delete(0, tk.END)
            seasonof.delete(0, tk.END)
            seasonof.insert(tk.END, item[item.find('.') + 1:item.find(';')].strip())
            seasonnol.grid(row=2, column=0)
            addbtn2.grid(row=3, column=1)
            addbtn2['command'] = lambda a=animelist[int(str(item[:item.find('.')].strip())) - 1][2]: s1animeadd3(a)

    def s1animeadd3(movie):
        global totalep
        if str(seasonof.get()) != "" and str(seasonno.get()) != "":
            movie = movie
            # movie=animename['text']
            exec(f'insert into anime values("{movie}","{totalep}","","ongoing","y");')
            exec(f'insert into transfer values("{movie}","{seasonof.get()}","season {seasonno.get()}","anime");')
            animename.grid_forget()
            seasonno.grid_forget()
            seasonof.grid_forget()
            seasonnol.grid_forget()
            seasonofl.grid_forget()
            addbtn2.grid_forget()

    def s1animelist(filename):
        f2.grid(row=2, column=0)
        f3.grid_forget()
        f4.grid_forget()
        f4.grid(row=1, column=0, sticky=tk.W)
        if filename == 'anime':
            cd['text'] = f'Currently Downloading '
        animelist = exec(f'select * from {filename}')
        if filename == 'anime':
            animelist = sorted(animelist, key=lambda x: x[0])
        cd.pack_forget()
        cd.pack(fill=tk.X)
        l1.delete(0, tk.END)
        l1['height'] = 15
        f2['text'] = f'Anime in list {len(animelist)}'
        if filename == 'history':
            animelist = exec('select animename from history;')[::-1]
            animelist = list(dict.fromkeys(animelist))[:-1]

            cd['text'] = f'Anime Downloaded till now: '
            f2['text'] = 'History'
        for i in animelist:
            if filename == 'anime':
                downloaded = '0'
                if not len(i[2].split(',')) < 1 and i[2].split(',')[-1] != '': downloaded = str(len(i[2].split(',')))
                if i == "": continue
                text = str(animelist.index(i) + 1).zfill(len(str(len(animelist)))) + '. ' + i[
                    0].title() + ', Total Episode= ' + i[1] + ', Downloaded=' + downloaded
                l1.insert(tk.END, text)
                l1.itemconfig("end", bg="green" if int(i[1]) > int(downloaded) else "grey")
            if filename == 'history':
                text = str(animelist.index(i) + 1).zfill(len(str(len(animelist)))) + '.  ' + i[0].title()
                l1.insert(tk.END, text)
        l1.insert(tk.END, '')
        l1.pack(side=tk.LEFT)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        currentdown()

    def s1animedelete():
        if 'Anime in list' in f2['text']:
            item = str(l1.get(tk.ANCHOR))
            item = item[item.find(' ') + 1:item.find(',')].lower()
            exec(f'delete from anime where animename="{item}";')
            s1animelist('anime')

    def currentdown():
        try:
            if 'Anime in list' in f2['text']:
                butn1['bg'] = 'cyan'
                butn4['bg'] = 'grey'
                f = exec('select * from temp;')
                if f:
                    f = f[0]
                    if cd['bg'] != 'green' or cd[
                        'text'] != f'Currently Downloading: {f[0]} Episode {f[1]} at {f[2]}p started at {f[3]}':
                        cd['text'] = f'Currently Downloading: {f[0]} Episode {f[1]} at {f[2]}p started at {f[3]}'
                        cd['bg'] = 'green'
                        f4['bg'] = 'green'
                else:
                    if cd['text'] != f'Currently Downloading: ': cd['text'] = f'Currently Downloading: '
                    cd['bg'] = 'grey'
                    f4['bg'] = 'grey'
            elif f2['text'] == 'History':
                butn4['bg'] = 'cyan'
                butn1['bg'] = 'grey'
                cd['bg'] = 'grey'
                f4['bg'] = 'grey'
                cd['text'] = 'Anime Downloaded till now'
        except:
            pass

    def double_click(event):
        print(end="")
        animename.grid_forget()
        seasonno.grid_forget()
        seasonof.grid_forget()
        seasonnol.grid_forget()
        seasonofl.grid_forget()
        addbtn2.grid_forget()
        if f2['text'] == "History":
            item = str(l1.get(tk.ANCHOR))
            if item.strip() == "": return
            if 'Episode' in item:
                aname = item[item.find(' ') + 1:item.find(',')].strip().lower()
                enu = int(item[item.find('=') + 2:item.find(' at')].strip())
                # enum=int(enum[:enum.find(' at')].strip())
                available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)][::-1]
                available_drives.append(SYS)
                for address in available_drives:
                    file = []
                    for root, folders, files in os.walk(address):
                        for i in files:
                            if aname in i.lower(): file.append(os.path.realpath(os.path.join(root, i)))
                    if len(file) == 0:
                        continue
                    elif (len(file)) == 1:
                        os.startfile(file[0])
                    else:
                        for i in file:
                            try:
                                if enu == int(i[i.rfind('e ') + 2:i.rfind('.')].strip()) and aname == i[i.rfind(
                                        "\\") + 1:i.find('Episode') - 1].lower(): os.startfile(i)
                            except:
                                pass
            else:
                l1.delete(0, tk.END)
                anime = item[item.find('.') + 1:].lower().strip()
                li = exec(f'select * from history where animename ="{anime.lower()}";')
                li = list(dict.fromkeys(li))
                # li=sorted(li, key=lambda x: x[1])
                if len(li) != 0:
                    l1.delete(0, tk.END)
                    e1.delete(0, tk.END)
                    for i in li:
                        text = str(li.index(i) + 1).zfill(len(str(len(li)))) + '.  ' + i[
                            0].title() + ', Episode No = ' + i[1] + f' at Date= {i[2]} Time= {i[3]}'
                        l1.insert(tk.END, text)
        elif f2['text'] == "Setting List":
            item = str(l1.get(tk.ANCHOR))
            item = item[:item.find(':')].strip()
            if item == 'Transfe':
                item = exec(f'select animename from anime where animename not in (select animename from transfer);')
                if item:
                    def forget():
                        settingbtn['command'] = setting
                        setting()

                    settingbtn['command'] = forget
                    cd['text'] = 'Transfer'
                    f2['text'] = 'Transfer'
                    l1.delete(0, tk.END)
                    for i in item:
                        l1.insert(tk.END, i[0].title())
            elif item == 'Hdd':
                hdd = filedialog.askdirectory()
                if hdd.strip() != '':
                    exec(f'update setting set value = "{hdd}" where variable="HDD"')
                setting()
            elif item == 'Quality':
                def forget():
                    R1.grid_forget()
                    R2.grid_forget()
                    settingbtn['command'] = setting
                    setting()

                settingbtn['command'] = forget
                f2.grid_forget()
                f3.grid_forget()
                f4.grid_forget()
                f4.grid(row=1, column=0, sticky=tk.W)
                l1.delete(0, tk.END)
                cd['text'] = "Quality"
                f2['text'] = 'Quality'
                f3.grid(row=2, column=0)

                def sel(quality):
                    exec(f'update setting set value="{quality}" where variable="quality";')
                    R1.grid_forget()
                    R2.grid_forget()
                    setting()

                var = ""
                R1 = tk.Radiobutton(f3, bg='grey', text="Highest", variable=var, value='high',
                                    command=lambda: sel('highest'))
                R1.grid(row=0, column=0)
                R2 = tk.Radiobutton(f3, bg='grey', text="Lowest", variable=var, value='low',
                                    command=lambda: sel('lowest'))
                R2.grid(row=1, column=0)
                if exec('select value from setting where variable="quality"')[0][0] == 'highest':
                    R1.select()
                else:
                    R2.select()
            elif item == 'Minimum Storage':
                def forget():
                    minstoragee.grid_forget()
                    updatebtn.grid_forget()
                    gb.grid_forget()
                    settingbtn['command'] = setting
                    setting()

                settingbtn['command'] = forget
                f2.grid_forget()
                f3.grid_forget()
                f4.grid_forget()
                f4.grid(row=1, column=0, sticky=tk.W)
                l1.delete(0, tk.END)
                cd['text'] = "Minimum Storage"
                f3.grid(row=2, column=0)

                def updateminstorage():
                    if str(minstoragee.get()).strip().isnumeric():
                        exec(
                            f'update setting set value="{str(minstoragee.get()).strip()}" where variable="Minimum Storage"')
                    minstoragee.grid_forget()
                    updatebtn.grid_forget()
                    gb.grid_forget()
                    setting()

                minstoragee = tk.Entry(f3)
                minstoragee.grid(row=0, column=0, pady=10, padx=5, sticky=tk.W)
                minstoragee.insert(tk.END, exec('select value from setting where variable="Minimum Storage";')[0][0])
                gb = tk.Label(f3, text='GB', bg='grey')
                gb.grid(row=0, column=1, sticky=tk.W)
                updatebtn = tk.Button(f3, text='Update Minimum Storage', bg='grey', command=updateminstorage)
                updatebtn.grid(row=1, column=0, columnspan=2, sticky=tk.W)
            elif item == 'Anime':
                def forget():
                    try:
                        animenamel.grid_forget()
                        seasonofupdatel.grid_forget()
                        seasonofupdatee.grid_forget()
                        seasonnoupdatel.grid_forget()
                        seasonnoupdatee.grid_forget()
                        update.grid_forget()
                        delete.grid_forget()
                    except:
                        pass
                    settingbtn['command'] = setting
                    setting()

                item = str(l1.get(tk.ANCHOR)).split(',')
                forget()
                settingbtn['command'] = forget
                addbtn2.grid_forget()
                addbtn.grid_forget()
                f2.grid_forget()
                f3.grid_forget()
                f4.grid_forget()
                f4.grid(row=1, column=0, sticky=tk.W)
                l1.delete(0, tk.END)
                cd['text'] = "Transfer Update"
                f3.grid(row=2, column=0)

                def delete():
                    forget()
                    exec(f'delete from transfer where animename="{item[0].split(":")[1].lower().strip()}"')
                    setting()

                def update():
                    seasonof = seasonofupdatee.get()
                    seasonno = seasonnoupdatee.get()
                    if seasonof.strip() != "" and seasonno.strip() != "":
                        if 'season' not in seasonno.lower(): seasonno = 'season ' + seasonno.strip()
                        exec(
                            f'update transfer set folder_name="{seasonof.strip()}" where animename="{item[0].split(":")[1].strip().lower()}";')
                        exec(
                            f'update transfer set season_name="{seasonno.strip()}" where animename="{item[0].split(":")[1].strip().lower()}";')
                    forget()
                    setting()

                animenamel = tk.Label(f3, text=f'Enter the details of {item[0].split(":")[1]} :', bg='grey')
                animenamel.grid(row=0, column=0, sticky=tk.W)
                seasonofupdatel = tk.Label(f3, text=f'Enter the Folder Name of {item[0].split(":")[1]} :', bg='grey')
                seasonofupdatel.grid(row=1, column=0, sticky=tk.W)
                seasonofupdatee = tk.Entry(f3)
                seasonofupdatee.insert(tk.END, item[1].split(":")[1])
                seasonofupdatee.grid(row=1, column=1, sticky=tk.W)
                seasonnoupdatel = tk.Label(f3, text=f'Enter the Season No. of {item[0].split(":")[1]} :', bg='grey')
                seasonnoupdatel.grid(row=2, column=0, sticky=tk.W)
                seasonnoupdatee = tk.Entry(f3)
                seasonnoupdatee.insert(tk.END, item[2].split(":")[1].title())
                seasonnoupdatee.grid(row=2, column=1, sticky=tk.W)
                update = tk.Button(f3, text='Update', bg='grey', command=update)
                update.grid(row=3, column=1, sticky=tk.W)
                delete = tk.Button(f3, text='Delete', bg='grey', command=delete)
                delete.grid(row=3, column=0, sticky=tk.E)
        elif f2['text'] == "Transfer":
            def forget():
                settingbtn['command'] = setting
                setting()

            settingbtn['command'] = forget
            item = str(l1.get(tk.ANCHOR))
            f2.grid_forget()
            f3.grid_forget()
            f4.grid_forget()
            f4.grid(row=1, column=0, sticky=tk.W)
            l1.delete(0, tk.END)
            f3.grid(row=2, column=0)
            seasonno.grid_forget()
            seasonof.grid_forget()
            seasonnol.grid_forget()
            seasonofl.grid_forget()
            seasonof.grid(row=1, column=1)
            seasonofl['text'] = f"Enter the name of anime whose part is {item} :"
            seasonof['text'] = ""
            seasonno['text'] = ""
            seasonofl.grid(row=1, column=0)
            seasonno.grid(row=2, column=1)
            seasonnol.grid(row=2, column=0)
            addbtn2.grid(row=3, column=1)
            addbtn2['text'] = 'Update'

            def update():
                global seasonno
                foldername = seasonof.get().strip()
                seasonno1 = seasonno.get().strip()
                seasonof.delete(0, tk.END)
                seasonno.delete(0, tk.END)
                if foldername != "" and seasonno1 != "":
                    if 'season' not in seasonno1: seasonno1 = f'season {seasonno1}'
                    a = item
                    res = anime_exists(a)
                    if not res[0]:
                        a += '-'
                        res = anime_exists(a)
                    type = 'anime'
                    if res[3].lower() == 'movie': type = 'movie'
                    exec(
                        f'insert into transfer values("{item.lower()}","{foldername.lower()}","{seasonno1.lower()}","{type.lower()}")')
                    forget()

            addbtn2['command'] = update
        elif 'Anime in list' in f2['text']:
            def webinterface():
                item = str(l1.get(tk.ANCHOR))
                if item.strip() == "": return
                item = item[item.find(' ') + 1:item.find(',')].lower()
                res = anime_exists(item)
                if res[0]:
                    webbrowser.open(url + '/category/' + item.replace(' ', '-'))
                    webbrowser.open(url2 + item.replace(' ', '-'))
                else:
                    webbrowser.open(url + '/category/' + item.replace(' ', '-') + '-')
                    webbrowser.open(url2 + item.replace(' ', '-'))

            x1 = threading.Thread(target=webinterface)
            x1.start()

    def double_click2(event):
        if cd['bg'] == 'green': subprocess.run(['explorer', os.path.realpath(retpath())])

    def setting():
        f2.grid(row=2, column=0)
        f3.grid_forget()
        f4.grid_forget()
        f4.grid(row=1, column=0, sticky=tk.W)
        l1.delete(0, tk.END)
        cd['text'] = "Setting"
        cd['bg'] = "grey"
        butn1['bg'] = 'grey'
        butn4['bg'] = 'grey'
        f2['text'] = 'Setting List'
        for i in exec('select * from setting;'):
            text = str(i[0]).title() + ' : ' + str(i[1]).title()
            l1.insert(tk.END, f'{text}')
        l1.insert(tk.END, f'Transfer')
        for i in exec('select * from transfer order by animename;'):
            if i[3] != 'movie':
                text = f'    Anime: {i[0].title()}, Folder name: {i[1].title()}, Season No.: {i[2]}'
                l1.insert(tk.END, f'{text}')

    def closebtn():
        s1.destroy()

    def transferb():
        t = threading.Thread(target=(transfer))
        t.start()

    def openwebsite(a):
        a = a

        def a2():
            res = anime_exists(a)
            if res[0]:
                webbrowser.open(url + '/category/' + a.replace(' ', '-'))
                webbrowser.open(url2 + a.replace(' ', '-'))
            else:
                webbrowser.open(url + '/category/' + a.replace(' ', '-') + '-')
                webbrowser.open(url2 + a.replace(' ', '-'))

        a3 = threading.Thread(target=a2)
        a3.start()

    def localstorage(a):
        a = a
        location = os.path.join(p1, 'Anime', a.title())
        if os.path.exists(location): subprocess.run(['explorer', os.path.realpath(location)])

    def backupstorage(a):
        a = a
        location = ''
        for root, folders, files in os.walk(exec('select value from setting where variable="HDD";')[0][0]):
            for i in files:
                if a.lower() in i.lower():
                    location = os.path.realpath(root)
                    break
        if os.path.exists(location) and location != '': subprocess.run(['explorer', os.path.realpath(location)])

    def openlatestepisode(a):
        a = a.lower()
        ac = anime_exists(a)
        if not (ac[0]):
            a = a = '-'
            ac = anime_exists(a)
        webbrowser.open((url + '/' + a.lower().replace(' ', '-') + f'-episode-{ac[1]}'))

    def copylink(a):

        a = a
        res = anime_exists(a)
        if res[0]:
            pyperclip.copy(url + '/category/' + a.replace(' ', '-'))
        else:
            pyperclip.copy(url + '/category/' + a.replace(' ', '-') + '-')

    def specificepisode(a):
        def epstartdown():
            def sta():
                global canimename,cepno,sizetotal
                fr=start.get()
                if not fr.isnumeric():return
                to=stop.get()
                if not to.isnumeric():return
                if cd['bg']=='green':return
                sizetotal=len(str(anime_exists(a)[1]))
                for i in range(int(fr),int(to)+1):
                    canimename=a
                    cepno=i
                    get_anime_download_link()
            threading.Thread(target=sta).start()

        a=a
        f2.grid_forget()
        f3.grid(row=2,column=0)
        for i in f3.winfo_children():i.destroy()
        tk.Label(f3,text=a).grid(row=0,column=0)
        tk.Label(f3,text=' From ',border=5,padx=5).grid(row=1,column=0)
        start=tk.Entry(f3,border=5,width=7)
        start.grid(row=1,column=1)
        tk.Label(f3,text=' to ',border=5,padx=5).grid(row=1,column=2)
        stop=tk.Entry(f3,border=5,width=7)
        stop.grid(row=1,column=3)
        tk.Button(f3,text='Download',border=5,command=epstartdown).grid(row=2,column=1)



    def right_click(event):
        widget = event.widget
        index = widget.nearest(event.y)
        item = widget.get(index)
        item=item.replace(';',',')
        l1.select_clear(0, tk.END)
        l1.select_set(index)
        if ',' in item:
            item = item[item.find(' ') + 1:item.find(',')].lower().strip()
        else:
            item = item[item.find(' ') + 1:].lower().strip()
        if item == "": return
        menu = tk.Menu(tearoff=0)
        menu.add_command(label='open websites', command=lambda a=item: openwebsite(a))
        menu.add_command(label='open latest episode', command=lambda a=item: openlatestepisode(a))
        menu.add_command(label='copy link', command=lambda a=item: copylink(a))
        menu.add_separator()
        menu.add_command(label='Specific Episode', command=lambda a=item.replace(' ','-'): specificepisode(a))
        menu.add_separator()
        menu.add_command(label='open local storage', command=lambda a=item: localstorage(a))
        menu.add_command(label='open backup storage', command=lambda a=item: backupstorage(a))
        menu.post(event.x_root, event.y_root)

    s1 = tk.Tk()
    s1.configure(bg='grey')
    s1.title("Anime Downloader")
    s1.geometry('715x501')#501
    s1.resizable(0, 0)
    # print(s1.winfo_screenwidth(),s1.winfo_screenheight(),s1.winfo_geometry())
    s1.protocol("WM_DELETE_WINDOW", closebtn)
    photo = tk.PhotoImage(file=os.path.join(p1, 'Anime_Downloader.png'))
    s1.iconphoto(False, photo)
    f1 = tk.LabelFrame(s1, bg='black', border=5, text="Main.", fg='white', padx=2)
    f1.grid(row=0, column=0)
    f2 = tk.LabelFrame(s1, border=5, bg='grey')
    f3 = tk.LabelFrame(s1, border=5, bg='grey')
    f4 = tk.LabelFrame(s1, border=5, bg='grey')
    f4.grid(row=1, column=0, sticky=tk.W)
    f5 = tk.LabelFrame(s1, border=2, bg='grey')
    f5.grid(row=3,column=0,sticky=tk.S)
    style= Style(f5)
    style.layout("LabeledProgressbar",[('LabeledProgressbar.trough',{'children': [('LabeledProgressbar.pbar',{'side': 'left', 'sticky': 'ns'}),
                             ("LabeledProgressbar.label",{"sticky": ""})],'sticky': 'nswe'})])
    style.configure("LabeledProgressbar",background='green')
    progress=Progressbar(f5 ,orient = tk.HORIZONTAL,length = 705,maximum=100, mode = 'determinate',style="LabeledProgressbar")
    s1.update_idletasks()
    cd = tk.Label(f4, text=f'Currently Downloading: ', anchor='w', pady=10, bg='grey', width=75, font=('Times', 11))
    cd.bind('<Double-Button-1>', double_click2)
    cd.pack()
    transferbtn = tk.Button(f4, text="Transfer", bg='grey', command=transferb)
    transferbtn.pack(side=tk.RIGHT)
    settingbtn = tk.Button(f4, text="Setting", bg='grey', command=setting)
    settingbtn.pack(side=tk.RIGHT)
    scroll = tk.Scrollbar(f2)
    l1 = tk.Listbox(f2, height=10, yscrollcommand=scroll.set, width=97, bg='grey', font=('Times', 11))
    l1.bind('<Double-1>', double_click)
    l1.bind('<Button-3>', right_click)
    scroll.config(command=l1.yview)
    s1animelist('anime')
    currentdown()
    tk.Label(f1, text='Anime Downloader', font=30, pady=10, bg='black', fg='white').grid(row=0, column=0, columnspan=5)
    butn1 = tk.Button(f1, text="Anime List", height=3, width=10, padx=33, border=5, bg='cyan', fg='black',
                      command=lambda: s1animelist('anime'))
    butn1.grid(row=1, column=0)
    butn2 = tk.Button(f1, text="Anime Delete", height=3, width=10, padx=33, border=5, bg='grey', fg='black',
                      command=s1animedelete)
    butn2.grid(row=1, column=1)
    butn4 = tk.Button(f1, text="History", height=3, width=10, padx=33, border=5, bg='grey', fg='black',
                      command=lambda: s1animelist('history'))
    butn4.grid(row=1, column=2)
    e1 = tk.Entry(f1, width=30, border=5, bg='white', fg='black')
    e1.bind('<Return>', s1animeadd1)
    e1.grid(row=1, column=3, pady=30)
    butn3 = tk.Button(f1, text='search', width=6, border=5, bg='grey', fg='black', command=s1animeadd)
    butn3.grid(row=1, column=4)
    addbtn = tk.Button(f3, text='ADD', height=2, width=10, bg='grey', pady=5, command=s1animeadd2)
    animename = tk.Label(f3, bg='grey', text="")
    seasonof = tk.Entry(f3, border=5)
    seasonno = tk.Entry(f3, border=5)
    seasonofl = tk.Label(f3, text="enter the name of anime whose part is:", bg='grey')
    seasonnol = tk.Label(f3, text='Enter the season no of the anime:', bg='grey')
    addbtn2 = tk.Button(f3, text='ADD', height=2, width=10, bg='grey', pady=5, command=s1animeadd3)

    x.start()
    s1.mainloop()


window()

try:
    closedriver()
    quit(0)
except:
    pass
