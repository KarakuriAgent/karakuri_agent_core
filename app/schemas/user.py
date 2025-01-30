# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from pydantic import BaseModel


class UserConfig(BaseModel):
    id: str
    last_name: str
    first_name: str


class UserResponse(BaseModel):
    user_id: str
    last_name: str
    first_name: str
