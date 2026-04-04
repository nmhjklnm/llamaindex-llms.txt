# Ionic shopping
##  IonicShoppingToolSpec #
Bases: `BaseToolSpec`
Ionic Shopping tool spec.
This tool can be used to build e-commerce experiences with LLMs.
Source code in `llama-index-integrations/tools/llama-index-tools-ionic-shopping/llama_index/tools/ionic_shopping/base.py`

| ```
class IonicShoppingToolSpec(BaseToolSpec):
    """
    Ionic Shopping tool spec.

    This tool can be used to build e-commerce experiences with LLMs.
    """

    spec_functions = ["query"]

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Ionic API Key.

        Learn more about attribution with Ionic API Keys
        https://docs.ioniccommerce.com/guides/attribution
        """
        from ionic import Ionic as IonicSDK

        if api_key:
            self.client = IonicSDK(api_key_header=api_key)
        else:
            self.client = IonicSDK()

    def query(
        self,
        query: str,
        num_results: Optional[int] = 5,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
    ) -> list[Product]:
        """
        Use this function to search for products and to get product recommendations.

        Args:
            query (str): A precise query of a product name or product category
            num_results (Optional[int]): Defaults to 5. The number of product results to return.
            min_price (Option[int]): The minimum price in cents the requester is willing to pay
            max_price (Option[int]): The maximum price in cents the requester is willing to pay

        """
        request = QueryAPIRequest(
            query=SDKQuery(
                query=query,
                num_results=num_results,
                min_price=min_price,
                max_price=max_price,
            )
        )
        response: QueryResponse = self.client.query(
            request=request,
            security=QuerySecurity(),
        )

        return [
            product
            for result in response.query_api_response.results
            for product in result.products
        ]

```
  
---|---  
###  query #
```
query(query: str, num_results: Optional[int] = 5, min_price: Optional[int] = None, max_price: Optional[int] = None) -> list[Product]

```

Use this function to search for products and to get product recommendations.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  A precise query of a product name or product category |  _required_  
`num_results` |  `Optional[int]` |  Defaults to 5. The number of product results to return. |  `5`  
`min_price` |  `Option[int]` |  The minimum price in cents the requester is willing to pay |  `None`  
`max_price` |  `Option[int]` |  The maximum price in cents the requester is willing to pay |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-ionic-shopping/llama_index/tools/ionic_shopping/base.py`

| ```
def query(
    self,
    query: str,
    num_results: Optional[int] = 5,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
) -> list[Product]:
    """
    Use this function to search for products and to get product recommendations.

    Args:
        query (str): A precise query of a product name or product category
        num_results (Optional[int]): Defaults to 5. The number of product results to return.
        min_price (Option[int]): The minimum price in cents the requester is willing to pay
        max_price (Option[int]): The maximum price in cents the requester is willing to pay

    """
    request = QueryAPIRequest(
        query=SDKQuery(
            query=query,
            num_results=num_results,
            min_price=min_price,
            max_price=max_price,
        )
    )
    response: QueryResponse = self.client.query(
        request=request,
        security=QuerySecurity(),
    )

    return [
        product
        for result in response.query_api_response.results
        for product in result.products
    ]

```
  
---|---
