import random
import re
import time
import requests
import os
from datetime import datetime

from ai_data import process_procurement_text
from buy_datas import extract_content

NOTICE_TYPE = {
    "0": "所有类型",
    "1": "公开招标",
    "2": "询价公告",
    "3": "竞争性谈判",
    "4": "单一来源",
    "5": "资格预审",
    "6": "邀请公告",
    "7": "中标公告",
    "8": "更正公告",
    "9": "其他公告",
    "10": "竞争性磋商",
    "11": "成交公告",
    "12": "终止公告",
}

current_time = datetime.now().strftime("%Y:%m:%d")


def get_type():
    user_input = input(
"""0: "所有类型",
1: "公开招标",
2: "询价公告",
3: "竞争性谈判",
4: "单一来源",
5: "资格预审",
6: "邀请公告",
7: "中标公告",
8: "更正公告",
9: "其他公告",
10: "竞争性磋商",
11: "成交公告",
12: "终止公告",
请选择类型（输入对应数字）：""")
    if user_input:
        if user_input < '0' or user_input > '12':
            return '7'
        return str(user_input)
    else:
        return '0'


def format_date():
    year = int(input("年："))
    month = int(input("月："))
    day = int(input("日："))
    return f"{year:04d}:{month:02d}:{day:02d}"


def get_param(page, kw, tp='7', st=current_time, et=current_time):
    param = {
        'searchtype': '1',
        'page_index': page,
        'bidSort': '0',
        'buyerName': '',
        'projectId': '',
        'pinMu': '0',
        'bidType': tp,  # 7是中标
        'dbselect': 'bidx',
        'kw': kw,
        'timeType': '6', #自动时间挡位
        'displayZone': '四川',# 地区
        'zoneId': '51',# 地区编号
        'pppStatus': '0',
        'agentName': '',
        'start_time': st,
        'end_time': et,
    }
    return param


def get_headers(referer=None):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'
    ]
    ua = random.choice(user_agents)
    headers = {
        "User-Agent": ua,
        "Host": "search.ccgp.gov.cn",
        "Referer": referer if referer else "http://search.ccgp.gov.cn/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    return headers


def tool(url, param=None, refer=None):
    headers = get_headers(refer)
    time.sleep(random.randint(2, 6))  # 随机延迟，避免反爬
    response = requests.get(url, headers=headers, params=param, allow_redirects=True)
    if response.status_code != 200:
        print(f"请求异常，状态码: {response.status_code}，URL: {response.url}")
    return response


def get_detail_url(htm):
    pattern = r'var ohtmlurls="([^"]+)"'
    match = re.search(pattern, htm)
    if match:
        ohtmlurls_value = match.group(1)
        url_array = [url for url in ohtmlurls_value.split(',') if url]  # 过滤空值
        url_array = [url.replace('http', 'https') for url in url_array]  # 统一协议
        print(f"共解析出 {len(url_array)} 个URL")
        for i, url in enumerate(url_array, 1):
            print(i, url)
        return url_array
    else:
        print("未找到ohtmlurls的值")
        return None


def get_datas(urls: list):
    results = []
    if urls:
        for url in urls:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/101.0.4951.64 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36'
                ])
            }
            time.sleep(random.randint(2, 6))
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                results.append({
                    'url': url,
                    'content': extract_content(response.text)
                })
                print(f"已爬取: {url}")
            except Exception as e:
                print(f"爬取{url}失败: {e}")
    return results


def batch_process(datas_array, keyword):
    """按10条一组拆分数据，分批处理"""
    batch_size = 10  # 每批处理10条
    total = len(datas_array)
    success_count = 0  # 记录成功处理的批次

    # 按批次拆分数据
    for i in range(0, total, batch_size):
        batch = datas_array[i:i + batch_size]  # 截取当前批次（最后一批可能不足10条）

        # 提取内容文本用于处理
        batch_text = "\n".join([item['content'] for item in batch])

        # 提取URL列表
        batch_urls = [item['url'] for item in batch]

        batch_num = i // batch_size + 1  # 批次号
        print(f"\n===== 开始处理第{batch_num}批数据（共{len(batch)}条） =====")

        # 调用处理函数，传入URL列表
        success = process_procurement_text(batch_text, keyword, batch_urls)
        if success:
            success_count += 1
            print(f"第{batch_num}批处理成功{success_count}")
        else:
            print(f"第{batch_num}批处理失败{success_count}")

        # 批次间增加延迟，避免API请求过于频繁
        if i + batch_size < total:
            delay = random.randint(1, 3)
            print(f"批次间隔延迟 {delay} 秒...")
            time.sleep(delay)

    # 输出总体处理结果
    print(f"\n===== 全部处理完成 =====")
    print(f"总数据量: {total} 条，分{(total + batch_size - 1) // batch_size}批处理")
    print(f"成功批次: {success_count}，失败批次: {(total + batch_size - 1) // batch_size - success_count}")
    return success_count > 0  # 只要有一个批次成功就返回True


if __name__ == '__main__':
    keyword = input('请输入关键词：').strip()
    pg = input('请输入页数：').strip()
    ty = get_type()
    print("请输入开始时间：")
    st = format_date()
    print("请输入截至时间：")
    et = format_date()
    # 获取列表页并解析详情URL
    res = tool('http://search.ccgp.gov.cn/bxsearch', get_param(pg, keyword, ty, st, et))
    url_array = get_detail_url(res.text)

    # 爬取详情页数据，同时保存URL
    datas_array = get_datas(url_array) if url_array else []

    # 保存原始数据到文件
    if datas_array:
        # 创建txt文件夹（如果不存在）
        if not os.path.exists('txt'):
            os.makedirs('txt')
        if keyword is None or keyword == '':
            filename = f"txt/{datetime.now().strftime('%Y%m%d%H%M%S')}第{pg}页共{len(datas_array)}条.txt"
        else:
            filename = f"txt/{keyword}第{pg}页共{len(datas_array)}条.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 保存URL和内容的对应关系
                for item in datas_array:
                    f.write(f"URL: {item['url']}\n")
                    f.write(f"{item['content']}\n\n")
            print(f"原始数据已保存至 {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")
    else:
        print("未获取到有效数据")
        exit()

    # 按10条一批处理数据并入库
    overall_success = batch_process(datas_array, keyword)
    print("全部数据处理完成" if overall_success else "数据处理失败")