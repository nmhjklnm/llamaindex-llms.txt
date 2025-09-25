# Llama guard moderator
##  LlamaGuardModeratorPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-llama-guard-moderator/llama_index/packs/llama_guard_moderator/base.py`

| ```
class LlamaGuardModeratorPack(BaseLlamaPack):
    def __init__(
        self,
        custom_taxonomy: str = DEFAULT_TAXONOMY,
    ) -> None:
        """Init params."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError(
                "Dependencies missing, run `pip install torch transformers`"
            )

        import os

        hf_access_token = os.environ.get("HUGGINGFACE_ACCESS_TOKEN")
        if not os.environ.get("HUGGINGFACE_ACCESS_TOKEN", None):
            raise ValueError("Hugging Face access token is missing or invalid.")

        from huggingface_hub import login

        login(token=hf_access_token)

        model_id = "meta-llama/LlamaGuard-7b"
        self.device = "cuda"
        dtype = torch.bfloat16

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=dtype, device_map=self.device
        )

        self.custom_taxonomy = custom_taxonomy

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "tokenizer": self.tokenizer,
            "model": self.model,
            "device": self.device,
            "custom_taxonomy": self.custom_taxonomy,
        }

    def run(self, message: str, **kwargs: Any) -> Any:
        """Run the pipeline."""
        # tailored for query engine input/output, using "user" role
        chat = [{"role": "user", "content": message}]

        prompt = self._moderation_prompt_for_chat(chat)
        inputs = self.tokenizer([prompt], return_tensors="pt").to(self.device)
        output = self.model.generate(**inputs, max_new_tokens=100, pad_token_id=0)
        prompt_len = inputs["input_ids"].shape[-1]
        return self.tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)

    def _moderation_prompt_for_chat(self, chat):
        # For simplicity, we assume the chat dictionary correctly alternates "user" and "assistant" roles
        conversation = [turn["content"] for turn in chat]
        role = "Agent" if len(conversation) % 2 == 0 else "User"
        prompt = f"""[INST] Task: Check if there is unsafe content in '{role}' messages in conversations according our safety policy with the below categories.

    <BEGIN UNSAFE CONTENT CATEGORIES>
    {self.custom_taxonomy}
    <END UNSAFE CONTENT CATEGORIES>

    <BEGIN CONVERSATION>

    """

        # Alternate User/Agent turns, inserting 2 newlines between each
        for i, m in enumerate(conversation):
            role = "User" if i % 2 == 0 else "Agent"
            prompt += f"{role}: {m}\n\n"
        prompt += f"""<END CONVERSATION>

    Provide your safety assessment for {role} in the above conversation:
    - First line must read 'safe' or 'unsafe'.
    - If unsafe, a second line must include a comma-separated list of violated categories. [/INST]"""
        return prompt

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-llama-guard-moderator/llama_index/packs/llama_guard_moderator/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "tokenizer": self.tokenizer,
        "model": self.model,
        "device": self.device,
        "custom_taxonomy": self.custom_taxonomy,
    }

```
  
---|---  
###  run #
```
run(message: str, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-llama-guard-moderator/llama_index/packs/llama_guard_moderator/base.py`

| ```
def run(self, message: str, **kwargs: Any) -> Any:
    """Run the pipeline."""
    # tailored for query engine input/output, using "user" role
    chat = [{"role": "user", "content": message}]

    prompt = self._moderation_prompt_for_chat(chat)
    inputs = self.tokenizer([prompt], return_tensors="pt").to(self.device)
    output = self.model.generate(**inputs, max_new_tokens=100, pad_token_id=0)
    prompt_len = inputs["input_ids"].shape[-1]
    return self.tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)

```
  
---|---
