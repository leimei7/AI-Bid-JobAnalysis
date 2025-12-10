import mysql.connector
from mysql.connector import Error
import json
from typing import List, Dict
from datetime import datetime
import jieba

from get_company import get_company_all

DB_CONFIG_1 = {
    'host': 'localhost',
    'database': 'gbdb',
    'user': 'root',
    'password': '*****',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True,
    'raise_on_warnings': True
}

# 数据库配置（替换为实际信息）
DB_CONFIG = {
    'host': '8.137.60.115',
    'user': 'kilaki',
    'password': '*****',
    'port': 3306,
    'database': 'gbdb',  # 需提前创建数据库
    'charset': 'utf8mb4',
    'autocommit': True
}


def create_target_table():
    """创建目标表，包含自增主键、唯一键和索引"""
    create_table_sql = """
                       CREATE TABLE IF NOT EXISTS project_info \
                       ( \
                           id           INT AUTO_INCREMENT PRIMARY KEY, \
                           project_code VARCHAR(255) NOT NULL, \
                           type         VARCHAR(100) NOT NULL, \
                           time         DATE         NOT NULL, \
                           keyword      VARCHAR(255), \
                           project_name VARCHAR(255), \
                           bidSort      VARCHAR(255), \
                           province     VARCHAR(100), \
                           is_important BOOLEAN DEFAULT 0, \
                           json_data    JSON         NOT NULL, \
                           UNIQUE KEY uk_project_code (project_code), \
                           INDEX idx_type (type), \
                           INDEX idx_time (time), \
                           INDEX idx_keyword (keyword), \
                           INDEX idx_project_name (project_name), \
                           INDEX idx_province (province) \
                       ) ENGINE = InnoDB \
                         DEFAULT CHARSET = utf8mb4; \
                       """
    try:
        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(create_table_sql)
                print("表创建成功或已存在")
    except Error as e:
        print(f"建表失败: {e}")
        raise


def insert_data(project_code: str, type_str: str, time_str: str, json_data: dict, keyword: str, project_name: str,
                bidSort: str, province: str) -> bool:
    try:
        # 转换时间格式（2025.07.14 -> 2025-07-14，适应DATE类型）
        time_obj = datetime.strptime(time_str, "%Y.%m.%d").date()

        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                insert_sql = """
                             INSERT INTO project_info
                             (project_code, type, time, keyword, project_name, bidSort, province, json_data)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE type         = %s, \
                                                     time         = %s, \
                                                     keyword      = %s, \
                                                     project_name = %s, \
                                                     bidSort      = %s, \
                                                     province     = %s, \
                                                     json_data    = %s;
                             """
                # 转换字典为JSON字符串
                json_str = json.dumps(json_data, ensure_ascii=False)
                # 执行插入（重复值更新时需重复传入参数）
                cursor.execute(
                    insert_sql,
                    (project_code, type_str, time_obj, keyword, project_name, bidSort, province, json_str,
                     type_str, time_obj, keyword, project_name, bidSort, province, json_str)
                )
                return True
    except Error as e:
        print(f"插入数据失败: {e}")
        return False
    except ValueError as e:
        print(f"时间格式错误（需形如2025.07.14）: {e}")
        return False


def get_unprocessed_data(limit: int = 20) -> List[Dict]:
    try:
        with mysql.connector.connect(**DB_CONFIG_1) as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                        SELECT project_code, json_data
                        FROM temp_data
                        WHERE processed = FALSE
                        LIMIT %s
                        """
                cursor.execute(query, (limit,))
                results = cursor.fetchall()

                # 解析json_data为字典
                for item in results:
                    try:
                        item['json_data'] = json.loads(item['json_data'])
                    except json.JSONDecodeError as e:
                        print(f"解析项目 {item['project_code']} 的JSON数据失败: {e}")
                        item['json_data'] = None  # 标记为解析失败
                return results
    except Error as e:
        print(f"查询未处理数据时出错: {e}")
        return []


def mark_as_processed(project_code: str) -> bool:
    try:
        with mysql.connector.connect(**DB_CONFIG_1) as connection:
            with connection.cursor() as cursor:
                query = """
                        UPDATE temp_data
                        SET processed = TRUE
                        WHERE project_code = %s
                        """
                cursor.execute(query, (project_code,))
                # 检查是否有记录被更新
                return cursor.rowcount > 0
    except Error as e:
        print(f"标记项目 {project_code} 为已处理时出错: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    # 示例：获取未处理数据并迁移到新项目表
    print("获取未处理数据：")
    unprocessed = get_unprocessed_data(limit=20)
    if unprocessed:
        create_target_table()
        for item in unprocessed:
            if item['json_data']:
                all_data = item['json_data']
                company_name = all_data['中标供应商']['名称']
                company_all = get_company_all(company_name)
                all_data['中标供应商']['企业详情'] = company_all

                code = item['project_code']
                ty = all_data['type']
                original_time = all_data['公告时间']
                target_time_str = original_time[:4] + "." + original_time[5:7] + "." + original_time[8:10]

                # 从JSON数据中提取项目名称
                project_name = all_data.get('项目名称', '')

                # 使用jieba对项目名称进行分词，生成关键词
                keyword_list = jieba.cut(project_name)
                # 过滤单个字符的分词结果，提高关键词质量
                keyword_list = [word for word in keyword_list if len(word) > 1]
                keyword = ",".join(keyword_list)

                # 提取bidSort
                bidSort = all_data.get('bidSort', '')

                # 提取省份
                province = all_data.get('省份', '')

                success = insert_data(code, ty, target_time_str, all_data, keyword, project_name, bidSort, province)
                if success:
                    mark_as_processed(code)
                    print(f"已处理项目: {code} (关键词: {keyword}, 省份: {province})")
            else:
                print(f"项目编号: {item['project_code']} (JSON解析失败)")
    else:
        print("没有未处理的数据")