# LLM Reranker Demonstration (Great Gatsby)¶
This tutorial showcases how to do a two-stage pass for retrieval. Use embedding-based retrieval with a high top-k value in order to maximize recall and get a large set of candidate items. Then, use LLM-based retrieval to dynamically select the nodes that are actually relevant to the query.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
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
## Load Data, Build Index¶
In [ ]:
Copied!
```
from llama_index.core import Settings

# LLM (gpt-3.5-turbo)
Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.chunk_size = 512

```

from llama_index.core import Settings # LLM (gpt-3.5-turbo) Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.chunk_size = 512
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("../../../examples/gatsby/data").load_data()

```

# load documents documents = SimpleDirectoryReader("../../../examples/gatsby/data").load_data()
In [ ]:
Copied!
```
documents

```

documents
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(
    documents,
)

```

index = VectorStoreIndex.from_documents( documents, )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 49266 tokens
> [build_index_from_nodes] Total embedding token usage: 49266 tokens

```

## Retrieval¶
In [ ]:
Copied!
```
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
import pandas as pd
from IPython.display import display, HTML


pd.set_option("display.max_colwidth", -1)


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
        reranker = LLMRerank(
            choice_batch_size=5,
            top_n=reranker_top_n,
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

from llama_index.core.retrievers import VectorIndexRetriever from llama_index.core import QueryBundle import pandas as pd from IPython.display import display, HTML pd.set_option("display.max_colwidth", -1) def get_retrieved_nodes( query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False ): query_bundle = QueryBundle(query_str) # configure retriever retriever = VectorIndexRetriever( index=index, similarity_top_k=vector_top_k, ) retrieved_nodes = retriever.retrieve(query_bundle) if with_reranker: # configure reranker reranker = LLMRerank( choice_batch_size=5, top_n=reranker_top_n, ) retrieved_nodes = reranker.postprocess_nodes( retrieved_nodes, query_bundle ) return retrieved_nodes def pretty_print(df): return display(HTML(df.to_html().replace("\\\n", "  
"))) def visualize_retrieved_nodes(nodes) -> None: result_dicts = [] for node in nodes: result_dict = {"Score": node.score, "Text": node.node.get_text()} result_dicts.append(result_dict) pretty_print(pd.DataFrame(result_dicts))
```
/var/folders/1r/c3h91d9s49xblwfvz79s78_c0000gn/T/ipykernel_44297/3519340226.py:7: FutureWarning: Passing a negative integer is deprecated in version 1.0 and will not be supported in future version. Instead, use None to not limit the column width.
  pd.set_option('display.max_colwidth', -1)

```

In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Who was driving the car that hit Myrtle?",
    vector_top_k=3,
    with_reranker=False,
)

```

new_nodes = get_retrieved_nodes( "Who was driving the car that hit Myrtle?", vector_top_k=3, with_reranker=False, )
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 10 tokens
> [retrieve] Total embedding token usage: 10 tokens

```

In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 0.828844 | and some garrulous man telling over and over what  
had happened, until it became less and less real even to him and he  
could tell it no longer, and Myrtle Wilson’s tragic achievement was  
forgotten. Now I want to go back a little and tell what happened at  
the garage after we left there the night before.  
  
They had difficulty in locating the sister, Catherine. She must have  
broken her rule against drinking that night, for when she arrived she  
was stupid with liquor and unable to understand that the ambulance had  
already gone to Flushing. When they convinced her of this, she  
immediately fainted, as if that was the intolerable part of the  
affair. Someone, kind or curious, took her in his car and drove her in  
the wake of her sister’s body.  
  
Until long after midnight a changing crowd lapped up against the front  
of the garage, while George Wilson rocked himself back and forth on  
the couch inside. For a while the door of the office was open, and  
everyone who came into the garage glanced irresistibly through it.  
Finally someone said it was a shame, and closed the door. Michaelis  
and several other men were with him; first, four or five men, later  
two or three men. Still later Michaelis had to ask the last stranger  
to wait there fifteen minutes longer, while he went back to his own  
place and made a pot of coffee. After that, he stayed there alone with  
Wilson until dawn.  
  
About three o’clock the quality of Wilson’s incoherent muttering  
changed—he grew quieter and began to talk about the yellow car. He  
announced that he had a way of finding out whom the yellow car  
belonged to, and then he blurted out that a couple of months ago his  
wife had come from the city with her face bruised and her nose  
swollen.  
  
But when he heard himself say this, he flinched and began to cry “Oh,  
my God!” again in his groaning voice. Michaelis made a clumsy  
1 | 0.827754 | she rushed out into the dusk, waving her hands and  
shouting—before he could move from his door the business was over.  
  
The “death car” as the newspapers called it, didn’t stop; it came out  
of the gathering darkness, wavered tragically for a moment, and then  
disappeared around the next bend. Mavro Michaelis wasn’t even sure of  
its colour—he told the first policeman that it was light green. The  
other car, the one going toward New York, came to rest a hundred yards  
beyond, and its driver hurried back to where Myrtle Wilson, her life  
violently extinguished, knelt in the road and mingled her thick dark  
blood with the dust.  
  
Michaelis and this man reached her first, but when they had torn open  
her shirtwaist, still damp with perspiration, they saw that her left  
breast was swinging loose like a flap, and there was no need to listen  
for the heart beneath. The mouth was wide open and ripped a little at  
the corners, as though she had choked a little in giving up the  
tremendous vitality she had stored so long.  
  
------------------------------------------------------------------------  
  
We saw the three or four automobiles and the crowd when we were still  
some distance away.  
  
“Wreck!” said Tom. “That’s good. Wilson’ll have a little business at  
last.”  
  
He slowed down, but still without any intention of stopping, until, as  
we came nearer, the hushed, intent faces of the people at the garage  
door made him automatically put on the brakes.  
  
“We’ll take a look,” he said doubtfully, “just a look.”  
  
I became aware now of a hollow, wailing sound which issued incessantly  
from the garage, a sound which as we got out of the coupé and walked  
toward the door resolved itself into the words “Oh, my God!” uttered  
over and over in a gasping  
2 | 0.826390 | went on, “and left the car in  
my garage. I don’t think anybody saw us, but of course I can’t be  
sure.”  
  
I disliked him so much by this time that I didn’t find it necessary to  
tell him he was wrong.  
  
“Who was the woman?” he inquired.  
  
“Her name was Wilson. Her husband owns the garage. How the devil did  
it happen?”  
  
“Well, I tried to swing the wheel—” He broke off, and suddenly I  
guessed at the truth.  
  
“Was Daisy driving?”  
  
“Yes,” he said after a moment, “but of course I’ll say I was. You see,  
when we left New York she was very nervous and she thought it would  
steady her to drive—and this woman rushed out at us just as we were  
passing a car coming the other way. It all happened in a minute, but  
it seemed to me that she wanted to speak to us, thought we were  
somebody she knew. Well, first Daisy turned away from the woman toward  
the other car, and then she lost her nerve and turned back. The second  
my hand reached the wheel I felt the shock—it must have killed her  
instantly.”  
  
“It ripped her open—”  
  
“Don’t tell me, old sport.” He winced. “Anyhow—Daisy stepped on it. I  
tried to make her stop, but she couldn’t, so I pulled on the emergency  
brake. Then she fell over into my lap and I drove on.  
  
“She’ll be all right tomorrow,” he said presently. “I’m just going to  
wait here and see if he tries to bother her about that unpleasantness  
this afternoon. She’s locked herself into her room, and if he tries  
any brutality she’s going to turn the light out and on again.”  
  
“He won’t touch  
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "Who was driving the car that hit Myrtle?",
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=True,
)

```

new_nodes = get_retrieved_nodes( "Who was driving the car that hit Myrtle?", vector_top_k=10, reranker_top_n=3, with_reranker=True, )
In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 10.0 | went on, “and left the car in  
my garage. I don’t think anybody saw us, but of course I can’t be  
sure.”  
  
I disliked him so much by this time that I didn’t find it necessary to  
tell him he was wrong.  
  
“Who was the woman?” he inquired.  
  
“Her name was Wilson. Her husband owns the garage. How the devil did  
it happen?”  
  
“Well, I tried to swing the wheel—” He broke off, and suddenly I  
guessed at the truth.  
  
“Was Daisy driving?”  
  
“Yes,” he said after a moment, “but of course I’ll say I was. You see,  
when we left New York she was very nervous and she thought it would  
steady her to drive—and this woman rushed out at us just as we were  
passing a car coming the other way. It all happened in a minute, but  
it seemed to me that she wanted to speak to us, thought we were  
somebody she knew. Well, first Daisy turned away from the woman toward  
the other car, and then she lost her nerve and turned back. The second  
my hand reached the wheel I felt the shock—it must have killed her  
instantly.”  
  
“It ripped her open—”  
  
“Don’t tell me, old sport.” He winced. “Anyhow—Daisy stepped on it. I  
tried to make her stop, but she couldn’t, so I pulled on the emergency  
brake. Then she fell over into my lap and I drove on.  
  
“She’ll be all right tomorrow,” he said presently. “I’m just going to  
wait here and see if he tries to bother her about that unpleasantness  
this afternoon. She’s locked herself into her room, and if he tries  
any brutality she’s going to turn the light out and on again.”  
  
“He won’t touch  
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "What did Gatsby want Daisy to do in front of Tom?",
    vector_top_k=3,
    with_reranker=False,
)

```

new_nodes = get_retrieved_nodes( "What did Gatsby want Daisy to do in front of Tom?", vector_top_k=3, with_reranker=False, )
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 14 tokens
> [retrieve] Total embedding token usage: 14 tokens

```

In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
```

****Score****: 0.8647796939111776
****Node text****
: got to make your house into a pigsty in order to have any
friends—in the modern world.”

Angry as I was, as we all were, I was tempted to laugh whenever he
opened his mouth. The transition from libertine to prig was so
complete.

“I’ve got something to tell you, old sport—” began Gatsby. But Daisy
guessed at his intention.

“Please don’t!” she interrupted helplessly. “Please let’s all go
home. Why don’t we all go home?”

“That’s a good idea,” I got up. “Come on, Tom. Nobody wants a drink.”

“I want to know what Mr. Gatsby has to tell me.”

“Your wife doesn’t love you,” said Gatsby. “She’s never loved you.
She loves me.”

“You must be crazy!” exclaimed Tom automatically.

Gatsby sprang to his feet, vivid with excitement.

“She never loved you, do you hear?” he cried. “She only married you
because I was poor and she was tired of waiting for me. It was a
terrible mistake, but in her heart she never loved anyone except me!”

At this point Jordan and I tried to go, but Tom and Gatsby insisted
with competitive firmness that we remain—as though neither of them had
anything to conceal and it would be a privilege to partake vicariously
of their emotions.

“Sit down, Daisy,” Tom’s voice groped unsuccessfully for the paternal
note. “What’s been going on? I want to hear all about it.”

“I told you what’s been going on,” said Gatsby. “Going on for five
years—and you didn’t know.”

Tom turned to Daisy


****Score****: 0.8609230717744326
****Node text****
: to keep your
shoes dry?” There was a husky tenderness in his tone … “Daisy?”

“Please don’t.” Her voice was cold, but the rancour was gone from it.
She looked at Gatsby. “There, Jay,” she said—but her hand as she tried
to light a cigarette was trembling. Suddenly she threw the cigarette
and the burning match on the carpet.

“Oh, you want too much!” she cried to Gatsby. “I love you now—isn’t
that enough? I can’t help what’s past.” She began to sob
helplessly. “I did love him once—but I loved you too.”

Gatsby’s eyes opened and closed.

“You loved me too?” he repeated.

“Even that’s a lie,” said Tom savagely. “She didn’t know you were
alive. Why—there’s things between Daisy and me that you’ll never know,
things that neither of us can ever forget.”

The words seemed to bite physically into Gatsby.

“I want to speak to Daisy alone,” he insisted. “She’s all excited
now—”

“Even alone I can’t say I never loved Tom,” she admitted in a pitiful
voice. “It wouldn’t be true.”

“Of course it wouldn’t,” agreed Tom.

She turned to her husband.

“As if it mattered to you,” she said.

“Of course it matters. I’m going to take better care of you from now
on.”

“You don’t understand,” said Gatsby, with a touch of panic. “You’re
not going to take care of her any more.”

“I’m not?” Tom opened his eyes wide and


****Score****: 0.8555028907426916
****Node text****
: shadowed well with awnings, was dark and cool. Daisy and
Jordan lay upon an enormous couch, like silver idols weighing down
their own white dresses against the singing breeze of the fans.

“We can’t move,” they said together.

Jordan’s fingers, powdered white over their tan, rested for a moment
in mine.

“And Mr. Thomas Buchanan, the athlete?” I inquired.

Simultaneously I heard his voice, gruff, muffled, husky, at the hall
telephone.

Gatsby stood in the centre of the crimson carpet and gazed around with
fascinated eyes. Daisy watched him and laughed, her sweet, exciting
laugh; a tiny gust of powder rose from her bosom into the air.

“The rumour is,” whispered Jordan, “that that’s Tom’s girl on the
telephone.”

We were silent. The voice in the hall rose high with annoyance: “Very
well, then, I won’t sell you the car at all … I’m under no obligations
to you at all … and as for your bothering me about it at lunch time, I
won’t stand that at all!”

“Holding down the receiver,” said Daisy cynically.

“No, he’s not,” I assured her. “It’s a bona-fide deal. I happen to
know about it.”

Tom flung open the door, blocked out its space for a moment with his
thick body, and hurried into the room.

“Mr. Gatsby!” He put out his broad, flat hand with well-concealed
dislike. “I’m glad to see you, sir … Nick …”

“Make us a cold drink,” cried Daisy.

As he left the room again she got up and went over to Gatsby and
pulled his face

```

In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "What did Gatsby want Daisy to do in front of Tom?",
    vector_top_k=10,
    reranker_top_n=3,
    with_reranker=True,
)

```

new_nodes = get_retrieved_nodes( "What did Gatsby want Daisy to do in front of Tom?", vector_top_k=10, reranker_top_n=3, with_reranker=True, )
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 14 tokens
> [retrieve] Total embedding token usage: 14 tokens
Doc: 2, Relevance: 10
No relevant documents found. Please provide a different question.

```

In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
```

****Score****: 10.0
****Node text****
: to keep your
shoes dry?” There was a husky tenderness in his tone … “Daisy?”

“Please don’t.” Her voice was cold, but the rancour was gone from it.
She looked at Gatsby. “There, Jay,” she said—but her hand as she tried
to light a cigarette was trembling. Suddenly she threw the cigarette
and the burning match on the carpet.

“Oh, you want too much!” she cried to Gatsby. “I love you now—isn’t
that enough? I can’t help what’s past.” She began to sob
helplessly. “I did love him once—but I loved you too.”

Gatsby’s eyes opened and closed.

“You loved me too?” he repeated.

“Even that’s a lie,” said Tom savagely. “She didn’t know you were
alive. Why—there’s things between Daisy and me that you’ll never know,
things that neither of us can ever forget.”

The words seemed to bite physically into Gatsby.

“I want to speak to Daisy alone,” he insisted. “She’s all excited
now—”

“Even alone I can’t say I never loved Tom,” she admitted in a pitiful
voice. “It wouldn’t be true.”

“Of course it wouldn’t,” agreed Tom.

She turned to her husband.

“As if it mattered to you,” she said.

“Of course it matters. I’m going to take better care of you from now
on.”

“You don’t understand,” said Gatsby, with a touch of panic. “You’re
not going to take care of her any more.”

“I’m not?” Tom opened his eyes wide and

```

## Query Engine¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[
        LLMRerank(
            choice_batch_size=5,
            top_n=2,
        )
    ],
    response_mode="tree_summarize",
)
response = query_engine.query(
    "What did the author do during his time at Y Combinator?",
)

```

query_engine = index.as_query_engine( similarity_top_k=10, node_postprocessors=[ LLMRerank( choice_batch_size=5, top_n=2, ) ], response_mode="tree_summarize", ) response = query_engine.query( "What did the author do during his time at Y Combinator?", )
