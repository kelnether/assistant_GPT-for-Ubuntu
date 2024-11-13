import openai
from rich import print
import logging

def get_shell_command(prompt):
    """
    使用OpenAI的GPT模型将自然语言描述转换为Shell命令。
    """
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': f'将以下描述转换为 Linux 命令：{prompt}'}],
            temperature=0,
            timeout=30
        )
        command = response.choices[0].message.content.strip()
        logging.info(f"Generated command for prompt '{prompt}': {command}")
        return command
    except openai.OpenAIError as e:
        print(f"[red]OpenAI API 调用失败: {e}[/red]")
        logging.error(f"OpenAI API error: {e}")
        raise
        
from rich.table import Table
from rich.console import Console

console = Console()

def display_commands(commands):
    """
    使用rich库显示命令列表。
    """
    if not commands:
        console.print("[yellow]暂无已保存的命令。[/yellow]")
        return
    table = Table(title="已保存的命令")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("类别", style="magenta")
    table.add_column("描述", style="magenta")
    table.add_column("命令", style="green")
    
    for cmd in commands:
        category = str(cmd[1]) if cmd[1] else "未分类"  # 确保类别也转换为字符串
        table.add_row(str(cmd[0]), category, str(cmd[2]), str(cmd[3]))
        
    console.print(table)


def display_categories(categories):
    if not categories:
        print("[yellow]暂无类别。[/yellow]")
        return
    table = Table(title="命令类别")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("名称", style="magenta")
    for cat in categories:
        table.add_row(str(cat[0]), cat[1])
    print(table)

def display_command_history(history):
    if not history:
        print("[yellow]暂无命令历史记录。[/yellow]")
        return
    table = Table(title="命令历史记录")
    table.add_column("命令", style="green")
    table.add_column("执行时间", style="cyan")
    for record in history:
        table.add_row(record[0], record[1])
    print(table)

def setup_logging():
    logging.basicConfig(
        filename='command_tool.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

import os
import sqlite3
from rich.prompt import Confirm
from assgpt.config import DATABASE_PATH

def reset_database(db_path=DATABASE_PATH):
    """
    重置数据库：删除现有数据库文件并创建新的数据库表结构。
    """
    if os.path.exists(db_path):
        print(f"[yellow]检测到现有的数据库文件 '{db_path}'。[/yellow]")
        if Confirm.ask("您确定要删除并重置数据库吗？此操作将删除所有已保存的数据。", default=False):
            try:
                os.remove(db_path)
                print(f"[green]成功删除数据库文件 '{db_path}'。[/green]")
            except Exception as e:
                print(f"[red]无法删除数据库文件: {e}[/red]")
                return
        else:
            print("[cyan]取消数据库重置操作。[/cyan]")
            return
    else:
        print(f"[yellow]未检测到数据库文件 '{db_path}'，将创建一个新的数据库。[/yellow]")

    # 这里重新初始化数据库
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # 创建类别表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        # 创建命令表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER,
                description TEXT NOT NULL,
                command TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')

        # 创建命令历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()
        print(f"[green]成功创建新的数据库表 'users', 'categories', 'commands' 和 'command_history'。[/green]")
    except sqlite3.Error as e:
        print(f"[red]无法创建数据库表: {e}[/red]")
