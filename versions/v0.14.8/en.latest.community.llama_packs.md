# Llama Packs 🦙📦#
## Concept#
Llama Packs are a community-driven hub of **prepackaged modules/templates** you can use to kickstart your LLM app.
This directly tackles a big pain point in building LLM apps; every use case requires cobbling together custom components and a lot of tuning/dev time. Our goal is to accelerate that through a community led effort.
They can be used in two ways:
  * On one hand, they are **prepackaged modules** that can be initialized with parameters and run out of the box to achieve a given use case (whether that’s a full RAG flow, application template, or more). You can also import submodules (e.g. LLMs, query engines) to use directly.
  * On the other hand, LlamaPacks are **templates** that you can inspect, modify, and use.


**All packs are found onLlamaHub.** Go to the dropdown menu and select "LlamaPacks" to filter by packs.
**Please check the README of each pack for details on how to use**. Example pack here.
See our launch blog post for more details.
## Usage Pattern#
You can use Llama Packs through either the CLI or Python.
CLI:
```
llamaindex-cli download-llamapack <pack_name> --download-dir <pack_directory>

```

Python:
```
from llama_index.core.llama_pack import download_llama_pack

# download and install dependencies
pack_cls = download_llama_pack("<pack_name>", "<pack_directory>")

```

You can use the pack in different ways, either to inspect modules, run it e2e, or customize the templates.
```
# every pack is initialized with different args
pack = pack_cls(*args, **kwargs)

# get modules
modules = pack.get_modules()
display(modules)

# run (every pack will have different args)
output = pack.run(*args, **kwargs)

```

Importantly, you can/should also go into `pack_directory` to inspect the source files/customize it. That's part of the point!
## Module Guides#
Some example module guides are given below. Remember, go on LlamaHub to access the full range of packs.
  * LlamaPacks Example
  * Resume LlamaPack
  * Ollama LlamaPack


