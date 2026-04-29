"""
检查数据库中的档案数据
"""
import asyncio
import sys
sys.path.insert(0, 'bazi-admin')

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import Archive


async def check_archives():
    """检查数据库中的档案"""
    async with AsyncSessionLocal() as db:
        try:
            # 查询所有档案
            stmt = select(Archive).limit(10)
            result = await db.execute(stmt)
            archives = result.scalars().all()
            
            print(f'\n📊 数据库中共有 {len(archives)} 条档案（显示前10条）\n')
            
            if len(archives) == 0:
                print('❌ 数据库中没有档案数据！')
                print('💡 请先在前端创建档案，或使用档案同步接口上传档案。')
                return
            
            for i, archive in enumerate(archives, 1):
                print(f'【档案 {i}】')
                print(f'  档案ID: {archive.archive_id}')
                print(f'  姓名: {archive.name}')
                print(f'  性别: {"男" if archive.gender == 1 else "女"}')
                print(f'  出生日期: {archive.birth_year}-{archive.birth_month:02d}-{archive.birth_day:02d} {archive.birth_hour:02d}:{archive.birth_minute:02d}')
                print(f'  历法类型: {archive.calendar_type}')
                print(f'  创建时间: {archive.created_at}')
                print('-' * 80)
                
        except Exception as e:
            print(f'❌ 查询失败: {e}')
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(check_archives())
