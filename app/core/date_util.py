# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from datetime import date, datetime
from zoneinfo import ZoneInfo


class DateUtil:
    DEFAULT_TIMEZONE = ZoneInfo("Asia/Tokyo")

    @classmethod
    def today(cls) -> date:
        """
        Returns today's date with timezone awareness.
        """
        return datetime.now(cls.DEFAULT_TIMEZONE).date()

    @classmethod
    def now(cls) -> datetime:
        """
        Returns the current datetime with timezone awareness.
        """
        return datetime.now(cls.DEFAULT_TIMEZONE)
