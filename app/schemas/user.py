# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user model with common fields"""

    id: str = Field(..., description="Unique identifier for the user")
    last_name: str = Field(..., description="User's last name")
    first_name: str = Field(..., description="User's first name")


class UserConfig(UserBase):
    """Configuration for a user"""

    pass


class UserResponse(UserBase):
    """Response model for user data"""

    pass
