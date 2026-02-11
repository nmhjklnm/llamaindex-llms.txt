# SlideNodeParser¶
SLIDE (Sliding Localized Information for Document Extraction) is a chunking method introduced to enhance entity and relationship extraction in long documents, especially for low-resource languages. It was designed to support GraphRAG pipelines by embedding localized context into each chunk without exceeding the context window of the LLM.
`SlideNodeParser` faithfully implements a almost similar version of this method to improve downstream retrieval and reasoning quality by generating short, meaningful context using a sliding window of nearby chunks. This technique is proven useful for Graph based Retrieval Augmented Generaration techniques.
Here is the technique as outlined in the paper:
```
Given a document D and a list of base chunks (C1, C2, ..., Ck) segmented by sentence boundaries and token count, SLIDE builds local context for each chunk using a fixed-size sliding window of neighboring chunks. This context is appended to the chunk using an LLM-generated summary.

The window size is a hyperparameter defined based on the model’s context length and compute budget. Each chunk Ci is enriched by including a few preceding and succeeding chunks (e.g., 5 on each side), resulting in a total of window_size + 1 inputs sent to the LLM.

This process is repeated for every chunk in the document. The result is a collection of chunks embedded with richer, window-specific local context, which significantly improves the quality of knowledge graphs and search retrieval, especially in multilingual or resource-constrained settings.

```

In [ ]:
Copied!
```
%pip install llama-index-node-parser-slide

```

%pip install llama-index-node-parser-slide
## Install ipy widgets for progress bars (Optional)¶
In [ ]:
Copied!
```
%pip install ipywidgets

```

%pip install ipywidgets
## Setup Data¶
Here we consider a sample text.
In [ ]:
Copied!
```
text = """Constructing accurate knowledge graphs from long texts and low-resource languages is challenging, as large language models (LLMs) experience degraded performance with longer input chunks.
This problem is amplified in low-resource settings where data scarcity hinders accurate entity and relationship extraction.
Contextual retrieval methods, while improving retrieval accuracy, struggle with long documents.
They truncate critical information in texts exceeding maximum context lengths of LLMs, significantly limiting knowledge graph construction.
We introduce SLIDE (Sliding Localized Information for Document Extraction), a chunking method that processes long documents by generating local context through overlapping windows.
SLIDE ensures that essential contextual information is retained, enhancing knowledge graph extraction from documents exceeding LLM context limits.
It significantly improves GraphRAG performance, achieving a 24% increase in entity extraction and a 39% improvement in relationship extraction for English.
For Afrikaans, a low-resource language, SLIDE achieves a 49% increase in entity extraction and an 82% improvement in relationship extraction.
Furthermore, it improves upon state-of-the-art in question-answering metrics such as comprehensiveness, diversity and empowerment, demonstrating its effectiveness in multilingual and resource-constrained settings.

Since SLIDE enhances knowledge graph construction in GraphRAG systems through contextual chunking, we first discuss related work in GraphRAG and chunking, highlighting their strengths and limitations.
This sets the stage for our approach, which builds on GraphRAG by using overlapping windows to improve entity and relationship extraction.
2.1 GraphRAG and Knowledge Graphs.
GraphRAG (Edge et al., 2024) is an advanced RAG framework that integrates knowledge graphs with large language models (LLMs) (Trajanoska et al., 2023) to enhance reasoning and contextual understanding.
Unlike traditional RAG systems, GraphRAG builds a knowledge graph with entities as nodes and relationships as edges, enabling precise and context-rich responses by leveraging the graph’s structure (Edge et al., 2024; Wu et al., 2024).
Large language models (LLMs), such as GPT-4, show reduced effectiveness in entity and relationship extraction as input chunk lengths increase, degrading accuracy for longer texts (Edge et al., 2024).
They also struggle with relationship extraction in low-resource languages, limiting their applicability (Chen et al., 2024; Jinensibieke et al., 2024).
Building upon this work, our approach further enhances knowledge graph extraction by incorporating localized context which improves entity and relationship extraction.
2.2 Contextual Chunking.
Recent work in RAG systems has explored advanced chunking techniques to enhance retrieval and knowledge graph construction.
Günther et al. (2024) implemented late chunking, where entire documents are embedded to capture global context before splitting into chunks, improving retrieval by emphasizing document-level coherence.
However, this focus on global embeddings is less suited for knowledge graph construction.
Our method instead uses localized context from raw text to retain meaningful relationships for improved entity and relationship extraction.
Wu et al. (2024) introduced a hybrid chunking approach for Medical Graph RAG, combining structural markers like paragraphs with semantic coherence to produce self-contained chunks.
While effective, this approach relies on predefined boundaries.
Our method extends this by generating contextual information from neighboring chunks, enhancing the completeness of knowledge graph construction.
Contextual retrieval (Anthropic, 2024) improves accuracy but struggles with longer documents, as embedding each chunk with full document context is computationally expensive and truncates critical information with documents exceeding maximum context length of the model (Jiang et al., 2024; Li et al., 2024).
Our overlapping window-based approach addresses these inefficiencies, improving performance in both retrieval and knowledge graph construction.
"""

from llama_index.core import Document

document = Document(text=text)

```

text = """Constructing accurate knowledge graphs from long texts and low-resource languages is challenging, as large language models (LLMs) experience degraded performance with longer input chunks. This problem is amplified in low-resource settings where data scarcity hinders accurate entity and relationship extraction. Contextual retrieval methods, while improving retrieval accuracy, struggle with long documents. They truncate critical information in texts exceeding maximum context lengths of LLMs, significantly limiting knowledge graph construction. We introduce SLIDE (Sliding Localized Information for Document Extraction), a chunking method that processes long documents by generating local context through overlapping windows. SLIDE ensures that essential contextual information is retained, enhancing knowledge graph extraction from documents exceeding LLM context limits. It significantly improves GraphRAG performance, achieving a 24% increase in entity extraction and a 39% improvement in relationship extraction for English. For Afrikaans, a low-resource language, SLIDE achieves a 49% increase in entity extraction and an 82% improvement in relationship extraction. Furthermore, it improves upon state-of-the-art in question-answering metrics such as comprehensiveness, diversity and empowerment, demonstrating its effectiveness in multilingual and resource-constrained settings. Since SLIDE enhances knowledge graph construction in GraphRAG systems through contextual chunking, we first discuss related work in GraphRAG and chunking, highlighting their strengths and limitations. This sets the stage for our approach, which builds on GraphRAG by using overlapping windows to improve entity and relationship extraction. 2.1 GraphRAG and Knowledge Graphs. GraphRAG (Edge et al., 2024) is an advanced RAG framework that integrates knowledge graphs with large language models (LLMs) (Trajanoska et al., 2023) to enhance reasoning and contextual understanding. Unlike traditional RAG systems, GraphRAG builds a knowledge graph with entities as nodes and relationships as edges, enabling precise and context-rich responses by leveraging the graph’s structure (Edge et al., 2024; Wu et al., 2024). Large language models (LLMs), such as GPT-4, show reduced effectiveness in entity and relationship extraction as input chunk lengths increase, degrading accuracy for longer texts (Edge et al., 2024). They also struggle with relationship extraction in low-resource languages, limiting their applicability (Chen et al., 2024; Jinensibieke et al., 2024). Building upon this work, our approach further enhances knowledge graph extraction by incorporating localized context which improves entity and relationship extraction. 2.2 Contextual Chunking. Recent work in RAG systems has explored advanced chunking techniques to enhance retrieval and knowledge graph construction. Günther et al. (2024) implemented late chunking, where entire documents are embedded to capture global context before splitting into chunks, improving retrieval by emphasizing document-level coherence. However, this focus on global embeddings is less suited for knowledge graph construction. Our method instead uses localized context from raw text to retain meaningful relationships for improved entity and relationship extraction. Wu et al. (2024) introduced a hybrid chunking approach for Medical Graph RAG, combining structural markers like paragraphs with semantic coherence to produce self-contained chunks. While effective, this approach relies on predefined boundaries. Our method extends this by generating contextual information from neighboring chunks, enhancing the completeness of knowledge graph construction. Contextual retrieval (Anthropic, 2024) improves accuracy but struggles with longer documents, as embedding each chunk with full document context is computationally expensive and truncates critical information with documents exceeding maximum context length of the model (Jiang et al., 2024; Li et al., 2024). Our overlapping window-based approach addresses these inefficiencies, improving performance in both retrieval and knowledge graph construction. """ from llama_index.core import Document document = Document(text=text)
## Setup LLM¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."  # Replace with your OpenAI API key

```

import os os.environ["OPENAI_API_KEY"] = "sk-..." # Replace with your OpenAI API key
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

embed_model = OpenAIEmbedding()
llm = OpenAI(model="gpt-4o-mini")

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI embed_model = OpenAIEmbedding() llm = OpenAI(model="gpt-4o-mini")
In [ ]:
Copied!
```
# Calculate token count of the text

from llama_index.core.utilities.token_counting import TokenCounter

token_counter = TokenCounter()
token_count = token_counter.get_string_tokens(text)
print(f"Token count: {token_count}")

```

# Calculate token count of the text from llama_index.core.utilities.token_counting import TokenCounter token_counter = TokenCounter() token_count = token_counter.get_string_tokens(text) print(f"Token count: {token_count}")
```
Token count: 759

```

## Setup SlideNodeParser¶
In [ ]:
Copied!
```
# Lets choose a chunk size of 200 tokens and window size of 5

from llama_index.node_parser.slide import SlideNodeParser

parser = SlideNodeParser.from_defaults(
    chunk_size=200,
    window_size=5,
)

```

# Lets choose a chunk size of 200 tokens and window size of 5 from llama_index.node_parser.slide import SlideNodeParser parser = SlideNodeParser.from_defaults( chunk_size=200, window_size=5, )
### Run the synchronous blocking function¶
In [ ]:
Copied!
```
import time

start_time = time.time()
nodes = parser.get_nodes_from_documents([document], show_progress=True)
end_time = time.time()
print(f"Time taken to parse: {end_time - start_time} seconds")

```

import time start_time = time.time() nodes = parser.get_nodes_from_documents([document], show_progress=True) end_time = time.time() print(f"Time taken to parse: {end_time - start_time} seconds")
## Lets inspect chunks¶
In [ ]:
Copied!
```
for i, node in enumerate(nodes):
    print(f"\n--- Chunk {i+1} ---")
    print("Text:", node.text)
    print("Local Context:", node.metadata.get("local_context"))

```

for i, node in enumerate(nodes): print(f"\n--- Chunk {i+1} ---") print("Text:", node.text) print("Local Context:", node.metadata.get("local_context"))
```
--- Chunk 1 ---
Text: Constructing accurate knowledge graphs from long texts and low-resource languages is challenging, as large language models (LLMs) experience degraded performance with longer input chunks. This problem is amplified in low-resource settings where data scarcity hinders accurate entity and relationship extraction. Contextual retrieval methods, while improving retrieval accuracy, struggle with long documents. They truncate critical information in texts exceeding maximum context lengths of LLMs, significantly limiting knowledge graph construction. We introduce SLIDE (Sliding Localized Information for Document Extraction), a chunking method that processes long documents by generating local context through overlapping windows. SLIDE ensures that essential contextual information is retained, enhancing knowledge graph extraction from documents exceeding LLM context limits. It significantly improves GraphRAG performance, achieving a 24% increase in entity extraction and a 39% improvement in relationship extraction for English. For Afrikaans, a low-resource language, SLIDE achieves a 49% increase in entity extraction and an 82% improvement in relationship extraction.
Local Context: assistant: The chunk provided introduces SLIDE (Sliding Localized Information for Document Extraction), a method that addresses the challenges of constructing accurate knowledge graphs from long texts and low-resource languages. It highlights how SLIDE improves knowledge graph extraction by processing long documents with overlapping windows, enhancing entity and relationship extraction performance significantly for both English and Afrikaans languages within the GraphRAG framework.

--- Chunk 2 ---
Text: Furthermore, it improves upon state-of-the-art in question-answering metrics such as comprehensiveness, diversity and empowerment, demonstrating its effectiveness in multilingual and resource-constrained settings.

 Since SLIDE enhances knowledge graph construction in GraphRAG systems through contextual chunking, we first discuss related work in GraphRAG and chunking, highlighting their strengths and limitations. This sets the stage for our approach, which builds on GraphRAG by using overlapping windows to improve entity and relationship extraction. 2.1 GraphRAG and Knowledge Graphs. GraphRAG (Edge et al., 2024) is an advanced RAG framework that integrates knowledge graphs with large language models (LLMs) (Trajanoska et al., 2023) to enhance reasoning and contextual understanding.
Local Context: assistant: The chunk provided discusses how SLIDE enhances knowledge graph construction in GraphRAG systems through contextual chunking. It also introduces GraphRAG as an advanced framework that integrates knowledge graphs with large language models to enhance reasoning and contextual understanding.

--- Chunk 3 ---
Text: Unlike traditional RAG systems, GraphRAG builds a knowledge graph with entities as nodes and relationships as edges, enabling precise and context-rich responses by leveraging the graph’s structure (Edge et al., 2024; Wu et al., 2024).
 Large language models (LLMs), such as GPT-4, show reduced effectiveness in entity and relationship extraction as input chunk lengths increase, degrading accuracy for longer texts (Edge et al., 2024). They also struggle with relationship extraction in low-resource languages, limiting their applicability (Chen et al., 2024; Jinensibieke et al., 2024). Building upon this work, our approach further enhances knowledge graph extraction by incorporating localized context which improves entity and relationship extraction. 2.2 Contextual Chunking. Recent work in RAG systems has explored advanced chunking techniques to enhance retrieval and knowledge graph construction. Günther et al.
Local Context: assistant: The chunk provided discusses the unique approach of GraphRAG in constructing knowledge graphs using entities and relationships, highlighting its advantages over traditional RAG systems. It also addresses the challenges faced by large language models in entity and relationship extraction, particularly in longer texts and low-resource languages. The chunk further introduces the enhancement of knowledge graph extraction through localized context and references recent advancements in chunking techniques within RAG systems.

--- Chunk 4 ---
Text: (2024) implemented late chunking, where entire documents are embedded to capture global context before splitting into chunks, improving retrieval by emphasizing document-level coherence.
 However, this focus on global embeddings is less suited for knowledge graph construction. Our method instead uses localized context from raw text to retain meaningful relationships for improved entity and relationship extraction. Wu et al. (2024) introduced a hybrid chunking approach for Medical Graph RAG, combining structural markers like paragraphs with semantic coherence to produce self-contained chunks. While effective, this approach relies on predefined boundaries. Our method extends this by generating contextual information from neighboring chunks, enhancing the completeness of knowledge graph construction. Contextual retrieval (Anthropic, 2024) improves accuracy but struggles with longer documents, as embedding each chunk with full document context is computationally expensive and truncates critical information with documents exceeding maximum context length of the model (Jiang et al., 2024; Li et al., 2024).
Local Context: assistant: This chunk discusses different chunking approaches in the context of knowledge graph construction within RAG systems. It contrasts the use of global embeddings for document-level coherence with localized context for improved entity and relationship extraction. It also mentions a hybrid chunking approach introduced by Wu et al. for Medical Graph RAG, highlighting the importance of contextual information from neighboring chunks in enhancing knowledge graph completeness.

--- Chunk 5 ---
Text: Our overlapping window-based approach addresses these inefficiencies, improving performance in both retrieval and knowledge graph construction.

Local Context: assistant: The chunk provided discusses an overlapping window-based approach that aims to address inefficiencies in retrieval and knowledge graph construction, as part of a broader discussion on enhancing RAG systems through advanced chunking techniques and contextual retrieval methods.

```

### Lets run the asynchronous version with parallel LLM calls¶
In [ ]:
Copied!
```
parser.llm_workers = 4
start_time = time.time()
nodes = await parser.aget_nodes_from_documents([document], show_progress=True)
end_time = time.time()
print(f"Time taken to parse: {end_time - start_time} seconds")

```

parser.llm_workers = 4 start_time = time.time() nodes = await parser.aget_nodes_from_documents([document], show_progress=True) end_time = time.time() print(f"Time taken to parse: {end_time - start_time} seconds")
## Lets inspect the chunks¶
In [ ]:
Copied!
```
for i, node in enumerate(nodes):
    print(f"\n--- Chunk {i+1} ---")
    print("Text:", node.text)
    print("Local Context:", node.metadata.get("local_context"))

```

for i, node in enumerate(nodes): print(f"\n--- Chunk {i+1} ---") print("Text:", node.text) print("Local Context:", node.metadata.get("local_context"))
```
--- Chunk 1 ---
Text: Constructing accurate knowledge graphs from long texts and low-resource languages is challenging, as large language models (LLMs) experience degraded performance with longer input chunks. This problem is amplified in low-resource settings where data scarcity hinders accurate entity and relationship extraction. Contextual retrieval methods, while improving retrieval accuracy, struggle with long documents. They truncate critical information in texts exceeding maximum context lengths of LLMs, significantly limiting knowledge graph construction. We introduce SLIDE (Sliding Localized Information for Document Extraction), a chunking method that processes long documents by generating local context through overlapping windows. SLIDE ensures that essential contextual information is retained, enhancing knowledge graph extraction from documents exceeding LLM context limits. It significantly improves GraphRAG performance, achieving a 24% increase in entity extraction and a 39% improvement in relationship extraction for English. For Afrikaans, a low-resource language, SLIDE achieves a 49% increase in entity extraction and an 82% improvement in relationship extraction.
Local Context: assistant: The chunk provided introduces SLIDE (Sliding Localized Information for Document Extraction), a method that addresses the challenges of constructing accurate knowledge graphs from long texts and low-resource languages. It highlights how SLIDE improves knowledge graph extraction by processing long documents with overlapping windows, enhancing entity and relationship extraction performance significantly for both English and Afrikaans languages within the GraphRAG framework.

--- Chunk 2 ---
Text: Furthermore, it improves upon state-of-the-art in question-answering metrics such as comprehensiveness, diversity and empowerment, demonstrating its effectiveness in multilingual and resource-constrained settings.

 Since SLIDE enhances knowledge graph construction in GraphRAG systems through contextual chunking, we first discuss related work in GraphRAG and chunking, highlighting their strengths and limitations. This sets the stage for our approach, which builds on GraphRAG by using overlapping windows to improve entity and relationship extraction. 2.1 GraphRAG and Knowledge Graphs. GraphRAG (Edge et al., 2024) is an advanced RAG framework that integrates knowledge graphs with large language models (LLMs) (Trajanoska et al., 2023) to enhance reasoning and contextual understanding.
Local Context: assistant: The chunk provided discusses how SLIDE enhances knowledge graph construction in GraphRAG systems through contextual chunking. It also introduces related work in GraphRAG and chunking, setting the stage for the approach that builds on GraphRAG by using overlapping windows to improve entity and relationship extraction.

--- Chunk 3 ---
Text: Unlike traditional RAG systems, GraphRAG builds a knowledge graph with entities as nodes and relationships as edges, enabling precise and context-rich responses by leveraging the graph’s structure (Edge et al., 2024; Wu et al., 2024).
 Large language models (LLMs), such as GPT-4, show reduced effectiveness in entity and relationship extraction as input chunk lengths increase, degrading accuracy for longer texts (Edge et al., 2024). They also struggle with relationship extraction in low-resource languages, limiting their applicability (Chen et al., 2024; Jinensibieke et al., 2024). Building upon this work, our approach further enhances knowledge graph extraction by incorporating localized context which improves entity and relationship extraction. 2.2 Contextual Chunking. Recent work in RAG systems has explored advanced chunking techniques to enhance retrieval and knowledge graph construction. Günther et al.
Local Context: assistant: The chunk provided discusses how GraphRAG differs from traditional RAG systems by constructing knowledge graphs with entities as nodes and relationships as edges, leading to precise responses. It also highlights the challenges faced by large language models in entity and relationship extraction, especially in longer texts and low-resource languages. The approach presented in the chunk aims to enhance knowledge graph extraction by incorporating localized context to improve entity and relationship extraction, building upon existing research in contextual chunking techniques within RAG systems.

--- Chunk 4 ---
Text: (2024) implemented late chunking, where entire documents are embedded to capture global context before splitting into chunks, improving retrieval by emphasizing document-level coherence.
 However, this focus on global embeddings is less suited for knowledge graph construction. Our method instead uses localized context from raw text to retain meaningful relationships for improved entity and relationship extraction. Wu et al. (2024) introduced a hybrid chunking approach for Medical Graph RAG, combining structural markers like paragraphs with semantic coherence to produce self-contained chunks. While effective, this approach relies on predefined boundaries. Our method extends this by generating contextual information from neighboring chunks, enhancing the completeness of knowledge graph construction. Contextual retrieval (Anthropic, 2024) improves accuracy but struggles with longer documents, as embedding each chunk with full document context is computationally expensive and truncates critical information with documents exceeding maximum context length of the model (Jiang et al., 2024; Li et al., 2024).
Local Context: assistant: This chunk discusses different approaches to chunking in the context of knowledge graph construction within RAG systems. It contrasts the use of global embeddings for document-level coherence with the utilization of localized context for improved entity and relationship extraction. Additionally, it mentions a hybrid chunking approach introduced by Wu et al. for Medical Graph RAG, highlighting the importance of generating contextual information from neighboring chunks to enhance knowledge graph completeness.

--- Chunk 5 ---
Text: Our overlapping window-based approach addresses these inefficiencies, improving performance in both retrieval and knowledge graph construction.

Local Context: assistant: The chunk provided discusses an overlapping window-based approach that addresses inefficiencies in retrieval and knowledge graph construction, aiming to improve performance within the broader context of advanced chunking techniques and knowledge graph extraction strategies discussed in the document.

```

