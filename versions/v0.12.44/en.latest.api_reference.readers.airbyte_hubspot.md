# Airbyte hubspot
##  AirbyteHubspotReader #
Bases: `AirbyteCDKReader`
AirbyteHubspotReader reader.
Retrieve documents from Hubspot
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `Mapping[str, Any]` |  The config object for the hubspot source. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airbyte-hubspot/llama_index/readers/airbyte_hubspot/base.py`

| ```
class AirbyteHubspotReader(AirbyteCDKReader):
    """
    AirbyteHubspotReader reader.

    Retrieve documents from Hubspot

    Args:
        config: The config object for the hubspot source.

    """

    def __init__(
        self,
        config: Mapping[str, Any],
        record_handler: Optional[RecordHandler] = None,
    ) -> None:
        """Initialize with parameters."""
        import source_hubspot

        super().__init__(
            source_class=source_hubspot.SourceHubspot,
            config=config,
            record_handler=record_handler,
        )

```
  
---|---
