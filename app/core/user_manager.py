# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from functools import lru_cache
from typing import Dict, List, Tuple
from app.core.config import get_settings
from app.schemas.user import UserConfig


class UserManager:
    def __init__(self):
        self.settings = get_settings()
        self.users: Dict[str, UserConfig] = self._load_users_from_env()

    def _load_users_from_env(self) -> Dict[str, UserConfig]:
        users: Dict[str, UserConfig] = {}
        i = 1
        while True:
            id = self.settings.get_user_env(i, "ID")
            display_name = self.settings.get_user_env(i, "DISPLAY_NAME")
            required_values = [
                id,
                display_name,
            ]

            if not all(required_values):
                break

            users[str(i)] = UserConfig(id=str(i), display_name=display_name)
            i += 1
        return users

    def get_user(self, user_id: str) -> UserConfig:
        user = self.users.get(user_id)
        if user is None:
            raise KeyError(f"User with user_id '{user_id}' not found.")
        return user

    def get_all_users(self) -> List[Tuple[str, str]]:
        return [(id, config.id) for id, config in self.users.items()]


@lru_cache()
def get_user_manager() -> UserManager:
    return UserManager()
