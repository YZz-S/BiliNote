from app.gpt.base import GPT
from app.gpt.prompt_builder import generate_base_prompt
from app.models.gpt_model import GPTSource
from app.gpt.prompt import BASE_PROMPT, AI_SUM, SCREENSHOT, LINK
from app.gpt.utils import fix_markdown
from app.models.transcriber_model import TranscriptSegment
from datetime import timedelta
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

# 默认阈值（可被环境变量覆盖）
DEFAULT_MAX_INPUT_LENGTH = 120000
DEFAULT_MIN_CHUNK_LENGTH = 6000

class UniversalGPT(GPT):
    def __init__(self, client, model: str, temperature: float = 0.7):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.screenshot = False
        self.link = False
        self.max_input_length = self._resolve_max_input_length(model)
        self.min_chunk_length = self._resolve_min_chunk_length()

    def _resolve_max_input_length(self, model_name: str) -> int:
        """
        优先级：
        1) 环境变量 BILINOTE_GPT_MAX_INPUT_LENGTH（手动配置）
        2) 按模型名自动估算
        3) 默认值
        """
        manual = os.getenv("BILINOTE_GPT_MAX_INPUT_LENGTH")
        if manual:
            try:
                value = int(manual)
                if value > 0:
                    return value
            except ValueError:
                logger.warning("BILINOTE_GPT_MAX_INPUT_LENGTH 非法，忽略该配置: %s", manual)

        name = (model_name or "").lower()
        # 这是 prompt 文本字符预算，不是 token 数；保守估计，避免网关/中转触发 413
        if any(k in name for k in ["deepseek-v4", "deepseek-r1", "deepseek-chat"]):
            return 200000
        if any(k in name for k in ["gpt-4.1", "gpt-5", "claude", "gemini"]):
            return 160000
        if any(k in name for k in ["qwen", "gpt-4o", "gpt-4-turbo"]):
            return 120000
        return DEFAULT_MAX_INPUT_LENGTH

    def _resolve_min_chunk_length(self) -> int:
        manual = os.getenv("BILINOTE_GPT_MIN_CHUNK_LENGTH")
        if manual:
            try:
                value = int(manual)
                if value > 0:
                    return value
            except ValueError:
                logger.warning("BILINOTE_GPT_MIN_CHUNK_LENGTH 非法，忽略该配置: %s", manual)
        return DEFAULT_MIN_CHUNK_LENGTH

    def _format_time(self, seconds: float) -> str:
        return str(timedelta(seconds=int(seconds)))[2:]

    def _build_segment_text(self, segments: List[TranscriptSegment]) -> str:
        return "\n".join(
            f"{self._format_time(seg.start)} - {seg.text.strip()}"
            for seg in segments
        )

    def ensure_segments_type(self, segments) -> List[TranscriptSegment]:
        return [TranscriptSegment(**seg) if isinstance(seg, dict) else seg for seg in segments]

    def create_messages(self, segments: List[TranscriptSegment], **kwargs):
        content_text = generate_base_prompt(
            title=kwargs.get('title'),
            segment_text=self._build_segment_text(segments),
            tags=kwargs.get('tags'),
            _format=kwargs.get('_format'),
            style=kwargs.get('style'),
            extras=kwargs.get('extras'),
        )

        # 检查并截断过长的输入文本
        if len(content_text) > self.max_input_length:
            logger.warning(
                "输入文本长度 %s 超过限制 %s，将进行截断处理",
                len(content_text),
                self.max_input_length,
            )
            # 保留提示词部分和前部分转录内容
            content_text = self._truncate_content(content_text, self.max_input_length)
            logger.info(f"截断后文本长度: {len(content_text)}")

        # ⛳ 组装 content 数组，支持 text + image_url 混合
        content = [{"type": "text", "text": content_text}]
        video_img_urls = kwargs.get('video_img_urls', [])

        for url in video_img_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": url,
                    "detail": "auto"
                }
            })

        #  正确格式：整体包在一个 message 里，role + content array
        messages = [{
            "role": "user",
            "content": content
        }]

        return messages

    def _truncate_content(self, content: str, max_length: int) -> str:
        """
        截断过长的内容，尽量保留提示词和前面的转录内容
        """
        # 简单实现：直接截断，但确保保留BASE_PROMPT的基本结构
        lines = content.split('\n')
        truncated_content = ""
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > max_length:
                # 添加说明文本表示内容已被截断
                remaining_chars = max_length - current_length - 50  # 留出空间给提示信息
                if remaining_chars > 0 and len(line) > remaining_chars:
                    truncated_content += line[:remaining_chars] + "\n...\n[内容因长度限制已被截断]"
                else:
                    truncated_content += "\n...\n[内容因长度限制已被截断]"
                break
            truncated_content += line + "\n"
            current_length += len(line) + 1
            
        return truncated_content

    def list_models(self):
        return self.client.models.list()

    def _is_request_too_large_error(self, error: Exception) -> bool:
        msg = str(error)
        return "413" in msg or "Request Entity Too Large" in msg

    def _is_image_input_unsupported_error(self, error: Exception) -> bool:
        msg = str(error).lower()
        return (
            "support image input" in msg
            or "image input" in msg
            or "multimodal" in msg
            or "vision" in msg
        )

    def _split_segments_by_length(
        self,
        source: GPTSource,
        segments: List[TranscriptSegment],
        max_length: int,
    ) -> List[List[TranscriptSegment]]:
        chunks: List[List[TranscriptSegment]] = []
        current: List[TranscriptSegment] = []
        base_args = {
            "title": source.title,
            "tags": source.tags,
            "_format": source._format,
            "style": source.style,
            "extras": source.extras,
        }
        for seg in segments:
            test_segments = current + [seg]
            test_text = generate_base_prompt(
                title=base_args["title"],
                segment_text=self._build_segment_text(test_segments),
                tags=base_args["tags"],
                _format=base_args["_format"],
                style=base_args["style"],
                extras=base_args["extras"],
            )
            if len(test_text) <= max_length:
                current = test_segments
            else:
                if current:
                    chunks.append(current)
                    current = [seg]
                else:
                    chunks.append([seg])
                    current = []
        if current:
            chunks.append(current)
        return chunks

    def _request_summary(self, messages) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def _summarize_with_chunk_limit(
        self,
        source: GPTSource,
        segments: List[TranscriptSegment],
        chunk_limit: int,
        include_images: bool,
    ) -> str:
        chunks = self._split_segments_by_length(source, segments, chunk_limit)
        if not chunks:
            return ""

        partial_summaries: List[str] = []
        for i, chunk in enumerate(chunks):
            use_images = include_images and len(chunks) == 1 and i == 0
            chunk_image_urls = source.video_img_urls if use_images else []
            try:
                chunk_messages = self.create_messages(
                    chunk,
                    title=source.title,
                    tags=source.tags,
                    video_img_urls=chunk_image_urls,
                    _format=source._format,
                    style=source.style,
                    extras=source.extras,
                )
                partial_summaries.append(self._request_summary(chunk_messages))
            except Exception as chunk_error:
                if use_images and self._is_image_input_unsupported_error(chunk_error):
                    logger.warning(
                        "模型 %s 不支持图像输入，分块总结自动降级为纯文本模式",
                        self.model,
                    )
                    fallback_messages = self.create_messages(
                        chunk,
                        title=source.title,
                        tags=source.tags,
                        video_img_urls=[],
                        _format=source._format,
                        style=source.style,
                        extras=source.extras,
                    )
                    partial_summaries.append(self._request_summary(fallback_messages))
                else:
                    raise chunk_error

        if len(partial_summaries) == 1:
            return partial_summaries[0]

        combined_segments = [
            TranscriptSegment(start=0, end=0, text=summary) for summary in partial_summaries
        ]
        return self._summarize_with_chunk_limit(
            source=source,
            segments=combined_segments,
            chunk_limit=chunk_limit,
            include_images=False,
        )

    def summarize(self, source: GPTSource) -> str:
        self.screenshot = source.screenshot
        self.link = source.link
        source.segment = self.ensure_segments_type(source.segment)
        try:
            messages = self.create_messages(
                source.segment,
                title=source.title,
                tags=source.tags,
                video_img_urls=source.video_img_urls,
                _format=source._format,
                style=source.style,
                extras=source.extras,
            )
            return self._request_summary(messages)
        except Exception as e:
            error_message = str(e)
            if "Range of input length should be [1" in error_message:
                raise Exception("视频内容过长，超出模型处理限制。请尝试缩短内容或降低采样密度。")
            if self._is_request_too_large_error(e):
                logger.warning(
                    "检测到 413 请求体过大，开始自动分块降载重试 (initial_chunk_limit=%s)",
                    self.max_input_length,
                )
                chunk_limit = self.max_input_length
                while chunk_limit >= self.min_chunk_length:
                    try:
                        return self._summarize_with_chunk_limit(
                            source=source,
                            segments=source.segment,
                            chunk_limit=chunk_limit,
                            include_images=True,
                        )
                    except Exception as retry_error:
                        if not self._is_request_too_large_error(retry_error):
                            raise retry_error
                        chunk_limit = chunk_limit // 2
                        logger.warning(
                            "分块重试仍触发 413，继续降低 chunk_limit=%s", chunk_limit
                        )
                raise Exception(
                    "请求体过大，自动分块后仍超限。请减少视频时长、关闭部分格式项或切换支持更大请求体的中转。"
                )
            if source.video_img_urls and self._is_image_input_unsupported_error(e):
                logger.warning(
                    "模型 %s 不支持图像输入，自动降级为纯文本总结模式", self.model
                )
                fallback_messages = self.create_messages(
                    source.segment,
                    title=source.title,
                    tags=source.tags,
                    video_img_urls=[],
                    _format=source._format,
                    style=source.style,
                    extras=source.extras,
                )
                return self._request_summary(fallback_messages)
            raise e
