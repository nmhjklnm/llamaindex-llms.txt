# Mbox
##  MboxReader #
Bases: `BaseReader`
Mbox e-mail reader.
Reads a set of e-mails saved in the mbox format.
Source code in `llama-index-integrations/readers/llama-index-readers-mbox/llama_index/readers/mbox/base.py`

| ```
class MboxReader(BaseReader):
    """
    Mbox e-mail reader.

    Reads a set of e-mails saved in the mbox format.
    """

    def __init__(self) -> None:
        """Initialize."""

    def load_data(self, input_dir: str, **load_kwargs: Any) -> List[Document]:
        """
        Load data from the input directory.

        load_kwargs:
            max_count (int): Maximum amount of messages to read.
            message_format (str): Message format overriding default.
        """
        docs: List[Document] = []
        for dirpath, dirnames, filenames in os.walk(input_dir):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for filename in filenames:
                if filename.endswith(".mbox"):
                    filepath = os.path.join(dirpath, filename)
                    file_docs = MboxFileReader(**load_kwargs).load_data(Path(filepath))
                    docs.extend(file_docs)
        return docs

```
  
---|---  
###  load_data #
```
load_data(input_dir: str, **load_kwargs: Any) -> List[Document]

```

Load data from the input directory.
load_kwargs
max_count (int): Maximum amount of messages to read. message_format (str): Message format overriding default.
Source code in `llama-index-integrations/readers/llama-index-readers-mbox/llama_index/readers/mbox/base.py`

| ```
def load_data(self, input_dir: str, **load_kwargs: Any) -> List[Document]:
    """
    Load data from the input directory.

    load_kwargs:
        max_count (int): Maximum amount of messages to read.
        message_format (str): Message format overriding default.
    """
    docs: List[Document] = []
    for dirpath, dirnames, filenames in os.walk(input_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.endswith(".mbox"):
                filepath = os.path.join(dirpath, filename)
                file_docs = MboxFileReader(**load_kwargs).load_data(Path(filepath))
                docs.extend(file_docs)
    return docs

```
  
---|---
