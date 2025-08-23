# src/core/llm.py
class LLMClient:
    def __init__(self, provider: str, model: str, max_tokens: int):
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens

    def parse_text(self, text: str, task_type: str, context: dict | None = None) -> dict:
        # Stub: 真實情況呼叫外部 API
        if task_type == "extract_specs":
            # 最簡：以行為單位抓關鍵詞 (示例)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            items = []
            for l in lines:
                if ":" in l:
                    k, v = l.split(":", 1)
                    items.append({"name": k.strip(), "spec": v.strip()})
            return {"status": True, "message": "parsed", "result": {"raw_items": items}}
        return {"status": True, "message": "noop", "result": {}}

_llm_client: LLMClient | None = None

def get_llm_client():
    from ..config import settings
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(settings.LLM_PROVIDER, settings.LLM_MODEL, settings.MAX_LLM_TOKENS)
    return _llm_client
