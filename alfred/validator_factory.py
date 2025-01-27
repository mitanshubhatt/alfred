import importlib
import os
from alfred.redis_manager import RedisManager


class ValidatorFactory:
    """
    Factory to initialize RedisManager and dynamically load validator instances
    based on the 'rule_class_name' field in the rule JSON.
    """

    def __init__(self, redis_url: str):
        """
        Initialize the ValidatorFactory with a Redis URL.
        """
        self.redis_manager = RedisManager(redis_url)

    @staticmethod
    def _find_class_in_module(module_name, class_name):
        """
        Import a module and return a class by name.

        Args:
            module_name (str): The module to import.
            class_name (str): The name of the class to find.

        Returns:
            type: The class object if found.

        Raises:
            ValueError: If the class is not found in the module.
        """
        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            return getattr(module, class_name)
        raise ValueError(f"Class '{class_name}' not found in module '{module_name}'.")

    def _get_validator_class(self, rule_class_name):
        """
        Dynamically find the validator class based on the 'rule_class_name'.

        Args:
            rule_class_name (str): Name of the rule class to load.

        Returns:
            type: The class object corresponding to the rule_class_name.

        Raises:
            ValueError: If the class cannot be found in the specified folders.
        """
        validator_folders = [
            "alfred.validations.free_plan",
            "alfred.validations.premium_plan",
        ]

        for folder in validator_folders:
            folder_path = folder.replace(".", "/")
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith(".py") and file != "__init__.py":
                        module_name = f"{folder}.{file[:-3]}"
                        try:
                            return self._find_class_in_module(module_name, rule_class_name)
                        except ValueError:
                            continue

        raise ValueError(
            f"Validator class '{rule_class_name}' not found in any of the specified folders."
        )

    def load_validator(self, rule_json: dict, **kwargs):
        """
        Load a validator instance based on the 'rule_class_name' in the rule JSON.

        Args:
            rule_json (dict): Rule JSON containing the 'rule_class_name'.

        Returns:
            BaseValidation: An instance of the specified validator class.

        Raises:
            ValueError: If 'rule_class_name' is missing or the class cannot be loaded.
        """
        if "rule_class_name" not in rule_json:
            raise ValueError("The rule JSON must contain a 'rule_class_name' field.")

        rule_class_name = rule_json["rule_class_name"]
        validator_class = self._get_validator_class(rule_class_name)
        return validator_class(self.redis_manager, rule_json["id"], rule_json["condition_data"], **kwargs)
