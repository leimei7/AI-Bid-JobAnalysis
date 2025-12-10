import requests
from bs4 import BeautifulSoup
from get_search import search
import time
import random
from get_zc_data import more_zc
from get_zl_data import more_zl
from get_rz_data import more_rz

cookies = {
    'CUID': '0ed8d9a0cbc22b4a1b2ef73d6fcaac56',
    'jsid': 'SEO-BING-ALL-SY-000001',
    'TYCID': '1d216e1061f411f0be2b27ede50318d6',
    'tyc-user-info': '%7B%22state%22%3A%220%22%2C%22vipManager%22%3A%220%22%2C%22mobile%22%3A%2218382076384%22%2C%22userId%22%3A%22337546178%22%7D',
    'tyc-user-info-save-time': '1752970946964',
    'auth_token': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxODM4MjA3NjM4NCIsImlhdCI6MTc1Mjk3MDk0NiwiZXhwIjoxNzU1NTYyOTQ2fQ.ZPbrpgq4G1cHtbQRBgkfBUSv1hPel-nGTGEIvTxMP8nsu0aju2iG7XKYrfsjdPScszPztsdo9sfnF7shHQmQog',
    'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22337546178%22%2C%22first_id%22%3A%2219811404c741792-097f1f40f738898-4c657b58-1474560-19811404c7522ac%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fcn.bing.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk4MTE0MDRjNzQxNzkyLTA5N2YxZjQwZjczODg5OC00YzY1N2I1OC0xNDc0NTYwLTE5ODExNDA0Yzc1MjJhYyIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjMzNzU0NjE3OCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22337546178%22%7D%2C%22%24device_id%22%3A%2219811415e0a641-03925db0eadc1c6-4c657b58-1474560-19811415e0b2c5a%22%7D',
    'searchSessionId': '1752989688.18564141',
    'HWWAFSESID': '80e3beb148ddef96c8',
    'HWWAFSESTIME': '1753058417332',
    'csrfToken': 'hMtEhA1IQNBbDYNUdfJDqv7r',
    'bannerFlag': 'true',
    'Hm_lvt_e92c8d65d92d534b0fc290df538b4758': '1752974170,1752979572,1752989686,1753058420',
    'HMACCOUNT': '82CB374ADB460A68',
    'Hm_lpvt_e92c8d65d92d534b0fc290df538b4758': '1753059417',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://www.tianyancha.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'CUID=0ed8d9a0cbc22b4a1b2ef73d6fcaac56; jsid=SEO-BING-ALL-SY-000001; TYCID=1d216e1061f411f0be2b27ede50318d6; tyc-user-info=%7B%22state%22%3A%220%22%2C%22vipManager%22%3A%220%22%2C%22mobile%22%3A%2218382076384%22%2C%22userId%22%3A%22337546178%22%7D; tyc-user-info-save-time=1752970946964; auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxODM4MjA3NjM4NCIsImlhdCI6MTc1Mjk3MDk0NiwiZXhwIjoxNzU1NTYyOTQ2fQ.ZPbrpgq4G1cHtbQRBgkfBUSv1hPel-nGTGEIvTxMP8nsu0aju2iG7XKYrfsjdPScszPztsdo9sfnF7shHQmQog; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22337546178%22%2C%22first_id%22%3A%2219811404c741792-097f1f40f738898-4c657b58-1474560-19811404c7522ac%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fcn.bing.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk4MTE0MDRjNzQxNzkyLTA5N2YxZjQwZjczODg5OC00YzY1N2I1OC0xNDc0NTYwLTE5ODExNDA0Yzc1MjJhYyIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjMzNzU0NjE3OCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22337546178%22%7D%2C%22%24device_id%22%3A%2219811415e0a641-03925db0eadc1c6-4c657b58-1474560-19811415e0b2c5a%22%7D; searchSessionId=1752989688.18564141; HWWAFSESID=80e3beb148ddef96c8; HWWAFSESTIME=1753058417332; csrfToken=hMtEhA1IQNBbDYNUdfJDqv7r; bannerFlag=true; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1752974170,1752979572,1752989686,1753058420; HMACCOUNT=82CB374ADB460A68; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1753059417',
}

def clean_html_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    company_info = {}

    # 提取统一社会信用代码
    credit_code_elem = soup.select_one('.index_detail-credit-code__fH1Ny span')
    company_info['credit_code'] = credit_code_elem.text.strip() if credit_code_elem else None

    # 提取法人
    legal_person_elem = soup.select_one('a.index_link-click__NmHxP.index_copy-val__Qdkxu')
    company_info['legal_person'] = legal_person_elem.text.strip() if legal_person_elem else None

    # 提取注册资本
    registered_capital_elem = soup.select_one('.index_detail-text__Ac9Py.index_copy-val__Qdkxu.index_inline-block__dAZxk')
    company_info['registered_capital'] = registered_capital_elem.text.strip() if registered_capital_elem else None

    # 提取成立日期
    date_elems = soup.select('.index_detail-text__Ac9Py.index_copy-val__Qdkxu.index_inline-block__dAZxk')
    company_info['establishment_date'] = date_elems[1].text.strip() if len(date_elems) > 1 else None

    # 提取电话
    phone_elem = soup.select_one('.index_detail-tel__fgpsE')
    company_info['phone'] = phone_elem.text.strip() if phone_elem else None

    # 提取邮箱
    email_elem = soup.select_one('a.index_detail-email__B_1Tq')
    company_info['email'] = email_elem.text.strip() if email_elem else None

    # 提取地址
    address_elem = soup.select_one('.index_detail-address-moretext__9R_Z1 .index_inline-flex__QLDiW')
    company_info['address'] = address_elem.text.strip() if address_elem else None

    # 提取简介
    intro_elem = soup.select_one('.introduceRich_collapse-left__5Vvd5 span:last-child')
    company_info['introduction'] = intro_elem.text.strip() if intro_elem else None

    # 提取公司状态
    status_elem = soup.select_one('td.num-opening')
    company_info['status'] = status_elem.text.strip() if status_elem else None

    return company_info

def company(url):
    print("正在接入企业查询接口...")
    delay = random.uniform(1, 2)
    time.sleep(delay)
    response = requests.get(url, cookies=cookies, headers=headers)
    return response.text

def get_company_all(ky):
    if ky == 'kilaki':
        return []
    else:
        link = search(ky, cookies, headers)
        if link:
            c_url = link.get('href')
            c_id = c_url.split("/company/")[-1]
            company_html = company(c_url)
            company_info = clean_html_text(company_html)
            zc_data = more_zc(c_id, headers)
            company_info['商标'] = zc_data
            zl_data = more_zl(c_id, headers)
            company_info['专利'] = zl_data
            rz_data = more_rz(c_id, headers)
            company_info['软著'] = rz_data
            return company_info
        else:
            return []

if __name__ == '__main__':
    print(get_company_all('腾讯'))

"""
统一社会信用代码
<span class="index_detail-credit-code__fH1Ny">
<span class="">91230110MA18XQKK86</span>
</span>
"""

"""
法人
<a class="index_link-click__NmHxP index_copy-val__Qdkxu" style="margin-right:4px" target="_blank" href="/human/1980936208-c2358436763" title="李双龙" rel="noreferrer">李双龙</a>
"""

"""
注册资本
<span class="index_detail-text__Ac9Py index_copy-val__Qdkxu index_inline-block__dAZxk">100万人民币
</span>
"""

"""
成立日期
<span class="index_detail-text__Ac9Py index_copy-val__Qdkxu index_inline-block__dAZxk">2016-04-28</span>
</span>
"""

"""
电话
<span class="index_detail-tel__fgpsE">13313692616</span>
"""

"""
邮箱
<a class="index_detail-email__B_1Tq" rel="nofollow noreferrer" href="mailto:491173756@qq.com">491173756@qq.com</a>
"""

"""
地址
<span class="index_inline-flex__QLDiW">哈尔滨经开区南岗集中区红旗大街160号海外学人创业园D栋1单元6层1号</span>
"""

"""
<div class="introduceRich_collapse-left__5Vvd5">
<span class="introduceRich_collapse-title__XzjQz">简介：</span>
<span>公司简介</span>
</div>
"""