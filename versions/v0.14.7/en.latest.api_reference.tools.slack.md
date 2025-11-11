# Slack
##  SlackToolSpec #
Bases: `BaseToolSpec`
Slack tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-slack/llama_index/tools/slack/base.py`

| ```
class SlackToolSpec(BaseToolSpec):
    """Slack tool spec."""

    spec_functions = ["load_data", "send_message", "fetch_channels"]

    def __init__(
        self,
        slack_token: Optional[str] = None,
        ssl: Optional[SSLContext] = None,
        earliest_date: Optional[datetime] = None,
        latest_date: Optional[datetime] = None,
    ) -> None:
        """Initialize with parameters."""
        self.reader = SlackReader(
            slack_token=slack_token,
            ssl=ssl,
            earliest_date=earliest_date,
            latest_date=latest_date,
        )

    def load_data(
        self,
        channel_ids: List[str],
        reverse_chronological: bool = True,
    ) -> List[Document]:
        """Load data from the input directory."""
        return self.reader.load_data(
            channel_ids=channel_ids,
            reverse_chronological=reverse_chronological,
        )

    def send_message(
        self,
        channel_id: str,
        message: str,
    ) -> None:
        """Send a message to a channel given the channel ID."""
        slack_client = self.reader._client
        try:
            msg_result = slack_client.chat_postMessage(
                channel=channel_id,
                text=message,
            )
            logger.info(msg_result)
        except Exception as e:
            logger.error(e)
            raise

    def fetch_channels(
        self,
    ) -> List[str]:
        """Fetch a list of relevant channels."""
        slack_client = self.reader._client
        try:
            msg_result = slack_client.conversations_list()
            logger.info(msg_result)
        except Exception as e:
            logger.error(e)
            raise

        return msg_result["channels"]

```
  
---|---  
###  load_data #
```
load_data(channel_ids: List[str], reverse_chronological: bool = True) -> List[Document]

```

Load data from the input directory.
Source code in `llama-index-integrations/tools/llama-index-tools-slack/llama_index/tools/slack/base.py`

| ```
def load_data(
    self,
    channel_ids: List[str],
    reverse_chronological: bool = True,
) -> List[Document]:
    """Load data from the input directory."""
    return self.reader.load_data(
        channel_ids=channel_ids,
        reverse_chronological=reverse_chronological,
    )

```
  
---|---  
###  send_message #
```
send_message(channel_id: str, message: str) -> None

```

Send a message to a channel given the channel ID.
Source code in `llama-index-integrations/tools/llama-index-tools-slack/llama_index/tools/slack/base.py`

| ```
def send_message(
    self,
    channel_id: str,
    message: str,
) -> None:
    """Send a message to a channel given the channel ID."""
    slack_client = self.reader._client
    try:
        msg_result = slack_client.chat_postMessage(
            channel=channel_id,
            text=message,
        )
        logger.info(msg_result)
    except Exception as e:
        logger.error(e)
        raise

```
  
---|---  
###  fetch_channels #
```
fetch_channels() -> List[str]

```

Fetch a list of relevant channels.
Source code in `llama-index-integrations/tools/llama-index-tools-slack/llama_index/tools/slack/base.py`

| ```
def fetch_channels(
    self,
) -> List[str]:
    """Fetch a list of relevant channels."""
    slack_client = self.reader._client
    try:
        msg_result = slack_client.conversations_list()
        logger.info(msg_result)
    except Exception as e:
        logger.error(e)
        raise

    return msg_result["channels"]

```
  
---|---
