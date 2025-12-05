![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# File Based Node Parsers¶
The `SimpleFileNodeParser` and `FlatReader` are designed to allow opening a variety of file types and automatically selecting the best `NodeParser` to process the files. The `FlatReader` loads the file in a raw text format and attaches the file information to the metadata, then the `SimpleFileNodeParser` maps file types to node parsers in `node_parser/file`, selecting the best node parser for the job.
The `SimpleFileNodeParser` does not perform token based chunking of the text, and is intended to be used in combination with a token node parser.
Let's look at an example of using the `FlatReader` and `SimpleFileNodeParser` to load content. For the README file I will be using the LlamaIndex README and the HTML file is the Stack Overflow landing page, however any README and HTML file will work.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-file

```

%pip install llama-index-readers-file
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.core.node_parser import SimpleFileNodeParser
from llama_index.readers.file import FlatReader
from pathlib import Path

```

from llama_index.core.node_parser import SimpleFileNodeParser from llama_index.readers.file import FlatReader from pathlib import Path
```
/Users/adamhofmann/opt/anaconda3/lib/python3.9/site-packages/langchain/__init__.py:24: UserWarning: Importing BasePromptTemplate from langchain root module is no longer supported.
  warnings.warn(
/Users/adamhofmann/opt/anaconda3/lib/python3.9/site-packages/langchain/__init__.py:24: UserWarning: Importing PromptTemplate from langchain root module is no longer supported.
  warnings.warn(

```

In [ ]:
Copied!
```
reader = FlatReader()
html_file = reader.load_data(Path("./stack-overflow.html"))
md_file = reader.load_data(Path("./README.md"))
print(html_file[0].metadata)
print(html_file[0])
print("----")
print(md_file[0].metadata)
print(md_file[0])

```

reader = FlatReader() html_file = reader.load_data(Path("./stack-overflow.html")) md_file = reader.load_data(Path("./README.md")) print(html_file[0].metadata) print(html_file[0]) print("----") print(md_file[0].metadata) print(md_file[0])
```
{'filename': 'stack-overflow.html', 'extension': '.html'}
Doc ID: a6750408-b0fa-466d-be28-ff2fcbcbaa97
Text: <!DOCTYPE html>       <html class="html__responsive
html__unpinned-leftnav" lang="en">      <head>          <title>Stack
Overflow - Where Developers Learn, Share, &amp; Build Careers</title>
<link rel="shortcut icon" href="https://cdn.sstatic.net/Sites/stackove
rflow/Img/favicon.ico?v=ec617d715196">         <link rel="apple-touch-
icon" hr...
----
{'filename': 'README.md', 'extension': '.md'}
Doc ID: 1d872f44-2bb3-4693-a1b8-a59392c23be2
Text: # 🗂️ LlamaIndex 🦙 [![PyPI -
Downloads](https://img.shields.io/pypi/dm/llama-
index)](https://pypi.org/project/llama-index/) [![GitHub contributors]
(https://img.shields.io/github/contributors/jerryjliu/llama_index)](ht
tps://github.com/jerryjliu/llama_index/graphs/contributors) [![Discord
](https://img.shields.io/discord/1059199217496772688)](https:...

```

## Parsing the files¶
The flat reader has simple loaded the content of the files into Document objects for further processing. We can see that the file information is retained in the metadata. Let's pass the documents to the node parser to see the parsing.
In [ ]:
Copied!
```
parser = SimpleFileNodeParser()
md_nodes = parser.get_nodes_from_documents(md_file)
html_nodes = parser.get_nodes_from_documents(html_file)
print(md_nodes[0].metadata)
print(md_nodes[0].text)
print(md_nodes[1].metadata)
print(md_nodes[1].text)
print("----")
print(html_nodes[0].metadata)
print(html_nodes[0].text)

```

parser = SimpleFileNodeParser() md_nodes = parser.get_nodes_from_documents(md_file) html_nodes = parser.get_nodes_from_documents(html_file) print(md_nodes[0].metadata) print(md_nodes[0].text) print(md_nodes[1].metadata) print(md_nodes[1].text) print("----") print(html_nodes[0].metadata) print(html_nodes[0].text)
```
{'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}
🗂️ LlamaIndex 🦙
[![PyPI - Downloads](https://img.shields.io/pypi/dm/llama-index)](https://pypi.org/project/llama-index/)
[![GitHub contributors](https://img.shields.io/github/contributors/jerryjliu/llama_index)](https://github.com/jerryjliu/llama_index/graphs/contributors)
[![Discord](https://img.shields.io/discord/1059199217496772688)](https://discord.gg/dGcwcsnxhU)


LlamaIndex (GPT Index) is a data framework for your LLM application.

PyPI: 
- LlamaIndex: https://pypi.org/project/llama-index/.
- GPT Index (duplicate): https://pypi.org/project/gpt-index/.

LlamaIndex.TS (Typescript/Javascript): https://github.com/run-llama/LlamaIndexTS.

Documentation: https://gpt-index.readthedocs.io/.

Twitter: https://twitter.com/llama_index.

Discord: https://discord.gg/dGcwcsnxhU.
{'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 3': 'Ecosystem'}
Ecosystem

- LlamaHub (community library of data loaders): https://llamahub.ai
- LlamaLab (cutting-edge AGI projects using LlamaIndex): https://github.com/run-llama/llama-lab
----
{'filename': 'stack-overflow.html', 'extension': '.html', 'tag': 'li'}
About
Products
For Teams
Stack Overflow
Public questions & answers
Stack Overflow for Teams
Where developers & technologists share private knowledge with coworkers
Talent

								Build your employer brand
Advertising
Reach developers & technologists worldwide
Labs
The future of collective knowledge sharing
About the company
current community
















            Stack Overflow
        



help
chat









            Meta Stack Overflow
        






your communities            



Sign up or log in to customize your list.                


more stack exchange communities

company blog

```

## Furter processing of files¶
We can see that the Markdown and HTML files have been split into chunks based on the structure of the document. The markdown node parser splits on any headers and attaches the hierarchy of headers into metadata. The HTML node parser extracted text from common text elements to simplifiy the HTML file, and combines neighbouring nodes of the same element. Compared to working with raw HTML, this is alreadly a big improvement in terms of retrieving meaningful text content.
Because these files were only split according to the structure of the file, we can apply further processing with a text splitter to prepare the content into nodes of limited token length.
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

# For clarity in the demo, make small splits without overlap
splitting_parser = SentenceSplitter(chunk_size=200, chunk_overlap=0)

html_chunked_nodes = splitting_parser(html_nodes)
md_chunked_nodes = splitting_parser(md_nodes)
print(f"\n\nHTML parsed nodes: {len(html_nodes)}")
print(html_nodes[0].text)

print(f"\n\nHTML chunked nodes: {len(html_chunked_nodes)}")
print(html_chunked_nodes[0].text)

print(f"\n\nMD parsed nodes: {len(md_nodes)}")
print(md_nodes[0].text)

print(f"\n\nMD chunked nodes: {len(md_chunked_nodes)}")
print(md_chunked_nodes[0].text)

```

from llama_index.core.node_parser import SentenceSplitter # For clarity in the demo, make small splits without overlap splitting_parser = SentenceSplitter(chunk_size=200, chunk_overlap=0) html_chunked_nodes = splitting_parser(html_nodes) md_chunked_nodes = splitting_parser(md_nodes) print(f"\n\nHTML parsed nodes: {len(html_nodes)}") print(html_nodes[0].text) print(f"\n\nHTML chunked nodes: {len(html_chunked_nodes)}") print(html_chunked_nodes[0].text) print(f"\n\nMD parsed nodes: {len(md_nodes)}") print(md_nodes[0].text) print(f"\n\nMD chunked nodes: {len(md_chunked_nodes)}") print(md_chunked_nodes[0].text)
```

HTML parsed nodes: 67
About
Products
For Teams
Stack Overflow
Public questions & answers
Stack Overflow for Teams
Where developers & technologists share private knowledge with coworkers
Talent

								Build your employer brand
Advertising
Reach developers & technologists worldwide
Labs
The future of collective knowledge sharing
About the company
current community
















            Stack Overflow
        



help
chat









            Meta Stack Overflow
        






your communities            



Sign up or log in to customize your list.                


more stack exchange communities

company blog


HTML chunked nodes: 87
About
Products
For Teams
Stack Overflow
Public questions & answers
Stack Overflow for Teams
Where developers & technologists share private knowledge with coworkers
Talent

								Build your employer brand
Advertising
Reach developers & technologists worldwide
Labs
The future of collective knowledge sharing
About the company
current community
















            Stack Overflow
        



help
chat









            Meta Stack Overflow
        






your communities


MD parsed nodes: 10
🗂️ LlamaIndex 🦙
[![PyPI - Downloads](https://img.shields.io/pypi/dm/llama-index)](https://pypi.org/project/llama-index/)
[![GitHub contributors](https://img.shields.io/github/contributors/jerryjliu/llama_index)](https://github.com/jerryjliu/llama_index/graphs/contributors)
[![Discord](https://img.shields.io/discord/1059199217496772688)](https://discord.gg/dGcwcsnxhU)


LlamaIndex (GPT Index) is a data framework for your LLM application.

PyPI: 
- LlamaIndex: https://pypi.org/project/llama-index/.
- GPT Index (duplicate): https://pypi.org/project/gpt-index/.

LlamaIndex.TS (Typescript/Javascript): https://github.com/run-llama/LlamaIndexTS.

Documentation: https://gpt-index.readthedocs.io/.

Twitter: https://twitter.com/llama_index.

Discord: https://discord.gg/dGcwcsnxhU.


MD chunked nodes: 13
🗂️ LlamaIndex 🦙
[![PyPI - Downloads](https://img.shields.io/pypi/dm/llama-index)](https://pypi.org/project/llama-index/)
[![GitHub contributors](https://img.shields.io/github/contributors/jerryjliu/llama_index)](https://github.com/jerryjliu/llama_index/graphs/contributors)
[![Discord](https://img.shields.io/discord/1059199217496772688)](https://discord.gg/dGcwcsnxhU)

```

## Summary¶
We can see that the files have been further processed within the splits created by `SimpleFileNodeParser`, and are now ready to be ingested by an index or vector store. The code cell below shows just the chaining of the parsers to go from raw file to chunked nodes:
In [ ]:
Copied!
```
from llama_index.core.ingestion import IngestionPipeline

pipeline = IngestionPipeline(
    documents=reader.load_data(Path("./README.md")),
    transformations=[
        SimpleFileNodeParser(),
        SentenceSplitter(chunk_size=200, chunk_overlap=0),
    ],
)

md_chunked_nodes = pipeline.run()
print(md_chunked_nodes)

```

from llama_index.core.ingestion import IngestionPipeline pipeline = IngestionPipeline( documents=reader.load_data(Path("./README.md")), transformations=[ SimpleFileNodeParser(), SentenceSplitter(chunk_size=200, chunk_overlap=0), ], ) md_chunked_nodes = pipeline.run() print(md_chunked_nodes)
```
[TextNode(id_='e6236169-45a1-4699-9762-c8d3d89f8fa0', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='e7bc328f-85c1-430a-9772-425e59909a58', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}, hash='e538ad7c04f635f1c707eba290b55618a9f0942211c4b5ca2a4e54e1fdf04973'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='51b40b54-dfd3-48ed-b377-5ca58a0f48a3', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}, hash='ca9e3590b951f1fca38687fd12bb43fbccd0133a38020c94800586b3579c3218')}, hash='ec733c85ad1dca248ae583ece341428ee20e4d796bc11adea1618c8e4ed9246a', text='🗂️ LlamaIndex 🦙\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/llama-index)](https://pypi.org/project/llama-index/)\n[![GitHub contributors](https://img.shields.io/github/contributors/jerryjliu/llama_index)](https://github.com/jerryjliu/llama_index/graphs/contributors)\n[![Discord](https://img.shields.io/discord/1059199217496772688)](https://discord.gg/dGcwcsnxhU)', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='51b40b54-dfd3-48ed-b377-5ca58a0f48a3', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='e7bc328f-85c1-430a-9772-425e59909a58', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}, hash='e538ad7c04f635f1c707eba290b55618a9f0942211c4b5ca2a4e54e1fdf04973'), <NodeRelationship.PREVIOUS: '2'>: RelatedNodeInfo(node_id='e6236169-45a1-4699-9762-c8d3d89f8fa0', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙'}, hash='ec733c85ad1dca248ae583ece341428ee20e4d796bc11adea1618c8e4ed9246a')}, hash='ca9e3590b951f1fca38687fd12bb43fbccd0133a38020c94800586b3579c3218', text='LlamaIndex (GPT Index) is a data framework for your LLM application.\n\nPyPI: \n- LlamaIndex: https://pypi.org/project/llama-index/.\n- GPT Index (duplicate): https://pypi.org/project/gpt-index/.\n\nLlamaIndex.TS (Typescript/Javascript): https://github.com/run-llama/LlamaIndexTS.\n\nDocumentation: https://gpt-index.readthedocs.io/.\n\nTwitter: https://twitter.com/llama_index.\n\nDiscord: https://discord.gg/dGcwcsnxhU.', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='ce269047-4718-4a08-b170-34fef19cdafe', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 3': 'Ecosystem'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='953934dc-dd4f-4069-9e2a-326ee8a593bf', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 3': 'Ecosystem'}, hash='ede2843c0f18e0f409ae9e2bb4090bca4409eaa992fe8ca149295406d3d7adac')}, hash='52b03025c73d7218bd4d66b9812f6e1f6fab6ccf64e5660dc31d123bf1caf5be', text='Ecosystem\n\n- LlamaHub (community library of data loaders): https://llamahub.ai\n- LlamaLab (cutting-edge AGI projects using LlamaIndex): https://github.com/run-llama/llama-lab', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='5ef55167-1fa1-4cae-b2b5-4a86beffbef6', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='2223925f-93a8-45db-9044-41838633e8cc', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview'}, hash='adc49240ff2bdd007e3462b2c3d3f6b6f3b394abbf043d4c291b1a029302c909')}, hash='dc3f175a9119976866e3e6fb2233a12590e8861dc91c621db131521d84e490c4', text='🚀 Overview\n\n**NOTE**: This README is not updated as frequently as the documentation. Please check out the documentation above for the latest updates!', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='8b8e4778-7943-424c-a160-b7da845dd7da', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Context'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='c1ea3027-aad7-4a6f-b8dc-460a8ffbc258', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Context'}, hash='632c76181233b32c03377ccc3d41e458aaec7de845d123a20ace6e3036bbdcd7')}, hash='b867ce7afa1cee176db4e5d0b147276c2e4c724223d590dd5017e68fab3aa29a', text='Context\n- LLMs are a phenomenonal piece of technology for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.\n- How do we best augment LLMs with our own private data?\n\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='be9d228a-91f6-4c39-845d-b79d3b8fa874', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Proposed Solution'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='f57a202a-cb3d-4a74-ab09-70bf93a0bf51', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Proposed Solution'}, hash='4d338f21570da1564e407877e2fceac4dc9e9f8c90cb3b34876507f85d29f41e'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='a18e1c90-0455-47be-9411-8e098df9c951', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Proposed Solution'}, hash='7b9bbe433d53e727b353864a38ad8a9e78b74c84dbef4ca931422f0f45a4906d')}, hash='b02a43b52686c62c8c4a2f32aa7b8a5bcf2a9e9ea7a033430645ec492f04a4fd', text='Proposed Solution\n\nThat\'s where **LlamaIndex** comes in. LlamaIndex is a "data framework" to help you build LLM apps. It provides the following tools:\n\n- Offers **data connectors** to ingest your existing data sources and data formats (APIs, PDFs, docs, SQL, etc.)\n- Provides ways to **structure your data** (indices, graphs) so that this data can be easily used with LLMs.\n- Provides an **advanced retrieval/query interface over your data**: Feed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\n- Allows easy integrations with your outer application framework (e.g.', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='a18e1c90-0455-47be-9411-8e098df9c951', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Proposed Solution'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='f57a202a-cb3d-4a74-ab09-70bf93a0bf51', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Proposed Solution'}, hash='4d338f21570da1564e407877e2fceac4dc9e9f8c90cb3b34876507f85d29f41e'), <NodeRelationship.PREVIOUS: '2'>: RelatedNodeInfo(node_id='be9d228a-91f6-4c39-845d-b79d3b8fa874', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '🚀 Overview', 'Header 3': 'Proposed Solution'}, hash='b02a43b52686c62c8c4a2f32aa7b8a5bcf2a9e9ea7a033430645ec492f04a4fd')}, hash='7b9bbe433d53e727b353864a38ad8a9e78b74c84dbef4ca931422f0f45a4906d', text='with LangChain, Flask, Docker, ChatGPT, anything else).\n\nLlamaIndex provides tools for both beginner users and advanced users. Our high-level API allows beginner users to use LlamaIndex to ingest and query their data in\n5 lines of code. Our lower-level APIs allow advanced users to customize and extend any module (data connectors, indices, retrievers, query engines, reranking modules),\nto fit their needs.', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='b3c6544a-6f68-4060-b3ec-27e5d4b9a599', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '💡 Contributing'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='6abcec78-98c1-4f74-b57b-d8cae4aa7112', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '💡 Contributing'}, hash='cdb950bc1703132df9c05c607702201177c1ad5f8f0de9dcfa3f6154a12a3acd')}, hash='4892fb635ac6b11743ca428676ed492ef7d264e440a205a68a0d752d43e3a19c', text='💡 Contributing\n\nInterested in contributing? See our [Contribution Guide](CONTRIBUTING.md) for more details.', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='e0fc56d6-ec94-476d-a3e4-c007daa2e405', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '📄 Documentation'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='f44afbd2-0bf3-46f5-8662-309e0cf7fa9c', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '📄 Documentation'}, hash='b01a7435fcbe2962f9b6a2cb397a07c1fed6632941e06a1814f4c4ea2300dc67')}, hash='f0215c48bf198d05ee1d6dcc74e12f70d9310c43f4b4dcea71452c9aec051612', text='📄 Documentation\n\nFull documentation can be found here: https://gpt-index.readthedocs.io/en/latest/. \n\nPlease check it out for the most up-to-date tutorials, how-to guides, references, and other resources!', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), TextNode(id_='b583e1f6-e696-42e3-9c87-fa1a12af5cc9', embedding=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '💻 Example Usage'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='f25c47c0-b8bd-451b-81bf-3879c48c55f4', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '💻 Example Usage'}, hash='dfe232d846ceae9f0ccbf96e053b01a00cf24382ff4f49f1380830522d8ae86c'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='82fcab04-4346-4fba-86ae-612e95285c8a', node_type=None, metadata={'filename': 'README.md', 'extension': '.md', 'Header 1': '🗂️ LlamaIndex 🦙', 'Header 2': '💻 Example Usage'}, hash='fe6196075f613ebae9f64bf5b1e04d8324c239e8f256d4455653ccade1da5541')}, hash='9073dfc928908788a3e174fe06f4689c081a6eeafe002180134a57c28c640c83', text='💻 Example Usage\n\n```\npip install llama-index\n

