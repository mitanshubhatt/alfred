import json

from alfred.redis_manager import RedisManager
from alfred.validations.base_model_validation import BaseModelValidation


class FreePlanModelValidation(BaseModelValidation):
    def __init__(self, redis_manager: RedisManager, rule_id, condition_data, **kwargs):
        super().__init__(
            redis_manager=redis_manager,
            limit=int(condition_data["request_limit"]),
            expiration_func=self.calculate_month_expiration
        )
        self.allowed_models = json.loads(condition_data["allowed_models"])
        self.rule_id = rule_id
        self.kwargs = kwargs

    async def validate(self) -> list:
        """
        Validate if the request is within the allowed limit for the model.
        """
        self._validate_kwargs(self.kwargs)
        model = self.kwargs.get("model_used")
        if model not in self.allowed_models:
            return [False, {}]
        user_id = self.kwargs.get("user_id")
        org_id = self.kwargs.get("org_id")
        return await self.validate_request(user_id, org_id, self.rule_id)
