from alfred.redis_manager import RedisManager
from alfred.validations.free_plan.model_validation import FreePlanModelValidation
from alfred.validations.premium_plan.model_validation import PremiumPlanModelValidation


class ValidatorFactory:
    """
    Factory to initialize RedisManager and load validator instances based on a name-to-class mapping.
    """

    VALIDATOR_MAPPER = {
        "FreePlanModelValidation": FreePlanModelValidation,
        "PremiumPlanModelValidation": PremiumPlanModelValidation,
    }

    def __init__(self, redis_url: str):
        """
        Initialize the ValidatorFactory with a Redis URL.
        """
        self.redis_manager = RedisManager(redis_url)

    def load_validator(self, validator_name: str):
        """
        Load a validator instance based on its name.

        Args:
            validator_name (str): Name of the validator class.

        Returns:
            BaseValidation: An instance of the specified validator class.

        Raises:
            ValueError: If the validator name is not found in the mapper.
        """
        if validator_name not in self.VALIDATOR_MAPPER:
            raise ValueError(f"Validator '{validator_name}' is not recognized.")

        validator_class = self.VALIDATOR_MAPPER[validator_name]
        return validator_class(self.redis_manager)