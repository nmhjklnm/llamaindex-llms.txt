![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Anthropic Prompt Caching¶
In this Notebook, we will demonstrate the usage of Anthropic Prompt Caching with LlamaIndex abstractions.
Prompt Caching is enabled by marking `cache_control` in the messages request.
## How Prompt Caching works¶
When you send a request with Prompt Caching enabled:
  1. The system checks if the prompt prefix is already cached from a recent query.
  2. If found, it uses the cached version, reducing processing time and costs.
  3. Otherwise, it processes the full prompt and caches the prefix for future use.


**Note:**
A. Prompt caching works with `Claude 3.5 Sonnet`, `Claude 3 Haiku` and `Claude 3 Opus` models.
B. The minimum cacheable prompt length is:
```
1. 1024 tokens for Claude 3.5 Sonnet and Claude 3 Opus
2. 2048 tokens for Claude 3 Haiku
```

C. Shorter prompts cannot be cached, even if marked with `cache_control`.
### Setup API Keys¶
In [ ]:
Copied!
```
import os

os.environ[
    "ANTHROPIC_API_KEY"
] = "sk-ant-..."  # replace with your Anthropic API key

```

import os os.environ[ "ANTHROPIC_API_KEY" ] = "sk-ant-..." # replace with your Anthropic API key
### Setup LLM¶
In [ ]:
Copied!
```
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(model="claude-3-5-sonnet-20240620")

```

from llama_index.llms.anthropic import Anthropic llm = Anthropic(model="claude-3-5-sonnet-20240620")
### Download Data¶
In this demonstration, we will use the text from the `Paul Graham Essay`. We will cache the text and run some queries based on it.
In [ ]:
Copied!
```
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O './paul_graham_essay.txt'

```

!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O './paul_graham_essay.txt'
```
--2024-12-14 18:39:03--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.111.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘./paul_graham_essay.txt’

./paul_graham_essay 100%[===================>]  73.28K  --.-KB/s    in 0.04s   

2024-12-14 18:39:03 (1.62 MB/s) - ‘./paul_graham_essay.txt’ saved [75042/75042]


```

### Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(
    input_files=["./paul_graham_essay.txt"],
).load_data()

document_text = documents[0].text

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader( input_files=["./paul_graham_essay.txt"], ).load_data() document_text = documents[0].text
### Prompt Caching¶
Enabling Prompt Cache:
  1. Include `"cache_control": {"type": "ephemeral"}` for the text prompt you want to cache.
  2. Add `extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}` in the request.


We can verify if the text is cached by checking the following parameters:
`cache_creation_input_tokens:` Number of tokens written to the cache when creating a new entry.
`cache_read_input_tokens:` Number of tokens retrieved from the cache for this request.
`input_tokens:` Number of input tokens which were not read from or used to create a cache.
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage, TextBlock

messages = [
    ChatMessage(role="system", content="You are helpful AI Assitant."),
    ChatMessage(
        role="user",
        content=[
            TextBlock(
                text=f"{document_text}",
                type="text",
            ),
            TextBlock(
                text="\n\nWhy did Paul Graham start YC?",
                type="text",
            ),
        ],
        additional_kwargs={"cache_control": {"type": "ephemeral"}},
    ),
]

resp = llm.chat(
    messages, extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
)

```

from llama_index.core.llms import ChatMessage, TextBlock messages = [ ChatMessage(role="system", content="You are helpful AI Assitant."), ChatMessage( role="user", content=[ TextBlock( text=f"{document_text}", type="text", ), TextBlock( text="\n\nWhy did Paul Graham start YC?", type="text", ), ], additional_kwargs={"cache_control": {"type": "ephemeral"}}, ), ] resp = llm.chat( messages, extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"} )
Let's examine the raw response.
In [ ]:
Copied!
```
resp.raw

```

resp.raw
Out[ ]:
```
{'id': 'msg_01PAaZDTjEqcZksFiiqYH42t',
 'content': [TextBlock(text='Based on the essay, it seems Paul Graham started Y Combinator (YC) for a few key reasons:\n\n1. He had experience as a startup founder with Viaweb and wanted to help other founders avoid mistakes he had made.\n\n2. He had ideas about how venture capital could be improved, like making more smaller investments in younger technical founders.\n\n3. He was looking for something new to work on after selling Viaweb to Yahoo and trying painting for a while.\n\n4. He wanted to gain experience as an investor and thought funding a batch of startups at once would be a good way to do that.\n\n5. It started as a "Summer Founders Program" to give undergrads an alternative to summer internships, but quickly grew into something more serious.\n\n6. He saw an opportunity to scale startup funding by investing in batches of companies at once.\n\n7. He was excited by the potential to help create new startups and technologies.\n\n8. It allowed him to continue working with his friends/former colleagues Robert Morris and Trevor Blackwell.\n\n9. He had built an audience through his essays that provided deal flow for potential investments.\n\nSo in summary, it was a combination of wanting to help founders, improve venture capital, gain investing experience, work with friends, and leverage his existing audience/expertise in the startup world. The initial idea evolved quickly from a summer program into a new model for seed investing.', type='text')],
 'model': 'claude-3-5-sonnet-20240620',
 'role': 'assistant',
 'stop_reason': 'end_turn',
 'stop_sequence': None,
 'type': 'message',
 'usage': Usage(input_tokens=4, output_tokens=305, cache_creation_input_tokens=9, cache_read_input_tokens=17467)}
```

As you can see, since I've ran this a few different times, `cache_creation_input_tokens` and `cache_read_input_tokens` are both higher than zero, indicating that the text was cached properly.
Now, let’s run another query on the same document. It should retrieve the document text from the cache, which will be reflected in `cache_read_input_tokens`.
In [ ]:
Copied!
```
messages = [
    ChatMessage(role="system", content="You are helpful AI Assitant."),
    ChatMessage(
        role="user",
        content=[
            TextBlock(
                text=f"{document_text}",
                type="text",
            ),
            TextBlock(
                text="\n\nWhat did Paul Graham do growing up?",
                type="text",
            ),
        ],
        additional_kwargs={"cache_control": {"type": "ephemeral"}},
    ),
]

resp = llm.chat(
    messages, extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
)

```

messages = [ ChatMessage(role="system", content="You are helpful AI Assitant."), ChatMessage( role="user", content=[ TextBlock( text=f"{document_text}", type="text", ), TextBlock( text="\n\nWhat did Paul Graham do growing up?", type="text", ), ], additional_kwargs={"cache_control": {"type": "ephemeral"}}, ), ] resp = llm.chat( messages, extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"} )
In [ ]:
Copied!
```
resp.raw

```

resp.raw
Out[ ]:
```
{'id': 'msg_011TQgbpBuBkZAJeatVVcqtp',
 'content': [TextBlock(text='Based on the essay, here are some key things Paul Graham did growing up:\n\n1. As a teenager, he focused mainly on writing and programming outside of school. He tried writing short stories but says they were "awful".\n\n2. At age 13-14, he started programming on an IBM 1401 computer at his school district\'s data processing center. He used an early version of Fortran.\n\n3. In high school, he convinced his father to buy a TRS-80 microcomputer around 1980. He wrote simple games, a program to predict model rocket flight, and a word processor his father used.\n\n4. He went to college intending to study philosophy, but found it boring. He then decided to switch to studying artificial intelligence (AI).\n\n5. In college, he learned Lisp programming language, which expanded his concept of what programming could be. \n\n6. For his undergraduate thesis, he reverse-engineered SHRDLU, an early natural language processing program.\n\n7. He applied to grad schools for AI and ended up going to Harvard for graduate studies.\n\n8. In grad school, he realized AI as practiced then was not going to achieve true intelligence. He pivoted to focusing more on Lisp programming.\n\n9. He started writing a book about Lisp hacking while in grad school, which was eventually published in 1993 as "On Lisp".\n\nSo in summary, his early years were focused on writing, programming (especially Lisp), and studying AI, before he eventually moved on to other pursuits after grad school. The essay provides a detailed account of his intellectual development in these areas.', type='text')],
 'model': 'claude-3-5-sonnet-20240620',
 'role': 'assistant',
 'stop_reason': 'end_turn',
 'stop_sequence': None,
 'type': 'message',
 'usage': Usage(input_tokens=4, output_tokens=356, cache_creation_input_tokens=0, cache_read_input_tokens=17476)}
```

As you can see, the response was generated using cached text, as indicated by `cache_read_input_tokens`.
