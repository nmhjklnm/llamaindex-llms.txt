# Query Engine#
## Concept#
Query engine is a generic interface that allows you to ask question over your data.
A query engine takes in a natural language query, and returns a rich response. It is most often (but not always) built on one or many indexes via retrievers. You can compose multiple query engines to achieve more advanced capability.
Tip
If you want to have a conversation with your data (multiple back-and-forth instead of a single question & answer), take a look at Chat Engine
## Usage Pattern#
Get started with:
```
query_engine = index.as_query_engine()
response = query_engine.query("Who is Paul Graham.")

```

To stream response:
```
query_engine = index.as_query_engine(streaming=True)
streaming_response = query_engine.query("Who is Paul Graham.")
streaming_response.print_response_stream()

```

See the full usage pattern for more details.
## Modules#
Find all the modules in the modules guide.
## Supporting Modules#
There are also supporting modules.
