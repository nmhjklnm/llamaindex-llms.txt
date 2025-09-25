# Airbyte typeform
##  AirbyteTypeformReader #
Bases: `AirbyteCDKReader`
AirbyteTypeformReader reader.
Retrieve documents from Typeform
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `Mapping[str, Any]` |  The config object for the typeform source. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airbyte-typeform/llama_index/readers/airbyte_typeform/base.py`

| ```
class AirbyteTypeformReader(AirbyteCDKReader):
    """
    AirbyteTypeformReader reader.

    Retrieve documents from Typeform

    Args:
        config: The config object for the typeform source.

    """

    def __init__(
        self,
        config: Mapping[str, Any],
        record_handler: Optional[RecordHandler] = None,
    ) -> None:
        """Initialize with parameters."""
        import source_typeform

        super().__init__(
            source_class=source_typeform.SourceTypeform,
            config=config,
            record_handler=record_handler,
        )

```
  
---|---
