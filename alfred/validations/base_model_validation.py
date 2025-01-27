from abc import ABC

from alfred.validations.base import BaseValidation
from alfred.redis_manager import RedisManager
from datetime import datetime, timedelta


class BaseModelValidation(BaseValidation, ABC):
    def __init__(self, redis_manager: RedisManager, limit: int, expiration_func):
        super().__init__(redis_manager)
        self.redis_manager = redis_manager
        self.limit = limit
        self.expiration_func = expiration_func

    async def validate_request(self, user_id: int, org_id: int, rule_id: str) -> bool:
        """
        Validate if the request is within the allowed limit.
        """
        current_count = await self.redis_manager.get_request_count(user_id, org_id, rule_id)
        if current_count >= self.limit:
            return False

        await self.redis_manager.increment_request_count(
            user_id=user_id, org_id=org_id, rule_id=rule_id, expiration=self.expiration_func()
        )
        return True

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
