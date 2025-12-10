
import requests
import time

params = {
    '_': str(int(time.time() * 1000)),
}


def extract_trademark_info(response_json):
    # 逐层获取items列表，处理可能的嵌套结构
    # 完整路径是：response_json -> data -> items
    data = response_json.get('data', {})  # 先获取data字段
    items = data.get('items', [])  # 再从data中获取items列表

    # 提取所需字段
    result = []
    for item in items:
        trademark = {
            'intCls': item.get('intCls'),  # 商标分类
            'tmName': item.get('tmName'),  # 商标名称
            'status': item.get('status'),  # 商标状态
            'tmPic': item.get('tmPic'),  # 商标图片链接
            'appDate': item.get('appDate') # 申请时间
        }
        result.append(trademark)

    return result

def more_zc(id,headers):
    json_data = {
        'id': id,
        'ps': 10,
        'pn': 1,
        'category': '-100',
        'fullSearchText': '',
        'sortField': '',
        'sortType': '',
    }

    response = requests.post(
        'https://capi.tianyancha.com/cloud-intellectual-property/intellectualProperty/trademarkList',
        params=params,
        headers=headers,
        json=json_data,
    )

    return extract_trademark_info(response.json())

if __name__ == '__main__':
    pass

    # intCls
    # tmName
    # status
    # tmPic
