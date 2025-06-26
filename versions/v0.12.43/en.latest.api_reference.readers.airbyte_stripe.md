# Airbyte stripe
##  AirbyteStripeReader #
Bases: `AirbyteCDKReader`
AirbyteStripeReader reader.
Retrieve documents from Stripe
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `Mapping[str, Any]` |  The config object for the stripe source. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airbyte-stripe/llama_index/readers/airbyte_stripe/base.py`

| ```
class AirbyteStripeReader(AirbyteCDKReader):
    """
    AirbyteStripeReader reader.

    Retrieve documents from Stripe

    Args:
        config: The config object for the stripe source.

    """

    def __init__(
        self,
        config: Mapping[str, Any],
        record_handler: Optional[RecordHandler] = None,
    ) -> None:
        """Initialize with parameters."""
        import source_stripe

        super().__init__(
            source_class=source_stripe.SourceStripe,
            config=config,
            record_handler=record_handler,
        )

```
  
---|---
