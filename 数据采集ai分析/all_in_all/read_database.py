import pymysql
from pymysql.cursors import DictCursor

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'gbdb',
    'user': 'root',
    'password': '*****',
    'charset': 'utf8mb4',
    'autocommit': True
}

def fetch_uncprocessed_data():
    """获取未处理的采购数据"""
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor(DictCursor) as cursor:
                # 查询未处理的数据
                select_query = """
                               SELECT json_data
                               FROM procurement_data
                               WHERE is_processed = 0
                               ORDER BY id DESC \
                               """
                cursor.execute(select_query)
                rows = cursor.fetchall()

                json_values = [row['json_data'] for row in rows]
                print(f"找到 {len(json_values)} 条未处理的数据")

                return json_values

    except pymysql.Error as e:
        print(f"数据库错误: {e}")
        return []


def mark_data_as_processed(record_id):
    """将指定ID的数据标记为已处理"""
    try:
        with pymysql.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                update_query = """
                               UPDATE procurement_data
                               SET is_processed = 1
                               WHERE project_code = %s \
                               """
                cursor.execute(update_query, (record_id,))
                print(f"已标记ID为 {record_id} 的数据为已处理")
                return True

    except pymysql.Error as e:
        print(f"数据库错误: {e}")
        return False

if __name__ == "__main__":
    # 获取未处理的数据
    unprocessed_data = fetch_uncprocessed_data()
    for data in unprocessed_data:
        print(data)