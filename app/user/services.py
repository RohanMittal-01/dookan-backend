import requests
from typing import Dict, Optional
from config import Config
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shopify_api.log'),
        logging.StreamHandler()
    ]
)

class ShopifyServiceError(Exception):
    """Base exception for Shopify service errors"""
    pass

class ShopifyService:
    SHOPIFY_STORE = Config.SHOPIFY_STORE
    SHOPIFY_ACCESS_TOKEN = Config.SHOPIFY_ACCESS_TOKEN
    API_VERSION = "2025-04" 
    BASE_URL = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/graphql.json"

    @classmethod
    def _log_request(cls, method: str, query: str, variables: Optional[Dict] = None, response: Optional[Dict] = None, error: Optional[str] = None):
        """Log Shopify API request details"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "query": query,
            "variables": json.dumps(variables, indent=2) if variables else None,
            "response": json.dumps(response, indent=2) if response else None,
            "error": error
        }
        
        if error:
            logging.error(f"Shopify API Error: {json.dumps(log_data, indent=2)}")
        else:
            logging.info(f"Shopify API Request: {json.dumps(log_data, indent=2)}")

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
                cls._log_request("POST", query, variables, None, str(data["errors"]))
                raise ShopifyServiceError(f"Shopify API errors: {data['errors']}")

            cls._log_request("POST", query, variables, data)
            return data.get("data", {})
        except requests.exceptions.RequestException as e:
            cls._log_request("POST", query, variables, None, str(e))
            raise ShopifyServiceError(f"Failed to make request to Shopify: {str(e)}")

    @classmethod
    def create_product(cls, data: Dict) -> Dict:
        """Create a new product in Shopify"""
        # Log the incoming data
        logging.info(f"Creating product with data: {json.dumps(data, indent=2)}")

        mutation = """
        mutation productCreate($product: ProductCreateInput!) {
            productCreate(product: $product) {
                product {
                    id
                    title
                    options {
                        id
                        name
                        position
                        optionValues {
                            id
                            name
                            hasVariants
                        }
                    }
                    media(first: 10) {
                        edges {
                            node {
                                id
                                alt
                                preview {
                                    image {
                                        url
                                    }
                                }
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
        
        # Transform the input data to match Shopify's expected format
        shopify_product = {
            "title": data.get("title", "").strip(),
            "productOptions": [
                {
                    "name": option.get("name"),
                    "values": [
                        {"name": value.get("name")}
                        for value in option.get("values", [])
                    ]
                }
                for option in data.get("options", [])
            ]
        }

        # Add media if provided
        if "images" in data and data["images"]:
            shopify_product["media"] = [
                {
                    "alt": image.get("altText", ""),
                    "originalSource": image.get("src")
                }
                for image in data["images"]
            ]
        
        # Log the transformed data
        logging.info(f"Transformed Shopify product data: {json.dumps(shopify_product, indent=2)}")
        
        result = cls._make_request(mutation, {"product": shopify_product})
        product_create = result.get("productCreate", {})
        
        if product_create.get("userErrors"):
            raise ShopifyServiceError(f"Product creation failed: {product_create['userErrors']}")
            
        return product_create.get("product")

    @classmethod
    def delete_product(cls, product_id: str) -> bool:
        """Delete a product from Shopify"""
        # Convert numeric ID to full Shopify ID if needed
        if product_id.isdigit():
            product_id = f"gid://shopify/Product/{product_id}"

        mutation = """
        mutation productDelete($input: ProductDeleteInput!) {
            productDelete(input: $input) {
                deletedProductId
                userErrors {
                    field
                    message
                }
            }
        }
        """
        
        variables = {
            "input": {
                "id": product_id
            }
        }
        
        result = cls._make_request(mutation, variables)
        product_delete = result.get("productDelete", {})
        
        if product_delete.get("userErrors"):
            raise ShopifyServiceError(f"Product deletion failed: {product_delete['userErrors']}")
            
        return bool(product_delete.get("deletedProductId"))

    @classmethod
    def create_variant(cls, product_id: str, variant_data: Dict) -> Dict:
        """Create a variant for a product"""
        mutation = """
        mutation productVariantCreate($input: ProductVariantInput!) {
            productVariantCreate(input: $input) {
                productVariant {
                    id
                    price
                    sku
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        
        variant_input = {
            "productId": product_id,
            "price": variant_data.get("price"),
            "sku": variant_data.get("sku"),
            "option1": variant_data.get("option1", "Default Title")
        }
        
        result = cls._make_request(mutation, {"input": variant_input})
        variant_create = result.get("productVariantCreate", {})
        
        if variant_create.get("userErrors"):
            raise ShopifyServiceError(f"Variant creation failed: {variant_create['userErrors']}")
            
        return variant_create.get("productVariant")

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
                        options {
                            id
                            name
                            position
                            optionValues {
                                id
                                name
                                hasVariants
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
        return result.get("products", {})