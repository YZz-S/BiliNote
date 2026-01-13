from app.gpt.base import GPT
from app.gpt.prompt_builder import generate_base_prompt
from app.models.gpt_model import GPTSource
from app.gpt.prompt import BASE_PROMPT, AI_SUM, SCREENSHOT, LINK
from app.gpt.utils import fix_markdown
from app.models.transcriber_model import TranscriptSegment
from datetime import timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)

# 定义最大输入长度
MAX_INPUT_LENGTH = 120000  # 留一些余量，避免精确边界问题

class UniversalGPT(GPT):
    def __init__(self, client, model: str, temperature: float = 0.7):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.screenshot = False
        self.link = False

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
        if len(content_text) > MAX_INPUT_LENGTH:
            logger.warning(f"输入文本长度 {len(content_text)} 超过限制 {MAX_INPUT_LENGTH}，将进行截断处理")
            # 保留提示词部分和前部分转录内容
            content_text = self._truncate_content(content_text, MAX_INPUT_LENGTH)
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

    def summarize(self, source: GPTSource) -> str:
        self.screenshot = source.screenshot
        self.link = source.link
        source.segment = self.ensure_segments_type(source.segment)

        full_text = generate_base_prompt(
            title=source.title,
            segment_text=self._build_segment_text(source.segment),
            tags=source.tags,
            _format=source._format,
            style=source.style,
            extras=source.extras,
        )
        if len(full_text) > MAX_INPUT_LENGTH:
            chunks = []
            current = []
            base_args = {
                "title": source.title,
                "tags": source.tags,
                "_format": source._format,
                "style": source.style,
                "extras": source.extras,
            }
            for seg in source.segment:
                test_segments = current + [seg]
                test_text = generate_base_prompt(
                    title=base_args["title"],
                    segment_text=self._build_segment_text(test_segments),
                    tags=base_args["tags"],
                    _format=base_args["_format"],
                    style=base_args["style"],
                    extras=base_args["extras"],
                )
                if len(test_text) <= MAX_INPUT_LENGTH:
                    current = test_segments
                else:
                    if current:
                        chunks.append(current)
                    current = [seg]
            if current:
                chunks.append(current)
            summaries = []
            for segs in chunks:
                msgs = self.create_messages(
                    segs,
                    title=source.title,
                    tags=source.tags,
                    video_img_urls=source.video_img_urls,
                    _format=source._format,
                    style=source.style,
                    extras=source.extras,
                )
                resp = self.client.chat.completions.create(
                    model=self.model, messages=msgs, temperature=0.7
                )
                summaries.append(resp.choices[0].message.content.strip())
            combined_segments = [
                TranscriptSegment(start=0, text=s) for s in summaries
            ]
            messages = self.create_messages(
                combined_segments,
                title=source.title,
                tags=source.tags,
                video_img_urls=[],
                _format=source._format,
                style=source.style,
                extras=source.extras,
            )
        else:
            messages = self.create_messages(
                source.segment,
                title=source.title,
                tags=source.tags,
                video_img_urls=source.video_img_urls,
                _format=source._format,
                style=source.style,
                extras=source.extras
            )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_message = str(e)
            if "Range of input length should be [1" in error_message:
                raise Exception("视频内容过长，超出模型处理限制。请尝试缩短内容或降低采样密度。")
            else:
                raise e
