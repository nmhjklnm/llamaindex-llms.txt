# Dad jokes
Init file.
##  DadJokesReader #
Bases: `BaseReader`
Dad jokes reader.
Reads a random dad joke.
Source code in `llama-index-integrations/readers/llama-index-readers-dad-jokes/llama_index/readers/dad_jokes/base.py`

| ```
class DadJokesReader(BaseReader):
    """
    Dad jokes reader.

    Reads a random dad joke.

    """

    def _get_random_dad_joke(self):
        response = requests.get(
            "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        json_data = response.json()
        return json_data["joke"]

    def load_data(self) -> List[Document]:
        """
        Return a random dad joke.

        Args:
            None.

        """
        return [Document(text=self._get_random_dad_joke())]

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Return a random dad joke.
Source code in `llama-index-integrations/readers/llama-index-readers-dad-jokes/llama_index/readers/dad_jokes/base.py`

| ```
def load_data(self) -> List[Document]:
    """
    Return a random dad joke.

    Args:
        None.

    """
    return [Document(text=self._get_random_dad_joke())]

```
  
---|---
