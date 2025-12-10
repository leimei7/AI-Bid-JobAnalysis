import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Date, JSON, or_, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import jieba
import time
from functools import wraps
import asyncio

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 数据库配置
DB_CONFIG = {
    'host': '8.137.60.115',
    'user': 'kilaki',
    'password': '*****',  # 替换为实际密码
    'port': 3306,
    'database': 'gbdb',
    'charset': 'utf8mb4'
}

# 创建数据库连接，添加连接池配置
engine = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}",
    echo=False,
    pool_size=10,                # 连接池大小
    max_overflow=20,             # 最大溢出连接数
    pool_recycle=3600,           # 连接回收时间（秒）
    pool_pre_ping=True           # 连接前测试
)

# 定义模型（与更新后的数据库表结构同步）
Base = declarative_base()

class ProjectInfo(Base):
    __tablename__ = 'project_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_code = Column(String(255), nullable=False, unique=True)
    type = Column(String(100), nullable=False)
    time = Column(Date, nullable=False)
    keyword = Column(String(255))
    project_name = Column(String(255))  # 项目名（独立字段）
    bidSort = Column(String(255))       # bidSort（独立字段）
    province = Column(String(100))      # 新增：省份字段
    is_important = Column(Boolean, default=False)  # 新增：重要信息标识
    json_data = Column(JSON, nullable=False)

# 创建表（如果不存在）
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)

# 数据库操作重试装饰器
def db_retry(max_retries=3, delay=2):
    def decorator(func):
        # 判断函数是否为异步函数
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except OperationalError as e:
                        if attempt < max_retries - 1:
                            print(f"数据库操作失败，正在重试 ({attempt + 1}/{max_retries}): {str(e)}")
                            await asyncio.sleep(delay)  # 异步等待
                            continue
                        else:
                            print(f"所有重试均失败: {str(e)}")
                            raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except OperationalError as e:
                        if attempt < max_retries - 1:
                            print(f"数据库操作失败，正在重试 ({attempt + 1}/{max_retries}): {str(e)}")
                            time.sleep(delay)
                            continue
                        else:
                            print(f"所有重试均失败: {str(e)}")
                            raise
            return sync_wrapper
    return decorator

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 搜索API（支持省份和重要信息筛选）
# 搜索API（支持分页、省份和重要信息筛选）
@app.post("/api/search")
@db_retry()
async def search_api(request: Request):
    data = await request.json()
    # 原有参数
    keyword = data.get('keyword', '').strip()
    type_filter = data.get('type', '')
    province = data.get('province', '').strip()
    only_important = data.get('onlyImportant', False)
    time_range = data.get('timeRange', {})
    start_time = time_range.get('start')
    end_time = time_range.get('end')

    # 新增分页参数：page（当前页，默认1）、page_size（每页条数，默认10）
    page = int(data.get('page', 1))  # 页码从1开始
    page_size = int(data.get('page_size', 10))  # 每页10条

    session = Session()
    try:
        # 基础查询（未执行，仅构建条件）
        query = session.query(ProjectInfo)

        # 关键词搜索逻辑（不变）
        if keyword:
            words = list(jieba.cut_for_search(keyword))
            conditions = []
            for word in words:
                conditions.append(ProjectInfo.project_code.like(f'%{word}%'))
                conditions.append(ProjectInfo.type.like(f'%{word}%'))
                conditions.append(ProjectInfo.keyword.like(f'%{word}%'))
                conditions.append(ProjectInfo.project_name.like(f'%{word}%'))
                conditions.append(ProjectInfo.province.like(f'%{word}%'))
            if conditions:
                query = query.filter(or_(*conditions))

        # 类型、省份、重要信息筛选（不变）
        if type_filter:
            query = query.filter(ProjectInfo.type == type_filter)
        if province:
            query = query.filter(ProjectInfo.province.like(f'%{province}%'))
        if only_important:
            query = query.filter(ProjectInfo.is_important == True)

        # 时间范围筛选（不变）
        if start_time and end_time:
            query = query.filter(ProjectInfo.time.between(start_time, end_time))
        elif start_time:
            query = query.filter(ProjectInfo.time >= start_time)
        elif end_time:
            query = query.filter(ProjectInfo.time <= end_time)

        # 计算总条数（用于前端判断是否还有更多数据）
        total = query.count()  # 总符合条件的记录数

        # 分页处理：offset(跳过前n条) = (page-1)*page_size；limit(最多返回page_size条)
        # 按发布时间倒序（最新的在前），可根据需求调整排序字段
        query = query.order_by(ProjectInfo.time.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size)

        # 执行分页查询
        results = query.all()

        # 处理返回结果（不变）
        result_list = [
            {
                'id': item.id,
                'project_code': item.project_code,
                'project_name': item.project_name or '未知项目名',
                'type': item.type,
                'bidSort': item.bidSort or '',
                'time': item.time.strftime('%Y-%m-%d'),
                'province': item.province or '',
                'isImportant': item.is_important,
                'json_data': item.json_data
            }
            for item in results
        ]

        # 返回分页相关信息：当前页、总条数、是否有下一页
        return JSONResponse({
            'results': result_list,
            'pagination': {
                'page': page,  # 当前页码
                'page_size': page_size,  # 每页条数
                'total': total,  # 总记录数
                'has_more': (page * page_size) < total  # 是否还有下一页
            },
            'query': {  # 回传查询条件，方便前端滚动刷新时复用
                'keyword': keyword,
                'type': type_filter,
                'province': province,
                'onlyImportant': only_important,
                'timeRange': time_range
            }
        })
    finally:
        session.close()

# 详情页API（包含新增字段）
@app.get("/api/item/{item_id}", response_class=HTMLResponse)
@db_retry()
async def item_detail(request: Request, item_id: int):
    session = Session()
    try:
        item = session.query(ProjectInfo).filter(ProjectInfo.id == item_id).first()
        if item:
            item_data = {
                'id': item.id,
                'project_code': item.project_code,
                'project_name': item.project_name or '未知项目名',
                'type': item.type,
                'bidSort': item.bidSort or '',
                'time': item.time.strftime('%Y-%m-%d'),
                'province': item.province or '',
                'isImportant': item.is_important,
                'json_data': item.json_data
            }
            # return JSONResponse(item_data)
            return templates.TemplateResponse("project_detail.html", {"request": request, "item": item_data})
        else:
            return templates.TemplateResponse("project_not_found.html", {"request": request, "item_id": item_id})
    finally:
        session.close()

@app.post("/api/item/{item_id}/mark_important")
@db_retry()
async def mark_important(item_id: int):
    session = Session()
    try:
        item = session.query(ProjectInfo).filter(ProjectInfo.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="项目未找到")

        item.is_important = True
        session.commit()
        session.refresh(item)

        return {"success": True, "message": "标记重点成功"}
    finally:
        session.close()

@app.post("/api/item/{item_id}/cancel_important")
@db_retry()
async def cancel_important(item_id: int):
    session = Session()
    try:
        item = session.query(ProjectInfo).filter(ProjectInfo.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="项目未找到")

        item.is_important = False
        session.commit()
        session.refresh(item)

        return {"success": True, "message": "取消重点成功"}
    finally:
        session.close()

if __name__ == "__main__":
    uvicorn.run(app, port=8000)