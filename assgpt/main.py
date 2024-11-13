import argparse
import json
import os
from assgpt.auth import login, register
from assgpt.commands import (
    generate_command, view_commands, delete_command, update_command,
    search_commands, manage_categories, export_commands, import_commands, view_history
)
from assgpt.database import CommandDatabase
from assgpt.utils import setup_logging, reset_database
from assgpt.config import DATABASE_PATH
import logging

# 用户会话文件路径
SESSION_FILE = "user_session.json"

def load_session():
    """
    从会话文件中加载用户信息。
    """
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as file:
            return json.load(file)
    return None

def save_session(user_id, username):
    """
    保存用户信息到会话文件。
    """
    with open(SESSION_FILE, 'w') as file:
        json.dump({"user_id": user_id, "username": username}, file)

def clear_session():
    """
    清除会话文件。
    """
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def main():
    setup_logging()
    db = CommandDatabase(DATABASE_PATH)

    parser = argparse.ArgumentParser(description="Shell-GPT Command Line Tool")
    subparsers = parser.add_subparsers(dest="command", help="可用的命令")

    # 登录
    login_parser = subparsers.add_parser("login", help="用户登录")
    login_parser.add_argument("--username", required=True, help="用户名")
    login_parser.add_argument("--password", required=True, help="用户密码")

    # 登出
    subparsers.add_parser("logout", help="用户登出")

    # 注册
    register_parser = subparsers.add_parser("register", help="用户注册")
    register_parser.add_argument("--username", required=True, help="用户名")
    register_parser.add_argument("--password", required=True, help="用户密码")

    # 生成命令
    generate_parser = subparsers.add_parser("generate", help="生成Shell命令")
    generate_parser.add_argument("--description", required=True, help="命令描述")

    # 查看命令
    subparsers.add_parser("view", help="查看当前用户的已保存命令")

    # 删除命令
    delete_parser = subparsers.add_parser("delete", help="删除命令")
    delete_parser.add_argument("--command-id", required=True, type=int, help="命令ID")


    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索命令")
    search_parser.add_argument("--keyword", required=True, help="搜索关键词")

    # 重置数据库
    subparsers.add_parser("reset", help="重置数据库")

    # 导出命令
    export_parser = subparsers.add_parser("export", help="导出命令到文件")
    export_parser.add_argument("--file-path", required=True, help="导出文件路径")

    # 导入命令
    import_parser = subparsers.add_parser("import", help="从文件导入命令")
    import_parser.add_argument("--file-path", required=True, help="导入文件路径")

    args = parser.parse_args()

    # 加载会话
    session = load_session()

    if args.command == "login":
        user_id, username = login(db, args.username, args.password)
        if user_id:
            save_session(user_id, username)
            print(f"[green]欢迎回来，{username}！[/green]")
    elif args.command == "logout":
        clear_session()
        print("[green]已成功登出。[/green]")
    elif args.command == "register":
        register(db, args.username, args.password)
    else:
        if not session:
            print("[red]请先登录。[/red]")
            return

        user_id = session["user_id"]
        username = session["username"]

        if args.command == "generate":
            generate_command(db, user_id, args.description)
        elif args.command == "view":
            view_commands(db, user_id)
        elif args.command == "delete":
            delete_command(db, user_id, args.command_id)
        elif args.command == "search":
            search_commands(db, user_id, args.keyword)
        elif args.command == "reset":
            reset_database()
        elif args.command == "export":
            export_commands(db, user_id, args.file_path)
        elif args.command == "import":
            import_commands(db, user_id, args.file_path)

if __name__ == '__main__':
    main()

