from subprocess import run, CalledProcessError
from rich import print
from rich.prompt import Prompt, Confirm
from assgpt.database import CommandDatabase
from assgpt.utils import get_shell_command, display_commands, display_categories, display_command_history
import subprocess
from rich.console import Console
import json
import logging
console = Console()





def generate_command(db: CommandDatabase, user_id: int, description: str):
    command = get_shell_command(description)
    print(f"[green]生成的命令: {command}[/green]")
    if Confirm.ask("是否立即执行该命令？"):
        try:
            subprocess.run(command, shell=True, check=True)
            print("[green]命令执行成功。[/green]")
            db.add_command_history(user_id, command)
        except subprocess.CalledProcessError as e:
            print(f"[red]命令执行失败：{e}[/red]")
    if Confirm.ask("是否保存该命令？"):
        db.add_command(user_id, description, command)

def view_commands(db: CommandDatabase, user_id: int):
    commands = db.get_all_commands(user_id)
    display_commands(commands)

def delete_command(db: CommandDatabase, user_id: int, command_id: int):
    db.delete_command(user_id, command_id)

def update_command(db, user_id, command_id, new_description, new_command, new_category_id=None):
    try:
        cursor = db.conn.cursor()
        cursor.execute('''
            UPDATE commands
            SET description = ?, command = ?, category_id = ?
            WHERE id = ? AND user_id = ?
        ''', (new_description, new_command, new_category_id, command_id, user_id))
        db.conn.commit()
        
        if cursor.rowcount:
            logging.info(f"用户ID {user_id} 成功更新命令ID {command_id}")
            console.print(f"[green]命令 ID {command_id} 已更新。[/green]")
        else:
            logging.warning(f"未找到命令 ID {command_id} 或不属于用户 ID {user_id}")
            console.print(f"[yellow]未找到命令 ID {command_id} 或此命令不属于用户。[/yellow]")
    except sqlite3.Error as e:
        console.print(f"[red]更新命令失败: {e}[/red]")
        logging.error(f"Update command error: {e}")
        
def search_commands(db: CommandDatabase, user_id: int, keyword: str):
    results = db.search_commands(user_id, keyword)
    display_commands(results)

def manage_categories(db: CommandDatabase, user_id: int):
    while True:
        print("\n[bold cyan]类别管理[/bold cyan]")
        print("1. 添加新类别")
        print("2. 查看所有类别")
        print("3. 删除类别")
        print("4. 返回主菜单")
        choice = Prompt.ask("请输入选项编号", choices=['1', '2', '3', '4'])

        if choice == '1':
            category_name = Prompt.ask("请输入新类别名称")
            db.add_category(category_name)
        elif choice == '2':
            categories = db.get_all_categories()
            display_categories(categories)
        elif choice == '3':
            categories = db.get_all_categories()
            display_categories(categories)
            del_id = Prompt.ask("请输入要删除的类别 ID，或按 Enter 返回", default='')
            if del_id.isdigit():
                db.delete_category(int(del_id))
        elif choice == '4':
            break

def export_commands(db: CommandDatabase, user_id: int):
    file_path = Prompt.ask("请输入导出文件的路径", default="commands_export.json")
    db.export_commands(user_id, file_path)

def import_commands(db: CommandDatabase, user_id: int):
    file_path = Prompt.ask("请输入要导入的文件路径")
    db.import_commands(user_id, file_path)

def view_history(db: CommandDatabase, user_id: int):
    history = db.get_command_history(user_id)
    display_command_history(history)

def export_commands(db, user_id, file_path):
    try:
        db.export_commands(user_id, file_path)
        console.print(f"[green]命令已成功导出到 '{file_path}'。[/green]")
    except Exception as e:
        console.print(f"[red]导出命令失败: {e}[/red]")
        logging.error(f"Export commands error: {e}")

def import_commands(db, user_id, file_path):
    try:
        db.import_commands(user_id, file_path)
        console.print(f"[green]命令已成功从 '{file_path}' 导入。[/green]")
    except Exception as e:
        console.print(f"[red]导入命令失败: {e}[/red]")
        logging.error(f"Import commands error: {e}")

