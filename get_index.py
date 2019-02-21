from config import COOKIES
import config
from urllib.parse import urlencode
from collections import defaultdict
import datetime
import requests
import json
import os

# wby 2019-1

headers = {
    'Host': 'index.baidu.com',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}


class BaiduIndex:
    """
        百度搜索指数
    """

    def __init__(self, para):
        # 当前使用的 COOKIE 索引
        self.cookie_index = 0

        self.nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self.data = []
        keyword = para['关键词']
        self.keywords = keyword if isinstance(
            keyword, list) else keyword.split('，')
        area = para['地区']
        self.areas = area if isinstance(area, list) else area.split('，')
        self._all_kind = ['all', 'pc', 'wise']
        self.setKind(para['平台'])
        self.output_dir = para['输出目录']

        for i in range(len(self.keywords)):
            keyword = self.keywords[i]
            print(f'关键词 {i+1}: ', keyword)
            try:
                self.result = None
                self.result = {area: defaultdict(list) for area in self.areas}
                self.setDay(para['开始日期'], para['结束日期'], keyword)
                for area in self.areas:
                    self.get_result(self.start_date, self.end_date, area, keyword)
                print(keyword + '查询完成\n')
                self.print_data(keyword)
            except Exception as e:
                print('错误: ', e)
                print(f'对关键词 [{keyword}] 的查询出了一点小问题，可能是因为访问太过频繁或者其他原因')
                print(f'建议您先到百度指数查询关键词 【{keyword}】，获取当前错误状态，再继续进行抓取')
                choice = ''
                while choice != 'r' and choice != 's' and choice != 'e' and choice != 'c':
                    choice = input(f'是否继续进行抓取？ (r)etry, (s)kip this keyword, (e)xit, (c)hange to use another cookie: ')
                if choice == 'r':
                    i = i - 1
                    print('Changed i: ', i)
                    continue
                elif choice == 's':
                    continue
                elif choice == 'c':
                    i = i - 1
                    self.cookie_index = (self.cookie_index + 1) % len(COOKIES)
                elif choice == 'e':
                    exit()

    def setKind(self, kind):
        if kind == 1:
            self.kind = 'pc'
        elif kind == 2:
            self.kind = 'wise'
        else:
            self.kind = 'all'

    def setDay(self, start_date, end_date, keyword):
        """
        设置查询起止时间
        """
        if start_date == '':
            encrypt_datas = self.get_encrypt_datas_all(keyword)
            self.start_date = encrypt_datas['startDate']
        else:
            self.start_date = start_date
        if end_date == '':
            self.end_date = str(datetime.datetime.now() -
                                datetime.timedelta(days=1))[:10]
        else:
            self.end_date = end_date
        
        print('setDay: ', '设置起止时间完毕')
        print('start_date: ', start_date)
        print('end_date: ', end_date)

    def get_result(self, start_date, end_date, area, keyword):
        """
        获取结果
        """
        self.time_range_list = self.get_time_range_list(start_date, end_date)
        for start_date, end_date in self.time_range_list:
            encrypt_data, uniqid = self.get_encrypt_datas(
                start_date, end_date, area, keyword)
            key = self.get_key(uniqid)
            c = self.decrypt_func(key, encrypt_data[self.kind]['data'])
            # print(c)
            self.data = self.data + c
        self.result[area][self.kind].append(self.data)
        self.data = []

    def get_encrypt_datas_all(self, keyword):

        request_args = {
            'word': keyword,
            'area': 0,
        }
        url = 'http://index.baidu.com/api/SearchApi/index?' + \
            urlencode(request_args)
        datas = json.loads(self.http_get(url, COOKIES[self.cookie_index]))
        encrypt_datas = datas['data']['userIndexes'][0]['all']
        return encrypt_datas

    def get_encrypt_datas(self, start_date, end_date, area, keyword):
        """
        :start_date; str, 2018-10-01
        :end_date; str, 2018-10-01
        """
        request_args = {
            'area': int(config.area[area]),
            'word': keyword,
            'startDate': str(start_date)[:10],
            'endDate': str(end_date)[:10],
        }
        url = 'http://index.baidu.com/api/SearchApi/index?' + \
            urlencode(request_args)
        html = self.http_get(url, COOKIES[self.cookie_index])
        datas = json.loads(html)
        uniqid = datas['data']['uniqid']
        encrypt_datas = []
        for single_data in datas['data']['userIndexes']:
            encrypt_datas.append(single_data)
        return (encrypt_datas[0], uniqid)

    def get_key(self, uniqid):
        """
        """
        url = 'http://index.baidu.com/Interface/api/ptbk?uniqid=%s' % uniqid
        html = self.http_get(url, COOKIES[self.cookie_index])
        datas = json.loads(html)
        key = datas['data']
        return key

    def print_data(self, keyword):
        """
        """
        file = open(self.output_dir +  '/' + str(self.nowTime) + ' 搜索指数.csv', 'a')
        file.write(keyword)
        file.write('\n')
        file.write('时间,')

        time_len = len(self.result[self.areas[0]]['all'][0])
        start_date = self.start_date
        cur_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        for i in range(time_len):
            file.write(cur_date.strftime('%Y-%m-%d'))
            cur_date += datetime.timedelta(days=1)
            file.write(',')
        file.write('\n')

        for area in self.areas:
            file.write(area)
            for i in range(time_len):
                try:
                    file.write(','+self.result[area]['all'][0][i])
                except Exception:
                    print(f'想要索引到 {time_len} 处的数据为止')
                    print(f'但总长度只有', len(self.result[area]['all'][0]))
                    break
            file.write('\n')
        file.write('\n')
        file.close()

    @staticmethod
    def http_get(url, cookies):
        headers['Cookie'] = cookies
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None

    @staticmethod
    def get_time_range_list(startdate, enddate):
        """
        从 startdate 到 enddate，生成 list，每隔 180 生成一个时间点
        之所以这样做，是因为百度最多只支持 180 天内的查询
        """
        date_range_list = []
        startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
        while 1:
            tempdate = startdate + datetime.timedelta(days=180)
            if tempdate > enddate:
                date_range_list.append((startdate, enddate))
                # print(date_range_list)
                return date_range_list
            date_range_list.append((startdate, tempdate))
            startdate = tempdate + datetime.timedelta(days=1)

    @staticmethod
    def decrypt_func(key, data):
        """
        decrypt data
        """
        a = key
        i = data
        n = {}
        s = []
        for o in range(len(a)//2):
            n[a[o]] = a[len(a)//2 + o]
        for r in range(len(data)):
            s.append(n[i[r]])
        return ''.join(s).split(',')

if __name__ == '__main__':
    # keywords_file = './data/test.txt'
    keywords_file = './data/companies.txt'
    output_dir = './results'
    
    companies = ''

    with open(keywords_file) as companies_txt:
        companies = companies_txt.readlines()[0]
    # print(companies)
    # exit()

    # 由于百度指数返回的是小写，这里将查询关键词转换为小写，避免因查询关键词与返回关键词不同而出现错误
    companies = companies.lower()
    print('===== 要查询的关键词如下 ===== \n\t', companies.replace('，', '\n\t'))
    print('============================= ')
    # exit()

    print('======== 传入参数如下 ========')
    para = {
        # 关键词不可省略，多个关键词使用 
        #   1. list，或者： 
        #   2. 全角逗号分隔的字符串
        '关键词': companies,            
        # 地区不可省略，多个地区使用 
        #   1. list，或者： 
        #   2. 全角逗号分隔的字符串
        '地区': '广州，北京',    
        # 可省略，默认为pc+移动，1：pc; 2: 移动； 3：pc+移动          
        '平台': '',              
        # 可省略，默认为百度定义的最早的时间，因关键词而异，如2018-1-1
        '开始日期': '2009-1-1',
        # 可省略，默认为今天
        '结束日期': '2017-12-31',
        '输出目录': 'results'
    }
    import pprint
    para['关键词'] = '(此处不打印)'
    pprint.pprint(para)
    # exit()
    print('============================= ')
    para['关键词'] = companies

    print('===== 开始查询 =====')
    baidu_index = BaiduIndex(para)
    print('===== 结束查询 =====')
