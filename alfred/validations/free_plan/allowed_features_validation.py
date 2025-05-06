import json
from alfred.redis_manager import RedisManager
from alfred.validations.base_feature_validation import BaseFeatureValidation


class FreePlanRestrictedEndpoints(BaseFeatureValidation):
    def __init__(self, redis_manager: RedisManager, rule_id, condition_data, **kwargs):
        super().__init__(
            redis_manager=redis_manager,
            limit=self._extract_request_limit(condition_data),
            expiration_func=self.get_expiration_function(condition_data.get("reset_period"))
        )
        self.condition_endpoints = self._extract_condition_endpoints(condition_data)
        self.rule_id = rule_id
        self.kwargs = kwargs
        self.error_message = "FEATURE_RESTRICTED"

    @staticmethod
    def _extract_request_limit(condition_data):
        """Extract and return the request limit from condition data."""
        return int(condition_data.get("request_limit", 0))

    async def validate(self) -> list:
        """
        Validate if the request is within the allowed limit for the feature and endpoint.
        """
        self._validate_kwargs(self.kwargs)
        endpoint = self.kwargs.get("endpoint")
        
        if self._is_endpoint_restricted(endpoint):
            return [False, {}, self.error_message]
        
        return [True, {}, self.success_message]
    
    def _is_endpoint_restricted(self, endpoint):
        """Check if the endpoint is in the list of restricted API endpoints."""
        return endpoint in self.condition_endpoints
