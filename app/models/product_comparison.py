from pydantic import BaseModel

class ProductComparison(BaseModel):
    brief_comparison_title: str
    product1: str
    product2: str
    pros_product1: list[str]
    pros_product2: list[str]
    cons_product1: list[str]
    cons_product2: list[str]
    comparison_summary: str