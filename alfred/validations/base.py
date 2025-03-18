from abc import ABC, abstractmethod
from alfred.redis_manager import RedisManager


class BaseValidation(ABC):
    """
    Abstract base class for validations.
    All validation classes must inherit from this class and implement the `validate` method.
    """
    def __init__(self, redis_manager: RedisManager):
        """
        Initialize the base validation class.

        :param redis_manager: Instance of RedisManager for Redis operations.
        """
        self.redis_manager = redis_manager
        self.success_message = "SUCCESS"

    @abstractmethod
    def validate(self, *args, **kwargs):
        """
        Abstract method to be implemented by subclasses for specific validation logic.

        :param args: Positional arguments for validation.
        :param kwargs: Keyword arguments for validation.
        :raises ValidationError: If validation fails.
        """
        pass

    async def get_usage_count(self, user_id: str, rule_id: str) -> int:
        """
        Retrieve the usage count for a specific user and rule from Redis.

        :param user_id: Unique identifier for the user.
        :param rule_id: Unique identifier for the rule.
        :return: Current usage count.
        """
        return await self.redis_manager.get_request_count(user_id, rule_id)

    async def increment_usage(self, user_id: str, rule_id: str) -> int:
        """
        Increment the usage count for a specific user and rule in Redis.

        :param user_id: Unique identifier for the user.
        :param rule_id: Unique identifier for the rule.
        :return: Updated usage count.
        """
        return await self.redis_manager.increment_request_count(user_id, rule_id)

    async def reset_usage(self, user_id: str, rule_id: str):
        """
        Reset the usage count for a specific user and rule in Redis.

        :param user_id: Unique identifier for the user.
        :param rule_id: Unique identifier for the rule.
        """
        await self.redis_manager.reset_request_count(user_id, rule_id)

    def _extract_condition_endpoints(condition_data):
        """Extract and return the allowed API endpoints from condition data."""
        condition_endpoints = condition_data.get("condition_endpoints", "[]")
        return eval(condition_endpoints)