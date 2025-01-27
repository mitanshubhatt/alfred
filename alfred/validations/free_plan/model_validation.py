from alfred.redis_manager import RedisManager
from alfred.validations.base_model_validation import BaseModelValidation


class FreePlanModelValidation(BaseModelValidation):
    def __init__(self, redis_manager: RedisManager):
        super().__init__(
            redis_manager=redis_manager,
            limit=200,
            expiration_func=self.calculate_month_expiration
        )
        self.allowed_models = {"gpt-4o", "gpt-4o-mini"}

    async def validate(self, model, user_id: int, org_id: int, rule_id: str) -> list:
        """
        Validate if the request is within the allowed limit for the model.
        """
        if model not in self.allowed_models:
            return [False, {}]
        return await self.validate_request(user_id, org_id, rule_id)
