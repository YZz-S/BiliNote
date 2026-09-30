import os

import requests

from app.decorators.timeit import timeit
from app.models.transcriber_model import TranscriptResult, TranscriptSegment
from app.transcriber.base import Transcriber
from app.utils.logger import get_logger

from events import transcription_finished

'''
whisper.cpp server 转写器（AMD GPU 可用：HIP/ROCm 或 Vulkan 后端）

server 端独立于本后端运行，例如在 WSL 中：
  ./build/bin/whisper-server -m ggml-base.bin --port 17899 --convert

环境变量：
  - WHISPER_CPP_URL:    server 地址，默认 http://127.0.0.1:17899
  - WHISPER_LANGUAGE:   语音语言（如 zh / en），不设置则自动检测
'''
logger = get_logger(__name__)


class WhisperCppTranscriber(Transcriber):
    def __init__(self, model_size: str = "base", device: str = None, **kwargs):
        # 模型由 server 启动时通过 -m 指定，这里仅记录，便于日志排查
        self.model_size = model_size
        self.server_url = os.environ.get('WHISPER_CPP_URL', 'http://127.0.0.1:17899').rstrip('/')
        self.language = os.environ.get('WHISPER_LANGUAGE') or None

        try:
            probe = requests.get(self.server_url, timeout=2)
            logger.info(f"whisper.cpp server 已连接: {self.server_url} (HTTP {probe.status_code}), 模型档位: {model_size}")
        except Exception as e:
            logger.warning(f"whisper.cpp server 暂不可达: {self.server_url} ({e})，将在转写时重试")

    @timeit
    def transcript(self, file_path: str) -> TranscriptResult:
        try:
            logger.info(f"开始转写文件: {file_path}")
            logger.info(f"使用 whisper.cpp server: {self.server_url}")

            with open(file_path, 'rb') as f:
                data = {
                    'response_format': 'verbose_json',
                    'no_language_probabilities': 'true',
                }
                if self.language:
                    data['language'] = self.language
                resp = requests.post(
                    f'{self.server_url}/inference',
                    files={'file': (os.path.basename(file_path), f)},
                    data=data,
                    timeout=3600,
                )
            resp.raise_for_status()
            result = resp.json()

            segments = [
                TranscriptSegment(
                    start=float(seg.get('start', 0.0)),
                    end=float(seg.get('end', 0.0)),
                    text=(seg.get('text') or '').strip(),
                )
                for seg in result.get('segments', [])
            ]
            full_text = ' '.join(seg.text for seg in segments).strip()
            if not full_text:
                full_text = (result.get('text') or '').strip()

            logger.info("转写完成")
            return TranscriptResult(
                language=result.get('language'),
                full_text=full_text,
                segments=segments,
                raw=result,
            )
        except Exception as e:
            logger.error(f"转写失败：{e}")
            raise e

    def on_finish(self, video_path: str, result: TranscriptResult) -> None:
        print("转写完成")
        transcription_finished.send({
            "file_path": video_path,
        })
