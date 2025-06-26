![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# RankGPT Reranker Demonstration (Van Gogh Wiki)¶
This demo integrates RankGPT into LlamaIndex as a reranker.
Paper: Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents
the idea of `RankGPT`:
  * it is a zero-shot listwise passage reranking using LLM (ChatGPT or GPT-4 or other LLMs)
  * it applies permutation generation approach and sliding window strategy to rerank passages efficiently.


In this example, we use Van Gogh's wikipedia as an example to compare the Retrieval results with/without RankGPT reranking. we showcase two models for RankGPT:
  * OpenAI `GPT3.5`
  * `Mistral` model.


In [ ]:
Copied!
```
%pip install llama-index-postprocessor-rankgpt-rerank
%pip install llama-index-llms-huggingface
%pip install llama-index-llms-huggingface-api
%pip install llama-index-llms-openai
%pip install llama-index-llms-ollama

```

%pip install llama-index-postprocessor-rankgpt-rerank %pip install llama-index-llms-huggingface %pip install llama-index-llms-huggingface-api %pip install llama-index-llms-openai %pip install llama-index-llms-ollama
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.postprocessor import LLMRerank
from llama_index.llms.openai import OpenAI
from IPython.display import Markdown, display

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.postprocessor import LLMRerank from llama_index.llms.openai import OpenAI from IPython.display import Markdown, display
In [ ]:
Copied!
```
import os

OPENAI_API_KEY = "sk-"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

```

import os OPENAI_API_KEY = "sk-" os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
## Load Data, Build Index¶
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.chunk_size = 512

```

from llama_index.core import Settings Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.chunk_size = 512
### Download Van Gogh wiki from Wikipedia¶
In [ ]:
Copied!
```
from pathlib import Path
import requests

wiki_titles = [
    "Vincent van Gogh",
]


data_path = Path("data_wiki")

for title in wiki_titles:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "explaintext": True,
        },
    ).json()
    page = next(iter(response["query"]["pages"].values()))
    wiki_text = page["extract"]

    if not data_path.exists():
        Path.mkdir(data_path)

    with open(data_path / f"{title}.txt", "w") as fp:
        fp.write(wiki_text)

```

from pathlib import Path import requests wiki_titles = [ "Vincent van Gogh", ] data_path = Path("data_wiki") for title in wiki_titles: response = requests.get( "https://en.wikipedia.org/w/api.php", params={ "action": "query", "format": "json", "titles": title, "prop": "extracts", "explaintext": True, }, ).json() page = next(iter(response["query"]["pages"].values())) wiki_text = page["extract"] if not data_path.exists(): Path.mkdir(data_path) with open(data_path / f"{title}.txt", "w") as fp: fp.write(wiki_text)
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data_wiki/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data_wiki/").load_data()
### Build vector store index for this Wikipedia page¶
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(
    documents,
)

```

index = VectorStoreIndex.from_documents( documents, )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

## Retrieval + RankGPT reranking¶
Steps:
  1. Setting up retriever and reranker (as an option)
  2. Retrieve results given a search query without reranking
  3. Retrieve results given a search query with RankGPT reranking enabled
  4. Comparing the results with and without reranking


In [ ]:
Copied!
```
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
from llama_index.postprocessor.rankgpt_rerank import RankGPTRerank

import pandas as pd
from IPython.display import display, HTML


def get_retrieved_nodes(
    query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False
):
    query_bundle = QueryBundle(query_str)
    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=vector_top_k,
    )
    retrieved_nodes = retriever.retrieve(query_bundle)

    if with_reranker:
        # configure reranker
        reranker = RankGPTRerank(
            llm=OpenAI(
                model="gpt-3.5-turbo-16k",
                temperature=0.0,
                api_key=OPENAI_API_KEY,
            ),
            top_n=reranker_top_n,
            verbose=True,
        )
        retrieved_nodes = reranker.postprocess_nodes(
            retrieved_nodes, query_bundle
        )

    return retrieved_nodes


def pretty_print(df):
    return display(HTML(df.to_html().replace("\\n", "<br>")))


def visualize_retrieved_nodes(nodes) -> None:
    result_dicts = []
    for node in nodes:
        result_dict = {"Score": node.score, "Text": node.node.get_text()}
        result_dicts.append(result_dict)

    pretty_print(pd.DataFrame(result_dicts))

```

from llama_index.core.retrievers import VectorIndexRetriever from llama_index.core import QueryBundle from llama_index.postprocessor.rankgpt_rerank import RankGPTRerank import pandas as pd from IPython.display import display, HTML def get_retrieved_nodes( query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False ): query_bundle = QueryBundle(query_str) # configure retriever retriever = VectorIndexRetriever( index=index, similarity_top_k=vector_top_k, ) retrieved_nodes = retriever.retrieve(query_bundle) if with_reranker: # configure reranker reranker = RankGPTRerank( llm=OpenAI( model="gpt-3.5-turbo-16k", temperature=0.0, api_key=OPENAI_API_KEY, ), top_n=reranker_top_n, verbose=True, ) retrieved_nodes = reranker.postprocess_nodes( retrieved_nodes, query_bundle ) return retrieved_nodes def pretty_print(df): return display(HTML(df.to_html().replace("\\\n", "  
"))) def visualize_retrieved_nodes(nodes) -> None: result_dicts = [] for node in nodes: result_dict = {"Score": node.score, "Text": node.node.get_text()} result_dicts.append(result_dict) pretty_print(pd.DataFrame(result_dicts))
### Retrieval top 3 results without Reranking¶
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles?",
    vector_top_k=3,
    with_reranker=False,
)

```

new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles?", vector_top_k=3, with_reranker=False, )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

### Expected result is:¶
`After much pleading from Van Gogh, Gauguin arrived in Arles on 23 October and, in November, the two painted together. Gauguin depicted Van Gogh in his The Painter of Sunflowers;`
In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 0.857523 | Gauguin fled Arles, never to see Van Gogh again. They continued to correspond, and in 1890, Gauguin proposed they form a studio in Antwerp. Meanwhile, other visitors to the hospital included Marie Ginoux and Roulin.Despite a pessimistic diagnosis, Van Gogh recovered and returned to the Yellow House on 7 January 1889. He spent the following month between hospital and home, suffering from hallucinations and delusions of poisoning. In March, the police closed his house after a petition by 30 townspeople (including the Ginoux family) who described him as le fou roux "the redheaded madman"; Van Gogh returned to hospital. Paul Signac visited him twice in March; in April, Van Gogh moved into rooms owned by Dr Rey after floods damaged paintings in his own home. Two months later, he left Arles and voluntarily entered an asylum in Saint-Rémy-de-Provence. Around this time, he wrote, "Sometimes moods of indescribable anguish, sometimes moments when the veil of time and fatality of circumstances seemed to be torn apart for an instant."Van Gogh gave his 1889 Portrait of Doctor Félix Rey to Dr Rey. The physician was not fond of the painting and used it to repair a chicken coop, then gave it away. In 2016, the portrait was housed at the Pushkin Museum of Fine Arts and estimated to be worth over $50 million.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Saint-Rémy (May 1889 – May 1890) ====  
  
Van Gogh entered the Saint-Paul-de-Mausole asylum on 8 May 1889, accompanied by his caregiver, Frédéric Salles, a Protestant clergyman. Saint-Paul was a former monastery in Saint-Rémy, located less than 30 kilometres (19 mi) from Arles, and it was run by a former naval doctor, Théophile Peyron. Van Gogh had two cells with barred windows, one of which he used as a studio. The clinic and its garden became the main subjects of his paintings.  
1 | 0.853599 | When he visited Saintes-Maries-de-la-Mer in June, he gave lessons to a Zouave second lieutenant – Paul-Eugène Milliet – and painted boats on the sea and the village. MacKnight introduced Van Gogh to Eugène Boch, a Belgian painter who sometimes stayed in Fontvieille, and the two exchanged visits in July.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Gauguin's visit (1888) ====  
  
When Gauguin agreed to visit Arles in 1888, Van Gogh hoped for friendship and to realize his idea of an artists' collective. Van Gogh prepared for Gauguin's arrival by painting four versions of Sunflowers in one week. "In the hope of living in a studio of our own with Gauguin," he wrote in a letter to Theo, "I'd like to do a decoration for the studio. Nothing but large Sunflowers."When Boch visited again, Van Gogh painted a portrait of him, as well as the study The Poet Against a Starry Sky.In preparation for Gauguin's visit, Van Gogh bought two beds on advice from the station's postal supervisor Joseph Roulin, whose portrait he painted. On 17 September, he spent his first night in the still sparsely furnished Yellow House. When Gauguin consented to work and live in Arles with him, Van Gogh started to work on the Décoration for the Yellow House, probably the most ambitious effort he ever undertook. He completed two chair paintings: Van Gogh's Chair and Gauguin's Chair.After much pleading from Van Gogh, Gauguin arrived in Arles on 23 October and, in November, the two painted together. Gauguin depicted Van Gogh in his The Painter of Sunflowers; Van Gogh painted pictures from memory, following Gauguin's suggestion. Among these "imaginative" paintings is Memory of the Garden at Etten. Their first joint outdoor venture was at the Alyscamps, when they produced the pendants Les Alyscamps. The single painting Gauguin completed during his visit was his portrait of Van Gogh.Van Gogh and Gauguin visited Montpellier in December 1888, where they saw works by Courbet and Delacroix in the Musée Fabre. Their relationship began to deteriorate; Van Gogh admired Gauguin and wanted to be treated as his equal, but Gauguin was arrogant and domineering, which frustrated Van Gogh. They often quarrelled; Van Gogh increasingly feared that Gauguin was going to desert him, and the situation, which Van Gogh described as one of "excessive tension", rapidly headed towards crisis point.  
2 | 0.842413 | === Artistic breakthrough ===  
  
  
==== Arles (1888–89) ====  
  
Ill from drink and suffering from smoker's cough, in February 1888 Van Gogh sought refuge in Arles. He seems to have moved with thoughts of founding an art colony. The Danish artist Christian Mourier-Petersen became his companion for two months, and, at first, Arles appeared exotic. In a letter, he described it as a foreign country: "The Zouaves, the brothels, the adorable little Arlésienne going to her First Communion, the priest in his surplice, who looks like a dangerous rhinoceros, the people drinking absinthe, all seem to me creatures from another world."The time in Arles became one of Van Gogh's more prolific periods: he completed 200 paintings and more than 100 drawings and watercolours. He was enchanted by the local countryside and light; his works from this period are rich in yellow, ultramarine and mauve. They include harvests, wheat fields and general rural landmarks from the area, including The Old Mill (1888), one of seven canvases sent to Pont-Aven on 4 October 1888 in an exchange of works with Paul Gauguin, Émile Bernard, Charles Laval and others.   
The portrayals of Arles are informed by his Dutch upbringing; the patchworks of fields and avenues are flat and lacking perspective, but excel in their use of colour.In March 1888, he painted landscapes using a gridded "perspective frame"; three of the works were shown at the annual exhibition of the Société des Artistes Indépendants. In April, he was visited by the American artist Dodge MacKnight, who was living nearby at Fontvieille. On 1 May 1888, for 15 francs per month, he signed a lease for the eastern wing of the Yellow House at 2 place Lamartine. The rooms were unfurnished and had been uninhabited for months.On 7 May, Van Gogh moved from the Hôtel Carrel to the Café de la Gare, having befriended the proprietors, Joseph and Marie Ginoux. The Yellow House had to be furnished before he could fully move in, but he was able to use it as a studio.  
#### Finding: the right result is ranked at 2nd without reranking¶
### Retrieve and Reranking top 10 results using RankGPT and return top 3¶
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles ?",
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=True,
)

```

new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles ?", vector_top_k=10, reranker_top_n=3, with_reranker=True, )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
After Reranking, new rank list for nodes: [1, 6, 0, 2, 7, 9, 4, 5, 3, 8]
```

In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 0.852371 | When he visited Saintes-Maries-de-la-Mer in June, he gave lessons to a Zouave second lieutenant – Paul-Eugène Milliet – and painted boats on the sea and the village. MacKnight introduced Van Gogh to Eugène Boch, a Belgian painter who sometimes stayed in Fontvieille, and the two exchanged visits in July.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Gauguin's visit (1888) ====  
  
When Gauguin agreed to visit Arles in 1888, Van Gogh hoped for friendship and to realize his idea of an artists' collective. Van Gogh prepared for Gauguin's arrival by painting four versions of Sunflowers in one week. "In the hope of living in a studio of our own with Gauguin," he wrote in a letter to Theo, "I'd like to do a decoration for the studio. Nothing but large Sunflowers."When Boch visited again, Van Gogh painted a portrait of him, as well as the study The Poet Against a Starry Sky.In preparation for Gauguin's visit, Van Gogh bought two beds on advice from the station's postal supervisor Joseph Roulin, whose portrait he painted. On 17 September, he spent his first night in the still sparsely furnished Yellow House. When Gauguin consented to work and live in Arles with him, Van Gogh started to work on the Décoration for the Yellow House, probably the most ambitious effort he ever undertook. He completed two chair paintings: Van Gogh's Chair and Gauguin's Chair.After much pleading from Van Gogh, Gauguin arrived in Arles on 23 October and, in November, the two painted together. Gauguin depicted Van Gogh in his The Painter of Sunflowers; Van Gogh painted pictures from memory, following Gauguin's suggestion. Among these "imaginative" paintings is Memory of the Garden at Etten. Their first joint outdoor venture was at the Alyscamps, when they produced the pendants Les Alyscamps. The single painting Gauguin completed during his visit was his portrait of Van Gogh.Van Gogh and Gauguin visited Montpellier in December 1888, where they saw works by Courbet and Delacroix in the Musée Fabre. Their relationship began to deteriorate; Van Gogh admired Gauguin and wanted to be treated as his equal, but Gauguin was arrogant and domineering, which frustrated Van Gogh. They often quarrelled; Van Gogh increasingly feared that Gauguin was going to desert him, and the situation, which Van Gogh described as one of "excessive tension", rapidly headed towards crisis point.  
1 | 0.819758 | ==== Hospital in Arles (December 1888) ====  
  
The exact sequence that led to the mutilation of van Gogh's ear is not known. Gauguin said, fifteen years later, that the night followed several instances of physically threatening behaviour. Their relationship was complex and Theo may have owed money to Gauguin, who suspected the brothers were exploiting him financially. It seems likely that Vincent realised that Gauguin was planning to leave. The following days saw heavy rain, leading to the two men being shut in the Yellow House. Gauguin recalled that Van Gogh followed him after he left for a walk and "rushed towards me, an open razor in his hand." This account is uncorroborated; Gauguin was almost certainly absent from the Yellow House that night, most likely staying in a hotel.After an altercation on the evening of 23 December 1888, Van Gogh returned to his room where he seemingly heard voices and either wholly or in part severed his left ear with a razor causing severe bleeding. He bandaged the wound, wrapped the ear in paper and delivered the package to a woman at a brothel Van Gogh and Gauguin both frequented. Van Gogh was found unconscious the next morning by a policeman and taken to hospital, where he was treated by Félix Rey, a young doctor still in training. The ear was brought to the hospital, but Rey did not attempt to reattach it as too much time had passed. Van Gogh researcher and art historian Bernadette Murphy discovered the true identity of the woman named Gabrielle, who died in Arles at the age of 80 in 1952, and whose descendants still lived (as of 2020) just outside Arles. Gabrielle, known in her youth as "Gaby," was a 17-year-old cleaning girl at the brothel and other local establishments at the time Van Gogh presented her with his ear.Van Gogh had no recollection of the event, suggesting that he may have suffered an acute mental breakdown. The hospital diagnosis was "acute mania with generalised delirium", and within a few days, the local police ordered that he be placed in hospital care. Gauguin immediately notified Theo, who, on 24 December, had proposed marriage to his old friend Andries Bonger's sister Johanna.  
2 | 0.855685 | Gauguin fled Arles, never to see Van Gogh again. They continued to correspond, and in 1890, Gauguin proposed they form a studio in Antwerp. Meanwhile, other visitors to the hospital included Marie Ginoux and Roulin.Despite a pessimistic diagnosis, Van Gogh recovered and returned to the Yellow House on 7 January 1889. He spent the following month between hospital and home, suffering from hallucinations and delusions of poisoning. In March, the police closed his house after a petition by 30 townspeople (including the Ginoux family) who described him as le fou roux "the redheaded madman"; Van Gogh returned to hospital. Paul Signac visited him twice in March; in April, Van Gogh moved into rooms owned by Dr Rey after floods damaged paintings in his own home. Two months later, he left Arles and voluntarily entered an asylum in Saint-Rémy-de-Provence. Around this time, he wrote, "Sometimes moods of indescribable anguish, sometimes moments when the veil of time and fatality of circumstances seemed to be torn apart for an instant."Van Gogh gave his 1889 Portrait of Doctor Félix Rey to Dr Rey. The physician was not fond of the painting and used it to repair a chicken coop, then gave it away. In 2016, the portrait was housed at the Pushkin Museum of Fine Arts and estimated to be worth over $50 million.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Saint-Rémy (May 1889 – May 1890) ====  
  
Van Gogh entered the Saint-Paul-de-Mausole asylum on 8 May 1889, accompanied by his caregiver, Frédéric Salles, a Protestant clergyman. Saint-Paul was a former monastery in Saint-Rémy, located less than 30 kilometres (19 mi) from Arles, and it was run by a former naval doctor, Théophile Peyron. Van Gogh had two cells with barred windows, one of which he used as a studio. The clinic and its garden became the main subjects of his paintings.  
#### Finding: After RankGPT reranking, the top 1st result is the right text containing the answer¶
## Using other LLM for RankGPT reranking¶
### Using `Ollama` for serving local `Mistral` models¶
In [ ]:
Copied!
```
from llama_index.llms.ollama import Ollama

llm = Ollama(
    model="mistral",
    request_timeout=30.0,
    # Manually set the context window to limit memory usage
    context_window=8000,
)

```

from llama_index.llms.ollama import Ollama llm = Ollama( model="mistral", request_timeout=30.0, # Manually set the context window to limit memory usage context_window=8000, )
In [ ]:
Copied!
```
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
import pandas as pd
from IPython.display import display, HTML
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.llms.huggingface import HuggingFaceLLM

from llama_index.postprocessor.rankgpt_rerank import RankGPTRerank


def get_retrieved_nodes(
    query_str, vector_top_k=5, reranker_top_n=3, with_reranker=False
):
    query_bundle = QueryBundle(query_str)
    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=vector_top_k,
    )
    retrieved_nodes = retriever.retrieve(query_bundle)

    if with_reranker:
        # configure reranker
        reranker = RankGPTRerank(
            llm=llm,
            top_n=reranker_top_n,
            verbose=True,
        )
        retrieved_nodes = reranker.postprocess_nodes(
            retrieved_nodes, query_bundle
        )

    return retrieved_nodes

```

from llama_index.core.retrievers import VectorIndexRetriever from llama_index.core import QueryBundle import pandas as pd from IPython.display import display, HTML from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI from llama_index.llms.huggingface import HuggingFaceLLM from llama_index.postprocessor.rankgpt_rerank import RankGPTRerank def get_retrieved_nodes( query_str, vector_top_k=5, reranker_top_n=3, with_reranker=False ): query_bundle = QueryBundle(query_str) # configure retriever retriever = VectorIndexRetriever( index=index, similarity_top_k=vector_top_k, ) retrieved_nodes = retriever.retrieve(query_bundle) if with_reranker: # configure reranker reranker = RankGPTRerank( llm=llm, top_n=reranker_top_n, verbose=True, ) retrieved_nodes = reranker.postprocess_nodes( retrieved_nodes, query_bundle ) return retrieved_nodes
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles ?",
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=True,
)

```

new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles ?", vector_top_k=10, reranker_top_n=3, with_reranker=True, )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://localhost:11434/api/chat "HTTP/1.1 200 OK"
HTTP Request: POST http://localhost:11434/api/chat "HTTP/1.1 200 OK"
After Reranking, new rank list for nodes: [4, 5, 0, 1, 2, 3, 6, 7, 8, 9]
```

In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 0.824605 | He adopted elements of Pointillism, a technique in which a multitude of small coloured dots are applied to the canvas so that when seen from a distance they create an optical blend of hues. The style stresses the ability of complementary colours – including blue and orange – to form vibrant contrasts.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
While in Asnières Van Gogh painted parks, restaurants and the Seine, including Bridges across the Seine at Asnières. In November 1887, Theo and Vincent befriended Paul Gauguin who had just arrived in Paris. Towards the end of the year, Vincent arranged an exhibition alongside Bernard, Anquetin, and probably Toulouse-Lautrec, at the Grand-Bouillon Restaurant du Chalet, 43 avenue de Clichy, Montmartre. In a contemporary account, Bernard wrote that the exhibition was ahead of anything else in Paris. There, Bernard and Anquetin sold their first paintings, and Van Gogh exchanged work with Gauguin. Discussions on art, artists, and their social situations started during this exhibition, continued and expanded to include visitors to the show, like Camille Pissarro and his son Lucien, Signac and Seurat. In February 1888, feeling worn out from life in Paris, Van Gogh left, having painted more than 200 paintings during his two years there. Hours before his departure, accompanied by Theo, he paid his first and only visit to Seurat in his studio.  
  
  
=== Artistic breakthrough ===  
  
  
==== Arles (1888–89) ====  
  
Ill from drink and suffering from smoker's cough, in February 1888 Van Gogh sought refuge in Arles. He seems to have moved with thoughts of founding an art colony. The Danish artist Christian Mourier-Petersen became his companion for two months, and, at first, Arles appeared exotic. In a letter, he described it as a foreign country: "The Zouaves, the brothels, the adorable little Arlésienne going to her First Communion, the priest in his surplice, who looks like a dangerous rhinoceros, the people drinking absinthe, all seem to me creatures from another world."The time in Arles became one of Van Gogh's more prolific periods: he completed 200 paintings and more than 100 drawings and watercolours.  
1 | 0.822903 | Two years later, Vincent and Theo paid for the publication of a book on Monticelli paintings, and Vincent bought some of Monticelli's works to add to his collection.Van Gogh learned about Fernand Cormon's atelier from Theo. He worked at the studio in April and May 1886, where he frequented the circle of the Australian artist John Russell, who painted his portrait in 1886. Van Gogh also met fellow students Émile Bernard, Louis Anquetin and Henri de Toulouse-Lautrec – who painted a portrait of him in pastel. They met at Julien "Père" Tanguy's paint shop, (which was, at that time, the only place where Paul Cézanne's paintings were displayed). In 1886, two large exhibitions were staged there, showing Pointillism and Neo-impressionism for the first time and bringing attention to Georges Seurat and Paul Signac. Theo kept a stock of Impressionist paintings in his gallery on boulevard Montmartre, but Van Gogh was slow to acknowledge the new developments in art.Conflicts arose between the brothers. At the end of 1886 Theo found living with Vincent to be "almost unbearable". By early 1887, they were again at peace, and Vincent had moved to Asnières, a northwestern suburb of Paris, where he got to know Signac. He adopted elements of Pointillism, a technique in which a multitude of small coloured dots are applied to the canvas so that when seen from a distance they create an optical blend of hues. The style stresses the ability of complementary colours – including blue and orange – to form vibrant contrasts.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
While in Asnières Van Gogh painted parks, restaurants and the Seine, including Bridges across the Seine at Asnières. In November 1887, Theo and Vincent befriended Paul Gauguin who had just arrived in Paris. Towards the end of the year, Vincent arranged an exhibition alongside Bernard, Anquetin, and probably Toulouse-Lautrec, at the Grand-Bouillon Restaurant du Chalet, 43 avenue de Clichy, Montmartre. In a contemporary account, Bernard wrote that the exhibition was ahead of anything else in Paris.  
2 | 0.855685 | Gauguin fled Arles, never to see Van Gogh again. They continued to correspond, and in 1890, Gauguin proposed they form a studio in Antwerp. Meanwhile, other visitors to the hospital included Marie Ginoux and Roulin.Despite a pessimistic diagnosis, Van Gogh recovered and returned to the Yellow House on 7 January 1889. He spent the following month between hospital and home, suffering from hallucinations and delusions of poisoning. In March, the police closed his house after a petition by 30 townspeople (including the Ginoux family) who described him as le fou roux "the redheaded madman"; Van Gogh returned to hospital. Paul Signac visited him twice in March; in April, Van Gogh moved into rooms owned by Dr Rey after floods damaged paintings in his own home. Two months later, he left Arles and voluntarily entered an asylum in Saint-Rémy-de-Provence. Around this time, he wrote, "Sometimes moods of indescribable anguish, sometimes moments when the veil of time and fatality of circumstances seemed to be torn apart for an instant."Van Gogh gave his 1889 Portrait of Doctor Félix Rey to Dr Rey. The physician was not fond of the painting and used it to repair a chicken coop, then gave it away. In 2016, the portrait was housed at the Pushkin Museum of Fine Arts and estimated to be worth over $50 million.  
  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Saint-Rémy (May 1889 – May 1890) ====  
  
Van Gogh entered the Saint-Paul-de-Mausole asylum on 8 May 1889, accompanied by his caregiver, Frédéric Salles, a Protestant clergyman. Saint-Paul was a former monastery in Saint-Rémy, located less than 30 kilometres (19 mi) from Arles, and it was run by a former naval doctor, Théophile Peyron. Van Gogh had two cells with barred windows, one of which he used as a studio. The clinic and its garden became the main subjects of his paintings.
