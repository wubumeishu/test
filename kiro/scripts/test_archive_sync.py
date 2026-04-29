"""
测试档案同步接口
"""
import asyncio
import sys
from pathlib import Path
import time

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent / "bazi-admin"
sys.path.insert(0, str(project_root))

from src.database import AsyncSessionLocal
from src.models import Archive, User
from sqlalchemy import select


async def test_archive_sync():
    """测试档案同步逻辑"""
    print("=" * 60)
    print("测试档案同步接口")
    print("=" * 60)
    
    # 模拟用户ID
    test_user_id = "00000000-0000-0000-0000-000000000001"
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. 创建测试用户 (如果不存在)
            print("\n1️⃣ 检查测试用户...")
            stmt = select(User).where(User.user_id == test_user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user is None:
                print("   创建测试用户...")
                user = User(
                    user_id=test_user_id,
                    nickname="测试用户",
                    phone="13800138000"
                )
                db.add(user)
                await db.commit()
                print("   ✅ 测试用户创建成功")
            else:
                print("   ✅ 测试用户已存在")
            
            # 2. 模拟第一次同步 (INSERT)
            print("\n2️⃣ 模拟第一次同步 (INSERT)...")
            archive_id_1 = "00000000-0000-0000-0000-000000000101"
            archive_id_2 = "00000000-0000-0000-0000-000000000102"
            timestamp_1 = int(time.time() * 1000)
            
            # 检查是否已存在
            stmt = select(Archive).where(Archive.archive_id == archive_id_1)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing is None:
                archive_1 = Archive(
                    archive_id=archive_id_1,
                    user_id=test_user_id,
                    name="张三",
                    gender=1,
                    calendar_type="solar",
                    birth_year=1990,
                    birth_month=5,
                    birth_day=15,
                    birth_hour=14,
                    birth_minute=30,
                    tags="本人,重要",
                    is_default=True,
                    local_created_at=timestamp_1,
                    cloud_uploaded_at=timestamp_1,
                )
                db.add(archive_1)
                await db.commit()  # 立即提交
                print(f"   ✅ 插入档案 1: {archive_id_1}")
            else:
                print(f"   ⚠️  档案 1 已存在: {archive_id_1}")
            
            stmt = select(Archive).where(Archive.archive_id == archive_id_2)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing is None:
                archive_2 = Archive(
                    archive_id=archive_id_2,
                    user_id=test_user_id,
                    name="李四",
                    gender=0,
                    calendar_type="solar",
                    birth_year=1992,
                    birth_month=8,
                    birth_day=20,
                    birth_hour=10,
                    birth_minute=0,
                    tags="朋友",
                    is_default=False,
                    local_created_at=timestamp_1,
                    cloud_uploaded_at=timestamp_1,
                )
                db.add(archive_2)
                await db.commit()  # 立即提交
                print(f"   ✅ 插入档案 2: {archive_id_2}")
            else:
                print(f"   ⚠️  档案 2 已存在: {archive_id_2}")
            
            # 3. 查询所有档案
            print("\n3️⃣ 查询所有档案...")
            stmt = select(Archive).where(Archive.user_id == test_user_id)
            result = await db.execute(stmt)
            archives = result.scalars().all()
            
            print(f"   ✅ 找到 {len(archives)} 个档案:")
            for archive in archives:
                print(f"      - {archive.name} ({archive.archive_id})")
                print(f"        性别: {'男' if archive.gender == 1 else '女'}")
                print(f"        生日: {archive.birth_year}-{archive.birth_month}-{archive.birth_day}")
                print(f"        本地时间戳: {archive.local_created_at}")
                print(f"        云端时间戳: {archive.cloud_uploaded_at}")
            
            # 4. 模拟更新 (UPDATE)
            print("\n4️⃣ 模拟更新档案 (时间戳更晚)...")
            timestamp_2 = int(time.time() * 1000) + 1000  # 1秒后
            
            stmt = select(Archive).where(Archive.archive_id == archive_id_1)
            result = await db.execute(stmt)
            archive = result.scalar_one_or_none()
            
            if archive and timestamp_2 > archive.local_created_at:
                old_name = archive.name
                archive.name = "张三 (已更新)"
                archive.tags = "本人,重要,已更新"
                archive.local_created_at = timestamp_2
                archive.cloud_uploaded_at = timestamp_2
                await db.commit()
                print(f"   ✅ 更新档案: {old_name} -> {archive.name}")
            
            # 5. 再次查询验证
            print("\n5️⃣ 验证更新结果...")
            stmt = select(Archive).where(Archive.archive_id == archive_id_1)
            result = await db.execute(stmt)
            archive = result.scalar_one_or_none()
            
            if archive:
                print(f"   ✅ 档案名称: {archive.name}")
                print(f"   ✅ 标签: {archive.tags}")
                print(f"   ✅ 本地时间戳: {archive.local_created_at}")
            
            print("\n" + "=" * 60)
            print("✅ 测试完成!")
            print("=" * 60)
            print("\n💡 提示: 现在可以启动服务并访问 http://127.0.0.1:9000/docs")
            print("   测试 POST /api/archives/sync 接口")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(test_archive_sync())
