from abc import ABC
from datetime import datetime, timedelta
from typing import Optional

from alfred.constants import ResetPeriod
from alfred.redis_manager import RedisManager
from alfred.validations.base import BaseValidation


class BaseFeatureValidation(BaseValidation, ABC):
    def __init__(self, redis_manager: RedisManager, limit: int, expiration_func):
        super().__init__(redis_manager)
        self.redis_manager = redis_manager
        self.limit = limit
        self.expiration_func = expiration_func
        self.limit_reached_message = "FEATURE_REQUEST_LIMIT_REACHED"

    async def validate_request(self, user_id: str, org_id: Optional[str], rule_id: str) -> list:
        """
        Validate if the request is within the allowed limit.
        """
        current_count = await self.redis_manager.get_request_count(user_id, org_id, rule_id)
        if current_count >= self.limit:
            return [False, {}, self.limit_reached_message]
        return await self.redis_manager.increment_request_count(
            user_id=user_id, org_id=org_id, rule_id=rule_id, expiration=self.expiration_func()
        )

    @staticmethod
    def _validate_kwargs(kwargs):
        """
        Helper method to validate required `kwargs`.
        """
        required_keys = ["user_id", "org_id", "endpoint"]
        missing_keys = [key for key in required_keys if not kwargs.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required keys in kwargs: {', '.join(missing_keys)}")

    @staticmethod
    def get_expiration_function(reset_period: ResetPeriod):
        switcher = {
            ResetPeriod.HOURLY: BaseFeatureValidation.calculate_hour_expiration,
            ResetPeriod.DAILY: BaseFeatureValidation.calculate_day_expiration,
            ResetPeriod.MONTHLY: BaseFeatureValidation.calculate_month_expiration
        }
        return switcher.get(reset_period, BaseFeatureValidation.calculate_month_expiration)

    @staticmethod
    def calculate_month_expiration():
        """
        Calculate the expiration time in seconds for the current month.
        """
        now = datetime.now()
        first_of_next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        return int((first_of_next_month - now).total_seconds())

    @staticmethod
    def calculate_day_expiration():
        """
        Calculate the expiration time in seconds for the current day.
        """
        now = datetime.now()
        start_of_next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((start_of_next_day - now).total_seconds())

    @staticmethod
    def calculate_hour_expiration():
        """
        Calculate the expiration time in seconds for the current hour.
        """
        now = datetime.now()
        start_of_next_day = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return int((start_of_next_day - now).total_seconds())
