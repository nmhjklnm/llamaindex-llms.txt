# Oxylabs
##  OxylabsAmazonSearchReader #
Bases: `OxylabsBaseReader`
Get data from the Amazon Search page.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/search
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/amazon_search.py`

| ```
class OxylabsAmazonSearchReader(OxylabsBaseReader):
    """
    Get data from the Amazon Search page.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/search
    """

    top_level_header: str = "Search Results"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsAmazonSearchReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.amazon.scrape_search(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.amazon.scrape_search(**payload)

```
  
---|---  
##  OxylabsAmazonPricingReader #
Bases: `OxylabsBaseReader`
Get data about Amazon product offer listings.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/pricing
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/amazon_pricing.py`

| ```
class OxylabsAmazonPricingReader(OxylabsBaseReader):
    """
    Get data about Amazon product offer listings.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/pricing
    """

    top_level_header: str = "Product pricing data"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsAmazonPricingReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.amazon.scrape_pricing(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.amazon.scrape_pricing(**payload)

```
  
---|---  
##  OxylabsAmazonProductReader #
Bases: `OxylabsBaseReader`
Get data about Amazon product.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/product
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/amazon_product.py`

| ```
class OxylabsAmazonProductReader(OxylabsBaseReader):
    """
    Get data about Amazon product.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/product
    """

    top_level_header: str = "Products"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsAmazonProductReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.amazon.scrape_product(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.amazon.scrape_product(**payload)

```
  
---|---  
##  OxylabsAmazonSellersReader #
Bases: `OxylabsBaseReader`
Get data about Amazon merchants.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/sellers
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/amazon_sellers.py`

| ```
class OxylabsAmazonSellersReader(OxylabsBaseReader):
    """
    Get data about Amazon merchants.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/sellers
    """

    top_level_header: str = "Sellers"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsAmazonSellersReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.amazon.scrape_sellers(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.amazon.scrape_sellers(**payload)

```
  
---|---  
##  OxylabsAmazonBestsellersReader #
Bases: `OxylabsBaseReader`
Get data from Amazon Best Sellers pages.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/best-sellers
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/amazon_bestsellers.py`

| ```
class OxylabsAmazonBestsellersReader(OxylabsBaseReader):
    """
    Get data from Amazon Best Sellers pages.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/best-sellers
    """

    top_level_header: str = "Bestsellers"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsAmazonBestsellersReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.amazon.scrape_bestsellers(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.amazon.scrape_bestsellers(**payload)

```
  
---|---  
##  OxylabsAmazonReviewsReader #
Bases: `OxylabsBaseReader`
Get data about Amazon product reviews.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/reviews
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/amazon_reviews.py`

| ```
class OxylabsAmazonReviewsReader(OxylabsBaseReader):
    """
    Get data about Amazon product reviews.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/reviews
    """

    top_level_header: str = "Reviews"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsAmazonReviewsReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.amazon.scrape_reviews(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.amazon.scrape_reviews(**payload)

```
  
---|---  
##  OxylabsGoogleSearchReader #
Bases: `OxylabsGoogleBaseReader`
Get Google Search results data.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/google/search/search
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/google_search.py`

| ```
class OxylabsGoogleSearchReader(OxylabsGoogleBaseReader):
    """
    Get Google Search results data.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/google/search/search
    """

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsGoogleSearchReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.google.scrape_search(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.google.scrape_search(**payload)

```
  
---|---  
##  OxylabsGoogleAdsReader #
Bases: `OxylabsGoogleBaseReader`
Get Google Search results data with paid ads.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/google/ads
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/google_ads.py`

| ```
class OxylabsGoogleAdsReader(OxylabsGoogleBaseReader):
    """
    Get Google Search results data with paid ads.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/google/ads
    """

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsGoogleAdsReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.google.scrape_ads(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.google.scrape_ads(**payload)

```
  
---|---  
##  OxylabsYoutubeTranscriptReader #
Bases: `OxylabsBaseReader`
Get YouTube video transcripts.
https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/youtube/youtube-transcript
Source code in `llama-index-integrations/readers/llama-index-readers-oxylabs/llama_index/readers/oxylabs/youtube_transcripts.py`

| ```
class OxylabsYoutubeTranscriptReader(OxylabsBaseReader):
    """
    Get YouTube video transcripts.

    https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/youtube/youtube-transcript
    """

    top_level_header: str = "YouTube video transcripts"

    def __init__(self, username: str, password: str, **data) -> None:
        super().__init__(username=username, password=password, **data)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsYoutubeTranscriptReader"

    def get_response(self, payload: dict[str, Any]) -> Response:
        return self.oxylabs_api.youtube_transcript.scrape_transcript(**payload)

    async def aget_response(self, payload: dict[str, Any]) -> Response:
        return await self.async_oxylabs_api.youtube_transcript.scrape_transcript(
            **payload
        )

```
  
---|---
