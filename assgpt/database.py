import sqlite3
from assgpt.config import DATABASE_PATH
import bcrypt
import logging
import json
import sqlite3
from rich.console import Console

console = Console()

class CommandDatabase:
    def __init__(self, db_path=DATABASE_PATH):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        try:
            cursor = self.conn.cursor()

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

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[red]无法创建表: {e}[/red]")
            logging.error(f"Create tables error: {e}")
            exit(1)

    def add_command_history(self, user_id, command):
        """
        将命令执行记录添加到命令历史表。
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO command_history (user_id, command) VALUES (?, ?)
            ''', (user_id, command))
            self.conn.commit()
            logging.info(f"用户ID {user_id} 执行命令: {command}")
        except sqlite3.Error as e:
            print(f"[red]无法记录命令历史: {e}[/red]")
            logging.error(f"Add command history error: {e}")


    def get_all_commands(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM commands WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

    def delete_command(self, user_id: int, command_id: int):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM commands WHERE id = ? AND user_id = ?', (command_id, user_id))
        self.conn.commit()

    def update_command(self, user_id, command_id, new_description, new_command, new_category_id=0):
        cursor = self.conn.cursor()
        
        cursor.execute('UPDATE commands SET description = ?, command = ?, category_id = ? WHERE id = ? AND user_id = ?', (new_description, new_command, new_category_id, command_id, user_id))

        self.conn.commit()

 

    def search_commands(self, user_id: int, keyword: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM commands
            WHERE user_id = ? AND (description LIKE ? OR command LIKE ?)
        ''', (user_id, f"%{keyword}%", f"%{keyword}%"))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
    
    def register_user(self, username, password):
        try:
            cursor = self.conn.cursor()
            # 哈希密码
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            self.conn.commit()
            logging.info(f"注册新用户: {username}")
            return True
        except sqlite3.IntegrityError:
            print("[red]用户名已存在，请选择其他用户名。[/red]")
            return False
        except sqlite3.Error as e:
            print(f"[red]无法注册用户: {e}[/red]")
            logging.error(f"Register user error: {e}")
            return False
    def authenticate_user(self, username, password):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, password FROM users WHERE username=?', (username,))
            result = cursor.fetchone()
            if result:
                user_id, hashed_password = result
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    logging.info(f"用户登录成功: {username}")
                    return user_id
                else:
                    print("[red]密码错误。[/red]")
                    return None
            else:
                print("[red]用户名不存在。[/red]")
                return None
        except sqlite3.Error as e:
            print(f"[red]无法验证用户: {e}[/red]")
            logging.error(f"Authenticate user error: {e}")
            return None
    def add_command(self, user_id, description, command, category_id=None):
        """
        将新命令添加到数据库。
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO commands (user_id, category_id, description, command)
                VALUES (?, ?, ?, ?)
            ''', (user_id, category_id, description, command))
            self.conn.commit()
            logging.info(f"用户ID {user_id} 添加命令: {description} -> {command}")
        except sqlite3.Error as e:
            print(f"[red]无法保存命令: {e}[/red]")
            logging.error(f"Add command error: {e}")
    def export_commands(self, user_id, file_path):
        """
        导出用户的命令到 JSON 文件。
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT commands.description, commands.command, categories.name
                FROM commands
                LEFT JOIN categories ON commands.category_id = categories.id
                WHERE commands.user_id=?
            ''', (user_id,))
            commands = cursor.fetchall()

            export_data = []
            for cmd in commands:
                export_data.append({
                    'description': cmd[0],
                    'command': cmd[1],
                    'category': cmd[2] if cmd[2] else "未分类"
                })

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            console.print(f"[green]命令已成功导出到 '{file_path}'。[/green]")
        except Exception as e:
            console.print(f"[red]无法导出命令: {e}[/red]")
    def import_commands(self, user_id, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            for cmd in import_data:
                description = cmd.get('description')
                command = cmd.get('command')
                category_name = cmd.get('category', "未分类")

                # 检查类别是否存在或添加新的类别
                cursor = self.conn.cursor()
                cursor.execute('SELECT id FROM categories WHERE name=?', (category_name,))
                result = cursor.fetchone()
                if result:
                    category_id = result[0]
                else:
                    cursor.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
                    category_id = cursor.lastrowid

                # 添加命令
                self.add_command(user_id, description, command, category_id)

            self.conn.commit()
            console.print(f"[green]命令已成功从 '{file_path}' 导入。[/green]")
            logging.info(f"用户ID {user_id} 从 '{file_path}' 导入命令。")
        except Exception as e:
            console.print(f"[red]无法导入命令: {e}[/red]")
            logging.error(f"Import commands error: {e}")


