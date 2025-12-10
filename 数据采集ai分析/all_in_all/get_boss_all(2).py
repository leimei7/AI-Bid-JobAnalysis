import asyncio
import json
import random
import os


import csv
from pyppeteer import launch
from pyppeteer.browser import Browser
import requests
from read_database import fetch_uncprocessed_data, mark_data_as_processed
from cloud_database_con import insert_data


browser: Browser | None = None
TOKEN_MAX_USAGE = 5  # 每个token严格有效使用5次
current_token = None  # 全局保留当前可用token
remaining_uses = 0  # 记录当前token剩余可用次数


async def init_browser(user_data_dir: str):
    global browser
    if not browser:
        browser = await launch(
            headless=False,
            executablePath=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            userDataDir=user_data_dir,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
            ignoreDefaultArgs=["--enable-automation"],
            slowMo=10,
        )
    return browser


async def close_browser():
    global browser
    if browser:
        await browser.close()
        browser = None


async def fetch_zp_stoken(user_data_dir: str) -> str | None:
    """获取新的zp_stoken"""
    global current_token, remaining_uses
    browser = await init_browser(user_data_dir)
    page = await browser.newPage()

    try:
        await page.setViewport({"width": 1536, "height": 912, "deviceScaleFactor": 1.0})
        await page.evaluateOnNewDocument("""
            () => {
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
                delete window.__pyppeteer;
            }
        """)
        await page.goto("https://www.zhipin.com/", waitUntil="networkidle2")
        await asyncio.sleep(random.uniform(5, 7))
        cookies = await page.cookies()
        zp_stoken = next((cookie for cookie in cookies if cookie['name'] == '__zp_stoken__'), None)
        token_value = zp_stoken['value'] if zp_stoken else None
        if token_value:
            print(f"成功获取新token: {token_value[:20]}...")
            current_token = token_value
            remaining_uses = TOKEN_MAX_USAGE  # 新token重置为5次可用
        return token_value
    finally:
        await page.close()


def get_request(query, page, zp_token):
    """使用指定token请求数据"""
    cookies = {
        '__zp_stoken__': zp_token,
        'lastCity': '101270100',
        'wt2': 'D6HghwDCepwtedsR71CAuyyJPsrxHqw3hqVSqmIDmkosW4nklhQd_gnUsX8UEHkpWQvMpoT0FjuEIzI78orxKnQ~~',
        'wbg': '0',
        'zp_at': 'ICPOhzfjwRylSD1AXpZr0QRv9UHkYuEPKauHOGs7co8~',
        '__zp_seo_uuid__': '50edf72e-90f5-44c9-ab65-08697565b2ab',
        '__g': 'sem_bingpc',
        '__l': 'r=https%3A%2F%2Fcn.bing.com%2F&l=%2Fwww.zhipin.com%2Fsem%2F10.html%3F_ts%3D1750917231726%26sid%3Dsem_bingpc%26qudao%3Dbing_pc_H120003UY5%26plan%3DBOSS-%25E5%25BF%2585%25E5%25BA%2594-%25E5%2593%2581%25E7%2589%258C%26unit%3D%25E7%25B2%25BE%25E5%2587%2586%26keyword%3Dboss%25E7%259B%25B4%25E8%2581%2598%26msclkid%3D24999f57ac6619c5979df70b4c0b6d1a&s=1&g=%2Fwww.zhipin.com%2Fsem%2F10.html%3F_ts%3D1750917231726%26sid%3Dsem_bingpc%26qudao%3Dbing_pc_H120003UY5%26plan%3DBOSS-%25E5%25BF%2585%25E5%25BA%2594-%25E5%2593%2581%25E7%2589%258C%26unit%3D%25E7%25B2%25BE%25E5%2587%2586%26keyword%3Dboss%25E7%259B%25B4%25E8%2581%2598%26msclkid%3D24999f57ac6619c5979df70b4c0b6d1a&s=3&friend_source=0',
        'Hm_lvt_194df3105ad7148dcf2b98a91b5e727a': '1750914744,1750915900,1750916385,1750917235',
        'Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a': '1750917235',
        'HMACCOUNT': 'EE2C631D6CC05F87',
        '__c': '1750917232',
        '__a': '12364210.1750905430.1750916382.1750917232.49.9.3.3',
        'BAIDUID_BFESS': '75C89348E095F1A1D125748402ED2BC4:FG=1',
        'ab_guid': 'd3643ee8-a80c-4da2-965d-16b8726f16cf',
        'bst': 'V2R9ohF-T_0lxjVtRuyhwfLSmw7DrSwys~|R9ohF-T_0lxjVtRuyhwfLSmw7DrezCU~',
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'priority': 'u=1, i',
        'referer': 'https://www.zhipin.com/web/geek/jobs?query=%E8%85%BE%E8%AE%AF&city=101270100',
        'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'token': 'ihzWemCouhxcuJCs',
        'traceid': 'F-1ac6f1sOQjMGwE05',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
        'zp_token': 'V2R9ohF-T_0lxjVtRuyhwfLSmw7DrSwys~|R9ohF-T_0lxjVtRuyhwfLSmw7DrezCU~',
    }

    params = {
         'scene': '1',
        'query': query,
        'city': '',
        'experience': '',
        'payType': '',
        'partTime': '',
        'degree': '',
        'industry': '',
        'scale': '',
        'stage': '',
        'position': '',
        'jobType': '',
        'salary': '',
        'multiBusinessDistrict': '',
        'multiSubway': '',
        'page': page,
        'pageSize': '30',
    }

    try:
        response = requests.get(
            'https://www.zhipin.com/wapi/zpgeek/search/joblist.json',
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None


def get_datas(json_data):
    """解析职位数据"""
    if not json_data or "zpData" not in json_data or "jobList" not in json_data["zpData"]:
        return []

    job_contents = json_data["zpData"]["jobList"]
    jobs = []
    for job_content in job_contents:
        try:
            # 提取职位信息（保持不变）
            jobs.append([
                job_content.get('encryptJobId', '未知'),
                job_content.get('jobName', '未知'),
                job_content.get('salaryDesc', '未标注'),
                job_content.get('skills', '无'),
                job_content.get('jobDegree', '不限'),
                job_content.get('jobExperience', '无要求'),
                job_content.get('brandName', '未标注公司'),
                job_content.get('cityName', '全国'),
                job_content.get('bossName', '未显示'),
                ', '.join(job_content.get('welfareList', [])) or '无福利',
                f"https://www.zhipin.com/job_detail/{job_content.get('encryptJobId', '未知')}.html?securityId={job_content.get('securityId', '')}"
            ])
        except Exception as e:
            print(f"解析数据出错: {e}")

    return jobs


def get_token_count():
    return 1


async def process_single_query(kw, co, user_data_dir):
    """处理单个查询任务，优先使用剩余token"""
    global current_token, remaining_uses

    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)
    filename = os.path.join(csv_folder, f"{co}_{kw}_职位信息.csv")

    all_jobs = []
    current_page = 1

    if kw == '多':
        print("多公司不爬取...")
    else:
        # 检查是否有可用token，没有则获取
        if not current_token or remaining_uses <= 0:
            print("无可用token，获取新token...")
            if not await fetch_zp_stoken(user_data_dir):
                print("获取token失败，终止当前查询")
                return

        # 使用当前token处理，直到用完剩余次数或数据不足
        while remaining_uses > 0:
            print(f"\n使用token {current_token[:20]}... 爬取第{current_page}页 (剩余可用次数: {remaining_uses})")
            json_data = get_request(kw, current_page, current_token)

            # 等待随机时间
            wait_time = random.uniform(2, 5)
            print(f"等待{wait_time:.1f}秒后继续...")
            await asyncio.sleep(wait_time)

            # 处理当前页数据
            jobs = []
            if json_data and json_data.get('code') == 0:
                jobs = get_datas(json_data)
                all_jobs.extend(jobs)
                print(f"第{current_page}页获取到{len(jobs)}条数据")
            else:
                print(f"第{current_page}页数据获取失败")

            # 无论成功或失败，都只消耗1次token
            remaining_uses -= 1

            # 数据不足30条时，提前结束当前查询
            if 30 * (current_page - 1) + len(jobs) >= 30:
                print("超出最大量")
                break
            if len(jobs) < 30:
                print(f"第{current_page}页数据不足30条，提前结束当前查询")
                break
            else:
                if not current_token or remaining_uses <= 0:
                    print("无可用token，获取新token...")
                    if not await fetch_zp_stoken(user_data_dir):
                        print("获取token失败，终止当前查询")
                        return
            current_page += 1

    # 写入CSV
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "encryptJobId", "职位名称", "薪资", "技能要求", "学历要求",
            "工作经验", "公司名称", "城市", "招聘负责人", "福利", "职位链接"
        ])
        writer.writerows(all_jobs)

    print(f"\n数据已保存至: {filename} (共{len(all_jobs)}条)")
    if remaining_uses > 0:
        print(f"当前token仍有{remaining_uses}次可用，保留供下一个查询使用")


async def main(kw=None, co=None):
    user_data_dir = r"E:\edge_data\User Data"

    # 处理关键词和项目编号（如果外部传入则直接使用，否则手动输入）
    if kw is None:
        kw = 'kilaki'
    if co is None:
        co = input("请输入项目编号: ").strip()
        while not co:
            print("项目编号不能为空！")
            co = input("请输入项目编号: ").strip()

    # 处理当前查询
    await process_single_query(kw, co, user_data_dir)
    await close_browser()


if __name__ == "__main__":
    datas = fetch_uncprocessed_data()
    for data in datas:
        try:
            parsed_data = json.loads(data)
            kw_parent = parsed_data['中标供应商']
            co = parsed_data["项目编号"]
            if kw_parent:
                kw = kw_parent['名称']
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                asyncio.run(main(kw=kw, co=co))
                mark_data_as_processed(co)
            else:
                import jieba
                ori_time = parsed_data['公告时间']
                target_time_str = ori_time[:4] + "." + ori_time[5:7] + "." + ori_time[8:10]
                project_name = parsed_data.get('项目名称', '')
                # 使用jieba对项目名称进行分词，生成关键词
                keyword_list = jieba.cut(project_name)
                # 过滤单个字符的分词结果，提高关键词质量
                keyword_list = [word for word in keyword_list if len(word) > 1]
                keyword = ",".join(keyword_list)
                insert_data(co,parsed_data['type'],target_time_str,parsed_data,keyword,project_name,parsed_data['bidSort'],parsed_data['省份'])
                mark_data_as_processed(co)
                print("直接写入成功")
        except json.JSONDecodeError:
            print("JSON解析失败")
            break
        except KeyError:
            print("数据结构不符合预期")
            break