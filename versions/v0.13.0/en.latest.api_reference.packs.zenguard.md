# Zenguard
##  ZenGuardPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-zenguard/llama_index/packs/zenguard/base.py`

| ```
class ZenGuardPack(BaseLlamaPack):
    def __init__(self, config: ZenGuardConfig):
        self._zenguard = ZenGuard(config)

    def get_modules(self) -> Dict[str, Any]:
        return {"zenguard": self._zenguard}

    def run(self, prompt: str, detectors: List[Detector]) -> Dict[str, Any]:
        return self._zenguard.detect(detectors, prompt)

```
  
---|---
