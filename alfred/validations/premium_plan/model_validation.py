from alfred.redis_manager import RedisManager
from alfred.validations.base_model_validation import BaseModelValidation


class ModelValidation(BaseModelValidation):
    def __init__(self, redis_manager: RedisManager):
        super().__init__(
            redis_manager=redis_manager,
            limit=None,
            expiration_func=None
        )
        self.standard_models = {"gpt-4o", "gpt-4o-mini"}
        self.premium_models = {"o1-preview", "o1-mini", "Claude 3.5 Sonnet", "3 Opus"}

    async def validate(self, model, user_id: int, org_id: int, rule_id: str) -> bool:
        """
        Validate if the request is within the allowed limits for standard or premium models.
        """
        if model in self.standard_models:
            self.limit = 500
            self.expiration_func = self.calculate_month_expiration
        elif model in self.premium_models:
            self.limit = 10
            self.expiration_func = self.calculate_day_expiration
        else:
            return False

        return await self.validate_request(user_id, org_id, rule_id)
