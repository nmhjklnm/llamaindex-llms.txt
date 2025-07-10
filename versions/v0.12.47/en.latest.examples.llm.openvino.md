![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# OpenVINO LLMs¶
OpenVINO™ is an open-source toolkit for optimizing and deploying AI inference. OpenVINO™ Runtime can enable running the same model optimized across various hardware devices. Accelerate your deep learning performance across use cases like: language + LLMs, computer vision, automatic speech recognition, and more.
OpenVINO models can be run locally through `OpenVINOLLM` entitiy wrapped by LlamaIndex :
In the below line, we install the packages necessary for this demo:
In [ ]:
Copied!
```
%pip install llama-index-llms-openvino transformers huggingface_hub

```

%pip install llama-index-llms-openvino transformers huggingface_hub
Now that we're set up, let's play around:
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.openvino import OpenVINOLLM

```

from llama_index.llms.openvino import OpenVINOLLM
In [ ]:
Copied!
```
def messages_to_prompt(messages):
    prompt = ""
    for message in messages:
        if message.role == "system":
            prompt += f"<|system|>\n{message.content}</s>\n"
        elif message.role == "user":
            prompt += f"<|user|>\n{message.content}</s>\n"
        elif message.role == "assistant":
            prompt += f"<|assistant|>\n{message.content}</s>\n"

    # ensure we start with a system prompt, insert blank if needed
    if not prompt.startswith("<|system|>\n"):
        prompt = "<|system|>\n</s>\n" + prompt

    # add final assistant prompt
    prompt = prompt + "<|assistant|>\n"

    return prompt


def completion_to_prompt(completion):
    return f"<|system|>\n</s>\n<|user|>\n{completion}</s>\n<|assistant|>\n"

```

def messages_to_prompt(messages): prompt = "" for message in messages: if message.role == "system": prompt += f"<|system|>\n{message.content}\n" elif message.role == "user": prompt += f"<|user|>\n{message.content}\n" elif message.role == "assistant": prompt += f"<|assistant|>\n{message.content}\n" # ensure we start with a system prompt, insert blank if needed if not prompt.startswith("<|system|>\n"): prompt = "<|system|>\n\n" + prompt # add final assistant prompt prompt = prompt + "<|assistant|>\n" return prompt def completion_to_prompt(completion): return f"<|system|>\n\n<|user|>\n{completion}\n<|assistant|>\n"
### Model Loading¶
Models can be loaded by specifying the model parameters using the `OpenVINOLLM` method.
If you have an Intel GPU, you can specify `device_map="gpu"` to run inference on it.
In [ ]:
Copied!
```
ov_config = {
    "PERFORMANCE_HINT": "LATENCY",
    "NUM_STREAMS": "1",
    "CACHE_DIR": "",
}

ov_llm = OpenVINOLLM(
    model_id_or_path="HuggingFaceH4/zephyr-7b-beta",
    context_window=3900,
    max_new_tokens=256,
    model_kwargs={"ov_config": ov_config},
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    device_map="cpu",
)

```

ov_config = { "PERFORMANCE_HINT": "LATENCY", "NUM_STREAMS": "1", "CACHE_DIR": "", } ov_llm = OpenVINOLLM( model_id_or_path="HuggingFaceH4/zephyr-7b-beta", context_window=3900, max_new_tokens=256, model_kwargs={"ov_config": ov_config}, generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95}, messages_to_prompt=messages_to_prompt, completion_to_prompt=completion_to_prompt, device_map="cpu", )
In [ ]:
Copied!
```
response = ov_llm.complete("What is the meaning of life?")
print(str(response))

```

response = ov_llm.complete("What is the meaning of life?") print(str(response))
### Inference with local OpenVINO model¶
It is possible to export your model to the OpenVINO IR format with the CLI, and load the model from local folder.
In [ ]:
Copied!
```
!optimum-cli export openvino --model HuggingFaceH4/zephyr-7b-beta ov_model_dir

```

!optimum-cli export openvino --model HuggingFaceH4/zephyr-7b-beta ov_model_dir
It is recommended to apply 8 or 4-bit weight quantization to reduce inference latency and model footprint using `--weight-format`:
In [ ]:
Copied!
```
!optimum-cli export openvino --model HuggingFaceH4/zephyr-7b-beta --weight-format int8 ov_model_dir

```

!optimum-cli export openvino --model HuggingFaceH4/zephyr-7b-beta --weight-format int8 ov_model_dir
In [ ]:
Copied!
```
!optimum-cli export openvino --model HuggingFaceH4/zephyr-7b-beta --weight-format int4 ov_model_dir

```

!optimum-cli export openvino --model HuggingFaceH4/zephyr-7b-beta --weight-format int4 ov_model_dir
In [ ]:
Copied!
```
ov_llm = OpenVINOLLM(
    model_id_or_path="ov_model_dir",
    context_window=3900,
    max_new_tokens=256,
    model_kwargs={"ov_config": ov_config},
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    device_map="gpu",
)

```

ov_llm = OpenVINOLLM( model_id_or_path="ov_model_dir", context_window=3900, max_new_tokens=256, model_kwargs={"ov_config": ov_config}, generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95}, messages_to_prompt=messages_to_prompt, completion_to_prompt=completion_to_prompt, device_map="gpu", )
You can get additional inference speed improvement with Dynamic Quantization of activations and KV-cache quantization. These options can be enabled with `ov_config` as follows:
In [ ]:
Copied!
```
ov_config = {
    "KV_CACHE_PRECISION": "u8",
    "DYNAMIC_QUANTIZATION_GROUP_SIZE": "32",
    "PERFORMANCE_HINT": "LATENCY",
    "NUM_STREAMS": "1",
    "CACHE_DIR": "",
}

```

ov_config = { "KV_CACHE_PRECISION": "u8", "DYNAMIC_QUANTIZATION_GROUP_SIZE": "32", "PERFORMANCE_HINT": "LATENCY", "NUM_STREAMS": "1", "CACHE_DIR": "", }
### Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
response = ov_llm.stream_complete("Who is Paul Graham?")
for r in response:
    print(r.delta, end="")

```

response = ov_llm.stream_complete("Who is Paul Graham?") for r in response: print(r.delta, end="")
Using `stream_chat` endpoint
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="What is your name"),
]
resp = ov_llm.stream_chat(messages)

for r in resp:
    print(r.delta, end="")

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="What is your name"), ] resp = ov_llm.stream_chat(messages) for r in resp: print(r.delta, end="")
For more information refer to:
  * OpenVINO LLM guide.
  * OpenVINO Documentation.
  * OpenVINO Get Started Guide.
  * RAG example with LlamaIndex.


