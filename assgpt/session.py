import json
import os

class SessionManager:
    def __init__(self, session_file='session.json'):
        self._user_id = None
        self._username = None
        self._session_file = session_file
        self._load_session()

    def _load_session(self):
        if os.path.exists(self._session_file):
            with open(self._session_file, 'r') as file:
                data = json.load(file)
                self._user_id = data.get('user_id')
                self._username = data.get('username')

    def _save_session(self):
        with open(self._session_file, 'w') as file:
            json.dump({'user_id': self._user_id, 'username': self._username}, file)

    def login(self, db, username, password):
        from assgpt.auth import login  # 延迟导入以避免循环导入
        user_id, username = login(db, username, password)
        if user_id:
            self._user_id = user_id
            self._username = username
            self._save_session()
            print(f"欢迎回来，{username}！")
            return True
        else:
            print("登录失败，请检查用户名或密码。")
            return False

    def logout(self):
        self._user_id = None
        self._username = None
        self._save_session()
        print("您已退出登录。")

    def is_logged_in(self):
        return self._user_id is not None

    def get_user_id(self):
        return self._user_id

    def get_username(self):
        return self._username

