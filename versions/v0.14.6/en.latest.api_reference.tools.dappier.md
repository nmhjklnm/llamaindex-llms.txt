# Dappier
##  DappierAIRecommendationsToolSpec #
Bases: `BaseToolSpec`
Dappier AI Recommendations tool spec.
Provides AI-powered recommendations across various domains such as Sports News, Lifestyle News, iHeartDogs, iHeartCats, GreenMonster, WISH-TV and 9 and 10 News.
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
class DappierAIRecommendationsToolSpec(BaseToolSpec):
    """
    Dappier AI Recommendations tool spec.

    Provides AI-powered recommendations across various domains such as Sports News,
    Lifestyle News, iHeartDogs, iHeartCats, GreenMonster, WISH-TV and 9 and 10 News.
    """

    spec_functions = [
        "get_sports_news_recommendations",
        "get_lifestyle_news_recommendations",
        "get_iheartdogs_recommendations",
        "get_iheartcats_recommendations",
        "get_greenmonster_recommendations",
        "get_wishtv_recommendations",
        "get_nine_and_ten_news_recommendations",
    ]

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Dappier AI Recommendations tool spec.

        To obtain an API key, visit: https://platform.dappier.com/profile/api-keys
        """
        from dappier import Dappier

        self.api_key = api_key or os.environ.get("DAPPIER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as a parameter or set DAPPIER_API_KEY in environment variables.\n"
                "To obtain an API key, visit: https://platform.dappier.com/profile/api-keys"
            )

        self.client = Dappier(api_key=self.api_key)

    def get_sports_news_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves sports news.

        Args:
            query (str): Query to fetch sports news.
            similarity_top_k (int): Number of documents to return.
            ref (Optional[str]): Site domain where recommendations should be displayed.
            num_articles_ref (int): Minimum number of articles to return from the reference domain.
            search_algorithm (str): The search algorithm to use.

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01j0pb465keqmatq9k83dthx34"  # Sports News
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

    def get_lifestyle_news_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves lifestyle news.

        Args:
            query (str): Query to fetch lifestyle news.
            similarity_top_k (int): Number of documents to return.
            ref (Optional[str]): Site domain where recommendations should be displayed.
            num_articles_ref (int): Minimum number of articles to return from the reference domain.
            search_algorithm (str): The search algorithm to use.

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01j0q82s4bfjmsqkhs3ywm3x6y"  # Lifestyle News
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

    def get_iheartdogs_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves iHeartDogs articles - a dog care expert.

        Args:
            query (str): Query to fetch dog care articles.
            similarity_top_k (int): Number of documents to return.
            ref (Optional[str]): Site domain where recommendations should be displayed.
            num_articles_ref (int): Minimum number of articles to return from the reference domain.
            search_algorithm (str): The search algorithm to use.

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01j1sz8t3qe6v9g8ad102kvmqn"  # iHeartDogs AI
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

    def get_iheartcats_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves iHeartCats articles - a cat care expert.

        Args:
            query (str): Query to fetch cat care articles.
            similarity_top_k (int): Number of documents to return.
            ref (Optional[str]): Site domain where recommendations should be displayed.
            num_articles_ref (int): Minimum number of articles to return from the reference domain.
            search_algorithm (str): The search algorithm to use.

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01j1sza0h7ekhaecys2p3y0vmj"  # iHeartCats AI
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

    def get_greenmonster_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves GreenMonster articles - Compassionate Living Guide.

        Args:
            query (str): Query to fetch compassionate living guides.
            similarity_top_k (int): Number of documents to return.
            ref (Optional[str]): Site domain where recommendations should be displayed.
            num_articles_ref (int): Minimum number of articles to return from the reference domain.
            search_algorithm (str): The search algorithm to use.

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01j5xy9w5sf49bm6b1prm80m27"  # GreenMonster
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

    def get_wishtv_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves news articles.

        Args:
            query (str): Query to fetch news articles.
            similarity_top_k (int): The number of top documents to retrieve based on similarity. Defaults to 10.
            ref (Optional[str]): The site domain where recommendations should be displayed. Defaults to None.
            num_articles_ref (int): Minimum number of articles to return from the reference domain. Defaults to 0.
            search_algorithm (str): The search algorithm to use. Defaults to "most_recent".

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01jagy9nqaeer9hxx8z1sk1jx6"  # WISH-TV AI
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

    def get_nine_and_ten_news_recommendations(
        self,
        query: str,
        similarity_top_k: int = 10,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ) -> str:
        """
        Retrieves up-to-date local news for Northern Michigan, Cadillac and
        Traverse City.

        Args:
            query (str): Query to fetch local news.
            similarity_top_k (int): Number of documents to return.
            ref (Optional[str]): Site domain where recommendations should be displayed.
            num_articles_ref (int): Minimum number of articles to return from the reference domain.
            search_algorithm (str): The search algorithm to use.

        Returns:
            str: A response message for the user specified query.

        """
        data_model_id = "dm_01jhtt138wf1b9j8jwswye99y5"  # 9 and 10 News
        response = self.client.get_ai_recommendations(
            query=query,
            data_model_id=data_model_id,
            similarity_top_k=similarity_top_k,
            ref=ref,
            num_articles_ref=num_articles_ref,
            search_algorithm=search_algorithm,
        )
        return format_results(response)

```
  
---|---  
###  get_sports_news_recommendations #
```
get_sports_news_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves sports news.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch sports news. |  _required_  
`similarity_top_k` |  `int` |  Number of documents to return. |  `10`  
`ref` |  `Optional[str]` |  Site domain where recommendations should be displayed. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_sports_news_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves sports news.

    Args:
        query (str): Query to fetch sports news.
        similarity_top_k (int): Number of documents to return.
        ref (Optional[str]): Site domain where recommendations should be displayed.
        num_articles_ref (int): Minimum number of articles to return from the reference domain.
        search_algorithm (str): The search algorithm to use.

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01j0pb465keqmatq9k83dthx34"  # Sports News
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
###  get_lifestyle_news_recommendations #
```
get_lifestyle_news_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves lifestyle news.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch lifestyle news. |  _required_  
`similarity_top_k` |  `int` |  Number of documents to return. |  `10`  
`ref` |  `Optional[str]` |  Site domain where recommendations should be displayed. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_lifestyle_news_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves lifestyle news.

    Args:
        query (str): Query to fetch lifestyle news.
        similarity_top_k (int): Number of documents to return.
        ref (Optional[str]): Site domain where recommendations should be displayed.
        num_articles_ref (int): Minimum number of articles to return from the reference domain.
        search_algorithm (str): The search algorithm to use.

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01j0q82s4bfjmsqkhs3ywm3x6y"  # Lifestyle News
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
###  get_iheartdogs_recommendations #
```
get_iheartdogs_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves iHeartDogs articles - a dog care expert.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch dog care articles. |  _required_  
`similarity_top_k` |  `int` |  Number of documents to return. |  `10`  
`ref` |  `Optional[str]` |  Site domain where recommendations should be displayed. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_iheartdogs_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves iHeartDogs articles - a dog care expert.

    Args:
        query (str): Query to fetch dog care articles.
        similarity_top_k (int): Number of documents to return.
        ref (Optional[str]): Site domain where recommendations should be displayed.
        num_articles_ref (int): Minimum number of articles to return from the reference domain.
        search_algorithm (str): The search algorithm to use.

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01j1sz8t3qe6v9g8ad102kvmqn"  # iHeartDogs AI
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
###  get_iheartcats_recommendations #
```
get_iheartcats_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves iHeartCats articles - a cat care expert.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch cat care articles. |  _required_  
`similarity_top_k` |  `int` |  Number of documents to return. |  `10`  
`ref` |  `Optional[str]` |  Site domain where recommendations should be displayed. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_iheartcats_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves iHeartCats articles - a cat care expert.

    Args:
        query (str): Query to fetch cat care articles.
        similarity_top_k (int): Number of documents to return.
        ref (Optional[str]): Site domain where recommendations should be displayed.
        num_articles_ref (int): Minimum number of articles to return from the reference domain.
        search_algorithm (str): The search algorithm to use.

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01j1sza0h7ekhaecys2p3y0vmj"  # iHeartCats AI
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
###  get_greenmonster_recommendations #
```
get_greenmonster_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves GreenMonster articles - Compassionate Living Guide.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch compassionate living guides. |  _required_  
`similarity_top_k` |  `int` |  Number of documents to return. |  `10`  
`ref` |  `Optional[str]` |  Site domain where recommendations should be displayed. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_greenmonster_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves GreenMonster articles - Compassionate Living Guide.

    Args:
        query (str): Query to fetch compassionate living guides.
        similarity_top_k (int): Number of documents to return.
        ref (Optional[str]): Site domain where recommendations should be displayed.
        num_articles_ref (int): Minimum number of articles to return from the reference domain.
        search_algorithm (str): The search algorithm to use.

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01j5xy9w5sf49bm6b1prm80m27"  # GreenMonster
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
###  get_wishtv_recommendations #
```
get_wishtv_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves news articles.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch news articles. |  _required_  
`similarity_top_k` |  `int` |  The number of top documents to retrieve based on similarity. Defaults to 10. |  `10`  
`ref` |  `Optional[str]` |  The site domain where recommendations should be displayed. Defaults to None. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. Defaults to 0. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. Defaults to "most_recent". |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_wishtv_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves news articles.

    Args:
        query (str): Query to fetch news articles.
        similarity_top_k (int): The number of top documents to retrieve based on similarity. Defaults to 10.
        ref (Optional[str]): The site domain where recommendations should be displayed. Defaults to None.
        num_articles_ref (int): Minimum number of articles to return from the reference domain. Defaults to 0.
        search_algorithm (str): The search algorithm to use. Defaults to "most_recent".

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01jagy9nqaeer9hxx8z1sk1jx6"  # WISH-TV AI
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
###  get_nine_and_ten_news_recommendations #
```
get_nine_and_ten_news_recommendations(query: str, similarity_top_k: int = 10, ref: Optional[str] = None, num_articles_ref: int = 0, search_algorithm: Literal['most_recent', 'semantic', 'most_recent_semantic', 'trending'] = 'most_recent') -> str

```

Retrieves up-to-date local news for Northern Michigan, Cadillac and Traverse City.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query to fetch local news. |  _required_  
`similarity_top_k` |  `int` |  Number of documents to return. |  `10`  
`ref` |  `Optional[str]` |  Site domain where recommendations should be displayed. |  `None`  
`num_articles_ref` |  `int` |  Minimum number of articles to return from the reference domain. |  `0`  
`search_algorithm` |  `str` |  The search algorithm to use. |  `'most_recent'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message for the user specified query.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/ai_recommendations/base.py`

| ```
def get_nine_and_ten_news_recommendations(
    self,
    query: str,
    similarity_top_k: int = 10,
    ref: Optional[str] = None,
    num_articles_ref: int = 0,
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = "most_recent",
) -> str:
    """
    Retrieves up-to-date local news for Northern Michigan, Cadillac and
    Traverse City.

    Args:
        query (str): Query to fetch local news.
        similarity_top_k (int): Number of documents to return.
        ref (Optional[str]): Site domain where recommendations should be displayed.
        num_articles_ref (int): Minimum number of articles to return from the reference domain.
        search_algorithm (str): The search algorithm to use.

    Returns:
        str: A response message for the user specified query.

    """
    data_model_id = "dm_01jhtt138wf1b9j8jwswye99y5"  # 9 and 10 News
    response = self.client.get_ai_recommendations(
        query=query,
        data_model_id=data_model_id,
        similarity_top_k=similarity_top_k,
        ref=ref,
        num_articles_ref=num_articles_ref,
        search_algorithm=search_algorithm,
    )
    return format_results(response)

```
  
---|---  
##  DappierRealTimeSearchToolSpec #
Bases: `BaseToolSpec`
Dappier Real Time Search tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/real_time_search/base.py`

| ```
class DappierRealTimeSearchToolSpec(BaseToolSpec):
    """Dappier Real Time Search tool spec."""

    spec_functions = ["search_real_time_data", "search_stock_market_data"]

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Dappier Real Time Search tool spec.

        To obtain an API key, visit: https://platform.dappier.com/profile/api-keys
        """
        from dappier import Dappier

        self.api_key = api_key or os.environ.get("DAPPIER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as a parameter or set DAPPIER_API_KEY in environment variables.\n"
                "To obtain an API key, visit: https://platform.dappier.com/profile/api-keys"
            )

        self.client = Dappier(api_key=self.api_key)

    def search_real_time_data(self, query: str) -> str:
        """
        Performs a real-time data search.

        Args:
            query (str): The user-provided input string for retrieving
            real-time google web search results including the latest news,
            weather, travel, deals and more.

        Returns:
            str: A response message containing the real-time data results.

        """
        ai_model_id = "am_01j0rzq4tvfscrgzwac7jv1p4c"
        response = self.client.search_real_time_data(
            query=query, ai_model_id=ai_model_id
        )
        return response.message if response else "No real-time data found."

    def search_stock_market_data(self, query: str) -> str:
        """
        Performs a stock market data search.

        Args:
            query (str): The user-provided input string for retrieving
            real-time financial news, stock prices, and trades from polygon.io,
            with AI-powered insights and up-to-the-minute updates to keep you
            informed on all your financial interests.

        Returns:
            str: A response message containing the stock market data results.

        """
        ai_model_id = "am_01j749h8pbf7ns8r1bq9s2evrh"
        response = self.client.search_real_time_data(
            query=query, ai_model_id=ai_model_id
        )
        return response.message if response else "No stock market data found."

```
  
---|---  
###  search_real_time_data #
```
search_real_time_data(query: str) -> str

```

Performs a real-time data search.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The user-provided input string for retrieving |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message containing the real-time data results.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/real_time_search/base.py`

| ```
def search_real_time_data(self, query: str) -> str:
    """
    Performs a real-time data search.

    Args:
        query (str): The user-provided input string for retrieving
        real-time google web search results including the latest news,
        weather, travel, deals and more.

    Returns:
        str: A response message containing the real-time data results.

    """
    ai_model_id = "am_01j0rzq4tvfscrgzwac7jv1p4c"
    response = self.client.search_real_time_data(
        query=query, ai_model_id=ai_model_id
    )
    return response.message if response else "No real-time data found."

```
  
---|---  
###  search_stock_market_data #
```
search_stock_market_data(query: str) -> str

```

Performs a stock market data search.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The user-provided input string for retrieving |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  A response message containing the stock market data results.  
Source code in `llama-index-integrations/tools/llama-index-tools-dappier/llama_index/tools/dappier/real_time_search/base.py`

| ```
def search_stock_market_data(self, query: str) -> str:
    """
    Performs a stock market data search.

    Args:
        query (str): The user-provided input string for retrieving
        real-time financial news, stock prices, and trades from polygon.io,
        with AI-powered insights and up-to-the-minute updates to keep you
        informed on all your financial interests.

    Returns:
        str: A response message containing the stock market data results.

    """
    ai_model_id = "am_01j749h8pbf7ns8r1bq9s2evrh"
    response = self.client.search_real_time_data(
        query=query, ai_model_id=ai_model_id
    )
    return response.message if response else "No stock market data found."

```
  
---|---
