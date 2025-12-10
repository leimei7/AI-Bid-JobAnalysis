from datetime import datetime
import time
import requests

def clean_software_data(data):
    """清洗软件数据，处理时间戳并提取需要的字段"""
    cleaned_data = []

    # 遍历每个软件项目
    for item in data.get('data', {}).get('items', []):
        # 提取需要的字段
        cleaned_item = {
            'fullname': item.get('fullname', ''),
            'regnum': item.get('regnum', ''),
            'version': item.get('version', ''),
        }

        # 处理时间戳
        regtime = item.get('regtime')
        if regtime:
            try:
                # 将毫秒级时间戳转换为秒级
                regtime_seconds = regtime / 1000
                # 转换为日期字符串
                cleaned_item['regtime'] = datetime.fromtimestamp(regtime_seconds).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                # 处理转换失败的情况
                cleaned_item['regtime'] = '时间格式错误'
        else:
            cleaned_item['regtime'] = '未提供'

        cleaned_data.append(cleaned_item)

    return cleaned_data

def more_rz(id,headers):
    params = {
        '_': str(int(time.time() * 1000)),
        'id': id,
        'pageSize': '10',
        'pageNum': '1',
    }

    response = requests.get(
        'https://capi.tianyancha.com/cloud-intellectual-property/intellectualProperty/softwareCopyrightListV2',
        params=params,
        headers=headers,
    )

    return clean_software_data(response.json())

if __name__ == '__main__':
    pass
    # fullname
    # regnum
    # regtime
    # version