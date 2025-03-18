import json

from alfred.redis_manager import RedisManager
from alfred.validations.base_model_validation import BaseModelValidation


class PremiumPlanModelValidation(BaseModelValidation):
    def __init__(self, redis_manager: RedisManager, rule_id, condition_data, **kwargs):
        super().__init__(
            redis_manager=redis_manager,
            limit=None,
            expiration_func=None
        )
        self.kwargs = kwargs
        self.rule_id = rule_id
        self.standard_models = json.loads(condition_data["allowed_standard_models"])
        self.premium_models = json.loads(condition_data["allowed_premium_models"])
        self.premium_models_limit = int(condition_data["premium_models_limit"])
        self.standard_models_limit = int(condition_data["standard_models_limit"])
        self.premium_limit_time_period = condition_data["premium_limit_time_period"]
        self.standard_limit_time_period = condition_data["standard_limit_time_period"]
        self.condition_endpoints = self._extract_condition_endpoints(condition_data)
        self.error_message = "MODEL_NOT_ALLOWED"


    async def validate(self) -> list:
        """
        Validate if the request is within the allowed limits for standard or premium models.
        """
        if self.kwargs.get("endpoint") not in self.restricted_endpoints:
            return [True, {}, self.success_message]
        
        self._validate_kwargs(self.kwargs)
        model = self.kwargs.get("model_used")
        user_id = self.kwargs.get("user_id")
        org_id = self.kwargs.get("org_id")
        time_period_mapper = {
            "monthly": self.calculate_month_expiration,
            "daily": self.calculate_month_expiration
        }
        if model in self.standard_models:
            self.limit = self.standard_models_limit
            self.expiration_func = time_period_mapper[self.standard_limit_time_period]
        elif model in self.premium_models:
            self.limit = self.premium_models_limit
            self.expiration_func = time_period_mapper[self.premium_limit_time_period]
        else:
            return [False, {}, self.error_message]

        return await self.validate_request(user_id, org_id, self.rule_id)
