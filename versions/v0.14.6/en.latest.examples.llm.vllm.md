# vLLM¶
There's two modes of using vLLM local and remote. Let's start form the former one, which requeries CUDA environment available locally.
### Install vLLM¶
`pip install vllm`   
or if you want to compile you can compile from source
### Orca-7b Completion Example¶
In [ ]:
Copied!
```
%pip install llama-index-llms-vllm

```

%pip install llama-index-llms-vllm
In [ ]:
Copied!
```
import os

os.environ["HF_HOME"] = "model/"

```

import os os.environ["HF_HOME"] = "model/"
In [ ]:
Copied!
```
from llama_index.llms.vllm import Vllm

```

from llama_index.llms.vllm import Vllm
In [ ]:
Copied!
```
llm = Vllm(
    model="microsoft/Orca-2-7b",
    tensor_parallel_size=4,
    max_new_tokens=100,
    vllm_kwargs={"swap_space": 1, "gpu_memory_utilization": 0.5},
)

```

llm = Vllm( model="microsoft/Orca-2-7b", tensor_parallel_size=4, max_new_tokens=100, vllm_kwargs={"swap_space": 1, "gpu_memory_utilization": 0.5}, )
```
2023-12-03 00:40:26,298	INFO worker.py:1642 -- Started a local Ray instance.

```

```
INFO 12-03 00:40:27 llm_engine.py:72] Initializing an LLM engine with config: model='microsoft/Orca-2-7b', tokenizer='microsoft/Orca-2-7b', tokenizer_mode=auto, revision=None, trust_remote_code=True, dtype=torch.float16, max_seq_len=4096, download_dir=None, load_format=auto, tensor_parallel_size=4, quantization=None, seed=0)

```

```
(raylet) [2023-12-03 00:40:36,195 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438410240; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:40:46,207 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438385664; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:40:56,219 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438385664; capacity: 232947798016. Object creation will fail if spilling is required.
(RayWorker pid=3872755) Blocksparse is not available: the current GPU does not expose Tensor cores
(raylet) [2023-12-03 00:41:06,230 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438377472; capacity: 232947798016. Object creation will fail if spilling is required.

```

```
INFO 12-03 00:41:07 llm_engine.py:205] # GPU blocks: 898, # CPU blocks: 512

```

In [ ]:
Copied!
```
llm.complete(
    ["[INST]You are a helpful assistant[/INST] What is a black hole ?"]
)

```

llm.complete( ["[INST]You are a helpful assistant[/INST] What is a black hole ?"] )
```
Processed prompts: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:04<00:00,  4.36s/it]

```

Out[ ]:
```
[CompletionResponse(text="\n Especially for a beginner, a black hole is a place where gravity is so strong that it pulls everything, even light, towards itself. Imagine a well with a bottomless pit, but in space. Instead of being able to see the bottom, the gravity of the black hole is so strong that it makes the bottom disappear. It's like a point where the laws of physics, as we know them, break down.", additional_kwargs={}, raw=None, delta=None)]
```

```
(raylet) [2023-12-03 00:42:06,287 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438160384; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:42:16,297 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438156288; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:42:26,307 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438119424; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:42:36,316 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438111232; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:42:46,325 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438098944; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:42:56,334 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438098944; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:43:06,343 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438094848; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:43:16,352 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438082560; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 00:43:26,361 E 3871478 3871491] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_00-40-24_132284_3871321 is over 95% full, available space: 2438029312; capacity: 232947798016. Object creation will fail if spilling is required.
*** SIGTERM received at time=1701544410 on cpu 27 ***
PC: @     0x7faffa6bb46e  (unknown)  epoll_wait
    @     0x7faffa906420  (unknown)  (unknown)
[2023-12-03 00:43:30,340 E 3871321 3871321] logging.cc:361: *** SIGTERM received at time=1701544410 on cpu 27 ***
[2023-12-03 00:43:30,340 E 3871321 3871321] logging.cc:361: PC: @     0x7faffa6bb46e  (unknown)  epoll_wait
[2023-12-03 00:43:30,340 E 3871321 3871321] logging.cc:361:     @     0x7faffa906420  (unknown)  (unknown)

```

### LLama-2-7b Completion Example¶
In [ ]:
Copied!
```
llm = Vllm(
    model="codellama/CodeLlama-7b-hf",
    dtype="float16",
    tensor_parallel_size=4,
    temperature=0,
    max_new_tokens=100,
    vllm_kwargs={
        "swap_space": 1,
        "gpu_memory_utilization": 0.5,
        "max_model_len": 4096,
    },
)

```

llm = Vllm( model="codellama/CodeLlama-7b-hf", dtype="float16", tensor_parallel_size=4, temperature=0, max_new_tokens=100, vllm_kwargs={ "swap_space": 1, "gpu_memory_utilization": 0.5, "max_model_len": 4096, }, )
```
WARNING 12-03 01:02:02 config.py:341] Casting torch.bfloat16 to torch.float16.

```

```
2023-12-03 01:02:04,400	INFO worker.py:1642 -- Started a local Ray instance.

```

```
INFO 12-03 01:02:05 llm_engine.py:72] Initializing an LLM engine with config: model='codellama/CodeLlama-7b-hf', tokenizer='codellama/CodeLlama-7b-hf', tokenizer_mode=auto, revision=None, trust_remote_code=True, dtype=torch.float16, max_seq_len=4096, download_dir=None, load_format=auto, tensor_parallel_size=4, quantization=None, seed=0)
INFO 12-03 01:02:05 tokenizer.py:30] For some LLaMA V1 models, initializing the fast tokenizer may take a long time. To reduce the initialization time, consider using 'hf-internal-testing/llama-tokenizer' instead of the original tokenizer.

```

```
(raylet) [2023-12-03 01:02:14,296 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434420736; capacity: 232947798016. Object creation will fail if spilling is required.
(RayWorker pid=3882520) Blocksparse is not available: the current GPU does not expose Tensor cores

```

```
INFO 12-03 01:02:22 llm_engine.py:205] # GPU blocks: 850, # CPU blocks: 512

```

In [ ]:
Copied!
```
llm.complete(["import socket\n\ndef ping_exponential_backoff(host: str):"])

```

llm.complete(["import socket\n\ndef ping_exponential_backoff(host: str):"])
```
Processed prompts:   0%|                                                                                                                                                              | 0/1 [00:00<?, ?it/s](raylet) [2023-12-03 01:02:24,306 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434400256; capacity: 232947798016. Object creation will fail if spilling is required.
Processed prompts: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:04<00:00,  4.64s/it]

```

Out[ ]:
```
[CompletionResponse(text='\n    """\n    Ping a host with exponential backoff.\n    """\n    # Setup the socket\n    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    s.settimeout(1)\n\n    # Setup the exponential backoff\n    backoff = 1\n    max_backoff = 10\n\n    # Ping the host\n    while True:\n        try', additional_kwargs={}, raw=None, delta=None)]
```

```
(raylet) [2023-12-03 01:02:34,315 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434396160; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:02:44,324 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434392064; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:02:54,333 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434383872; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:03:04,342 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434355200; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:03:14,352 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434199552; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:03:24,361 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434174976; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:03:34,371 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434166784; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:03:44,380 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434162688; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:03:54,389 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434158592; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:04:04,398 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434117632; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:04:14,407 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434142208; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:04:24,416 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434134016; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:04:34,425 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434125824; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:04:44,434 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434121728; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:04:54,443 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434109440; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:05:04,453 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2434072576; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:05:14,461 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2433916928; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:05:24,471 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2433912832; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:05:34,480 E 3881242 3881255] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-02-02_227423_3880966 is over 95% full, available space: 2433904640; capacity: 232947798016. Object creation will fail if spilling is required.
*** SIGTERM received at time=1701545737 on cpu 19 ***
PC: @     0x7fd7e3e3246e  (unknown)  epoll_wait
    @     0x7fd7e407d420  (unknown)  (unknown)
[2023-12-03 01:05:37,122 E 3880966 3880966] logging.cc:361: *** SIGTERM received at time=1701545737 on cpu 19 ***
[2023-12-03 01:05:37,122 E 3880966 3880966] logging.cc:361: PC: @     0x7fd7e3e3246e  (unknown)  epoll_wait
[2023-12-03 01:05:37,122 E 3880966 3880966] logging.cc:361:     @     0x7fd7e407d420  (unknown)  (unknown)

```

### Mistral chat 7b Completion Example¶
In [ ]:
Copied!
```
llm = Vllm(
    model="mistralai/Mistral-7B-Instruct-v0.1",
    dtype="float16",
    tensor_parallel_size=4,
    temperature=0,
    max_new_tokens=100,
    vllm_kwargs={
        "swap_space": 1,
        "gpu_memory_utilization": 0.5,
        "max_model_len": 4096,
    },
)

```

llm = Vllm( model="mistralai/Mistral-7B-Instruct-v0.1", dtype="float16", tensor_parallel_size=4, temperature=0, max_new_tokens=100, vllm_kwargs={ "swap_space": 1, "gpu_memory_utilization": 0.5, "max_model_len": 4096, }, )
```
WARNING 12-03 01:06:44 config.py:341] Casting torch.bfloat16 to torch.float16.

```

```
2023-12-03 01:06:47,045	INFO worker.py:1642 -- Started a local Ray instance.

```

```
INFO 12-03 01:06:48 llm_engine.py:72] Initializing an LLM engine with config: model='mistralai/Mistral-7B-Instruct-v0.1', tokenizer='mistralai/Mistral-7B-Instruct-v0.1', tokenizer_mode=auto, revision=None, trust_remote_code=True, dtype=torch.float16, max_seq_len=4096, download_dir=None, load_format=auto, tensor_parallel_size=4, quantization=None, seed=0)

```

```
(raylet) [2023-12-03 01:06:56,943 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433503232; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:07:06,955 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433474560; capacity: 232947798016. Object creation will fail if spilling is required.
(RayWorker pid=3885160) Blocksparse is not available: the current GPU does not expose Tensor cores
(raylet) [2023-12-03 01:07:16,966 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433470464; capacity: 232947798016. Object creation will fail if spilling is required.

```

```
INFO 12-03 01:07:19 llm_engine.py:205] # GPU blocks: 2764, # CPU blocks: 2048

```

```
(raylet) [2023-12-03 01:07:26,975 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433462272; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:07:36,984 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433458176; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:07:46,994 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433429504; capacity: 232947798016. Object creation will fail if spilling is required.

```

In [ ]:
Copied!
```
llm.complete([" What is a black hole ?"])

```

llm.complete([" What is a black hole ?"])
```
Processed prompts:   0%|                                                                                                                                                              | 0/1 [00:00<?, ?it/s](raylet) [2023-12-03 01:08:07,011 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433265664; capacity: 232947798016. Object creation will fail if spilling is required.
Processed prompts: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:05<00:00,  5.30s/it]

```

Out[ ]:
```
[CompletionResponse(text='\nA black hole is a region of space from which nothing, not even light, can escape. It is believed to be the result of the gravitational collapse of the remnants of an extremely massive star. The gravitational force within a black hole is incredibly strong and is due to the fact that a massive amount of matter has been squeezed into an incredibly small space. Because of this, black holes are extremely difficult to observe directly, as nothing can escape from them. Instead, scientists study the', additional_kwargs={}, raw=None, delta=None)]
```

```
(raylet) [2023-12-03 01:08:17,020 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433232896; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:08:27,029 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433200128; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:08:37,038 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433200128; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:08:47,048 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433163264; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:08:57,058 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433150976; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:09:07,067 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433146880; capacity: 232947798016. Object creation will fail if spilling is required.
(raylet) [2023-12-03 01:09:17,076 E 3883882 3883896] (raylet) file_system_monitor.cc:111: /tmp/ray/session_2023-12-03_01-06-44_873224_3883710 is over 95% full, available space: 2433138688; capacity: 232947798016. Object creation will fail if spilling is required.

```

# Calling vLLM via HTTP¶
In this mode there is no need to install `vllm` model nor have CUDA available locally. To setup the vLLM API you can follow the guide present here. Note: `llama-index-llms-vllm` module is a client for `vllm.entrypoints.api_server` which is only a demo.   
If vLLM server is launched with `vllm.entrypoints.openai.api_server` as OpenAI Compatible Server or via Docker you need `OpenAILike` class from `llama-index-llms-openai-like` module
### Completion Response¶
In [ ]:
Copied!
```
from llama_index.llms.vllm import VllmServer
from llama_index.core.llms import ChatMessage

```

from llama_index.llms.vllm import VllmServer from llama_index.core.llms import ChatMessage
In [ ]:
Copied!
```
llm = VllmServer(
    api_url="http://localhost:8000/generate", max_new_tokens=100, temperature=0
)

```

llm = VllmServer( api_url="http://localhost:8000/generate", max_new_tokens=100, temperature=0 )
In [ ]:
Copied!
```
llm.complete("what is a black hole ?")

```

llm.complete("what is a black hole ?")
Out[ ]:
```
CompletionResponse(text='what is a black hole ?\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed when a massive star dies and its core collapses under the intense pressure of its own gravity. The core becomes infinitely dense and small, known as a singularity, and anything that gets too close to it is pulled in by the incredibly strong gravitational force. Black holes can have different masses, from small ones that are barely noticeable to', additional_kwargs={}, raw=None, delta=None)
```

In [ ]:
Copied!
```
message = [ChatMessage(content="hello", role="user")]
llm.chat(message)

```

message = [ChatMessage(content="hello", role="user")] llm.chat(message)
Out[ ]:
```
ChatResponse(message=ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='user: hello\nassistant: 안녕하세요! 어떻게 도움이 되겠습니까?', additional_kwargs={}), raw=None, delta=None, additional_kwargs={})
```

### Streaming Response¶
In [ ]:
Copied!
```
list(llm.stream_complete("what is a black hole"))[-1]

```

list(llm.stream_complete("what is a black hole"))[-1]
Out[ ]:
```
CompletionResponse(text='what is a black hole?\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed when a massive star dies and its core collapses under the intense pressure of its own gravity. They are invisible, but their presence can be detected by the effects of their gravity on nearby matter, such as stars and gas. Black holes are thought to be the most dense objects in the universe, with masses up to several times that of the', additional_kwargs={}, raw=None, delta=None)
```

In [ ]:
Copied!
```
message = [ChatMessage(content="what is a black hole", role="user")]
[x for x in llm.stream_chat(message)][-1]

```

message = [ChatMessage(content="what is a black hole", role="user")] [x for x in llm.stream_chat(message)][-1]
Out[ ]:
```
ChatResponse(message=ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='user: what is a black hole\nassistant: \n\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed when a massive star dies and its core collapses under the intense pressure of its own gravity. They are invisible, but their presence can be detected by the effects of their gravity on nearby matter, such as stars and gas. Black holes are thought to be the most dense objects in the universe, with masses up to several times that of the', additional_kwargs={}), raw=None, delta=None, additional_kwargs={})
```

### Async Response¶
In [ ]:
Copied!
```
await llm.acomplete("What is a black hole")

```

await llm.acomplete("What is a black hole")
Out[ ]:
```
CompletionResponse(text='What is a black hole?\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed from the remnants of massive stars that have collapsed onto themselves. They are invisible, but their presence can be detected by the effects of their gravity on nearby matter, such as stars and gas. Black holes come in different sizes, with the smallest being only a few miles across, and the largest being billions of times larger than our Sun', additional_kwargs={}, raw=None, delta=None)
```

In [ ]:
Copied!
```
await llm.achat(message)

```

await llm.achat(message)
Out[ ]:
```
ChatResponse(message=ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='user: what is a black hole\nassistant: \n\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed when a massive star dies and its core collapses under the intense pressure of its own gravity. They are invisible, but their presence can be detected by the effects of their gravity on nearby matter, such as stars and gas. Black holes are thought to be the most dense objects in the universe, with masses up to several times that of the', additional_kwargs={}), raw=None, delta=None, additional_kwargs={})
```

In [ ]:
Copied!
```
[x async for x in await llm.astream_complete("what is a black hole")][-1]

```

[x async for x in await llm.astream_complete("what is a black hole")][-1]
Out[ ]:
```
CompletionResponse(text='what is a black hole?\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed when a massive star dies and its core collapses under the intense pressure of its own gravity. They are invisible, but their presence can be detected by the effects of their gravity on nearby matter, such as stars and gas. Black holes are thought to be the most dense objects in the universe, with masses up to several times that of the', additional_kwargs={}, raw=None, delta=None)
```

In [ ]:
Copied!
```
[x for x in await llm.astream_chat(message)][-1]

```

[x for x in await llm.astream_chat(message)][-1]
Out[ ]:
```
ChatResponse(message=ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='user: what is a black hole\nassistant: \n\nA black hole is a region of space-time where gravity is so strong that nothing, not even light, can escape. Black holes are formed when a massive star dies and its core collapses under the intense pressure of its own gravity. They are invisible, but their presence can be detected by the effects of their gravity on nearby matter, such as stars and gas. Black holes are thought to be the most dense objects in the universe, with masses up to several times that of the', additional_kwargs={}), raw=None, delta=None, additional_kwargs={})
```

