# Guardrails
##  GuardrailsOutputParser #
Bases: `ChainableOutputParser`
Guardrails output parser.
Source code in `llama-index-integrations/output_parsers/llama-index-output-parsers-guardrails/llama_index/output_parsers/guardrails/base.py`

| ```
class GuardrailsOutputParser(ChainableOutputParser):
    """Guardrails output parser."""

    def __init__(
        self,
        guard: Guard,
        format_key: Optional[str] = None,
    ):
        """Initialize a Guardrails output parser."""
        self.guard: Guard = guard
        self.format_key = format_key

    @classmethod
    @deprecated(version="0.8.46")
    def from_rail(cls, rail: str) -> "GuardrailsOutputParser":
        """From rail."""
        if Guard is None:
            raise ImportError(
                "Guardrails is not installed. Run `pip install guardrails-ai`. "
            )

        return cls(Guard.from_rail(rail))

    @classmethod
    @deprecated(version="0.8.46")
    def from_rail_string(cls, rail_string: str) -> "GuardrailsOutputParser":
        """From rail string."""
        if Guard is None:
            raise ImportError(
                "Guardrails is not installed. Run `pip install guardrails-ai`. "
            )

        return cls(Guard.from_rail_string(rail_string))

    def parse(self, output: str, *args: Any, **kwargs: Any) -> Any:
        """Parse, validate, and correct errors programmatically."""
        return self.guard.parse(output, *args, **kwargs).validated_output

    def format(self, query: str) -> str:
        """Format a query with structured output formatting instructions."""
        output_schema_text = deepcopy(self.guard.rail.prompt)

        # Add format instructions here.
        format_instructions_tmpl = self.guard.raw_prompt.format_instructions
        # NOTE: output_schema is fixed
        format_instructions = format_instructions_tmpl.format(
            output_schema=output_schema_text
        )

        if self.format_key is not None:
            fmt_query = query.format(**{self.format_key: format_instructions})
        else:
            fmt_query = query + "\n\n" + format_instructions

        return fmt_query

```
  
---|---  
###  from_rail `classmethod` #
```
from_rail(rail: str) -> GuardrailsOutputParser

```

From rail.
Source code in `llama-index-integrations/output_parsers/llama-index-output-parsers-guardrails/llama_index/output_parsers/guardrails/base.py`

| ```
@classmethod
@deprecated(version="0.8.46")
def from_rail(cls, rail: str) -> "GuardrailsOutputParser":
    """From rail."""
    if Guard is None:
        raise ImportError(
            "Guardrails is not installed. Run `pip install guardrails-ai`. "
        )

    return cls(Guard.from_rail(rail))

```
  
---|---  
###  from_rail_string `classmethod` #
```
from_rail_string(rail_string: str) -> GuardrailsOutputParser

```

From rail string.
Source code in `llama-index-integrations/output_parsers/llama-index-output-parsers-guardrails/llama_index/output_parsers/guardrails/base.py`

| ```
@classmethod
@deprecated(version="0.8.46")
def from_rail_string(cls, rail_string: str) -> "GuardrailsOutputParser":
    """From rail string."""
    if Guard is None:
        raise ImportError(
            "Guardrails is not installed. Run `pip install guardrails-ai`. "
        )

    return cls(Guard.from_rail_string(rail_string))

```
  
---|---  
###  parse #
```
parse(output: str, *args: Any, **kwargs: Any) -> Any

```

Parse, validate, and correct errors programmatically.
Source code in `llama-index-integrations/output_parsers/llama-index-output-parsers-guardrails/llama_index/output_parsers/guardrails/base.py`

| ```
def parse(self, output: str, *args: Any, **kwargs: Any) -> Any:
    """Parse, validate, and correct errors programmatically."""
    return self.guard.parse(output, *args, **kwargs).validated_output

```
  
---|---  
###  format #
```
format(query: str) -> str

```

Format a query with structured output formatting instructions.
Source code in `llama-index-integrations/output_parsers/llama-index-output-parsers-guardrails/llama_index/output_parsers/guardrails/base.py`

| ```
def format(self, query: str) -> str:
    """Format a query with structured output formatting instructions."""
    output_schema_text = deepcopy(self.guard.rail.prompt)

    # Add format instructions here.
    format_instructions_tmpl = self.guard.raw_prompt.format_instructions
    # NOTE: output_schema is fixed
    format_instructions = format_instructions_tmpl.format(
        output_schema=output_schema_text
    )

    if self.format_key is not None:
        fmt_query = query.format(**{self.format_key: format_instructions})
    else:
        fmt_query = query + "\n\n" + format_instructions

    return fmt_query

```
  
---|---
