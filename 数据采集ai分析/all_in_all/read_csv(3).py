import os
import csv
import json
import pickle
from typing import List, Dict, Optional
import mysql.connector
from mysql.connector import Error
from ai_data import generate_text

# 数据库配置（关闭警告自动获取，避免连接同步问题）
DB_CONFIG = {
    'host': 'localhost',
    'database': 'gbdb',
    'user': 'root',
    'password': '*****',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True,
    'raise_on_warnings': False  # 关键：关闭自动获取警告，避免连接同步问题
}


def get_json_data_by_code(project_code: str) -> str | None:
    try:
        # 每次查询使用独立连接，避免结果集残留
        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = "SELECT json_data,keyword FROM procurement_data WHERE project_code = %s"
                cursor.execute(query, (project_code,))
                result = cursor.fetchone()
                # 确保结果集完全读取
                cursor.fetchall()  # 清空可能的残留结果
                return result if result else None
    except Error as e:
        print(f"数据库错误: {e}")
        return None


def create_temp_table():
    """创建/升级temp_data表，使用独立连接"""
    try:
        with mysql.connector.connect(** DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS temp_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_code VARCHAR(255) NOT NULL UNIQUE,
                    json_data TEXT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    INDEX idx_processed (processed)
                ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
                """
                cursor.execute(create_table_query)
                print("temp_data表创建成功或已存在")

                # 检查并添加id字段
                cursor.execute("SHOW COLUMNS FROM temp_data LIKE 'id'")
                if not cursor.fetchone():
                    print("添加自增主键id...")
                    cursor.execute("ALTER TABLE temp_data ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST")
                    cursor.execute("ALTER TABLE temp_data ADD UNIQUE KEY idx_unique_project (project_code)")
                    print("id字段添加完成")

                # 检查并添加processed字段
                cursor.execute("SHOW COLUMNS FROM temp_data LIKE 'processed'")
                if not cursor.fetchone():
                    print("添加processed字段...")
                    cursor.execute("ALTER TABLE temp_data ADD COLUMN processed BOOLEAN DEFAULT FALSE")
                    print("processed字段添加完成")
                cursor.fetchall()  # 清空结果集
    except Error as e:
        if e.errno != 1050:
            print(f"创建表失败: {e}")
            raise


def save_to_temp_data(project_code: str, json_data: str) -> bool:
    """使用独立连接保存数据，避免命令同步问题"""
    try:
        with mysql.connector.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                query = """
                INSERT INTO temp_data (project_code, json_data, processed)
                VALUES (%s, %s, FALSE)
                ON DUPLICATE KEY UPDATE 
                    json_data = VALUES(json_data),
                    processed = FALSE;
                """
                cursor.execute(query, (project_code, json_data))
                connection.commit()  # 显式提交（虽然autocommit=True，但确保生效）
                cursor.fetchall()  # 清空可能的警告结果集
                return True
    except Error as e:
        print(f"保存到temp_data表时出错: {e}")
        return False


class CSVProcessor:
    # 保持原有逻辑不变
    def __init__(self, directory: str, sort_key: str = 'name'):
        self.directory = directory
        self.processed_file = os.path.join(directory, 'processed_files.pkl')
        self.sort_key = sort_key
        self.processed_files = self._load_processed_files()

    def _load_processed_files(self) -> Dict[str, float]:
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"加载已处理文件列表出错: {e}")
                return {}
        return {}

    def _save_processed_files(self) -> None:
        try:
            with open(self.processed_file, 'wb') as f:
                pickle.dump(self.processed_files, f)
        except Exception as e:
            print(f"保存已处理文件列表出错: {e}")

    def list_files(self) -> List[str]:
        files = [f for f in os.listdir(self.directory) if f.endswith('.csv') and os.path.isfile(os.path.join(self.directory, f))]
        if not files:
            return []
        unprocessed_files = []
        for file in files:
            file_path = os.path.join(self.directory, file)
            file_mtime = os.path.getmtime(file_path)
            if file not in self.processed_files or self.processed_files[file] < file_mtime:
                unprocessed_files.append(file)
        if self.sort_key == 'mtime':
            unprocessed_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.directory, x)))
        else:
            unprocessed_files.sort()
        return unprocessed_files

    def read_file(self, file_name: str) -> List[Dict]:
        file_path = os.path.join(self.directory, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        records = []
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if '技能要求' in row and row['技能要求']:
                        try:
                            row['技能要求'] = json.loads(row['技能要求'].replace("'", '"'))
                            if not isinstance(row['技能要求'], list):
                                row['技能要求'] = [row['技能要求']]
                        except json.JSONDecodeError:
                            row['技能要求'] = [row['技能要求']]
                    records.append(row)
            return records
        except Exception as e:
            print(f"读取文件出错: {e}")
            raise

    def mark_file_as_processed(self, file_name: str) -> None:
        file_path = os.path.join(self.directory, file_name)
        try:
            self.processed_files[file_name] = os.path.getmtime(file_path)
            self._save_processed_files()
            print(f"已标记文件 {file_name} 为已导入")
        except Exception as e:
            print(f"标记文件出错: {e}")

    def process_next_file(self) -> Optional[Dict]:
        files = self.list_files()
        if not files:
            return None
        next_file = files[0]
        data = self.read_file(next_file)
        return {'file_name': next_file, 'data': data}


if __name__ == "__main__":
    csv_dir = "./csv"
    BATCH_SIZE = 10
    try:
        create_temp_table()
        processor = CSVProcessor(csv_dir)
        print("开始处理文件...")
        while True:
            result = processor.process_next_file()
            if not result:
                print("无更多文件需要处理")
                break
            file_name = result['file_name']
            data = result['data']
            code_id = file_name.split('_')[0]
            print(f"\n处理文件: {file_name}，项目编号: {code_id}")

            data_all = get_json_data_by_code(code_id) or {}
            json_data_str = data_all.get("json_data", "")

            if not json_data_str:
                print(f"未找到项目 {code_id} 的数据，跳过")
                processor.mark_file_as_processed(file_name)
                continue

            try:
                json_data = json.loads(json_data_str)
            except json.JSONDecodeError as e:
                print(f"解析JSON失败: {e}，跳过")
                processor.mark_file_as_processed(file_name)
                continue

            extracted_data = {
                "采购单位": json_data.get("采购单位", ""),
                "项目名称": json_data.get("项目名称", ""),
                "项目编号": json_data.get("项目编号", code_id)
            }

            total_records = len(data)
            batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE
            all_batch_results = []

            for batch_num in range(batches):
                start_idx = batch_num * BATCH_SIZE
                end_idx = min((batch_num + 1) * BATCH_SIZE, total_records)
                batch_data = data[start_idx:end_idx]
                print(f"处理批次 {batch_num + 1}/{batches}")

                inp = f"""
                分析匹配度，返回JSON：
                {{
                    "招聘岗位": [
                        {{
                            "encryptJobId": null,
                            "职位": "",
                            "薪资": "",
                            "技能要求": "",
                            "匹配度": "",
                            "匹配度原因": "",
                            "职位链接": null
                        }}
                    ]
                }}
                项目信息：{extracted_data}
                职位信息：{batch_data}
                """
                try:
                    res = generate_text(inp)
                    cleaned = res.strip('```json').strip('```').strip()
                    res_dict = json.loads(cleaned)
                    all_batch_results.extend(res_dict.get("招聘岗位", []))
                except Exception as e:
                    print(f"AI处理出错: {e}")

            json_data["招聘岗位"] = all_batch_results

            res_json = json.dumps(json_data, ensure_ascii=False, indent=2)

            save_success = save_to_temp_data(code_id, res_json)
            if save_success:
                print(f"项目 {code_id} 保存成功")
                processor.mark_file_as_processed(file_name)
            else:
                print(f"项目 {code_id} 保存失败")
    except Exception as e:
        print(f"程序错误: {e}")