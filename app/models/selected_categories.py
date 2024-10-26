from typing import List

class SelectedCategories:
    VALID_CATEGORIES = ["Price", "Model", "Condition", "Features", "Estimated Delivery"]

    @classmethod
    def validate_categories(cls, categories: List[str]) -> List[str]:
        """
        Validates the selected categories by checking if they are in the predefined VALID_CATEGORIES list.
        Raises a ValueError if any invalid categories are found.
        """
        invalid = [category for category in categories if category not in cls.VALID_CATEGORIES]
        if invalid:
            raise ValueError(f"Invalid categories: {invalid}")
        return categories

    @classmethod
    def get_default_categories(cls) -> List[str]:
        """
        Returns a list of default categories to compare products when no specific categories are provided.
        """
        return cls.VALID_CATEGORIES