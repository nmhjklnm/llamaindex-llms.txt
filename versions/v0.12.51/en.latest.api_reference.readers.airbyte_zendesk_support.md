# Airbyte zendesk support
##  AirbyteZendeskSupportReader #
Bases: `AirbyteCDKReader`
AirbyteZendeskSupportReader reader.
Retrieve documents from ZendeskSupport
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `Mapping[str, Any]` |  The config object for the zendesk_support source. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airbyte-zendesk-support/llama_index/readers/airbyte_zendesk_support/base.py`

| ```
class AirbyteZendeskSupportReader(AirbyteCDKReader):
    """
    AirbyteZendeskSupportReader reader.

    Retrieve documents from ZendeskSupport

    Args:
        config: The config object for the zendesk_support source.

    """

    def __init__(
        self,
        config: Mapping[str, Any],
        record_handler: Optional[RecordHandler] = None,
    ) -> None:
        """Initialize with parameters."""
        import source_zendesk_support

        super().__init__(
            source_class=source_zendesk_support.SourceZendeskSupport,
            config=config,
            record_handler=record_handler,
        )

```
  
---|---
