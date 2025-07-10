![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Vectara Managed Index¶
In this notebook we are going to show how to use Vectara with LlamaIndex. Please note that this notebook is for Vectara ManagedIndex versions >=0.4.0.
Vectara is the trusted AI Assistant and Agent platform which focuses on enterprise readiness for mission-critical applications.
Vectara provides an end-to-end managed service for Retrieval Augmented Generation or RAG, which includes:
  1. An integrated API for processing input data, including text extraction from documents and ML-based chunking.
  2. The state-of-the-art Boomerang embeddings model. Each text chunk is encoded into a vector embedding using Boomerang, and stored in the Vectara internal knowledge (vector+text) store. Thus, when using Vectara with LlamaIndex you do not need to call a separate embedding model - this happens automatically within the Vectara backend.
  3. A query service that automatically encodes the query into embeddings and retrieves the most relevant text segmentsthrough hybrid search and a variety of reranking strategies, including a multilingual reranker, maximal marginal relevance (MMR) reranker, user-defined function reranker, and a chain reranker that provides a way to chain together multiple reranking methods to achieve better control over the reranking, combining the strengths of various reranking methods.
  4. An option to create a generative summary with a wide selection of LLM summarizers (including Vectara's Mockingbird, trained specifically for RAG-based tasks), based on the retrieved documents, including citations.


See the Vectara API documentation for more information on how to use the API.
The main benefits of using Vectara RAG-as-a-service to build your application are:
  * **Accuracy and Quality** : Vectara provides an end-to-end platform that focuses on eliminating hallucinations, reducing bias, and safeguarding copyright integrity.
  * **Security** : Vectara's platform provides acess control--protecting against prompt injection attacks--and meets SOC2 and HIPAA compliance.
  * **Explainability** : Vectara makes it easy to troubleshoot bad results by clearly explaining rephrased queries, LLM prompts, retrieved results, and agent actions.


## Getting Started¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index llama-index-indices-managed-vectara

```

!pip install llama-index llama-index-indices-managed-vectara
To get started with Vectara, sign up (if you haven't already) and follow our quickstart guide to create a corpus and an API key.
Once you have these, you can provide them as environment variables `VECTARA_CORPUS_KEY`, and `VECTARA_API_KEY`. Make sure your API key has both query and index permissions.
## RAG with LlamaIndex and Vectara¶
There are a few ways you can index your data into Vectara, including:
  1. With the `from_documents()` or `insert_file()` methods of `VectaraIndex`
  2. Uploading files directly in the Vectara console
  3. Using Vectara's file upload or document index APIs
  4. Using vectara-ingest, an open source crawler/indexer project
  5. Using one of our ingest integration partners like Airbyte, Unstructured or DataVolo.


For this purpose, we will use a simple set of small documents, so using `VectaraIndex` directly for the ingest is good enough.
Let's ingest the "AI bill of rights" document into our new corpus.
In [ ]:
Copied!
```
from llama_index.indices.managed.vectara import VectaraIndex
import requests

url = "https://www.whitehouse.gov/wp-content/uploads/2022/10/Blueprint-for-an-AI-Bill-of-Rights.pdf"
response = requests.get(url)
local_path = "ai-bill-of-rights.pdf"
with open(local_path, "wb") as file:
    file.write(response.content)

index = VectaraIndex()
index.insert_file(
    local_path, metadata={"name": "AI bill of rights", "year": 2022}
)

```

from llama_index.indices.managed.vectara import VectaraIndex import requests url = "https://www.whitehouse.gov/wp-content/uploads/2022/10/Blueprint-for-an-AI-Bill-of-Rights.pdf" response = requests.get(url) local_path = "ai-bill-of-rights.pdf" with open(local_path, "wb") as file: file.write(response.content) index = VectaraIndex() index.insert_file( local_path, metadata={"name": "AI bill of rights", "year": 2022} )
Out[ ]:
```
'ai-bill-of-rights.pdf'
```

### Running single queries with Vectara Query Engine¶
Now that we've uploaded the document (or if documents have been uploaded previously) we can go and ask questions directly in LlamaIndex. This activates Vectara's RAG pipeline.
To use Vectara's internal LLM for summarization, make sure you specify `summary_enabled=True` when you generate the Query engine. Here's an example:
In [ ]:
Copied!
```
questions = [
    "What are the risks of AI?",
    "What should we do to prevent bad actors from using AI?",
    "What are the benefits?",
]

```

questions = [ "What are the risks of AI?", "What should we do to prevent bad actors from using AI?", "What are the benefits?", ]
In [ ]:
Copied!
```
qe = index.as_query_engine(
    n_sentences_before=1,
    n_sentences_after=1,
    summary_enabled=True,
    summary_prompt_name="mockingbird-1.0-2024-07-16",
)
qe.query(questions[0]).response

```

qe = index.as_query_engine( n_sentences_before=1, n_sentences_after=1, summary_enabled=True, summary_prompt_name="mockingbird-1.0-2024-07-16", ) qe.query(questions[0]).response
Out[ ]:
```
'The risks of AI include biased data and discriminatory outcomes, opaque decision-making processes, and lack of public trust and understanding of algorithmic systems [1]. These risks can have significant impacts on individuals and communities, particularly those who are directly affected by AI systems [5]. To mitigate these risks, it is essential to identify and address potential risks before deployment, and to implement ongoing monitoring and mitigation strategies [2][6]. This includes risk assessments, auditing mechanisms, and public consultation to ensure that AI systems are designed and used in a responsible and transparent manner [2][6]. Additionally, the development of AI systems should be guided by principles that prioritize lawfulness, accuracy, and transparency, and that are regularly monitored and accountable [7].'
```

If you want the response to be returned in streaming mode, simply set `streaming=True`
In [ ]:
Copied!
```
qe = index.as_query_engine(
    n_sentences_before=1,
    n_sentences_after=1,
    summary_enabled=True,
    summary_prompt_name="mockingbird-1.0-2024-07-16",
    streaming=True,
)
response = qe.query(questions[0])

response.print_response_stream()

```

qe = index.as_query_engine( n_sentences_before=1, n_sentences_after=1, summary_enabled=True, summary_prompt_name="mockingbird-1.0-2024-07-16", streaming=True, ) response = qe.query(questions[0]) response.print_response_stream()
```
The risks of AI include biased data and discriminatory outcomes, opaque decision-making processes, and lack of public trust and understanding of algorithmic systems [1]. These risks can have significant impacts on individuals and communities, particularly those who are directly affected by AI systems [5]. To mitigate these risks, it is essential to identify and address potential risks before deployment, and to implement ongoing monitoring and mitigation strategies [2][6]. This includes risk assessments, auditing mechanisms, and public consultation to ensure that AI systems are designed and used in a responsible and transparent manner [2][6]. Additionally, the development of AI systems should be guided by principles that prioritize lawfulness, accuracy, and transparency, and that are regularly monitored and accountable [7].
```

### Using Vectara Chat¶
Vectara also supports a simple chat mode. In this mode the chat history is maintained by Vectara and so you don't have to worry about it. To use it simple call `as_chat_engine`.
(Chat mode always uses Vectara's summarization so you don't have to explicitly specify `summary_enabled=True` like before)
In [ ]:
Copied!
```
ce = index.as_chat_engine(n_sentences_before=1, n_sentences_after=1)

```

ce = index.as_chat_engine(n_sentences_before=1, n_sentences_after=1)
In [ ]:
Copied!
```
for q in questions:
    print(f"Question: {q}\n")
    response = ce.chat(q).response
    print(f"Response: {response}\n")

```

for q in questions: print(f"Question: {q}\n") response = ce.chat(q).response print(f"Response: {response}\n")
```
Question: What are the risks of AI?

Response: The risks of AI include potential biases and discriminatory outcomes due to biased data, opaque decision-making processes, and lack of public trust and understanding of algorithmic systems. Mitigating these risks involves ongoing transparency, participatory design, explanations for stakeholders, and public consultation [1]. Industry is developing innovative solutions like risk assessments, auditing mechanisms, and monitoring tools to ensure the safety and efficacy of AI systems [2]. Identifying and mitigating risks before deployment is crucial, focusing on impacts on rights, opportunities, and communities, as well as risks from misuse of the system [6]. The Executive Order on Trustworthy AI in the Federal Government outlines principles for lawful, purposeful, accurate, safe, understandable, responsible, monitored, transparent, and accountable AI use [7].

Question: What should we do to prevent bad actors from using AI?

Response: To prevent bad actors from using AI, we should implement a set of principles and practices to ensure the safe and effective use of AI systems. This includes adhering to specific principles such as legality, respect for values, accuracy, reliability, safety, transparency, and accountability in the design and use of AI [2]. Additionally, entities should follow privacy and security best practices to prevent data leaks and employ audits and impact assessments to identify and mitigate algorithmic discrimination [3][4]. It is crucial to involve the public in discussions about the promises and potential harms of AI technologies to shape policies that protect against discrimination and ensure fairness in the use of automated systems [1][6][7]. By promoting transparency, ongoing monitoring, and public consultation, we can work towards building trust, understanding, and ethical use of AI while safeguarding against misuse by bad actors.

Question: What are the benefits?

Response: The benefits of AI include the potential to build innovative infrastructure, improve customer service through faster responses, and enhance decision-making processes. AI can also lead to transformative improvements in people's lives, protect individuals from potential harms, and ensure the ethical use of automated systems. By incorporating principles for responsible stewardship and trustworthy AI, companies and government agencies can create safe, effective, and transparent AI systems that respect values, ensure accuracy, and promote accountability [1][4][6][7].


```

Of course streaming works as well with Chat:
In [ ]:
Copied!
```
ce = index.as_chat_engine(
    n_sentences_before=1, n_sentences_after=1, streaming=True
)

```

ce = index.as_chat_engine( n_sentences_before=1, n_sentences_after=1, streaming=True )
In [ ]:
Copied!
```
response = ce.stream_chat("Will artificial intelligence rule the government?")

response.print_response_stream()

```

response = ce.stream_chat("Will artificial intelligence rule the government?") response.print_response_stream()
```
Artificial intelligence will not rule the government. The government has established principles and guidelines for the ethical use of AI, ensuring it is used responsibly, lawfully, and in alignment with the nation's values. These principles emphasize safety, accountability, transparency, and regular monitoring of AI systems within the federal government [1] [2]. Additionally, there are specific considerations for law enforcement and national security activities, highlighting the need for oversight and adherence to existing policies and safeguards [3]. The government is focused on promoting equity, fairness, civil rights, and racial justice through the use of AI, guided by principles that protect the American public [5]. Transparency and accountability are key aspects to ensure that AI technologies are used in ways that respect people's rights and expectations [7].
```

### Agentic RAG¶
Vectara also has its own package, vectara-agentic, built on top of many features from LlamaIndex to easily implement agentic RAG applications. It allows you to create your own AI assistant with RAG query tools and other custom tools, such as making API calls to retrieve information from financial websites. You can find the full documentation for vectara-agentic here.
Let's create a ReAct Agent with a single RAG tool using vectara-agentic (to create a ReAct agent, specify `VECTARA_AGENTIC_AGENT_TYPE` as `"REACT"` in your environment).
Vectara does not yet have an LLM capable of acting as an agent for planning and tool use, so we will need to use another LLM as the driver of the agent resoning.
In this demo, we are using OpenAI's GPT4o. Please make sure you have `OPENAI_API_KEY` defined in your environment or specify another LLM with the corresponding key (for the full list of supported LLMs, check out our documentation for setting up your environment).
In [ ]:
Copied!
```
!pip install -U vectara-agentic

```

!pip install -U vectara-agentic
In [ ]:
Copied!
```
from vectara_agentic.agent import Agent
from IPython.display import display, Markdown

agent = Agent.from_corpus(
    tool_name="query_ai",
    data_description="AI regulations",
    assistant_specialty="artificial intelligence",
    vectara_reranker="mmr",
    vectara_rerank_k=50,
    vectara_summary_num_results=5,
    vectara_summarizer="mockingbird-1.0-2024-07-16",
    verbose=True,
)

response = agent.chat(
    "What are the risks of AI? What are the benefits? Compare and contrast and provide a summary with arguments for and against from experts."
)

display(Markdown(response))

```

from vectara_agentic.agent import Agent from IPython.display import display, Markdown agent = Agent.from_corpus( tool_name="query_ai", data_description="AI regulations", assistant_specialty="artificial intelligence", vectara_reranker="mmr", vectara_rerank_k=50, vectara_summary_num_results=5, vectara_summarizer="mockingbird-1.0-2024-07-16", verbose=True, ) response = agent.chat( "What are the risks of AI? What are the benefits? Compare and contrast and provide a summary with arguments for and against from experts." ) display(Markdown(response))
```
Failed to set up observer (No module named 'phoenix.otel'), ignoring
> Running step 21fe2d4d-c74c-45df-9921-94c7f9e4f670. Step input: What are the risks of AI? What are the benefits? Compare and contrast and provide a summary with arguments for and against from experts.
Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
Action: query_ai
Action Input: {'query': 'risks and benefits of AI, expert opinions'}
Observation: 
                    Response: '''According to expert opinions, the risks of AI include biased data and discriminatory outcomes, opaque decision-making processes, and lack of public trust and understanding of algorithmic systems [1]. To mitigate these risks, experts emphasize the importance of ongoing transparency, value-sensitive and participatory design, explanations designed for relevant stakeholders, and public consultation [1]. Additionally, industry is providing innovative solutions to mitigate risks to the safety and efficacy of AI systems, including risk assessments, auditing mechanisms, and documentation procedures [3]. The National Institute of Standards and Technology (NIST) is developing a risk management framework to better manage risks posed to individuals, organizations, and society by AI [3]. Furthermore, the White House Office of Science and Technology Policy has led a year-long process to seek input from people across the country on the issue of algorithmic and data-driven harms and potential remedies [4].'''
                    References:
                    [1]: CreationDate='1663695035'; Producer='iLovePDF'; Title='Blueprint for an AI Bill of Rights'; Creator='Adobe Illustrator 26.3 (Macintosh)'; ModDate='1664808078'; name='AI bill of rights'; year='2022'; framework='llama_index'; title='Blueprint for an AI Bill of Rights'.
[3]: CreationDate='1663695035'; Producer='iLovePDF'; Title='Blueprint for an AI Bill of Rights'; Creator='Adobe Illustrator 26.3 (Macintosh)'; ModDate='1664808078'; name='AI bill of rights'; year='2022'; framework='llama_index'; title='Blueprint for an AI Bill of Rights'.
[4]: CreationDate='1663695035'; Producer='iLovePDF'; Title='Blueprint for an AI Bill of Rights'; Creator='Adobe Illustrator 26.3 (Macintosh)'; ModDate='1664808078'; name='AI bill of rights'; year='2022'; framework='llama_index'; title='Blueprint for an AI Bill of Rights'.

                
> Running step a2b4d751-9f91-4fd9-9004-e276da54b75f. Step input: None
Thought: I can answer without using any more tools. I'll use the user's language to answer
Answer: The risks and benefits of AI are widely discussed among experts, and there are several key points to consider.

**Risks of AI:**
1. **Bias and Discrimination:** AI systems can perpetuate and even amplify biases present in the data they are trained on, leading to discriminatory outcomes.
2. **Opaque Decision-Making:** The decision-making processes of AI systems can be difficult to understand, leading to a lack of transparency.
3. **Public Trust:** There is often a lack of public trust and understanding of how AI systems work, which can hinder their acceptance and use.

To mitigate these risks, experts suggest measures such as ensuring transparency, involving stakeholders in the design process, providing clear explanations, and conducting public consultations. Additionally, there are efforts to develop frameworks and guidelines, such as the National Institute of Standards and Technology (NIST) risk management framework, to manage these risks effectively.

**Benefits of AI:**
1. **Efficiency and Productivity:** AI can automate repetitive tasks, leading to increased efficiency and productivity in various industries.
2. **Innovation:** AI drives innovation by enabling new applications and solutions that were not possible before.
3. **Improved Decision-Making:** AI can process large amounts of data quickly, providing insights that can improve decision-making processes.

**Expert Opinions:**
Experts argue for the benefits of AI in terms of its potential to transform industries and improve quality of life. However, they also caution against the risks, emphasizing the need for responsible development and deployment of AI technologies. The balance between leveraging AI's benefits and managing its risks is crucial for its successful integration into society.

References:
- [Blueprint for an AI Bill of Rights](https://www.whitehouse.gov/ostp/ai-bill-of-rights/)
Time taken: 20.452504634857178

```

The risks and benefits of AI are widely discussed among experts, and there are several key points to consider.
**Risks of AI:**
  1. **Bias and Discrimination:** AI systems can perpetuate and even amplify biases present in the data they are trained on, leading to discriminatory outcomes.
  2. **Opaque Decision-Making:** The decision-making processes of AI systems can be difficult to understand, leading to a lack of transparency.
  3. **Public Trust:** There is often a lack of public trust and understanding of how AI systems work, which can hinder their acceptance and use.


To mitigate these risks, experts suggest measures such as ensuring transparency, involving stakeholders in the design process, providing clear explanations, and conducting public consultations. Additionally, there are efforts to develop frameworks and guidelines, such as the National Institute of Standards and Technology (NIST) risk management framework, to manage these risks effectively.
**Benefits of AI:**
  1. **Efficiency and Productivity:** AI can automate repetitive tasks, leading to increased efficiency and productivity in various industries.
  2. **Innovation:** AI drives innovation by enabling new applications and solutions that were not possible before.
  3. **Improved Decision-Making:** AI can process large amounts of data quickly, providing insights that can improve decision-making processes.


**Expert Opinions:** Experts argue for the benefits of AI in terms of its potential to transform industries and improve quality of life. However, they also caution against the risks, emphasizing the need for responsible development and deployment of AI technologies. The balance between leveraging AI's benefits and managing its risks is crucial for its successful integration into society.
References:
  * Blueprint for an AI Bill of Rights


