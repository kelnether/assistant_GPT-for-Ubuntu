import bcrypt
from rich import print
from rich.prompt import Prompt
from assgpt.database import CommandDatabase

def login(db, username, password):
    user_id = db.authenticate_user(username, password)
    if user_id:
        print(f"[green]欢迎回来，{username}！[/green]")
        return user_id, username
    else:
        print(f"[red]登录失败。[/red]")
        return None, None

def register(db, username, password):
    if db.register_user(username, password):
        print(f"[green]用户 '{username}' 注册成功。[/green]")
    else:
        print(f"[red]用户 '{username}' 注册失败。[/red]")

def logout():
    # 清除当前用户会话信息
    print("已登出")

