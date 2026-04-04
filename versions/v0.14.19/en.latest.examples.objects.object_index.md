![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# The `ObjectIndex` Class¶
The `ObjectIndex` class is one that allows for the indexing of arbitrary Python objects. As such, it is quite flexible and applicable to a wide-range of use cases. As examples:
  * Use an `ObjectIndex` to index Tool objects to then be used by an agent.
  * Use an `ObjectIndex` to index a SQLTableSchema objects


To construct an `ObjectIndex`, we require an index as well as another abstraction, namely `ObjectNodeMapping`. This mapping, as its name suggests, provides the means to go between node and the associated object, and vice versa. Alternatively, there exists a `from_objects()` class method, that can conveniently construct an `ObjectIndex` from a set of objects.
In this notebook, we'll quickly cover how you can build an `ObjectIndex` using a `SimpleObjectNodeMapping`.
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.embed_model = "local"

```

from llama_index.core import Settings Settings.embed_model = "local"
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex, SimpleObjectNodeMapping

# some really arbitrary objects
obj1 = {"input": "Hey, how's it going"}
obj2 = ["a", "b", "c", "d"]
obj3 = "llamaindex is an awesome library!"
arbitrary_objects = [obj1, obj2, obj3]

# (optional) object-node mapping
obj_node_mapping = SimpleObjectNodeMapping.from_objects(arbitrary_objects)
nodes = obj_node_mapping.to_nodes(arbitrary_objects)

# object index
object_index = ObjectIndex(
    index=VectorStoreIndex(nodes=nodes),
    object_node_mapping=obj_node_mapping,
)

# object index from_objects (default index_cls=VectorStoreIndex)
object_index = ObjectIndex.from_objects(
    arbitrary_objects, index_cls=VectorStoreIndex
)

```

from llama_index.core import VectorStoreIndex from llama_index.core.objects import ObjectIndex, SimpleObjectNodeMapping # some really arbitrary objects obj1 = {"input": "Hey, how's it going"} obj2 = ["a", "b", "c", "d"] obj3 = "llamaindex is an awesome library!" arbitrary_objects = [obj1, obj2, obj3] # (optional) object-node mapping obj_node_mapping = SimpleObjectNodeMapping.from_objects(arbitrary_objects) nodes = obj_node_mapping.to_nodes(arbitrary_objects) # object index object_index = ObjectIndex( index=VectorStoreIndex(nodes=nodes), object_node_mapping=obj_node_mapping, ) # object index from_objects (default index_cls=VectorStoreIndex) object_index = ObjectIndex.from_objects( arbitrary_objects, index_cls=VectorStoreIndex )
### As a retriever¶
With the `object_index` in hand, we can use it as a retriever, to retrieve against the index objects.
In [ ]:
Copied!
```
object_retriever = object_index.as_retriever(similarity_top_k=1)
object_retriever.retrieve("llamaindex")

```

object_retriever = object_index.as_retriever(similarity_top_k=1) object_retriever.retrieve("llamaindex")
Out[ ]:
```
['llamaindex is an awesome library!']
```

We can also add node-postprocessors to an object index retriever, for easy convience to things like rerankers and more.
In [ ]:
Copied!
```
%pip install llama-index-postprocessor-colbert-rerank

```

%pip install llama-index-postprocessor-colbert-rerank
In [ ]:
Copied!
```
from llama_index.postprocessor.colbert_rerank import ColbertRerank

retriever = object_index.as_retriever(
    similarity_top_k=2, node_postprocessors=[ColbertRerank(top_n=1)]
)
retriever.retrieve("a random list object")

```

from llama_index.postprocessor.colbert_rerank import ColbertRerank retriever = object_index.as_retriever( similarity_top_k=2, node_postprocessors=[ColbertRerank(top_n=1)] ) retriever.retrieve("a random list object")
Out[ ]:
```
['llamaindex is an awesome library!']
```

## Using a Storage Integration (i.e. Chroma)¶
The object index supports integrations with any existing storage backend in LlamaIndex.
The following section walks through how to set that up using `Chroma` as an example.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-chroma

```

%pip install llama-index-vector-stores-chroma
In [ ]:
Copied!
```
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("quickstart2")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

object_index = ObjectIndex.from_objects(
    arbitrary_objects,
    index_cls=VectorStoreIndex,
    storage_context=storage_context,
)

```

from llama_index.core import StorageContext, VectorStoreIndex from llama_index.vector_stores.chroma import ChromaVectorStore import chromadb db = chromadb.PersistentClient(path="./chroma_db") chroma_collection = db.get_or_create_collection("quickstart2") vector_store = ChromaVectorStore(chroma_collection=chroma_collection) storage_context = StorageContext.from_defaults(vector_store=vector_store) object_index = ObjectIndex.from_objects( arbitrary_objects, index_cls=VectorStoreIndex, storage_context=storage_context, )
```
---------------------------------------------------------------------------
FileNotFoundError                         Traceback (most recent call last)
Cell In[31], line 5
      2 from llama_index.vector_stores.chroma import ChromaVectorStore
      3 import chromadb
----> 5 db = chromadb.PersistentClient(path="./chroma_db2")
      6 chroma_collection = db.get_or_create_collection("quickstart2")
      7 vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/__init__.py:146, in PersistentClient(path, settings, tenant, database)
    143 tenant = str(tenant)
    144 database = str(database)
--> 146 return ClientCreator(tenant=tenant, database=database, settings=settings)

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/api/client.py:139, in Client.__init__(self, tenant, database, settings)
    133 def __init__(
    134     self,
    135     tenant: str = DEFAULT_TENANT,
    136     database: str = DEFAULT_DATABASE,
    137     settings: Settings = Settings(),
    138 ) -> None:
--> 139     super().__init__(settings=settings)
    140     self.tenant = tenant
    141     self.database = database

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/api/client.py:43, in SharedSystemClient.__init__(self, settings)
     38 def __init__(
     39     self,
     40     settings: Settings = Settings(),
     41 ) -> None:
     42     self._identifier = SharedSystemClient._get_identifier_from_settings(settings)
---> 43     SharedSystemClient._create_system_if_not_exists(self._identifier, settings)

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/api/client.py:54, in SharedSystemClient._create_system_if_not_exists(cls, identifier, settings)
     51     cls._identifer_to_system[identifier] = new_system
     53     new_system.instance(ProductTelemetryClient)
---> 54     new_system.instance(ServerAPI)
     56     new_system.start()
     57 else:

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/config.py:382, in System.instance(self, type)
    379     type = get_class(fqn, type)
    381 if type not in self._instances:
--> 382     impl = type(self)
    383     self._instances[type] = impl
    384     if self._running:

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/api/segment.py:102, in SegmentAPI.__init__(self, system)
    100 super().__init__(system)
    101 self._settings = system.settings
--> 102 self._sysdb = self.require(SysDB)
    103 self._manager = self.require(SegmentManager)
    104 self._quota = self.require(QuotaEnforcer)

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/config.py:281, in Component.require(self, type)
    278 def require(self, type: Type[T]) -> T:
    279     """Get a Component instance of the given type, and register as a dependency of
    280     that instance."""
--> 281     inst = self._system.instance(type)
    282     self._dependencies.add(inst)
    283     return inst

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/config.py:382, in System.instance(self, type)
    379     type = get_class(fqn, type)
    381 if type not in self._instances:
--> 382     impl = type(self)
    383     self._instances[type] = impl
    384     if self._running:

File ~/giant_change/llama_index/venv/lib/python3.10/site-packages/chromadb/db/impl/sqlite.py:88, in SqliteDB.__init__(self, system)
     84     self._db_file = (
     85         self._settings.require("persist_directory") + "/chroma.sqlite3"
     86     )
     87     if not os.path.exists(self._db_file):
---> 88         os.makedirs(os.path.dirname(self._db_file), exist_ok=True)
     89     self._conn_pool = PerThreadPool(self._db_file)
     90 self._tx_stack = local()

File ~/miniforge3/lib/python3.10/os.py:225, in makedirs(name, mode, exist_ok)
    223         return
    224 try:
--> 225     mkdir(name, mode)
    226 except OSError:
    227     # Cannot rely on checking for EEXIST, since the operating system
    228     # could give priority to other errors like EACCES or EROFS
    229     if not exist_ok or not path.isdir(name):

FileNotFoundError: [Errno 2] No such file or directory: './chroma_db2'
```

In [ ]:
Copied!
```
object_retriever = object_index.as_retriever(similarity_top_k=1)
object_retriever.retrieve("llamaindex")

```

object_retriever = object_index.as_retriever(similarity_top_k=1) object_retriever.retrieve("llamaindex")
Out[ ]:
```
['llamaindex is an awesome library!']
```

Now, lets "reload" the index
In [ ]:
Copied!
```
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

object_index = ObjectIndex.from_objects_and_index(arbitrary_objects, index)

```

db = chromadb.PersistentClient(path="./chroma_db") chroma_collection = db.get_or_create_collection("quickstart") vector_store = ChromaVectorStore(chroma_collection=chroma_collection) index = VectorStoreIndex.from_vector_store(vector_store=vector_store) object_index = ObjectIndex.from_objects_and_index(arbitrary_objects, index)
In [ ]:
Copied!
```
object_retriever = object_index.as_retriever(similarity_top_k=1)
object_retriever.retrieve("llamaindex")

```

object_retriever = object_index.as_retriever(similarity_top_k=1) object_retriever.retrieve("llamaindex")
Out[ ]:
```
['llamaindex is an awesome library!']
```

Note that when we reload the index, we still have to pass the objects, since those are not saved in the actual index/vector db.
## [Advanced] Customizing the Mapping¶
For specialized cases where you want full control over how objects are mapped to nodes, you can also provide a `to_node_fn()` and `from_node_fn()` hook.
This is useful for when you are converting specialized objects, or want to dynamically create objects at runtime rather than keeping them in memory.
A small example is shown below.
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode

my_objects = {
    str(hash(str(obj))): obj for i, obj in enumerate(arbitrary_objects)
}


def from_node_fn(node):
    return my_objects[node.id]


def to_node_fn(obj):
    return TextNode(id=str(hash(str(obj))), text=str(obj))


object_index = ObjectIndex.from_objects(
    arbitrary_objects,
    index_cls=VectorStoreIndex,
    from_node_fn=from_node_fn,
    to_node_fn=to_node_fn,
)

object_retriever = object_index.as_retriever(similarity_top_k=1)

object_retriever.retrieve("llamaindex")

```

from llama_index.core.schema import TextNode my_objects = { str(hash(str(obj))): obj for i, obj in enumerate(arbitrary_objects) } def from_node_fn(node): return my_objects[node.id] def to_node_fn(obj): return TextNode(id=str(hash(str(obj))), text=str(obj)) object_index = ObjectIndex.from_objects( arbitrary_objects, index_cls=VectorStoreIndex, from_node_fn=from_node_fn, to_node_fn=to_node_fn, ) object_retriever = object_index.as_retriever(similarity_top_k=1) object_retriever.retrieve("llamaindex")
Out[ ]:
```
['llamaindex is an awesome library!']
```

## Persisting `ObjectIndex` to Disk with Objects¶
When it comes to persisting the `ObjectIndex`, we have to handle both the index as well as the object-node mapping. Persisting the index is straightforward and can be handled by usual means (e.g., see this guide). However, it's a bit of a different story when it comes to persisting the `ObjectNodeMapping`. Since we're indexing aribtrary Python objects with the `ObjectIndex`, it may be the case (and perhaps more often than we'd like), that the arbitrary objects are not serializable. In those cases, you can persist the index, but the user would have to maintain a way to re-construct the `ObjectNodeMapping` to be able to re-construct the `ObjectIndex`. For convenience, there are the `persist` and `from_persist_dir` methods on the `ObjectIndex` that will attempt to persist and load a previously saved `ObjectIndex`, respectively.
### Happy example¶
In [ ]:
Copied!
```
# persist to disk (no path provided will persist to the default path ./storage)
object_index.persist()

```

# persist to disk (no path provided will persist to the default path ./storage) object_index.persist()
In [ ]:
Copied!
```
# re-loading (no path provided will attempt to load from the default path ./storage)
reloaded_object_index = ObjectIndex.from_persist_dir()

```

# re-loading (no path provided will attempt to load from the default path ./storage) reloaded_object_index = ObjectIndex.from_persist_dir()
In [ ]:
Copied!
```
reloaded_object_index._object_node_mapping.obj_node_mapping

```

reloaded_object_index._object_node_mapping.obj_node_mapping
Out[ ]:
```
{7981070310142320670: {'input': "Hey, how's it going"},
 -5984737625581842527: ['a', 'b', 'c', 'd'],
 -8305186196625446821: 'llamaindex is an awesome library!'}
```

In [ ]:
Copied!
```
object_index._object_node_mapping.obj_node_mapping

```

object_index._object_node_mapping.obj_node_mapping
Out[ ]:
```
{7981070310142320670: {'input': "Hey, how's it going"},
 -5984737625581842527: ['a', 'b', 'c', 'd'],
 -8305186196625446821: 'llamaindex is an awesome library!'}
```

### Example of when it doesn't work¶
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool
from llama_index.core import SummaryIndex
from llama_index.core.objects import SimpleToolNodeMapping


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)
add_tool = FunctionTool.from_defaults(fn=add)

object_mapping = SimpleToolNodeMapping.from_objects([add_tool, multiply_tool])
object_index = ObjectIndex.from_objects(
    [add_tool, multiply_tool], object_mapping
)

```

from llama_index.core.tools import FunctionTool from llama_index.core import SummaryIndex from llama_index.core.objects import SimpleToolNodeMapping def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b multiply_tool = FunctionTool.from_defaults(fn=multiply) add_tool = FunctionTool.from_defaults(fn=add) object_mapping = SimpleToolNodeMapping.from_objects([add_tool, multiply_tool]) object_index = ObjectIndex.from_objects( [add_tool, multiply_tool], object_mapping )
In [ ]:
Copied!
```
# trying to persist the object_mapping directly will raise an error
object_mapping.persist()

```

# trying to persist the object_mapping directly will raise an error object_mapping.persist()
```
---------------------------------------------------------------------------
NotImplementedError                       Traceback (most recent call last)
Cell In[4], line 2
      1 # trying to persist the object_mapping directly will raise an error
----> 2 object_mapping.persist()

File ~/Projects/llama_index/llama_index/objects/tool_node_mapping.py:47, in BaseToolNodeMapping.persist(self, persist_dir, obj_node_mapping_fname)
     43 def persist(
     44     self, persist_dir: str = ..., obj_node_mapping_fname: str = ...
     45 ) -> None:
     46     """Persist objs."""
---> 47     raise NotImplementedError("Subclasses should implement this!")

NotImplementedError: Subclasses should implement this!
```

In [ ]:
Copied!
```
# try to persist the object index here will throw a Warning to the user
object_index.persist()

```

# try to persist the object index here will throw a Warning to the user object_index.persist()
```
/var/folders/0g/wd11bmkd791fz7hvgy1kqyp00000gn/T/ipykernel_77363/46708458.py:2: UserWarning: Unable to persist ObjectNodeMapping. You will need to reconstruct the same object node mapping to build this ObjectIndex
  object_index.persist()

```

**In this case, only the index has been persisted.** In order to re-construct the `ObjectIndex` as mentioned above, we will need to manually re-construct `ObjectNodeMapping` and supply that to the `ObjectIndex.from_persist_dir` method.
In [ ]:
Copied!
```
reloaded_object_index = ObjectIndex.from_persist_dir(
    object_node_mapping=object_mapping  # without this, an error will be thrown
)

```

reloaded_object_index = ObjectIndex.from_persist_dir( object_node_mapping=object_mapping # without this, an error will be thrown )
