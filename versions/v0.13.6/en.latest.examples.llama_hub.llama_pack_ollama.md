# Ollama Llama Pack Example¶
### Setup Data¶
In [ ]:
Copied!
```
!wget "https://www.dropbox.com/s/f6bmb19xdg0xedm/paul_graham_essay.txt?dl=1" -O paul_graham_essay.txt

```

!wget "https://www.dropbox.com/s/f6bmb19xdg0xedm/paul_graham_essay.txt?dl=1" -O paul_graham_essay.txt
```
--2023-12-06 10:57:29--  https://www.dropbox.com/s/f6bmb19xdg0xedm/paul_graham_essay.txt?dl=1
Resolving www.dropbox.com (www.dropbox.com)... 2620:100:6057:18::a27d:d12, 162.125.13.18
Connecting to www.dropbox.com (www.dropbox.com)|2620:100:6057:18::a27d:d12|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: /s/dl/f6bmb19xdg0xedm/paul_graham_essay.txt [following]
--2023-12-06 10:57:29--  https://www.dropbox.com/s/dl/f6bmb19xdg0xedm/paul_graham_essay.txt
Reusing existing connection to [www.dropbox.com]:443.
HTTP request sent, awaiting response... 302 Found
Location: https://uc2fc064df073edb14568cb68878.dl.dropboxusercontent.com/cd/0/get/CI6sL69BcU1vwbM-TAz-tGmRw4WlbgfQuJZeNXywf2hq34Y0hCCL--A7gVBWo6T3igijCNDkLGnPwDiugV9pIEtnFODeIcET5PwUgToHl2-1P77MqJy2okrGt6CmC5bxwI5OPEV4MGsUNvSHP34FLMWZ/file?dl=1# [following]
--2023-12-06 10:57:30--  https://uc2fc064df073edb14568cb68878.dl.dropboxusercontent.com/cd/0/get/CI6sL69BcU1vwbM-TAz-tGmRw4WlbgfQuJZeNXywf2hq34Y0hCCL--A7gVBWo6T3igijCNDkLGnPwDiugV9pIEtnFODeIcET5PwUgToHl2-1P77MqJy2okrGt6CmC5bxwI5OPEV4MGsUNvSHP34FLMWZ/file?dl=1
Resolving uc2fc064df073edb14568cb68878.dl.dropboxusercontent.com (uc2fc064df073edb14568cb68878.dl.dropboxusercontent.com)... 2620:100:6057:15::a27d:d0f, 162.125.13.15
Connecting to uc2fc064df073edb14568cb68878.dl.dropboxusercontent.com (uc2fc064df073edb14568cb68878.dl.dropboxusercontent.com)|2620:100:6057:15::a27d:d0f|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75047 (73K) [application/binary]
Saving to: ‘paul_graham_essay.txt’

paul_graham_essay.t 100%[===================>]  73.29K  --.-KB/s    in 0.02s   

2023-12-06 10:57:30 (4.02 MB/s) - ‘paul_graham_essay.txt’ saved [75047/75047]


```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# load in some sample data
reader = SimpleDirectoryReader(input_files=["paul_graham_essay.txt"])
documents = reader.load_data()

```

from llama_index.core import SimpleDirectoryReader # load in some sample data reader = SimpleDirectoryReader(input_files=["paul_graham_essay.txt"]) documents = reader.load_data()
### Start Ollama¶
Make sure you run `ollama run llama2` in a terminal.
In [ ]:
Copied!
```
# !ollama run llama2

```

# !ollama run llama2
### Download and Initialize Pack¶
We use `download_llama_pack` to download the pack class, and then we initialize it with documents.
Every pack will have different initialization parameters. You can find more about the initialization parameters for each pack through its README (also on LlamaHub).
**NOTE** : You must also specify an output directory. In this case the pack is downloaded to `voyage_pack`. This allows you to customize and make changes to the file, and import it later!
In [ ]:
Copied!
```
from llama_index.core.llama_pack import download_llama_pack

# download and install dependencies
OllamaQueryEnginePack = download_llama_pack(
    "OllamaQueryEnginePack", "./ollama_pack"
)

```

from llama_index.core.llama_pack import download_llama_pack # download and install dependencies OllamaQueryEnginePack = download_llama_pack( "OllamaQueryEnginePack", "./ollama_pack" )
In [ ]:
Copied!
```
# You can use any llama-hub loader to get documents!
ollama_pack = OllamaQueryEnginePack(model="llama2", documents=documents)

```

# You can use any llama-hub loader to get documents! ollama_pack = OllamaQueryEnginePack(model="llama2", documents=documents)
In [ ]:
Copied!
```
response = ollama_pack.run("What did the author do growing up?")

```

response = ollama_pack.run("What did the author do growing up?")
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Based on the information provided in the context, the author did not mention anything about what he did growing up. The text only covers his experiences as an adult, including his work at Viaweb, Y Combinator, and his interest in painting. There is no information given about the author's childhood or formative years.

```

