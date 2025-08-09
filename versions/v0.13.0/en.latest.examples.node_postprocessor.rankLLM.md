# RankLLM Reranker Demonstration (Van Gogh Wiki)¶
This demo showcases how to use RankLLM to rerank passages.
RankLLM offers a suite of listwise, pairwise, and pointwise rerankers, albeit with focus on open source LLMs finetuned for the task - RankVicuna and RankZephyr being two of them. It also features ranking with OpenAI and GenAI.
It compares query search results from Van Gogh’s wikipedia with just retrieval (using VectorIndexRetriever from llama-index) and retrieval+reranking with RankLLM. We show an example of reranking 50 candidates using the RankZephyr reranker, which uses a listwise sliding window algorithm.
* * *
Dependencies:
  * RankLLM's dependencies
  * The built-in retriever, which uses Pyserini, requires `JDK11`, `PyTorch`, and `Faiss`


### castorini/rank_llm¶
RankLLM is a Python toolkit for reproducible information retrieval research using rerankers, with a focus on listwise reranking.  
Website: http://rankllm.ai\
In [ ]:
Copied!
```
%pip install llama-index-core
%pip install llama-index-llms-openai
%pip install llama-index-postprocessor-rankllm-rerank
%pip install rank-llm

```

%pip install llama-index-core %pip install llama-index-llms-openai %pip install llama-index-postprocessor-rankllm-rerank %pip install rank-llm
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
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.chunk_size = 512

```

from llama_index.core import Settings Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.chunk_size = 512
## Load Data, Build Index¶
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

### Retrieval + RankLLM Reranking (sliding window)¶
  1. Set up retriever and reranker
  2. Retrieve results given search query without reranking
  3. Retrieve results given search query with RankZephyr reranking


**All the field arguments and defaults for RankLLMRerank:**
```
model: str = Field(
  description="Model name.",
  default="rank_zephyr"
)
top_n: Optional[int] = Field(
  description="Number of nodes to return sorted by reranking score."
)
window_size: int = Field(
  description="Reranking window size. Applicable only for listwise and pairwise models.",
  default=20
)
batch_size: Optional[int] = Field(
  description="Reranking batch size. Applicable only for pointwise models."
)
context_size: int = Field(
  description="Maximum number of tokens for the context window.",
  default=4096
)
prompt_mode: PromptMode = Field(
  description="Prompt format and strategy used when invoking the reranking model.",
  default=PromptMode.RANK_GPT
)
num_gpus: int = Field(
  description="Number of GPUs to use for inference if applicable.",
  default=1
)
num_few_shot_examples: int = Field(
  description="Number of few-shot examples to include in the prompt.",
  default=0
)
few_shot_file: Optional[str] = Field(
  description="Path to a file containing few-shot examples, used if few-shot prompting is enabled.",
  default=None
)
use_logits: bool = Field(
  description="Whether to use raw logits for reranking scores instead of probabilities.",
  default=False
)
use_alpha: bool = Field(
  description="Whether to apply an alpha scaling factor in the reranking score calculation.",
  default=False
)
variable_passages: bool = Field(
  description="Whether to allow passages of variable lengths instead of fixed-size chunks.",
  default=False
)
stride: int = Field(
  description="Stride to use when sliding over long documents for reranking.",
  default=10
)
use_azure_openai: bool = Field(
  description="Whether to use Azure OpenAI instead of the standard OpenAI API.",
  default=False
)

```

In [ ]:
Copied!
```
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
from llama_index.postprocessor.rankllm_rerank import RankLLMRerank

import pandas as pd
import torch
from IPython.display import display, HTML


def get_retrieved_nodes(
    query_str,
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=False,
    model="rank_zephyr",
    window_size=None,
):
    query_bundle = QueryBundle(query_str)
    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=vector_top_k,
    )
    retrieved_nodes = retriever.retrieve(query_bundle)
    retrieved_nodes.reverse()

    if with_reranker:
        # configure reranker
        reranker = RankLLMRerank(
            model=model, top_n=reranker_top_n, window_size=window_size
        )
        retrieved_nodes = reranker.postprocess_nodes(
            retrieved_nodes, query_bundle
        )

        # clear cache, rank_zephyr uses 16GB of GPU VRAM
        del reranker
        torch.cuda.empty_cache()

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

from llama_index.core.retrievers import VectorIndexRetriever from llama_index.core import QueryBundle from llama_index.postprocessor.rankllm_rerank import RankLLMRerank import pandas as pd import torch from IPython.display import display, HTML def get_retrieved_nodes( query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False, model="rank_zephyr", window_size=None, ): query_bundle = QueryBundle(query_str) # configure retriever retriever = VectorIndexRetriever( index=index, similarity_top_k=vector_top_k, ) retrieved_nodes = retriever.retrieve(query_bundle) retrieved_nodes.reverse() if with_reranker: # configure reranker reranker = RankLLMRerank( model=model, top_n=reranker_top_n, window_size=window_size ) retrieved_nodes = reranker.postprocess_nodes( retrieved_nodes, query_bundle ) # clear cache, rank_zephyr uses 16GB of GPU VRAM del reranker torch.cuda.empty_cache() return retrieved_nodes def pretty_print(df): return display(HTML(df.to_html().replace("\\\n", "  
"))) def visualize_retrieved_nodes(nodes) -> None: result_dicts = [] for node in nodes: result_dict = {"Score": node.score, "Text": node.node.get_text()} result_dicts.append(result_dict) pretty_print(pd.DataFrame(result_dicts))
### Without `RankZephyr` reranking, the correct result is ranked `47`th/50.¶
#### Expected result:¶
`After much pleading from Van Gogh, Gauguin arrived in Arles on 23 October and, in November, the two painted together. Gauguin depicted Van Gogh in his The Painter of Sunflowers;`
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles?",
    vector_top_k=50,
    with_reranker=False,
)

visualize_retrieved_nodes(new_nodes[:3])

```

new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles?", vector_top_k=50, with_reranker=False, ) visualize_retrieved_nodes(new_nodes[:3])
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

| Score | Text  
---|---|---  
0 | 0.766322 | Yellow meant the most to him, because it symbolised emotional truth. He used yellow as a symbol for sunlight, life, and God.  
Van Gogh strove to be a painter of rural life and nature; during his first summer in Arles he used his new palette to paint landscapes and traditional rural life. His belief that a power existed behind the natural led him to try to capture a sense of that power, or the essence of nature in his art, sometimes through the use of symbols. His renditions of the sower, at first copied from Jean-François Millet, reflect the influence of Thomas Carlyle and Friedrich Nietzsche's thoughts on the heroism of physical labour, as well as van Gogh's religious beliefs: the sower as Christ sowing life beneath the hot sun. These were themes and motifs he returned to often to rework and develop. His paintings of flowers are filled with symbolism, but rather than use traditional Christian iconography he made up his own, where life is lived under the sun and work is an allegory of life. In Arles, having gained confidence after painting spring blossoms and learning to capture bright sunlight, he was ready to paint The Sower.  
  
Van Gogh stayed within what he called the "guise of reality" and was critical of overly stylised works. He wrote afterwards that the abstraction of Starry Night had gone too far and that reality had "receded too far in the background". Hughes describes it as a moment of extreme visionary ecstasy: the stars are in a great whirl, reminiscent of Hokusai's Great Wave, the movement in the heaven above is reflected by the movement of the cypress on the earth below, and the painter's vision is "translated into a thick, emphatic plasma of paint".  
Between 1885 and his death in 1890, van Gogh appears to have been building an oeuvre, a collection that reflected his personal vision and could be commercially successful. He was influenced by Blanc's definition of style, that a true painting required optimal use of colour, perspective and brushstrokes. Van Gogh applied the word "purposeful" to paintings he thought he had mastered, as opposed to those he thought of as studies.  
1 | 0.768032 | ==== Self-portraits ====  
  
Van Gogh created more than 43 self-portraits between 1885 and 1889. They were usually completed in series, such as those painted in Paris in mid-1887, and continued until shortly before his death. Generally the portraits were studies, created during periods when he was reluctant to mix with others or when he lacked models and painted himself.  
Van Gogh's self-portraits reflect a high degree of self-scrutiny. Often they were intended to mark important periods in his life; for example, the mid-1887 Paris series were painted at the point where he became aware of Claude Monet, Paul Cézanne and Signac. In Self-Portrait with Grey Felt Hat, heavy strains of paint spread outwards across the canvas. It is one of his most renowned self-portraits of that period, "with its highly organized rhythmic brushstrokes, and the novel halo derived from the Neo-impressionist repertoire was what van Gogh himself called a 'purposeful' canvas".  
They contain a wide array of physiognomical representations. Van Gogh's mental and physical condition is usually apparent; he may appear unkempt, unshaven or with a neglected beard, with deeply sunken eyes, a weak jaw, or having lost teeth. Some show him with full lips, a long face or prominent skull, or sharpened, alert features. His hair is sometimes depicted in a vibrant reddish hue and at other times ash colored.  
Van Gogh's self-portraits vary stylistically. In those painted after December 1888, the strong contrast of vivid colors highlight the haggard pallor of his skin. Some depict the artist with a beard, others without. He can be seen with bandages in portraits executed just after he mutilated his ear. In only a few does he depict himself as a painter. Those painted in Saint-Rémy show the head from the right, the side opposite his damaged ear, as he painted himself reflected in his mirror.  
2 | 0.769051 | With their broad brushstrokes, inventive perspectives, colours, contours and designs, these paintings represent the style he sought.  
  
  
=== Major series ===  
  
Van Gogh's stylistic developments are usually linked to the periods he spent living in different places across Europe. He was inclined to immerse himself in local cultures and lighting conditions, although he maintained a highly individual visual outlook throughout. His evolution as an artist was slow and he was aware of his painterly limitations. Van Gogh moved home often, perhaps to expose himself to new visual stimuli, and through exposure develop his technical skill. Art historian Melissa McQuillan believes the moves also reflect later stylistic changes and that van Gogh used the moves to avoid conflict, and as a coping mechanism for when the idealistic artist was faced with the realities of his then current situation.  
  
  
==== Portraits ====  
  
Van Gogh said portraiture was his greatest interest. "What I'm most passionate about, much much more than all the rest in my profession", he wrote in 1890, "is the portrait, the modern portrait." It is "the only thing in painting that moves me deeply and that gives me a sense of the infinite." He wrote to his sister that he wished to paint portraits that would endure, and that he would use colour to capture their emotions and character rather than aiming for photographic realism. Those closest to van Gogh are mostly absent from his portraits; he rarely painted Theo, van Rappard or Bernard. The portraits of his mother were from photographs.  
Van Gogh painted Arles' postmaster Joseph Roulin and his family repeatedly. In five versions of La Berceuse (The Lullaby), van Gogh painted Augustine Roulin quietly holding a rope that rocks the unseen cradle of her infant daughter. Van Gogh had planned for it to be the central image of a triptych, flanked by paintings of sunflowers.  
### With `RankZephyr` reranking, the correct result is ranked `1`st/50¶
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles?",
    vector_top_k=50,
    reranker_top_n=3,
    with_reranker=True,
    model="rank_zephyr",
    window_size=15,
)

visualize_retrieved_nodes(new_nodes)

```

new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles?", vector_top_k=50, reranker_top_n=3, with_reranker=True, model="rank_zephyr", window_size=15, ) visualize_retrieved_nodes(new_nodes)
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
Loading rank_zephyr ...

```

```
Loading checkpoint shards: 100%|██████████| 3/3 [00:02<00:00,  1.11it/s]

```

```
Completed loading rank_zephyr

```

```
100%|██████████| 1/1 [00:11<00:00, 11.38s/it]

```

| Score | Text  
---|---|---  
0 | 0.857234 | After much pleading from van Gogh, Gauguin arrived in Arles on 23 October and, in November, the two painted together. Gauguin depicted van Gogh in his The Painter of Sunflowers; van Gogh painted pictures from memory, following Gauguin's suggestion. Among these "imaginative" paintings is Memory of the Garden at Etten. Their first joint outdoor venture was at the Alyscamps, when they produced the pendants Les Alyscamps. The single painting Gauguin completed during his visit was his portrait of van Gogh.  
Van Gogh and Gauguin visited Montpellier in December 1888, where they saw works by Courbet and Delacroix in the Musée Fabre. Their relationship began to deteriorate; van Gogh admired Gauguin and wanted to be treated as his equal, but Gauguin was arrogant and domineering, which frustrated van Gogh. They often quarreled; van Gogh increasingly feared that Gauguin was going to desert him, and the situation, which van Gogh described as one of "excessive tension", rapidly headed towards crisis point.  
  
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
\t\t  
\t\t\t  
\t\t\t  
\t\t  
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Hospital in Arles (December 1888) ====  
  
The exact sequence that led to the mutilation of van Gogh's ear is not known. Gauguin said, fifteen years later, that the night followed several instances of physically threatening behaviour. Their relationship was complex and Theo may have owed money to Gauguin, who suspected the brothers were exploiting him financially. It seems likely that Vincent realised that Gauguin was planning to leave. The following days saw heavy rain, leading to the two men being shut in the Yellow House. Gauguin recalled that van Gogh followed him after he left for a walk and "rushed towards me, an open razor in his hand." This account is uncorroborated; Gauguin was almost certainly absent from the Yellow House that night, most likely staying in a hotel.  
After an altercation on the evening of 23 December 1888, van Gogh returned to his room where he seemingly heard voices and either wholly or in part severed his left ear with a razor causing severe bleeding.  
1 | 0.861649 | ==== Gauguin's visit (1888) ====  
  
  
When Gauguin agreed to visit Arles in 1888, van Gogh hoped for friendship and to realize his idea of an artists' collective. Van Gogh prepared for Gauguin's arrival by painting four versions of Sunflowers in one week. "In the hope of living in a studio of our own with Gauguin," he wrote in a letter to Theo, "I'd like to do a decoration for the studio. Nothing but large Sunflowers."   
When Boch visited again, van Gogh painted a portrait of him, as well as the study The Poet Against a Starry Sky.  
In preparation for Gauguin's visit, van Gogh bought two beds on advice from the station's postal supervisor Joseph Roulin, whose portrait he painted. On 17 September, he spent his first night in the still sparsely furnished Yellow House. When Gauguin consented to work and live in Arles with him, van Gogh started to work on the Décoration for the Yellow House, probably the most ambitious effort he ever undertook. He completed two chair paintings: Van Gogh's Chair and Gauguin's Chair.  
After much pleading from van Gogh, Gauguin arrived in Arles on 23 October and, in November, the two painted together. Gauguin depicted van Gogh in his The Painter of Sunflowers; van Gogh painted pictures from memory, following Gauguin's suggestion. Among these "imaginative" paintings is Memory of the Garden at Etten. Their first joint outdoor venture was at the Alyscamps, when they produced the pendants Les Alyscamps. The single painting Gauguin completed during his visit was his portrait of van Gogh.  
Van Gogh and Gauguin visited Montpellier in December 1888, where they saw works by Courbet and Delacroix in the Musée Fabre. Their relationship began to deteriorate; van Gogh admired Gauguin and wanted to be treated as his equal, but Gauguin was arrogant and domineering, which frustrated van Gogh.  
2 | 0.852035 | Gauguin fled Arles, never to see van Gogh again. They continued to correspond, and in 1890, Gauguin proposed they form a studio in Antwerp. Meanwhile, other visitors to the hospital included Marie Ginoux and Roulin.  
Despite a pessimistic diagnosis, van Gogh recovered and returned to the Yellow House on 7 January 1889. He spent the following month between hospital and home, suffering from hallucinations and delusions of poisoning. In March, the police closed his house after a petition by 30 townspeople (including the Ginoux family) who described him as le fou roux "the redheaded madman"; Van Gogh returned to hospital. Paul Signac visited him twice in March; in April, van Gogh moved into rooms owned by Dr Rey after floods damaged paintings in his own home. Two months later, he left Arles and voluntarily entered an asylum in Saint-Rémy-de-Provence. Around this time, he wrote, "Sometimes moods of indescribable anguish, sometimes moments when the veil of time and fatality of circumstances seemed to be torn apart for an instant."  
Van Gogh gave his 1889 Portrait of Doctor Félix Rey to Dr Rey. The physician was not fond of the painting and used it to repair a chicken coop, then gave it away. In 2016, the portrait was housed at the Pushkin Museum of Fine Arts and estimated to be worth over $50 million.  
  
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
\t\t  
\t\t\t  
\t\t\t  
\t\t  
  
  
==== Saint-Rémy (May 1889 – May 1890) ====  
  
Van Gogh entered the Saint-Paul-de-Mausole asylum on 8 May 1889, accompanied by his caregiver, Frédéric Salles, a Protestant clergyman. Saint-Paul was a former monastery in Saint-Rémy, located less than 30 kilometres (19 mi) from Arles, and it was run by a former naval doctor, Théophile Peyron. Van Gogh had two cells with barred windows, one of which he used as a studio. The clinic and its garden became the main subjects of his paintings.  
## Retrieve and Rerank top 10 results using RankVicuna, RankGPT¶
In [ ]:
Copied!
```
# RankVicuna
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles?",
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=True,
    model="rank_vicuna",
)

# Using RankGPT
new_nodes = get_retrieved_nodes(
    "Which date did Paul Gauguin arrive in Arles?",
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=True,
    model="gpt-3.5-turbo",
)

visualize_retrieved_nodes(new_nodes)

```

# RankVicuna new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles?", vector_top_k=10, reranker_top_n=3, with_reranker=True, model="rank_vicuna", ) # Using RankGPT new_nodes = get_retrieved_nodes( "Which date did Paul Gauguin arrive in Arles?", vector_top_k=10, reranker_top_n=3, with_reranker=True, model="gpt-3.5-turbo", ) visualize_retrieved_nodes(new_nodes)
#### For other models, use `model=`¶
  * `monot5` for MonoT5 pointwise reranker
  * `castorini/LiT5-Distill-base` for LiT5 distill reranker
  * `castorini/LiT5-Score-base` for LiT5 score reranker
  * or any hugging face model path


