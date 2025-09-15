# Discord Thread Management¶
This notebook walks through the process of managing documents that come from ever-updating data sources.
In this example, we have a directory where the #issues-and-help channel on the LlamaIndex discord is dumped periodically. We want to ensure our index always has the latest data, without duplicating any messages.
## Indexing discord data¶
Discord data is dumped as sequential messages. Every message has useful information such as timestamps, authors, and links to parent messages if the message is part of a thread.
The help channel on our discord commonly uses threads when solving issues, so we will group all the messages into threads, and index each thread as it's own document.
First, let's explore the data we are working with.
In [ ]:
Copied!
```
import os

print(os.listdir("./discord_dumps"))

```

import os print(os.listdir("./discord_dumps"))
```
['help_channel_dump_06_02_23.json', 'help_channel_dump_05_25_23.json']

```

As you can see, we have two dumps from two different dates. Let's pretend we only have the older dump to start with, and we want to make an index from that data.
First, let's explore the data a bit
In [ ]:
Copied!
```
import json

with open("./discord_dumps/help_channel_dump_05_25_23.json", "r") as f:
    data = json.load(f)
print("JSON keys: ", data.keys(), "\n")
print("Message Count: ", len(data["messages"]), "\n")
print("Sample Message Keys: ", data["messages"][0].keys(), "\n")
print("First Message: ", data["messages"][0]["content"], "\n")
print("Last Message: ", data["messages"][-1]["content"])

```

import json with open("./discord_dumps/help_channel_dump_05_25_23.json", "r") as f: data = json.load(f) print("JSON keys: ", data.keys(), "\n") print("Message Count: ", len(data["messages"]), "\n") print("Sample Message Keys: ", data["messages"][0].keys(), "\n") print("First Message: ", data["messages"][0]["content"], "\n") print("Last Message: ", data["messages"][-1]["content"])
```
JSON keys:  dict_keys(['guild', 'channel', 'dateRange', 'messages', 'messageCount']) 

Message Count:  5087 

Sample Message Keys:  dict_keys(['id', 'type', 'timestamp', 'timestampEdited', 'callEndedTimestamp', 'isPinned', 'content', 'author', 'attachments', 'embeds', 'stickers', 'reactions', 'mentions']) 

First Message:  If you're running into any bugs, issues, or you have questions as to how to best use GPT Index, put those here! 
- If it's a bug, let's also track as a GH issue: https://github.com/jerryjliu/gpt_index/issues. 

Last Message:  Hello there! How can I use llama_index with GPU?

```

Conviently, I have provided a script that will group these messages into threads. You can see the `group_conversations.py` script for more details. The output file will be a json list where each item in the list is a discord thread.
In [ ]:
Copied!
```
!python ./group_conversations.py ./discord_dumps/help_channel_dump_05_25_23.json

```

!python ./group_conversations.py ./discord_dumps/help_channel_dump_05_25_23.json
```
Done! Written to conversation_docs.json

```

In [ ]:
Copied!
```
with open("conversation_docs.json", "r") as f:
    threads = json.load(f)
print("Thread keys: ", threads[0].keys(), "\n")
print(threads[0]["metadata"], "\n")
print(threads[0]["thread"], "\n")

```

with open("conversation_docs.json", "r") as f: threads = json.load(f) print("Thread keys: ", threads[0].keys(), "\n") print(threads[0]["metadata"], "\n") print(threads[0]["thread"], "\n")
```
Thread keys:  dict_keys(['thread', 'metadata']) 

{'timestamp': '2023-01-02T03:36:04.191+00:00', 'id': '1059314106907242566'} 

arminta7:
Hello all! Thanks to GPT_Index I've managed to put together a script that queries my extensive personal note collection which is a local directory of about 20k markdown files. Some of which are very long. I work in this folder all day everyday, so there are frequent changes. Currently I would need to rerun the entire indexing (is that the correct term?) when I want to incorporate edits I've made. 

So my question is... is there a way to schedule indexing to maybe once per day and only add information for files that have changed? Or even just manually run it but still only add edits? This would make a huge difference in saving time (I have to leave it running overnight for the entire directory) as well as cost 😬. 

Excuse me if this is a dumb question, I'm not a programmer and am sort of muddling around figuring this out 🤓 

Thank you for making this sort of project accessible to someone like me!
ragingWater_:
I had a similar problem which I solved the following way in another world:
- if you have a list of files, you want something which says that edits were made in the last day, possibly looking at the last_update_time of the file should help you.
- for decreasing the cost, I would suggest maybe doing a keyword extraction or summarization of your notes and generating an embedding for it. Take your NLP query and get the most similar file (cosine similarity by pinecone db should help, GPTIndex also has a faiss) this should help with your cost needs
 


```

Now, we have a list of threads, that we can transform into documents and index!
## Create the initial index¶
In [ ]:
Copied!
```
from llama_index.core import Document

# create document objects using doc_id's and dates from each thread
documents = []
for thread in threads:
    thread_text = thread["thread"]
    thread_id = thread["metadata"]["id"]
    timestamp = thread["metadata"]["timestamp"]
    documents.append(
        Document(text=thread_text, id_=thread_id, metadata={"date": timestamp})
    )

```

from llama_index.core import Document # create document objects using doc_id's and dates from each thread documents = [] for thread in threads: thread_text = thread["thread"] thread_id = thread["metadata"]["id"] timestamp = thread["metadata"]["timestamp"] documents.append( Document(text=thread_text, id_=thread_id, metadata={"date": timestamp}) )
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
Let's double check what documents the index has actually ingested
In [ ]:
Copied!
```
print("ref_docs ingested: ", len(index.ref_doc_info))
print("number of input documents: ", len(documents))

```

print("ref_docs ingested: ", len(index.ref_doc_info)) print("number of input documents: ", len(documents))
```
ref_docs ingested:  767
number of input documents:  767

```

So far so good. Let's also check a specific thread to make sure the metadata worked, as well as checking how many nodes it was broken into
In [ ]:
Copied!
```
thread_id = threads[0]["metadata"]["id"]
print(index.ref_doc_info[thread_id])

```

thread_id = threads[0]["metadata"]["id"] print(index.ref_doc_info[thread_id])
```
RefDocInfo(node_ids=['0c530273-b6c3-4848-a760-fe73f5f8136e'], metadata={'date': '2023-01-02T03:36:04.191+00:00'})

```

Perfect! Our thread is rather short, so it was directly chunked into a single node. Furthermore, we can see the date field was set correctly.
Next, let's backup our index so that we don't have to waste tokens indexing again.
In [ ]:
Copied!
```
# save the initial index
index.storage_context.persist(persist_dir="./storage")

# load it again to confirm it worked
from llama_index.core import StorageContext, load_index_from_storage

index = load_index_from_storage(
    StorageContext.from_defaults(persist_dir="./storage")
)

print("Double check ref_docs ingested: ", len(index.ref_doc_info))

```

# save the initial index index.storage_context.persist(persist_dir="./storage") # load it again to confirm it worked from llama_index.core import StorageContext, load_index_from_storage index = load_index_from_storage( StorageContext.from_defaults(persist_dir="./storage") ) print("Double check ref_docs ingested: ", len(index.ref_doc_info))
```
Double check ref_docs ingested:  767

```

## Refresh the index with new data!¶
Now, suddenly we remember we have that new dump of discord messages! Rather than rebuilding the entire index from scratch, we can index only the new documents using the `refresh()` function.
Since we manually set the `doc_id` of each index, LlamaIndex can compare incoming documents with the same `doc_id` to confirm a) if the `doc_id` has actually been ingested and b) if the content as changed
The refresh function will return a boolean array, indicating which documents in the input were refreshed or inserted. We can use this to confirm that only the new discord threads are inserted!
When a documents content has changed, the `update()` function is called, which removes and re-inserts the document from the index.
In [ ]:
Copied!
```
import json

with open("./discord_dumps/help_channel_dump_06_02_23.json", "r") as f:
    data = json.load(f)
print("JSON keys: ", data.keys(), "\n")
print("Message Count: ", len(data["messages"]), "\n")
print("Sample Message Keys: ", data["messages"][0].keys(), "\n")
print("First Message: ", data["messages"][0]["content"], "\n")
print("Last Message: ", data["messages"][-1]["content"])

```

import json with open("./discord_dumps/help_channel_dump_06_02_23.json", "r") as f: data = json.load(f) print("JSON keys: ", data.keys(), "\n") print("Message Count: ", len(data["messages"]), "\n") print("Sample Message Keys: ", data["messages"][0].keys(), "\n") print("First Message: ", data["messages"][0]["content"], "\n") print("Last Message: ", data["messages"][-1]["content"])
```
JSON keys:  dict_keys(['guild', 'channel', 'dateRange', 'messages', 'messageCount']) 

Message Count:  5286 

Sample Message Keys:  dict_keys(['id', 'type', 'timestamp', 'timestampEdited', 'callEndedTimestamp', 'isPinned', 'content', 'author', 'attachments', 'embeds', 'stickers', 'reactions', 'mentions']) 

First Message:  If you're running into any bugs, issues, or you have questions as to how to best use GPT Index, put those here! 
- If it's a bug, let's also track as a GH issue: https://github.com/jerryjliu/gpt_index/issues. 

Last Message:  Started a thread.

```

As we can see, the first message is the same as the orignal dump. But now we have ~200 more messages, and the last message is clearly new! `refresh()` will make updating our index easy.
First, let's create our new threads/documents
In [ ]:
Copied!
```
!python ./group_conversations.py ./discord_dumps/help_channel_dump_06_02_23.json

```

!python ./group_conversations.py ./discord_dumps/help_channel_dump_06_02_23.json
```
Done! Written to conversation_docs.json

```

In [ ]:
Copied!
```
with open("conversation_docs.json", "r") as f:
    threads = json.load(f)
print("Thread keys: ", threads[0].keys(), "\n")
print(threads[0]["metadata"], "\n")
print(threads[0]["thread"], "\n")

```

with open("conversation_docs.json", "r") as f: threads = json.load(f) print("Thread keys: ", threads[0].keys(), "\n") print(threads[0]["metadata"], "\n") print(threads[0]["thread"], "\n")
```
Thread keys:  dict_keys(['thread', 'metadata']) 

{'timestamp': '2023-01-02T03:36:04.191+00:00', 'id': '1059314106907242566'} 

arminta7:
Hello all! Thanks to GPT_Index I've managed to put together a script that queries my extensive personal note collection which is a local directory of about 20k markdown files. Some of which are very long. I work in this folder all day everyday, so there are frequent changes. Currently I would need to rerun the entire indexing (is that the correct term?) when I want to incorporate edits I've made. 

So my question is... is there a way to schedule indexing to maybe once per day and only add information for files that have changed? Or even just manually run it but still only add edits? This would make a huge difference in saving time (I have to leave it running overnight for the entire directory) as well as cost 😬. 

Excuse me if this is a dumb question, I'm not a programmer and am sort of muddling around figuring this out 🤓 

Thank you for making this sort of project accessible to someone like me!
ragingWater_:
I had a similar problem which I solved the following way in another world:
- if you have a list of files, you want something which says that edits were made in the last day, possibly looking at the last_update_time of the file should help you.
- for decreasing the cost, I would suggest maybe doing a keyword extraction or summarization of your notes and generating an embedding for it. Take your NLP query and get the most similar file (cosine similarity by pinecone db should help, GPTIndex also has a faiss) this should help with your cost needs
 


```

In [ ]:
Copied!
```
# create document objects using doc_id's and dates from each thread
new_documents = []
for thread in threads:
    thread_text = thread["thread"]
    thread_id = thread["metadata"]["id"]
    timestamp = thread["metadata"]["timestamp"]
    new_documents.append(
        Document(text=thread_text, id_=thread_id, metadata={"date": timestamp})
    )

```

# create document objects using doc_id's and dates from each thread new_documents = [] for thread in threads: thread_text = thread["thread"] thread_id = thread["metadata"]["id"] timestamp = thread["metadata"]["timestamp"] new_documents.append( Document(text=thread_text, id_=thread_id, metadata={"date": timestamp}) )
In [ ]:
Copied!
```
print("Number of new documents: ", len(new_documents) - len(documents))

```

print("Number of new documents: ", len(new_documents) - len(documents))
```
Number of new documents:  13

```

In [ ]:
Copied!
```
# now, refresh!
refreshed_docs = index.refresh(
    new_documents,
    update_kwargs={"delete_kwargs": {"delete_from_docstore": True}},
)

```

# now, refresh! refreshed_docs = index.refresh( new_documents, update_kwargs={"delete_kwargs": {"delete_from_docstore": True}}, )
By default, if a document's content has changed and it is updated, we can pass an extra flag to `delete_from_docstore`. This flag is `False` by default because indexes can share the docstore. But since we only have one index, removing from the docstore is fine here.
If we kept the option as `False`, the document information would still be removed from the `index_struct`, which effectively makes that document invisibile to the index.
In [ ]:
Copied!
```
print("Number of newly inserted/refreshed docs: ", sum(refreshed_docs))

```

print("Number of newly inserted/refreshed docs: ", sum(refreshed_docs))
```
Number of newly inserted/refreshed docs:  15

```

Interesting, we have 13 new documents, but 15 documents were refreshed. Did someone edit their message? Add more text to a thread? Let's find out
In [ ]:
Copied!
```
print(refreshed_docs[-25:])

```

print(refreshed_docs[-25:])
```
[False, True, False, False, True, False, False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True]

```

In [ ]:
Copied!
```
new_documents[-21]

```

new_documents[-21]
Out[ ]:
```
Document(id_='1110938122902048809', embedding=None, weight=1.0, metadata={'date': '2023-05-24T14:31:28.732+00:00'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='36d308d1d2d1aa5cbfdb2f7d64709644a68805ec22a6053943f985084eec340e', text='Siddhant Saurabh:\nhey facing error\n```\n*error_trace: Traceback (most recent call last):\n File "/app/src/chatbot/query_gpt.py", line 248, in get_answer\n   context_answer = self.call_pinecone_index(request)\n File "/app/src/chatbot/query_gpt.py", line 229, in call_pinecone_index\n   self.source.append(format_cited_source(source_node.doc_id))\n File "/usr/local/lib/python3.8/site-packages/llama_index/data_structs/node.py", line 172, in doc_id\n   return self.node.ref_doc_id\n File "/usr/local/lib/python3.8/site-packages/llama_index/data_structs/node.py", line 87, in ref_doc_id\n   return self.relationships.get(DocumentRelationship.SOURCE, None)\nAttributeError: \'Field\' object has no attribute \'get\'\n

In [ ]:
Copied!
```
documents[-8]

```

documents[-8]
Out[ ]:
```
Document(id_='1110938122902048809', embedding=None, weight=1.0, metadata={'date': '2023-05-24T14:31:28.732+00:00'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='c995c43873440a9d0263de70fff664269ec70d751c6e8245b290882ec5b656a1', text='Siddhant Saurabh:\nhey facing error\n```\n*error_trace: Traceback (most recent call last):\n File "/app/src/chatbot/query_gpt.py", line 248, in get_answer\n   context_answer = self.call_pinecone_index(request)\n File "/app/src/chatbot/query_gpt.py", line 229, in call_pinecone_index\n   self.source.append(format_cited_source(source_node.doc_id))\n File "/usr/local/lib/python3.8/site-packages/llama_index/data_structs/node.py", line 172, in doc_id\n   return self.node.ref_doc_id\n File "/usr/local/lib/python3.8/site-packages/llama_index/data_structs/node.py", line 87, in ref_doc_id\n   return self.relationships.get(DocumentRelationship.SOURCE, None)\nAttributeError: \'Field\' object has no attribute \'get\'\n

Nice! The newer documents contained threads that had more messages. As you can see, `refresh()` was able to detect this and automatically replaced the older thread with the updated text.
