# Yelp
##  YelpToolSpec #
Bases: `BaseToolSpec`
Yelp tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-yelp/llama_index/tools/yelp/base.py`

| ```
class YelpToolSpec(BaseToolSpec):
    """Yelp tool spec."""

    # TODO add disclaimer
    spec_functions = ["business_search", "business_reviews"]

    def __init__(self, api_key: str, client_id: str) -> Document:
        """Initialize with parameters."""
        from yelpapi import YelpAPI

        self.client = YelpAPI(api_key)

    def business_search(self, location: str, term: str, radius: Optional[int] = None):
        """
        Make a query to Yelp to find businesses given a location to search.

        Args:
            Businesses returned in the response may not be strictly within the specified location.
            term (str): Search term, e.g. "food" or "restaurants", The term may also be the business's name, such as "Starbucks"
            radius (int): A suggested search radius in meters. This field is used as a suggestion to the search. The actual search radius may be lower than the suggested radius in dense urban areas, and higher in regions of less business density.


        """
        response = self.client.search_query(location=location, term=term)
        return [Document(text=str(response))]

    def business_reviews(self, id: str):
        """
        Make a query to Yelp to find a business using an id from business_search.

        Args:
            # The id

        """
        response = self.client.reviews_query(id=id)
        return [Document(text=str(response))]

```
  
---|---  
###  business_search #
```
business_search(location: str, term: str, radius: Optional[int] = None)

```

Make a query to Yelp to find businesses given a location to search.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`term` |  `str` |  Search term, e.g. "food" or "restaurants", The term may also be the business's name, such as "Starbucks" |  _required_  
`radius` |  `int` |  A suggested search radius in meters. This field is used as a suggestion to the search. The actual search radius may be lower than the suggested radius in dense urban areas, and higher in regions of less business density. |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-yelp/llama_index/tools/yelp/base.py`

| ```
def business_search(self, location: str, term: str, radius: Optional[int] = None):
    """
    Make a query to Yelp to find businesses given a location to search.

    Args:
        Businesses returned in the response may not be strictly within the specified location.
        term (str): Search term, e.g. "food" or "restaurants", The term may also be the business's name, such as "Starbucks"
        radius (int): A suggested search radius in meters. This field is used as a suggestion to the search. The actual search radius may be lower than the suggested radius in dense urban areas, and higher in regions of less business density.


    """
    response = self.client.search_query(location=location, term=term)
    return [Document(text=str(response))]

```
  
---|---  
###  business_reviews #
```
business_reviews(id: str)

```

Make a query to Yelp to find a business using an id from business_search.
Source code in `llama-index-integrations/tools/llama-index-tools-yelp/llama_index/tools/yelp/base.py`

| ```
def business_reviews(self, id: str):
    """
    Make a query to Yelp to find a business using an id from business_search.

    Args:
        # The id

    """
    response = self.client.reviews_query(id=id)
    return [Document(text=str(response))]

```
  
---|---
