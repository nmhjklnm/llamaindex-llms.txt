# Panel chatbot
##  PanelChatPack #
Bases: `BaseLlamaPack`
Panel chatbot pack.
Source code in `llama-index-packs/llama-index-packs-panel-chatbot/llama_index/packs/panel_chatbot/base.py`

| ```
class PanelChatPack(BaseLlamaPack):
    """Panel chatbot pack."""

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {}

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        for variable in ENVIRONMENT_VARIABLES:
            if variable not in os.environ:
                raise ValueError("%s environment variable is not set", variable)

        import panel as pn

        if __name__ == "__main__":
            # 'pytest tests' will fail if app is imported elsewhere
            from app import create_chat_ui

            pn.serve(create_chat_ui)
        elif __name__.startswith("bokeh"):
            from app import create_chat_ui

            create_chat_ui().servable()
        else:
            print(
                "To serve the Panel ChatBot please run this file with 'panel serve' or 'python'"
            )

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-panel-chatbot/llama_index/packs/panel_chatbot/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {}

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-panel-chatbot/llama_index/packs/panel_chatbot/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    for variable in ENVIRONMENT_VARIABLES:
        if variable not in os.environ:
            raise ValueError("%s environment variable is not set", variable)

    import panel as pn

    if __name__ == "__main__":
        # 'pytest tests' will fail if app is imported elsewhere
        from app import create_chat_ui

        pn.serve(create_chat_ui)
    elif __name__.startswith("bokeh"):
        from app import create_chat_ui

        create_chat_ui().servable()
    else:
        print(
            "To serve the Panel ChatBot please run this file with 'panel serve' or 'python'"
        )

```
  
---|---
