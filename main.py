# 作者：aoyijiaozhu
# 创建时间：2023/8/10
# 更新时间：2023/8/13
#爬取拷贝漫画网站图片
#转pdf

import random
import time
from selenium import webdriver
import os
import glob
from fake_useragent import UserAgent
import requests
import img2pdf
from concurrent.futures import ThreadPoolExecutor

driver_path= 'chromedriver.exe'     #驱动目录
ua = UserAgent(path='fake_useragent.json')      #模拟ua,从本地导入ua头

requests_proxies=[
    {'HTTP':'117.94.120.236:9000'},
    {'HTTP': '114.231.8.116:8888'},
    {'HTTP': '36.134.91.82:8888'},
    {'HTTP': '183.247.221.119:30001'},
    {'HTTP': '61.216.185.88:60808'},
    {'HTTP': '183.236.123.242:8060'},
    {'HTTP': '60.170.204.30:8060'},
    {'HTTP': '144.255.49.151:9999'},
    {'HTTP': '123.169.38.158:9999'},
    {'HTTP': '58.20.184.187:9091'},
    {'HTTP': '123.169.37.104:9999'},
    {'HTTP': '221.236.170.13:9000'},
    {'HTTP': '117.94.112.152:9000'},
    {'HTTP': '117.94.112.152:9000'},
    {'HTTP': '47.97.191.179:8018'},
    {'HTTP': '183.236.232.160:8080'},
    {'HTTP': '222.74.73.202:42055'},
    {'HTTP': '114.231.45.40:8888'},
    {'HTTP': '61.216.156.222:60808'},
    {'HTTP': '113.121.43.220:9999'},
    {'HTTP': '112.244.230.142:9000'},
    {'HTTP': '113.121.38.168:9999'},
    {'HTTP': '182.34.18.25:9999'},
    {'HTTP': '182.34.37.157:9999'},
    {'HTTP': '182.34.103.237:9999'},
    {'HTTP': '58.20.184.187:9091'},
    {'HTTP': '114.231.46.205:8888'},
    {'HTTP': '61.216.185.88:60808'},
    {'HTTP': '113.121.23.148:9999'},
    {'HTTP': '182.34.100.86:9999'},
    {'HTTP': '182.34.100.227:9999'},
    {'HTTP': '222.74.73.202:42055'}
] #requests请求用的,不够再加,自己替换
proxies = {
    'HTTP1':'183.236.123.242:8060',
    'HTTP2':'60.167.102.145:1133',
    'HTTP3':'114.231.41.239:8888',
    'HTTP4':'39.99.54.91:80',
    'HTTP5':'183.247.221.119:30001',
    'HTTP6':'114.231.42.156:8888',
    'HTTP7': '182.139.111.228:9000',
    'HTTP8': '183.236.232.160:8080',
    'HTTP9': '58.20.184.187:9091',
    'HTTP10': '27.42.168.46:55481',
    'HTTP11': '180.121.131.224:8888',
    'HTTP12': '114.231.8.225:8888',
    'HTTP13': '114.232.110.131:8888',
    'HTTP14': '182.140.244.163:8118',
    'HTTP15': '223.241.78.53:1133',
    'HTTP16': '117.114.149.66:55443',
    'HTTP17': '183.236.232.160:8080',
    'HTTP18': '60.167.20.123:1133',
    'HTTP19': '61.216.156.222:60808',
    'HTTP20': '27.192.174.225:9000',
    'HTTP21': '36.134.91.82:8888',
    'HTTP22': '223.241.119.32:1133',
    'HTTP23': '223.241.78.198:1133',
    'HTTP24': '114.231.45.153:8888',
    'HTTP25': '183.247.221.119:30001',
    'HTTP26': '112.14.47.6:52024',
    'HTTP27': '60.167.103.114:1133',
    'HTTP28': '27.42.168.46:55481',
    'HTTP29': '182.139.110.84:9000',
    'HTTP30': '117.68.195.56:9999',
    'HTTP31': '115.29.170.58:8118',
    'HTTP32': '183.236.232.160:8080',
    'HTTP33': '60.167.102.53:1133',
    'HTTP34': '58.20.184.187:9091',
    'HTTP35': '183.64.239.19:8060',
    'HTTP36': '60.167.22.215:1133'
}   # 加入selenium浏览器代理池（其实没必要加，懒得删了）
proxy_name,proxy=random.choice(list(proxies.items()))


xpath_pic_element='/html/body/div[2]/div/ul/li//img'     #图片元素xpath位置
#xpath_pic='/html/body/div[2]/div/ul/li/img/@src'       #图片xpath位置
xpath_chapter='/html/body/h4'       #章节名称xpath位置

def random_proxies(requests_proxies):   #返回一个随机的proxy
    requests_proxy=random.choice(requests_proxies)
    return requests_proxy

def create_browser():      #创建浏览器，返回一个browser对象
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.139 Safari/537.36"')
    options.add_argument("--proxy-server=http://" + proxy)  # 待添加
    browser = webdriver.Chrome(driver_path, )
    return browser

def get_num_name_url_lst(base_url,browser):     # 返回一个列表，以序号+章节名+章节url的格式，用“*”符号分隔
    browser.get(base_url)  # 打开目录网站
    time.sleep(1)
    xpath_chapter_element = '/html/body/main/div[2]/div[3]/div[1]/div[2]/div/div[1]/ul[1]/a'  # 章节元素xpath
    chapter_elemennts = browser.find_elements('xpath', xpath_chapter_element)
    num_name_url_lst = []
    for count, e in enumerate(chapter_elemennts, 1):
        count = '{:05d}'.format(count)
        chapter_url = e.get_attribute('href')
        chapter_name = e.get_attribute('title')
        print('-----------' + f'正在获取: {chapter_name} 信息（第{count}章）' + '-----------')
        num_name_url = str(count) + str('*') + chapter_name + str('*') + chapter_url
        num_name_url_lst.append(num_name_url)
    return num_name_url_lst

def scroll_top_to_bottom(browser):
    step = 200  # 滑动步长
    t = 0.02  # 间隔时间
    page_height = 0  # 从顶部开始滚动

    while page_height < browser.execute_script('return document.body.scrollHeight'):
        browser.execute_script(f"window.scrollTo(0, {page_height});")
        page_height += step
        time.sleep(t)

def get_pic(num_name_url):      #传入之前格式的列表，拆分，创建文件夹（title/num+name命名），文件夹里下载图片（按顺序数字命名）
###
    def download_pic(count_picurl):     #下载单张图片
        count,pic_url=count_picurl.split('*')
        with open('./' + bookname + '/' + num + name + '/' + str(count) + '.jpg', 'wb') as img_file:
            headers = {'user-agent': ua.random}  # 网页请求头
            requests_proxy = random_proxies(requests_proxies)
            response = requests.get(pic_url, headers=headers, proxies=requests_proxy)
            print(f'-----------正在下载: {name} 第{count}张-----------')
            # print(headers)
            # print(requests_proxy)
            img_file.write(response.content)
###

    num,name,url=num_name_url.split('*')
    num=num+'_'     #防止某些情况下数字序号和章节名称里的数字连续，导致拼接pdf时无法正确排序

    if not os.path.exists('./'+bookname+'/'+num+name):
        os.mkdir('./'+bookname+'/'+num+name)
        print(f'已在当前目录创建文件夹：{bookname}/{num+name}')
    else:
        print('该文件夹已存在')

    browser = create_browser()
    browser.get(url)
    scroll_top_to_bottom(browser)   #滚动模拟加载
    pic_elemennts = browser.find_elements('xpath', xpath_pic_element)
    pic_urls=[]
    for e in pic_elemennts:
        pic_url=e.get_attribute('data-src')
        pic_urls.append(pic_url)
    browser.delete_all_cookies()
    browser.quit()
#多线程下载图片
    count_picurl_lst=[]
    for count,pic_url in enumerate(pic_urls,1):     #获取每张图片的url和序号，拼接count+url,用'*'连接,生成一个迭代用的列表
        count='{:05d}'.format(count)
        count_picurl=str(count)+'*'+pic_url
        count_picurl_lst.append(count_picurl)
    with ThreadPoolExecutor(max_workers=8) as download_pool:  # 创建线程池,最大任务max_workers
        download_pool.map(download_pic,count_picurl_lst)
    #browser.delete_all_cookies()
    #browser.quit()

###下面是不用多线程下载的，待修改
'''
    for count,e in enumerate(pic_elemennts,1):     #获取每张图片的url,然后下载
        pic_url=e.get_attribute('src')
        count='{:05d}'.format(count)
        #print(pic_url)
        with open('./'+bookname+'/'+num+name+'/'+str(count)+'.jpg', 'wb') as img_file:
            headers = {'user-agent': ua.random}     #网页请求头
            requests_proxy=random_proxies(requests_proxies)
            response=requests.get(pic_url,headers=headers,proxies=requests_proxy)
            print(f'-----------正在下载: {name} 第{count}张-----------')
            #print(headers)
            #print(requests_proxy)
            img_file.write(response.content)
    browser.delete_all_cookies()
    browser.quit()
'''


def get_bookname(browser):      #获取书名
    xpath_bookname = '/html/body/main/div[1]/div/div[2]/ul/li[1]/h6'  # 书名元素xpath
    bookname = browser.find_element('xpath', xpath_bookname).get_attribute('title')  # 获取书名
    browser.quit()
    return bookname

def turn_to_pdf():  #转换为pdf
    start_time=time.time()
    path = bookname+'\*\*.jpg'

    file_list = glob.glob(path, recursive=True)
    with open(bookname+'.pdf', 'wb') as pdf:
        pdf.write(img2pdf.convert(file_list))
    print('----------转换为pdf完成----------')
    end_time=time.time()
    print('转换耗时: '+str(end_time-start_time)+' s')

if __name__ == '__main__':
    base_url=input('请输入漫画首页网址（格式如： https://mangacopy.com/comic/haizeiwang  ）：')

    start_time = time.time()

    browser = create_browser()
    num_name_url_lst=get_num_name_url_lst(base_url,browser)
    bookname=get_bookname(browser)

    if not os.path.exists('./'+bookname):
        os.mkdir('./'+bookname)
        print(f'已在当前目录创建文件夹：{bookname}')
    else:
        print('该文件夹已存在')

    with ThreadPoolExecutor(max_workers=4) as pool:  # 创建线程池,最大任务max_workers
        pool.map(get_pic,num_name_url_lst)
    print('----------下载完成----------')

    end_time=time.time()
    print('下载耗时: '+str(end_time-start_time)+' s')

    is_pdf=input('是否转换为pdf？Y/N：')
    if is_pdf =='Y' or is_pdf =='y':
        try:
            turn_to_pdf()
        except:
            print('转换失败')
    else:
        print('----------程序结束----------')



