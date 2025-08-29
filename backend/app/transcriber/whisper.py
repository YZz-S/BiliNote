from faster_whisper import WhisperModel

from app.decorators.timeit import timeit
from app.models.transcriber_model import TranscriptSegment, TranscriptResult
from app.transcriber.base import Transcriber
from app.utils.env_checker import is_cuda_available, is_torch_installed, _add_cuda_paths, check_cuda
from app.utils.logger import get_logger
from app.utils.path_helper import get_model_dir

from events import transcription_finished
from pathlib import Path
import os
import platform
from tqdm import tqdm
from modelscope import snapshot_download
import logging


'''
 Size of the model to use (tiny, tiny.en, base, base.en, small, small.en, distil-small.en, medium, medium.en, large-v1, large-v2, large-v3, large, distil-large-v2, distil-large-v3, large-v3-turbo, or turbo
'''
logger=get_logger(__name__)

MODEL_MAP={
    "tiny": "pengzhendong/faster-whisper-tiny",
    'base':'pengzhendong/faster-whisper-base',
    'small':'pengzhendong/faster-whisper-small',
    'medium':'pengzhendong/faster-whisper-medium',
    'large-v1':'pengzhendong/faster-whisper-large-v1',
    'large-v2':'pengzhendong/faster-whisper-large-v2',
    'large-v3':'pengzhendong/faster-whisper-large-v3',
    'large-v3-turbo':'pengzhendong/faster-whisper-large-v3-turbo',
}

class WhisperTranscriber(Transcriber):
    # TODO:修改为可配置
    def __init__(
            self,
            model_size: str = "base",
            device: str = None,
            compute_type: str = None,
            cpu_threads: int = 1,
    ):
        # 添加CUDA路径检查
        _add_cuda_paths()
        
        # 如果没有指定设备，则从环境变量获取或自动检测
        if device is None:
            device = os.environ.get('DEVICE', 'cuda')
            
        if device == 'cpu':
            self.device = 'cpu'
        else:
            self.device = "cuda" if self.is_cuda() else "cpu"
            if device == 'cuda' and self.device == 'cpu':
                logger.warning('CUDA不可用，使用CPU进行计算')
                # 当CUDA不可用时，强制使用CPU
                self.device = 'cpu'

        self.compute_type = compute_type or ("float16" if self.device == "cuda" else "int8")

        model_dir = get_model_dir("whisper")
        model_path = os.path.join(model_dir, f"whisper-{model_size}")
        if not Path(model_path).exists():
            logger.info(f"模型 whisper-{model_size} 不存在，开始下载...")
            repo_id = MODEL_MAP[model_size]
            try:
                model_path = snapshot_download(
                    repo_id,
                    local_dir=model_path,
                )
                logger.info("模型下载完成")
            except Exception as e:
                logger.error(f"使用modelscope下载模型失败: {e}")
                # 如果modelscope下载失败，尝试使用huggingface_hub下载
                try:
                    from huggingface_hub import snapshot_download as hf_snapshot_download
                    logger.info("尝试使用huggingface_hub下载模型...")
                    model_path = hf_snapshot_download(
                        f"Systran/faster-whisper-{model_size}",
                        local_dir=model_path,
                        local_files_only=False
                    )
                    logger.info("模型下载完成")
                except Exception as hf_e:
                    logger.error(f"使用huggingface_hub下载模型也失败了: {hf_e}")
                    raise Exception(f"无法下载模型: {e} 和 {hf_e}")

        logger.info(f"正在加载Whisper模型，使用设备: {self.device}")
        try:
            self.model = WhisperModel(
                model_size_or_path=model_path,
                device=self.device,
                compute_type=self.compute_type,
                download_root=model_dir
            )
        except (RuntimeError, OSError) as e:
            error_msg = str(e).lower()
            if ("cublas64_12.dll" in error_msg or "cublas" in error_msg) and platform.system() == "Windows":
                logger.warning("检测到CUDA库版本不兼容，尝试切换到CPU模式")
                self.device = "cpu"
                self.compute_type = "int8"
                logger.info("正在以CPU模式加载Whisper模型")
                self.model = WhisperModel(
                    model_size_or_path=model_path,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=model_dir
                )
            else:
                logger.error(f"加载模型时发生错误: {e}")
                raise e
        except Exception as e:
            logger.error(f"加载模型时发生未知错误: {e}")
            raise e

    @staticmethod
    def is_torch_installed() -> bool:
        try:
            import torch
            return True
        except ImportError:
            return False
        except Exception as e:
            print(f"检查torch安装状态时出错: {e}")
            return False

    @staticmethod
    def is_cuda() -> bool:
        # 首先检查CUDA环境
        if not check_cuda():
            print(" CUDA 环境检查失败，使用 CPU")
            return False
            
        try:
            if is_cuda_available():
                print(" CUDA 可用，使用 GPU")
                return True
            elif is_torch_installed():
                print(" 只装了 torch，但没有 CUDA，用 CPU")
                return False
            else:
                print(" 还没有安装 torch，请先安装")
                return False

        except ImportError as e:
            print(f"导入错误: {e}")
            return False
        except Exception as e:
            print(f"检查CUDA时发生未知错误: {e}")
            return False

    @timeit
    def transcript(self, file_path: str) -> TranscriptResult:
        try:
            logger.info(f"开始转写文件: {file_path}")
            logger.info(f"使用的设备: {self.device}")
            logger.info(f"CUDA可用性: {is_cuda_available()}")
            
            segments_raw, info = self.model.transcribe(file_path)

            segments = []
            full_text = ""

            for seg in segments_raw:
                text = seg.text.strip()
                full_text += text + " "
                segments.append(TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=text
                ))

            result= TranscriptResult(
                language=info.language,
                full_text=full_text.strip(),
                segments=segments,
                raw=info
            )
            # self.on_finish(file_path, result)
            logger.info("转写完成")
            return result
        except Exception as e:
            logger.error(f"转写失败：{e}")
            logger.error(f"设备信息: {self.device}")
            logger.error(f"CUDA可用性: {is_cuda_available()}")
            raise e  # 重新抛出异常，以便上层可以正确处理


    def on_finish(self,video_path:str,result: TranscriptResult)->None:
        print("转写完成")
        transcription_finished.send({
            "file_path": video_path,
        })