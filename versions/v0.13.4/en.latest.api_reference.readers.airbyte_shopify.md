# Airbyte shopify
##  AirbyteShopifyReader #
Bases: `AirbyteCDKReader`
AirbyteShopifyReader reader.
Retrieve documents from Shopify
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `Mapping[str, Any]` |  The config object for the shopify source. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airbyte-shopify/llama_index/readers/airbyte_shopify/base.py`

| ```
class AirbyteShopifyReader(AirbyteCDKReader):
    """
    AirbyteShopifyReader reader.

    Retrieve documents from Shopify

    Args:
        config: The config object for the shopify source.

    """

    def __init__(
        self,
        config: Mapping[str, Any],
        record_handler: Optional[RecordHandler] = None,
    ) -> None:
        """Initialize with parameters."""
        import source_shopify

        super().__init__(
            source_class=source_shopify.SourceShopify,
            config=config,
            record_handler=record_handler,
        )

```
  
---|---
