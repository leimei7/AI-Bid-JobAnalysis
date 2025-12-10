# 数据采集与AI分析系统

## 项目简介

本项目是一个**复合数据分析系统**，主要用于采集政府采购公告数据，通过AI技术进行结构化处理，结合企业信息（天眼查）和招聘数据（Boss直聘）进行深度关联分析，最终提供高效的搜索和展示功能。

**核心价值**：将招投标项目与企业招聘需求关联，分析企业在中标后的人才需求变化，为市场分析、行业趋势研究提供数据支持。

## 项目结构

```
数据采集ai分析/
├── all_in_all/           # 数据采集与处理模块
│   ├── ai_data.py        # 核心数据处理逻辑
│   ├── get_boss_all(2).py # Boss直聘职位爬虫
│   ├── get_company.py    # 企业信息获取（天眼查）
│   ├── get_company_data.py # 公司查询接口定义
│   ├── get_rz_data.py    # 融资数据获取
│   ├── get_zc_data.py    # 政策数据获取
│   ├── get_zl_data.py    # 专利数据获取
│   ├── get_search.py     # 搜索辅助功能
│   ├── buy_datas.py      # 采购数据提取
│   ├── buy_urls(1).py    # 采购网址管理
│   ├── cloud_database_con.py  # 云数据库连接与数据迁移
│   └── read_database.py  # 数据库读取工具
├── search-website/       # Web搜索服务模块
│   ├── main.py           # FastAPI主应用
│   ├── static/           # 静态资源
│   │   ├── bootstrap.min.css
│   │   ├── bootstrap.bundle.min.js
│   │   ├── style.css
│   │   └── script.js
│   └── templates/        # HTML模板
│       ├── base.html
│       ├── index.html
│       └── project_detail.html
└── README.md             # 项目说明文档
```

## 功能模块

### 1. 数据采集与处理模块 (all_in_all)

#### 核心功能
- **政府采购数据采集**：从公开政府采购网站采集招标、中标等公告信息
- **AI文本结构化**：使用DeepSeek API将非结构化文本转换为结构化JSON数据
- **企业信息关联**：自动关联中标企业的详细信息（天眼查），包括工商信息、知识产权等
- **招聘数据关联**：根据中标企业名称，自动从Boss直聘采集相关职位信息
- **智能去重**：基于项目编号等唯一标识进行数据去重
- **数据存储**：将处理后的数据存储到MySQL数据库
- **数据迁移**：支持数据从旧表结构迁移到新表结构，同时补充企业详情

#### 主要文件说明
- `ai_data.py`：核心数据处理逻辑，包括API调用、数据转换、数据库操作
- `get_boss_all(2).py`：Boss直聘职位爬虫，根据企业名称采集相关职位信息
- `get_company.py`：企业信息获取（天眼查），提取公司工商信息、知识产权等
- `get_company_data.py`：公司查询接口定义，规范企业信息结构
- `get_rz_data.py`：融资数据获取
- `get_zc_data.py`：政策数据获取
- `get_zl_data.py`：专利数据获取
- `buy_datas.py`：采购数据提取，从政府采购网站HTML中提取结构化信息
- `buy_urls(1).py`：采购网址管理，处理政府采购网站的URL
- `cloud_database_con.py`：云数据库连接与数据迁移，将处理后的数据存储到云数据库
- `read_database.py`：数据库读取工具，获取未处理数据
- `get_search.py`：搜索辅助功能，用于在企业查询中进行搜索

### 2. 复合数据分析流程

1. **数据采集**：从政府采购网站采集招标/中标公告
2. **AI结构化**：使用DeepSeek API将非结构化文本转换为结构化JSON
3. **企业关联**：根据中标企业名称，从天眼查获取详细企业信息
4. **招聘关联**：根据企业名称，从Boss直聘获取相关职位信息
5. **数据存储**：将完整数据（招投标+企业信息+招聘数据）存储到数据库
6. **搜索展示**：通过Web界面提供多维度搜索和展示功能

### 3. Web搜索服务模块 (search-website)

#### 核心功能
- **高效搜索**：支持关键词搜索、类型筛选、省份筛选、时间范围筛选
- **复合数据展示**：同时展示招投标信息、企业详情、相关职位信息
- **分页查询**：优化大量数据的展示性能
- **重点标记**：支持将重要项目标记为重点
- **项目详情**：完整展示项目的详细信息，包括企业工商信息、知识产权、招聘职位等
- **响应式设计**：适配不同设备尺寸

#### 技术栈
- **后端**：FastAPI + SQLAlchemy + MySQL
- **前端**：HTML + CSS + JavaScript + Bootstrap
- **搜索优化**：jieba中文分词
- **数据可视化**：直观展示企业关联数据

## 环境要求

### 依赖安装

#### 数据采集模块
```bash
pip install requests mysql-connector-python jieba
```

#### Web服务模块
```bash
pip install fastapi uvicorn sqlalchemy pymysql jieba
```

## 快速开始

### 1. 配置数据库

在相应文件中配置数据库连接信息：
- 数据采集模块：`all_in_all/ai_data.py` 中的 `DB_CONFIG`
- Web服务模块：`search-website/main.py` 中的 `DB_CONFIG`

### 2. 配置API密钥

在 `all_in_all/ai_data.py` 中配置DeepSeek API密钥：
```python
API_KEY = "your_deepseek_api_key"
```

### 3. 运行数据采集

```bash
cd all_in_all
python ai_data.py
```

### 4. 启动Web服务

```bash
cd search-website
python main.py
```

服务将在 `http://localhost:8000` 启动

## 使用说明

### 数据采集流程

1. **准备数据源**：获取待处理的原始文本数据
2. **运行采集脚本**：执行相应的采集脚本
3. **AI结构化处理**：脚本自动调用DeepSeek API进行数据结构化
4. **数据存储**：处理后的数据自动存储到数据库

### Web搜索使用

1. **访问首页**：打开浏览器访问 `http://localhost:8000`
2. **输入关键词**：在搜索框中输入要搜索的关键词
3. **筛选条件**：可选择类型、省份、时间范围等筛选条件
4. **查看结果**：浏览搜索结果，点击项目查看详情
5. **标记重点**：在详情页可将重要项目标记为重点

## API接口

### 搜索接口

```
POST /api/search
```

**请求参数**：
```json
{
  "keyword": "防洪",
  "type": "",
  "province": "",
  "onlyImportant": false,
  "timeRange": {
    "start": "2025-01-01",
    "end": "2025-12-31"
  },
  "page": 1,
  "page_size": 10
}
```

**响应示例**：
```json
{
  "results": [
    {
      "id": 1,
      "project_code": "ZJF-2025-005",
      "project_name": "吉林鸭绿江上游国家级自然保护区2025年研学宣教与防洪设施加固项目施工",
      "type": "施工",
      "bidSort": "成交公告",
      "time": "2025-07-11",
      "province": "吉林省",
      "isImportant": false,
      "json_data": {...}
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "has_more": true
  }
}
```

### 项目详情接口

```
GET /api/item/{item_id}
```

### 标记重点接口

```
POST /api/item/{item_id}/mark_important
```

### 取消重点接口

```
POST /api/item/{item_id}/cancel_important
```

## 数据库设计

### 主要表结构

#### procurement_data表（原始数据存储）
- `id`：主键，自增
- `project_code`：项目编号，唯一索引
- `project_name`：项目名称
- `keyword`：关键词，索引
- `json_data`：完整JSON数据（中标公告原始数据）
- `is_processed`：是否已处理，索引

#### project_info表（最终数据存储，含复合关联）
- `id`：主键，自增
- `project_code`：项目编号，唯一
- `type`：类型
- `time`：时间
- `keyword`：关键词
- `project_name`：项目名称
- `bidSort`：公告类型
- `province`：省份
- `is_important`：是否重要
- `json_data`：完整JSON数据（含企业详情和招聘关联）

### 复合数据结构

```json
{
  "项目编号": "",
  "项目名称": "",
  "采购单位": "",
  "type": "",
  "bidSort": "",
  "省份": "",
  "中标供应商": {
    "名称": "",
    "地址": "",
    "中标金额": "",
    "评审得分": "",
    "企业详情": {
      "credit_code": "",
      "legal_person": "",
      "registered_capital": "",
      "establishment_date": "",
      "phone": "",
      "email": "",
      "address": "",
      "introduction": "",
      "status": "",
      "专利": [],
      "商标": [],
      "软著": []
    }
  },
  "公告时间": ""
}
```

## 技术亮点

1. **复合数据分析**：创新性地将招投标数据与企业信息、招聘数据关联，实现多维度分析
2. **AI驱动的数据结构化**：使用先进的LLM模型将非结构化文本转换为结构化数据
3. **自动化数据关联**：自动从多源（天眼查、Boss直聘）获取关联数据，无需人工干预
4. **高效的搜索机制**：结合jieba分词和SQLAlchemy查询优化，实现快速搜索
5. **可靠的数据库操作**：包含重试机制，提高系统稳定性
6. **响应式设计**：适配各种设备尺寸
7. **模块化架构**：各模块独立，便于扩展和维护
8. **数据可视化**：直观展示企业关联数据，提升数据分析效率

## 扩展建议

1. **增加更多招聘平台**：除Boss直聘外，扩展到智联招聘、前程无忧等平台
2. **深化数据分析**：添加数据挖掘算法，分析招投标与招聘需求的相关性
3. **优化AI模型调用**：添加缓存机制，减少API调用次数
4. **增强搜索功能**：添加高级搜索、模糊搜索、语义搜索等功能
5. **完善数据可视化**：添加更多图表类型，如趋势图、关系图等
6. **用户系统**：添加用户登录、权限管理、个性化推荐等功能
7. **定时任务**：添加定时自动采集、更新数据的功能
8. **API服务**：提供对外API服务，方便其他系统调用
9. **情感分析**：对招聘职位描述进行情感分析，了解企业招聘需求的紧急程度
10. **多维度统计**：添加按行业、地区、时间等维度的统计分析

## 注意事项

1. **API密钥安全**：妥善保管DeepSeek API密钥，避免泄露
2. **数据库连接**：确保数据库连接信息正确，网络通畅
3. **数据合法性**：确保采集的数据符合相关法律法规
4. **定期备份**：定期备份数据库，防止数据丢失
5. **性能优化**：对于大量数据，考虑添加索引、优化查询等

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，欢迎联系项目负责人。

---

**更新时间**：2025-12-10
**版本**：1.0.0
