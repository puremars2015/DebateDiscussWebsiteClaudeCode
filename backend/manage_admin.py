"""
管理員帳號管理工具

使用方法：
1. 確保已經透過 Line Login 登入過，在資料庫中有使用者記錄
2. 執行此腳本來設置或移除管理員權限

python manage_admin.py --list                    # 列出所有使用者
python manage_admin.py --set-admin USER_ID       # 設置使用者為管理員
python manage_admin.py --remove-admin USER_ID    # 移除管理員權限
python manage_admin.py --set-admin-by-line LINE_ID  # 透過 LINE ID 設置管理員
"""

import sys
import os
import argparse

# 添加父目錄到路徑，以便導入 config 和 database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from app.utils.database import db


def list_users():
    """列出所有使用者"""
    users = db.execute_query(
        """
        SELECT user_id, line_id, nickname, rating, is_admin, created_at
        FROM Users
        ORDER BY created_at DESC
        """,
        fetch_all=True
    )
    
    if not users:
        print("❌ 沒有找到任何使用者")
        return
    
    print("\n📋 使用者列表:")
    print("-" * 100)
    print(f"{'ID':<5} {'LINE ID':<20} {'暱稱':<20} {'Rating':<8} {'管理員':<8} {'建立時間':<20}")
    print("-" * 100)
    
    for user in users:
        is_admin_text = "✅ 是" if user['is_admin'] else "❌ 否"
        created = user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if user['created_at'] else 'N/A'
        print(f"{user['user_id']:<5} {user['line_id']:<20} {user['nickname']:<20} {user['rating']:<8} {is_admin_text:<8} {created:<20}")
    
    print("-" * 100)
    print(f"總共 {len(users)} 位使用者")


def set_admin(user_id, is_admin=True):
    """設置使用者管理員權限"""
    # 檢查使用者是否存在
    user = db.execute_query(
        "SELECT user_id, nickname, is_admin FROM Users WHERE user_id = ?",
        (user_id,),
        fetch_one=True
    )
    
    if not user:
        print(f"❌ 找不到 ID 為 {user_id} 的使用者")
        return False
    
    # 更新管理員狀態
    db.execute_query(
        "UPDATE Users SET is_admin = ? WHERE user_id = ?",
        (1 if is_admin else 0, user_id)
    )
    
    action = "設置為管理員" if is_admin else "移除管理員權限"
    print(f"✅ 成功將使用者 '{user['nickname']}' (ID: {user_id}) {action}")
    return True


def set_admin_by_line_id(line_id, is_admin=True):
    """透過 LINE ID 設置管理員權限"""
    user = db.execute_query(
        "SELECT user_id, nickname, is_admin FROM Users WHERE line_id = ?",
        (line_id,),
        fetch_one=True
    )
    
    if not user:
        print(f"❌ 找不到 LINE ID 為 {line_id} 的使用者")
        return False
    
    return set_admin(user['user_id'], is_admin)


def main():
    parser = argparse.ArgumentParser(description='辯論平台管理員管理工具')
    parser.add_argument('--list', action='store_true', help='列出所有使用者')
    parser.add_argument('--set-admin', type=int, metavar='USER_ID', help='設置使用者為管理員')
    parser.add_argument('--remove-admin', type=int, metavar='USER_ID', help='移除使用者的管理員權限')
    parser.add_argument('--set-admin-by-line', type=str, metavar='LINE_ID', help='透過 LINE ID 設置管理員')
    parser.add_argument('--remove-admin-by-line', type=str, metavar='LINE_ID', help='透過 LINE ID 移除管理員權限')
    
    args = parser.parse_args()
    
    # 如果沒有參數，顯示幫助訊息
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "=" * 60)
        print("快速開始:")
        print("1. 先列出所有使用者: python manage_admin.py --list")
        print("2. 設置管理員: python manage_admin.py --set-admin USER_ID")
        print("=" * 60)
        return
    
    try:
        if args.list:
            list_users()
        elif args.set_admin:
            set_admin(args.set_admin, True)
        elif args.remove_admin:
            set_admin(args.remove_admin, False)
        elif args.set_admin_by_line:
            set_admin_by_line_id(args.set_admin_by_line, True)
        elif args.remove_admin_by_line:
            set_admin_by_line_id(args.remove_admin_by_line, False)
            
    except Exception as e:
        print(f"❌ 發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()