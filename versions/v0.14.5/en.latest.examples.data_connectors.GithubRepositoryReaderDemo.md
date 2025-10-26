![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Github Repo Reader¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-github

```

%pip install llama-index-readers-github
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# This is due to the fact that we use asyncio.loop_until_complete in
# the DiscordReader. Since the Jupyter kernel itself runs on
# an event loop, we need to add some help with nesting
import nest_asyncio

nest_asyncio.apply()

```

# This is due to the fact that we use asyncio.loop_until_complete in # the DiscordReader. Since the Jupyter kernel itself runs on # an event loop, we need to add some help with nesting import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
%env OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
from llama_index.core import VectorStoreIndex
from llama_index.readers.github import GithubRepositoryReader, GithubClient
from IPython.display import Markdown, display
import os

```

%env OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx from llama_index.core import VectorStoreIndex from llama_index.readers.github import GithubRepositoryReader, GithubClient from IPython.display import Markdown, display import os
```
env: OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```

In [ ]:
Copied!
```
%env GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
github_token = os.environ.get("GITHUB_TOKEN")
owner = "jerryjliu"
repo = "llama_index"
branch = "main"

github_client = GithubClient(github_token=github_token, verbose=True)

documents = GithubRepositoryReader(
    github_client=github_client,
    owner=owner,
    repo=repo,
    use_parser=False,
    verbose=False,
    filter_directories=(
        ["docs"],
        GithubRepositoryReader.FilterType.INCLUDE,
    ),
    filter_file_extensions=(
        [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            "json",
            ".ipynb",
        ],
        GithubRepositoryReader.FilterType.EXCLUDE,
    ),
).load_data(branch=branch)

```

%env GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx github_token = os.environ.get("GITHUB_TOKEN") owner = "jerryjliu" repo = "llama_index" branch = "main" github_client = GithubClient(github_token=github_token, verbose=True) documents = GithubRepositoryReader( github_client=github_client, owner=owner, repo=repo, use_parser=False, verbose=False, filter_directories=( ["docs"], GithubRepositoryReader.FilterType.INCLUDE, ), filter_file_extensions=( [ ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", "json", ".ipynb", ], GithubRepositoryReader.FilterType.EXCLUDE, ), ).load_data(branch=branch)
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query(
    "What is the difference between VectorStoreIndex and SummaryIndex?",
    verbose=True,
)

```

query_engine = index.as_query_engine() response = query_engine.query( "What is the difference between VectorStoreIndex and SummaryIndex?", verbose=True, )
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
