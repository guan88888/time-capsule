import os
"""
数据库初始化脚本 - 自动创建数据库
"""
import pymysql
from sqlalchemy import create_engine, text

# MySQL连接信息（不指定数据库）
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
DATABASE_NAME = "my_app"

def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute(f"SHOW DATABASES LIKE '{DATABASE_NAME}'")
            result = cursor.fetchone()
            
            if not result:
                # 创建数据库
                cursor.execute(f"CREATE DATABASE {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"数据库 {DATABASE_NAME} 创建成功")
            else:
                print(f"数据库 {DATABASE_NAME} 已存在")
        
        connection.close()
        return True
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    create_database_if_not_exists()

