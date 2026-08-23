import mlx_whisper
from pathlib import Path
import os
import platform

# huggingface_hub 相关配置必须在 import 前生效
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")  # 国内镜像，可被外部环境变量覆盖

from huggingface_hub import snapshot_download

from app.decorators.timeit import timeit
from app.models.transcriber_model import TranscriptSegment, TranscriptResult
from app.transcriber.base import Transcriber
from app.utils.logger import get_logger
from app.utils.path_helper import get_model_dir
from events import transcription_finished

logger = get_logger(__name__)

# mlx-community 的仓库名后缀不统一，需显式映射
MLX_MODEL_MAP = {
    "tiny": "mlx-community/whisper-tiny-mlx",
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v2": "mlx-community/whisper-large-v2-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
}

class MLXWhisperTranscriber(Transcriber):
    def __init__(
            self,
            model_size: str = "base"
    ):
        # 检查平台
        if platform.system() != "Darwin":
            raise RuntimeError("MLX Whisper 仅支持 Apple 平台")
            
        # 检查环境变量
        if os.environ.get("TRANSCRIBER_TYPE") != "mlx-whisper":
            raise RuntimeError("必须设置环境变量 TRANSCRIBER_TYPE=mlx-whisper 才能使用 MLX Whisper")
            
        self.model_size = model_size
        self.model_name = MLX_MODEL_MAP.get(model_size, f"mlx-community/whisper-{model_size}")
        # 允许直接传完整仓库名覆盖映射
        if "/" in model_size:
            self.model_name = model_size
        self.model_path = None
        
        # 设置模型路径（与 fast-whisper 一致：models/mlx-whisper/<repo名>）
        model_dir = get_model_dir("mlx-whisper")
        self.model_path = os.path.join(model_dir, self.model_name.split("/")[-1])
        # 检查并下载模型
        if not Path(self.model_path).exists() or not any(Path(self.model_path).glob("*.npz")):
            logger.info(f"模型 {self.model_name} 不存在，开始下载...")
            snapshot_download(
                self.model_name,
                local_dir=self.model_path,
            )
            logger.info("模型下载完成")
        
        logger.info(f"初始化 MLX Whisper 转录器，模型：{self.model_name}，路径：{self.model_path}")
        
    @timeit
    def transcript(self, file_path: str) -> TranscriptResult:
        try:
            # 使用 MLX Whisper 进行转录（优先本地路径，避免每次联网校验）
            result = mlx_whisper.transcribe(
                file_path,
                path_or_hf_repo=self.model_path
            )
            
            # 转换为标准格式
            segments = []
            full_text = ""
            
            for segment in result["segments"]:
                text = segment["text"].strip()
                full_text += text + " "
                segments.append(TranscriptSegment(
                    start=segment["start"],
                    end=segment["end"],
                    text=text
                ))
            
            transcript_result = TranscriptResult(
                language=result.get("language", "unknown"),
                full_text=full_text.strip(),
                segments=segments,
                raw=result
            )
            
            # self.on_finish(file_path, transcript_result)
            return transcript_result
            
        except Exception as e:
            logger.error(f"MLX Whisper 转写失败：{e}")
            raise e

    def on_finish(self, video_path: str, result: TranscriptResult) -> None:
        logger.info("MLX Whisper 转写完成")
        transcription_finished.send({
            "file_path": video_path,
        }) 
