import requests
from typing import Dict, Optional
from config import Config

class ShopifyServiceError(Exception):
    """Base exception for Shopify service errors"""
    pass

class ShopifyService:
    SHOPIFY_STORE = Config.SHOPIFY_STORE
    SHOPIFY_ACCESS_TOKEN = Config.SHOPIFY_ACCESS_TOKEN
    API_VERSION = "2025-04" 
    BASE_URL = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/graphql.json"

    @classmethod
    def _make_request(cls, query: str, variables: Optional[Dict] = None) -> Dict:
        """Make a GraphQL request to Shopify API with error handling"""
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": cls.SHOPIFY_ACCESS_TOKEN
        }
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(cls.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                raise ShopifyServiceError(f"Shopify API errors: {data['errors']}")

            return data.get("data", {})
        except requests.exceptions.RequestException as e:
            raise ShopifyServiceError(f"Failed to make request to Shopify: {str(e)}")

    @classmethod
    def create_product(cls, data: Dict) -> Dict:
        """Create a new product in Shopify"""
        mutation = """
        mutation createProduct($input: ProductInput!) {
            productCreate(input: $input) {
                product {
                    id
                    title
                    variants(first: 1) {
                        edges {
                            node {
                                price
                                sku
                            }
                        }
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        
        result = cls._make_request(mutation, {"input": data})
        product_create = result.get("productCreate", {})
        
        if product_create.get("userErrors"):
            raise ShopifyServiceError(f"Product creation failed: {product_create['userErrors']}")
            
        return product_create.get("product")

    @classmethod
    def get_products(cls, first: int = 10, after: Optional[str] = None) -> Dict:
        """Get products from Shopify with pagination support"""
        query = """
        query getProducts($first: Int!, $after: String) {
            products(first: $first, after: $after) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                edges {
                    node {
                        id
                        title
                        variants(first: 1) {
                            edges {
                                node {
                                    price
                                    sku
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"first": first}
        if after:
            variables["after"] = after
            
        result = cls._make_request(query, variables)
        return result.get("products", {})