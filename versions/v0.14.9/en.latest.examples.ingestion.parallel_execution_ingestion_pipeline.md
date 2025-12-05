![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Parallelizing Ingestion Pipeline¶
In this notebook, we demonstrate how to execute ingestion pipelines using parallel processes. Both sync and async versions of batched parallel execution are possible with `IngestionPipeline`.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai

```

%pip install llama-index-embeddings-openai
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
import cProfile, pstats
from pstats import SortKey

```

import cProfile, pstats from pstats import SortKey
### Load data¶
For this notebook, we'll load the `PatronusAIFinanceBenchDataset` llama-dataset from llamahub.
In [ ]:
Copied!
```
!llamaindex-cli download-llamadataset PatronusAIFinanceBenchDataset --download-dir ./data

```

!llamaindex-cli download-llamadataset PatronusAIFinanceBenchDataset --download-dir ./data
```
Successfully downloaded PatronusAIFinanceBenchDataset to ./data

```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(input_dir="./data/source_files").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader(input_dir="./data/source_files").load_data()
### Define our IngestionPipeline¶
In [ ]:
Copied!
```
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline

# create the pipeline with transformations
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024, chunk_overlap=20),
        TitleExtractor(),
        OpenAIEmbedding(),
    ]
)

# since we'll be testing performance, using timeit and cProfile
# we're going to disable cache
pipeline.disable_cache = True

```

from llama_index.core import Document from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core.node_parser import SentenceSplitter from llama_index.core.extractors import TitleExtractor from llama_index.core.ingestion import IngestionPipeline # create the pipeline with transformations pipeline = IngestionPipeline( transformations=[ SentenceSplitter(chunk_size=1024, chunk_overlap=20), TitleExtractor(), OpenAIEmbedding(), ] ) # since we'll be testing performance, using timeit and cProfile # we're going to disable cache pipeline.disable_cache = True
### Parallel Execution¶
A single run. Setting `num_workers` to a value greater than 1 will invoke parallel execution.
In [ ]:
Copied!
```
nodes = pipeline.run(documents=documents, num_workers=4)

```

nodes = pipeline.run(documents=documents, num_workers=4)
```
100%|██████████| 5/5 [00:01<00:00,  3.74it/s]
100%|██████████| 5/5 [00:01<00:00,  4.25it/s]
100%|██████████| 5/5 [00:01<00:00,  4.54it/s]
100%|██████████| 5/5 [00:01<00:00,  3.27it/s]
100%|██████████| 2/2 [00:00<00:00,  2.43it/s]

```

In [ ]:
Copied!
```
len(nodes)

```

len(nodes)
Out[ ]:


In [ ]:
Copied!
```
%timeit pipeline.run(documents=documents, num_workers=4)

```

%timeit pipeline.run(documents=documents, num_workers=4)
```
100%|██████████| 5/5 [00:01<00:00,  3.65it/s]
100%|██████████| 5/5 [00:01<00:00,  4.05it/s]
100%|██████████| 5/5 [00:01<00:00,  4.14it/s]
100%|██████████| 5/5 [00:01<00:00,  2.83it/s]
100%|██████████| 2/2 [00:00<00:00,  2.07it/s]
100%|██████████| 5/5 [00:01<00:00,  3.64it/s]
100%|██████████| 5/5 [00:00<00:00,  5.26it/s]
100%|██████████| 5/5 [00:00<00:00,  6.17it/s]
100%|██████████| 5/5 [00:01<00:00,  3.80it/s]
100%|██████████| 2/2 [00:00<00:00,  2.12it/s]
100%|██████████| 5/5 [00:01<00:00,  3.56it/s]
100%|██████████| 5/5 [00:00<00:00,  6.90it/s]
100%|██████████| 5/5 [00:01<00:00,  2.86it/s]
100%|██████████| 5/5 [00:01<00:00,  3.15it/s]
100%|██████████| 2/2 [00:00<00:00,  2.10it/s]
100%|██████████| 5/5 [00:00<00:00,  5.10it/s]
100%|██████████| 5/5 [00:01<00:00,  3.17it/s]
100%|██████████| 5/5 [00:01<00:00,  4.75it/s]
100%|██████████| 5/5 [00:01<00:00,  3.46it/s]
100%|██████████| 2/2 [00:00<00:00,  2.03it/s]
100%|██████████| 5/5 [00:00<00:00,  7.27it/s]
100%|██████████| 5/5 [00:01<00:00,  3.25it/s]
100%|██████████| 5/5 [00:01<00:00,  4.09it/s]
100%|██████████| 5/5 [00:01<00:00,  3.93it/s]
100%|██████████| 2/2 [00:00<00:00,  2.51it/s]
100%|██████████| 5/5 [00:00<00:00,  6.94it/s]
100%|██████████| 5/5 [00:01<00:00,  3.34it/s]
100%|██████████| 5/5 [00:01<00:00,  4.66it/s]
100%|██████████| 5/5 [00:01<00:00,  3.84it/s]
100%|██████████| 2/2 [00:00<00:00,  2.64it/s]
100%|██████████| 5/5 [00:01<00:00,  3.69it/s]
100%|██████████| 5/5 [00:01<00:00,  4.43it/s]
100%|██████████| 5/5 [00:00<00:00,  5.24it/s]
100%|██████████| 5/5 [00:01<00:00,  4.01it/s]
100%|██████████| 2/2 [00:00<00:00,  2.52it/s]
100%|██████████| 5/5 [00:01<00:00,  4.82it/s]
100%|██████████| 5/5 [00:00<00:00,  5.39it/s]
100%|██████████| 5/5 [00:01<00:00,  4.57it/s]
100%|██████████| 5/5 [00:01<00:00,  3.55it/s]
100%|██████████| 2/2 [00:00<00:00,  2.58it/s]

```

```
29 s ± 1.56 s per loop (mean ± std. dev. of 7 runs, 1 loop each)

```

In [ ]:
Copied!
```
cProfile.run(
    "pipeline.run(documents=documents, num_workers=4)",
    "newstats",
)
p = pstats.Stats("newstats")
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)

```

cProfile.run( "pipeline.run(documents=documents, num_workers=4)", "newstats", ) p = pstats.Stats("newstats") p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)
```
100%|██████████| 5/5 [00:01<00:00,  4.26it/s]
100%|██████████| 5/5 [00:01<00:00,  3.44it/s]
100%|██████████| 5/5 [00:01<00:00,  4.14it/s]
100%|██████████| 5/5 [00:01<00:00,  3.31it/s]
100%|██████████| 2/2 [00:00<00:00,  2.72it/s]

```

```
Tue Jan  9 14:59:20 2024    newstats

         2048 function calls in 29.897 seconds

   Ordered by: cumulative time
   List reduced from 214 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   29.897   29.897 {built-in method builtins.exec}
        1    0.057    0.057   29.896   29.896 <string>:1(<module>)
        1    0.000    0.000   29.840   29.840 pipeline.py:378(run)
       12    0.000    0.000   29.784    2.482 threading.py:589(wait)
       12    0.000    0.000   29.784    2.482 threading.py:288(wait)
       75   29.784    0.397   29.784    0.397 {method 'acquire' of '_thread.lock' objects}
        1    0.000    0.000   29.783   29.783 pool.py:369(starmap)
        1    0.000    0.000   29.782   29.782 pool.py:767(get)
        1    0.000    0.000   29.782   29.782 pool.py:764(wait)
        1    0.000    0.000    0.045    0.045 context.py:115(Pool)
        1    0.000    0.000    0.045    0.045 pool.py:183(__init__)
        1    0.000    0.000    0.043    0.043 pool.py:305(_repopulate_pool)
        1    0.000    0.000    0.043    0.043 pool.py:314(_repopulate_pool_static)
        4    0.000    0.000    0.043    0.011 process.py:110(start)
        4    0.000    0.000    0.043    0.011 context.py:285(_Popen)



```

Out[ ]:
```
<pstats.Stats at 0x139cbc1f0>
```

### Async Parallel Execution¶
Here the `ProcessPoolExecutor` from `concurrent.futures` is used to execute processes asynchronously. The tasks are being processed are blocking, but also performed asynchronously on the individual processes.
In [ ]:
Copied!
```
nodes = await pipeline.arun(documents=documents, num_workers=4)

```

nodes = await pipeline.arun(documents=documents, num_workers=4)
```
100%|██████████| 5/5 [00:01<00:00,  3.78it/s]
100%|██████████| 5/5 [00:01<00:00,  4.33it/s]
100%|██████████| 5/5 [00:01<00:00,  4.96it/s]
100%|██████████| 5/5 [00:01<00:00,  3.73it/s]
100%|██████████| 2/2 [00:00<00:00,  2.26it/s]

```

In [ ]:
Copied!
```
len(nodes)

```

len(nodes)
Out[ ]:


In [ ]:
Copied!
```
import asyncio

loop = asyncio.get_event_loop()
%timeit loop.run_until_complete(pipeline.arun(documents=documents, num_workers=4))

```

import asyncio loop = asyncio.get_event_loop() %timeit loop.run_until_complete(pipeline.arun(documents=documents, num_workers=4))
```
100%|██████████| 5/5 [00:01<00:00,  4.61it/s]
100%|██████████| 5/5 [00:00<00:00,  6.02it/s]
100%|██████████| 5/5 [00:01<00:00,  4.78it/s]
100%|██████████| 5/5 [00:01<00:00,  3.78it/s]
100%|██████████| 2/2 [00:00<00:00,  2.45it/s]
100%|██████████| 5/5 [00:01<00:00,  4.30it/s]
100%|██████████| 5/5 [00:00<00:00,  5.27it/s]
100%|██████████| 5/5 [00:01<00:00,  4.55it/s]
100%|██████████| 5/5 [00:02<00:00,  1.92it/s]
100%|██████████| 2/2 [00:00<00:00,  2.53it/s]
100%|██████████| 5/5 [00:00<00:00,  5.50it/s]
100%|██████████| 5/5 [00:01<00:00,  3.81it/s]
100%|██████████| 5/5 [00:01<00:00,  3.69it/s]
100%|██████████| 5/5 [00:02<00:00,  2.26it/s]
100%|██████████| 2/2 [00:00<00:00,  2.78it/s]
100%|██████████| 5/5 [00:01<00:00,  3.70it/s]
100%|██████████| 5/5 [00:01<00:00,  4.99it/s]
100%|██████████| 5/5 [00:01<00:00,  4.44it/s]
100%|██████████| 5/5 [00:01<00:00,  3.45it/s]
100%|██████████| 2/2 [00:00<00:00,  2.60it/s]
100%|██████████| 5/5 [00:01<00:00,  3.81it/s]
100%|██████████| 5/5 [00:01<00:00,  4.67it/s]
100%|██████████| 5/5 [00:01<00:00,  4.97it/s]
100%|██████████| 5/5 [00:01<00:00,  2.70it/s]
100%|██████████| 2/2 [00:00<00:00,  2.52it/s]
100%|██████████| 5/5 [00:01<00:00,  4.20it/s]
100%|██████████| 5/5 [00:01<00:00,  4.31it/s]
100%|██████████| 5/5 [00:01<00:00,  3.84it/s]
100%|██████████| 5/5 [00:01<00:00,  3.06it/s]
100%|██████████| 2/2 [00:00<00:00,  2.65it/s]
100%|██████████| 5/5 [00:01<00:00,  4.39it/s]
100%|██████████| 5/5 [00:01<00:00,  4.78it/s]
100%|██████████| 5/5 [00:01<00:00,  3.68it/s]
100%|██████████| 5/5 [00:01<00:00,  4.64it/s]
100%|██████████| 2/2 [00:00<00:00,  2.36it/s]
100%|██████████| 5/5 [00:01<00:00,  4.88it/s]
100%|██████████| 5/5 [00:00<00:00,  6.65it/s]
100%|██████████| 5/5 [00:01<00:00,  4.55it/s]
100%|██████████| 5/5 [00:01<00:00,  3.25it/s]
100%|██████████| 2/2 [00:00<00:00,  3.87it/s]

```

```
20.3 s ± 6.01 s per loop (mean ± std. dev. of 7 runs, 1 loop each)

```

In [ ]:
Copied!
```
loop = asyncio.get_event_loop()
cProfile.run(
    "loop.run_until_complete(pipeline.arun(documents=documents, num_workers=4))",
    "async-newstats",
)
p = pstats.Stats("async-newstats")
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)

```

loop = asyncio.get_event_loop() cProfile.run( "loop.run_until_complete(pipeline.arun(documents=documents, num_workers=4))", "async-newstats", ) p = pstats.Stats("async-newstats") p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)
```
100%|██████████| 5/5 [00:01<00:00,  3.55it/s]
100%|██████████| 5/5 [00:01<00:00,  4.64it/s]
100%|██████████| 5/5 [00:01<00:00,  4.65it/s]
100%|██████████| 5/5 [00:01<00:00,  2.83it/s]
100%|██████████| 2/2 [00:00<00:00,  3.81it/s]

```

```
Tue Jan  9 15:02:31 2024    async-newstats

         2780 function calls in 21.186 seconds

   Ordered by: cumulative time
   List reduced from 302 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   21.186   21.186 {built-in method builtins.exec}
        1    0.046    0.046   21.186   21.186 <string>:1(<module>)
        1    0.000    0.000   21.140   21.140 nest_asyncio.py:87(run_until_complete)
       14    0.000    0.000   21.140    1.510 nest_asyncio.py:101(_run_once)
       14    0.000    0.000   20.797    1.486 selectors.py:554(select)
       14   20.797    1.486   20.797    1.486 {method 'control' of 'select.kqueue' objects}
       27    0.000    0.000    0.343    0.013 events.py:78(_run)
       27    0.000    0.000    0.342    0.013 {method 'run' of '_contextvars.Context' objects}
        2    0.000    0.000    0.342    0.171 nest_asyncio.py:202(step)
        2    0.000    0.000    0.342    0.171 tasks.py:215(__step)
        2    0.000    0.000    0.342    0.171 {method 'send' of 'coroutine' objects}
        2    0.000    0.000    0.342    0.171 pipeline.py:478(arun)
       66    0.245    0.004    0.245    0.004 {method 'acquire' of '_thread.lock' objects}
        1    0.000    0.000    0.244    0.244 tasks.py:302(__wakeup)
        1    0.000    0.000    0.244    0.244 _base.py:648(__exit__)



```

Out[ ]:
```
<pstats.Stats at 0x1037abb80>
```

### Sequential Execution¶
By default `num_workers` is set to `None` and this will invoke sequential execution.
In [ ]:
Copied!
```
nodes = pipeline.run(documents=documents)

```

nodes = pipeline.run(documents=documents)
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.10it/s]

```

In [ ]:
Copied!
```
len(nodes)

```

len(nodes)
Out[ ]:


In [ ]:
Copied!
```
%timeit pipeline.run(documents=documents)

```

%timeit pipeline.run(documents=documents)
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00,  5.96it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.80it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.58it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.14it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.19it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.41it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.28it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  2.75it/s]

```

```
1min 11s ± 3.37 s per loop (mean ± std. dev. of 7 runs, 1 loop each)

```

In [ ]:
Copied!
```
cProfile.run("pipeline.run(documents=documents)", "oldstats")
p = pstats.Stats("oldstats")
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)

```

cProfile.run("pipeline.run(documents=documents)", "oldstats") p = pstats.Stats("oldstats") p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.95it/s]

```

```
Tue Jan  9 15:14:23 2024    oldstats

         5514413 function calls (5312843 primitive calls) in 74.119 seconds

   Ordered by: cumulative time
   List reduced from 1253 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   74.125   74.125 {built-in method builtins.exec}
        1    0.057    0.057   74.125   74.125 <string>:1(<module>)
        1    0.000    0.000   74.068   74.068 pipeline.py:378(run)
        1    0.000    0.000   74.068   74.068 pipeline.py:53(run_transformations)
        1    0.010    0.010   66.055   66.055 base.py:334(__call__)
        1    0.007    0.007   65.996   65.996 base.py:234(get_text_embedding_batch)
       53    0.000    0.000   65.976    1.245 openai.py:377(_get_text_embeddings)
       53    0.000    0.000   65.975    1.245 __init__.py:287(wrapped_f)
       53    0.003    0.000   65.975    1.245 __init__.py:369(__call__)
       53    0.001    0.000   65.966    1.245 openai.py:145(get_embeddings)
       53    0.001    0.000   65.947    1.244 embeddings.py:33(create)
       53    0.001    0.000   65.687    1.239 _base_client.py:1074(post)
       53    0.000    0.000   65.680    1.239 _base_client.py:844(request)
       53    0.002    0.000   65.680    1.239 _base_client.py:861(_request)
       53    0.001    0.000   64.171    1.211 _client.py:882(send)



```

Out[ ]:
```
<pstats.Stats at 0x154f45060>
```

### Async on Main Processor¶
As with the sync case, `num_workers` is default to `None`, which will then lead to single-batch execution of async tasks.
In [ ]:
Copied!
```
nodes = await pipeline.arun(documents=documents)

```

nodes = await pipeline.arun(documents=documents)
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.18it/s]

```

In [ ]:
Copied!
```
len(nodes)

```

len(nodes)
Out[ ]:


In [ ]:
Copied!
```
%timeit loop.run_until_complete(pipeline.arun(documents=documents))

```

%timeit loop.run_until_complete(pipeline.arun(documents=documents))
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.11it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.18it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.60it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.93it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.19it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.22it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.83it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.85it/s]

```

```
20.5 s ± 7.02 s per loop (mean ± std. dev. of 7 runs, 1 loop each)

```

In [ ]:
Copied!
```
cProfile.run(
    "loop.run_until_complete(pipeline.arun(documents=documents))",
    "async-oldstats",
)
p = pstats.Stats("async-oldstats")
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)

```

cProfile.run( "loop.run_until_complete(pipeline.arun(documents=documents))", "async-oldstats", ) p = pstats.Stats("async-oldstats") p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(15)
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  3.31it/s]

```

```
Tue Jan  9 15:17:38 2024    async-oldstats

         6967591 function calls (6754866 primitive calls) in 28.185 seconds

   Ordered by: cumulative time
   List reduced from 1210 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   28.191   28.191 {built-in method builtins.exec}
        1    0.000    0.000   28.191   28.191 <string>:1(<module>)
        1    0.008    0.008   28.191   28.191 nest_asyncio.py:87(run_until_complete)
     5111    0.046    0.000   28.181    0.006 nest_asyncio.py:101(_run_once)
     5111    0.031    0.000   18.727    0.004 selectors.py:554(select)
     8561   18.696    0.002   18.696    0.002 {method 'control' of 'select.kqueue' objects}
     8794    0.010    0.000    9.356    0.001 events.py:78(_run)
     8794    0.007    0.000    9.346    0.001 {method 'run' of '_contextvars.Context' objects}
     4602    0.007    0.000    9.154    0.002 nest_asyncio.py:202(step)
     4602    0.024    0.000    9.147    0.002 tasks.py:215(__step)
     4531    0.003    0.000    9.093    0.002 {method 'send' of 'coroutine' objects}
       16    0.000    0.000    6.004    0.375 pipeline.py:478(arun)
       16    0.000    0.000    6.004    0.375 pipeline.py:88(arun_transformations)
        1    0.000    0.000    5.889    5.889 schema.py:130(acall)
        1    0.000    0.000    5.889    5.889 interface.py:108(__call__)



```

Out[ ]:
```
<pstats.Stats at 0x2b157f310>
```

### In Summary¶
The results from the above experiments are re-shared below where each strategy is listed from fastest to slowest with this example dataset and pipeline.
  1. (Async, Parallel Processing): 20.3s
  2. (Async, No Parallel Processing): 20.5s
  3. (Sync, Parallel Processing): 29s
  4. (Sync, No Parallel Processing): 1min 11s


We can see that both cases that use Parallel Processing outperforms the Sync, No Parallel Processing (i.e., `.run(num_workers=None)`). Also, that at least for this case for Async tasks, there is little gains in using Parallel Processing. Perhaps for larger workloads and IngestionPipelines, using Async with Parallel Processing can lead to larger gains.
