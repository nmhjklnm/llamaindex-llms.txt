# Airbyte gong
##  AirbyteGongReader #
Bases: `AirbyteCDKReader`
AirbyteGongReader reader.
Retrieve documents from Gong
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `Mapping[str, Any]` |  The config object for the gong source. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airbyte-gong/llama_index/readers/airbyte_gong/base.py`

| ```
class AirbyteGongReader(AirbyteCDKReader):
    """
    AirbyteGongReader reader.

    Retrieve documents from Gong

    Args:
        config: The config object for the gong source.

    """

    def __init__(
        self,
        config: Mapping[str, Any],
        record_handler: Optional[RecordHandler] = None,
    ) -> None:
        """Initialize with parameters."""
        import source_gong

        super().__init__(
            source_class=source_gong.SourceGong,
            config=config,
            record_handler=record_handler,
        )

```
  
---|---
