import json
from alfred.redis_manager import RedisManager
from alfred.validations.base_model_validation import BaseModelValidation


class FreePlanModelValidation(BaseModelValidation):
    def __init__(self, redis_manager: RedisManager, rule_id, condition_data, **kwargs):
        super().__init__(
            redis_manager=redis_manager,
            limit=self._extract_request_limit(condition_data),
            expiration_func=self.calculate_month_expiration
        )
        self.allowed_models = self._extract_allowed_models(condition_data)
        self.condition_endpoints = self._extract_condition_endpoints(condition_data)
        self.rule_id = rule_id
        self.kwargs = kwargs
        self.error_message = "MODEL_NOT_ALLOWED"

    @staticmethod
    def _extract_request_limit(condition_data):
        """Extract and return the request limit from condition data."""
        return int(condition_data.get("request_limit", 0))

    @staticmethod
    def _extract_allowed_models(condition_data):
        """Extract and return the allowed models from condition data."""
        allowed_models_json = condition_data.get("allowed_models", [])
        return allowed_models_json

    async def validate(self) -> list:
        """
        Validate if the request is within the allowed limit for the model.
        """
        if self.kwargs.get("endpoint") not in self.condition_endpoints:
            return [True, {}, self.success_message]
        
        self._validate_kwargs(self.kwargs)
        model = self.kwargs.get("model_used")
        if not self._is_model_allowed(model):
            return [False, {}, self.error_message]
        
        user_id = self.kwargs.get("user_id")
        org_id = self.kwargs.get("org_id")
        return await self.validate_request(user_id, org_id, self.rule_id)

    def _is_model_allowed(self, model):
        """Check if the model is in the list of allowed models."""
        return model in self.allowed_models
