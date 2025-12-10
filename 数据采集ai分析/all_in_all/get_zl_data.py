import time
import requests


def extract_patent_info(response_json):
    # 从JSON结构中逐层获取items列表（完整路径：response_json -> data -> items）
    data = response_json.get('data', {})
    patent_items = data.get('items', [])

    # 提取所需字段
    result = []
    for item in patent_items:
        patent_info = {
            'patentName': item.get('patentName'),  # 专利名称
            'patentType': item.get('patentType'),  # 专利类型
            'lprs': item.get('lprs'),  # 专利状态（如"专利公开"）
            'appnumber': item.get('appnumber'),  # 申请号
            'applicationPublishTime': item.get('applicationPublishTime')  # 申请公布时间
        }
        result.append(patent_info)

    return result

def more_zl(id,headers):
    params = {
        '_': str(int(time.time() * 1000)),
        'id': id,
        'pageNum': '1',
        'pageSize': '10',
        'history': '0',
        'sortField': '',
        'sortType': '-100',
    }

    response = requests.get(
        'https://capi.tianyancha.com/cloud-intellectual-property/patent/patentListV7',
        params=params,
        headers=headers,
    )

    return extract_patent_info(response.json())

if __name__ == '__main__':
    pass
    # patentName
    # patentType
    # lprs
    # appnumber
    # applicationPublishTime