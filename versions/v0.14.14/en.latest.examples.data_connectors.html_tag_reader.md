![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# HTML Tag Reader¶
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
### Download HTML file¶
In [ ]:
Copied!
```
%%bash
wget -e robots=off --no-clobber --page-requisites \
  --html-extension --convert-links --restrict-file-names=windows \
  --domains docs.ray.io --no-parent --accept=html \
  -P data/ https://docs.ray.io/en/master/ray-overview/installation.html

```

%%bash wget -e robots=off --no-clobber --page-requisites \ --html-extension --convert-links --restrict-file-names=windows \ --domains docs.ray.io --no-parent --accept=html \ -P data/ https://docs.ray.io/en/master/ray-overview/installation.html
```
Both --no-clobber and --convert-links were specified, only --convert-links will be used.
--2023-09-07 16:36:36--  https://docs.ray.io/en/master/ray-overview/installation.html
Resolving docs.ray.io (docs.ray.io)... 104.18.1.163, 104.18.0.163
Connecting to docs.ray.io (docs.ray.io)|104.18.1.163|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: unspecified [text/html]
Saving to: ‘data/docs.ray.io/en/master/ray-overview/installation.html’

     0K .......... .......... .......... .......... ..........  125M
    50K .......... .......... .......... .......... .......... 21.4M
   100K .......... .......... .......... ........              1.01M=0.04s

2023-09-07 16:36:37 (3.37 MB/s) - ‘data/docs.ray.io/en/master/ray-overview/installation.html’ saved [142067]

FINISHED --2023-09-07 16:36:37--
Total wall clock time: 0.3s
Downloaded: 1 files, 139K in 0.04s (3.37 MB/s)
Converting links in data/docs.ray.io/en/master/ray-overview/installation.html... 116.
48-68
Converted links in 1 files in 0.002 seconds.

```

In [ ]:
Copied!
```
from llama_index.readers.file import HTMLTagReader

reader = HTMLTagReader(tag="section", ignore_no_id=True)
docs = reader.load_data(
    "data/docs.ray.io/en/master/ray-overview/installation.html"
)

```

from llama_index.readers.file import HTMLTagReader reader = HTMLTagReader(tag="section", ignore_no_id=True) docs = reader.load_data( "data/docs.ray.io/en/master/ray-overview/installation.html" )
In [ ]:
Copied!
```
for doc in docs:
    print(doc.metadata)

```

for doc in docs: print(doc.metadata)
```
{'tag': 'section', 'tag_id': 'installing-ray', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'official-releases', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'from-wheels', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'daily-releases-nightlies', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'installing-from-a-specific-commit', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'install-ray-java-with-maven', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'install-ray-c', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'm1-mac-apple-silicon-support', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'windows-support', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'installing-ray-on-arch-linux', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'installing-from-conda-forge', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'building-ray-from-source', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'docker-source-images', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'launch-ray-in-docker', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'test-if-the-installation-succeeded', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}
{'tag': 'section', 'tag_id': 'installed-python-dependencies', 'file_path': 'data/docs.ray.io/en/master/ray-overview/installation.html'}

```

