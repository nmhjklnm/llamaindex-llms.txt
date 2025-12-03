![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Legacy Office Reader¶
The `LegacyOfficeReader` is the reader for Word-97(.doc) files. Under the hood, it uses Apache Tika to parse the file.
### Get Started¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙 and the legacy office reader.
> Note: Apache Tika is a dependency of the legacy office reader and it requires Java to be installed and call-able via `java --version`.
> For instance, on colab, you can install it with `!apt-get install default-jdk`. or on macOS, you can install it with `brew install openjdk`.
In [ ]:
Copied!
```
%pip install llama-index-readers-legacy-office

```

%pip install llama-index-readers-legacy-office
Prepare Data
So we need to prepare a .doc file for testing. Supposedly it's in `test_dir/harry_potter_lagacy.doc`
In [ ]:
Copied!
```
from llama_index.readers.legacy_office import LegacyOfficeReader

```

from llama_index.readers.legacy_office import LegacyOfficeReader
**Option 1** : Load the file with `LegacyOfficeReader`
In [ ]:
Copied!
```
file_path = "./test_dir/harry_potter_lagacy.doc"
reader = LegacyOfficeReader(
    excluded_embed_metadata_keys=["file_path", "file_name"],
    excluded_llm_metadata_keys=["file_type"],
)

```

file_path = "./test_dir/harry_potter_lagacy.doc" reader = LegacyOfficeReader( excluded_embed_metadata_keys=["file_path", "file_name"], excluded_llm_metadata_keys=["file_type"], )
In [ ]:
Copied!
```
docs = reader.load_data(file=file_path)
print(f"Loaded {len(docs)} docs")

```

docs = reader.load_data(file=file_path) print(f"Loaded {len(docs)} docs")
```
Loaded 1 docs

```

**Option 2** : Load the file with `SimpleDirectoryReader`
This is the path where we have `.doc` files together with other files in the same directory.
```
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader(
    input_dir="./test_dir/",
    file_extractor={
        ".doc": LegacyOfficeReader(),
        }
)

```

