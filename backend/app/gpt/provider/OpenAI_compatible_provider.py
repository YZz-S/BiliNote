from typing import Iterable, Optional, Union

from openai import OpenAI

from app.utils.logger import get_logger

logging= get_logger(__name__)
class OpenAICompatibleProvider:
    def __init__(self, api_key: str, base_url: str, model: Union[str, None]=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    @property
    def get_client(self):
        return self.client

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        return (base_url or "").strip().rstrip("/")

    @staticmethod
    def _merge_candidates(*candidate_groups: Iterable[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for group in candidate_groups:
            for candidate in group or []:
                value = (candidate or "").strip()
                if value and value not in seen:
                    seen.add(value)
                    merged.append(value)
        return merged

    @staticmethod
    def _guess_model_candidates(base_url: str, provider_name: Optional[str]) -> list[str]:
        hint = f"{provider_name or ''} {base_url}".lower()
        if "xiaomimimo" in hint or "mimo" in hint:
            return ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-v2.5", "mimo-v2-flash"]
        if "deepseek" in hint:
            return ["deepseek-chat"]
        if "dashscope" in hint or "qwen" in hint:
            return ["qwen-plus", "qwen-turbo", "qwen-max"]
        if "generativelanguage.googleapis.com" in hint or "gemini" in hint:
            return ["gemini-2.5-flash", "gemini-2.5-pro"]
        if "api.openai.com" in hint or "openai" in hint:
            return ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"]
        if "api.groq.com" in hint or "groq" in hint:
            return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        return []

    @staticmethod
    def _is_auth_error(error: Optional[Exception]) -> bool:
        if error is None:
            return False
        message = str(error).lower()
        return "invalid api key" in message or "invalid_key" in message or "401" in message

    @staticmethod
    def test_connection(
        api_key: str,
        base_url: str,
        provider_name: Optional[str] = None,
        model_candidates: Optional[list[str]] = None,
    ) -> bool:
        normalized_base_url = OpenAICompatibleProvider._normalize_base_url(base_url)
        if not normalized_base_url:
            raise ValueError("Base URL 不能为空")
        if normalized_base_url.endswith("/chat/completions"):
            raise ValueError("Base URL 只需填写到 /v1，不要填写 /chat/completions")

        client = OpenAI(api_key=api_key, base_url=normalized_base_url)
        discovered_models: list[str] = []
        list_error: Optional[Exception] = None

        try:
            models = client.models.list()
            discovered_models = [
                item.id for item in getattr(models, "data", []) if getattr(item, "id", None)
            ]
        except Exception as e:
            list_error = e
            logging.info(f"模型列表探测失败：{e}")

        if OpenAICompatibleProvider._is_auth_error(list_error):
            raise ValueError("API Key 无效，请检查 Xiaomi Mimo 控制台生成的 Key 是否填写正确")

        candidates = OpenAICompatibleProvider._merge_candidates(
            model_candidates or [],
            OpenAICompatibleProvider._guess_model_candidates(
                normalized_base_url, provider_name
            ),
            discovered_models,
        )

        if not candidates:
            if "xiaomimimo" in normalized_base_url.lower() or "mimo" in (
                provider_name or ""
            ).lower():
                raise ValueError(
                    "未探测到可用模型。Xiaomi Mimo 请将 Base URL 填为 https://api.xiaomimimo.com/v1，"
                    "然后使用如 mimo-v2.5-pro 或 mimo-v2-flash 的模型名。"
                )
            if list_error:
                raise ValueError(f"无法探测可用模型：{list_error}")
            raise ValueError("未探测到可用模型，请先保存至少一个模型后再测试连通性")

        last_error: Optional[Exception] = None
        for model_name in candidates:
            try:
                client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "ping"}],
                    temperature=0,
                )
                logging.info("连通性测试成功，model=%s", model_name)
                return True
            except Exception as e:
                last_error = e
                logging.info("聊天探活失败，model=%s error=%s", model_name, e)
                if OpenAICompatibleProvider._is_auth_error(e):
                    raise ValueError("API Key 无效，请检查 Xiaomi Mimo 控制台生成的 Key 是否填写正确")

        if "xiaomimimo" in normalized_base_url.lower() or "mimo" in (
            provider_name or ""
        ).lower():
            raise ValueError(
                "Xiaomi Mimo 连通性测试失败。请确认 Base URL 为 https://api.xiaomimimo.com/v1，"
                "不要填写 /chat/completions，并检查 API Key 与模型名是否有效。"
            )
        raise ValueError(f"连通性测试失败：{last_error or '未知错误'}")
