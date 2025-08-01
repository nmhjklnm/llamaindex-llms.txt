# Gpt repo
Init file.
##  GPTRepoReader #
Bases: `BaseReader`
GPTRepoReader.
Reads a github repo in a prompt-friendly format.
Source code in `llama-index-integrations/readers/llama-index-readers-gpt-repo/llama_index/readers/gpt_repo/base.py`

| ```
class GPTRepoReader(BaseReader):
    """
    GPTRepoReader.

    Reads a github repo in a prompt-friendly format.

    """

    def __init__(self, concatenate: bool = False) -> None:
        """Initialize."""
        self.concatenate = concatenate

    def load_data(
        self,
        repo_path: str,
        preamble_str: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        encoding: Optional[str] = "utf-8",
    ) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            pages (List[str]): List of pages to read.

        """
        ignore_file_path = os.path.join(repo_path, ".gptignore")

        if os.path.exists(ignore_file_path):
            ignore_list = get_ignore_list(ignore_file_path)
        else:
            ignore_list = []

        output_text = ""
        if preamble_str:
            output_text += f"{preamble_str}\n"
        elif self.concatenate:
            output_text += (
                "The following text is a Git repository with code. "
                "The structure of the text are sections that begin with ----, "
                "followed by a single line containing the file path and file "
                "name, followed by a variable amount of lines containing the "
                "file contents. The text representing the Git repository ends "
                "when the symbols --END-- are encountered. Any further text beyond "
                "--END-- are meant to be interpreted as instructions using the "
                "aforementioned Git repository as context.\n"
            )
        else:
            # self.concatenate is False
            output_text += (
                "The following text is a file in a Git repository. "
                "The structure of the text are sections that begin with ----, "
                "followed by a single line containing the file path and file "
                "name, followed by a variable amount of lines containing the "
                "file contents. The text representing the file ends "
                "when the symbols --END-- are encountered. Any further text beyond "
                "--END-- are meant to be interpreted as instructions using the "
                "aforementioned file as context.\n"
            )
        text_list = process_repository(
            repo_path,
            ignore_list,
            concatenate=self.concatenate,
            extensions=extensions,
            encoding=encoding,
        )
        docs = []
        for text in text_list:
            doc_text = output_text + text + "\n--END--\n"
            docs.append(Document(text=doc_text))

        return docs

```
  
---|---  
###  load_data #
```
load_data(repo_path: str, preamble_str: Optional[str] = None, extensions: Optional[List[str]] = None, encoding: Optional[str] = 'utf-8') -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`pages` |  `List[str]` |  List of pages to read. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-gpt-repo/llama_index/readers/gpt_repo/base.py`

| ```
def load_data(
    self,
    repo_path: str,
    preamble_str: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    encoding: Optional[str] = "utf-8",
) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        pages (List[str]): List of pages to read.

    """
    ignore_file_path = os.path.join(repo_path, ".gptignore")

    if os.path.exists(ignore_file_path):
        ignore_list = get_ignore_list(ignore_file_path)
    else:
        ignore_list = []

    output_text = ""
    if preamble_str:
        output_text += f"{preamble_str}\n"
    elif self.concatenate:
        output_text += (
            "The following text is a Git repository with code. "
            "The structure of the text are sections that begin with ----, "
            "followed by a single line containing the file path and file "
            "name, followed by a variable amount of lines containing the "
            "file contents. The text representing the Git repository ends "
            "when the symbols --END-- are encountered. Any further text beyond "
            "--END-- are meant to be interpreted as instructions using the "
            "aforementioned Git repository as context.\n"
        )
    else:
        # self.concatenate is False
        output_text += (
            "The following text is a file in a Git repository. "
            "The structure of the text are sections that begin with ----, "
            "followed by a single line containing the file path and file "
            "name, followed by a variable amount of lines containing the "
            "file contents. The text representing the file ends "
            "when the symbols --END-- are encountered. Any further text beyond "
            "--END-- are meant to be interpreted as instructions using the "
            "aforementioned file as context.\n"
        )
    text_list = process_repository(
        repo_path,
        ignore_list,
        concatenate=self.concatenate,
        extensions=extensions,
        encoding=encoding,
    )
    docs = []
    for text in text_list:
        doc_text = output_text + text + "\n--END--\n"
        docs.append(Document(text=doc_text))

    return docs

```
  
---|---
