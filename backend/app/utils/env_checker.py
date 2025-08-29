import os
import sys
import logging
from typing import List
import platform

logger = logging.getLogger(__name__)

def is_torch_installed():
    """检查PyTorch是否安装"""
    try:
        import torch
        return True
    except ImportError:
        return False

def is_cuda_available():
    """检查CUDA是否可用"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def _add_cuda_paths():
    """添加CUDA库路径到系统PATH"""
    if platform.system() != "Windows":
        return
        
    # 检查常见的CUDA路径
    cuda_paths = [
        "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.0\\bin",
        "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.8\\bin",
    ]
    
    # 添加conda环境中的CUDA路径
    conda_cuda_paths = [
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', 'cublas', 'bin'),
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', 'cudnn', 'bin'),
    ]
    
    # 添加用户目录中的CUDA路径
    user_cuda_paths = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python310', 'site-packages', 'nvidia', 'cudnn', 'bin'),
    ]
    
    # 检查并添加路径
    current_path = os.environ.get('PATH', '')
    paths_to_add = []
    
    for path in cuda_paths + conda_cuda_paths + user_cuda_paths:
        if os.path.exists(path) and path not in current_path:
            paths_to_add.append(path)
            
    if paths_to_add:
        os.environ['PATH'] = current_path + os.pathsep + os.pathsep.join(paths_to_add)
        logger.info(f"已添加CUDA路径到环境变量: {paths_to_add}")

def check_cuda():
    try:
        # 尝试添加CUDA路径
        _add_cuda_paths()
        
        import torch
        if not torch.cuda.is_available():
            logger.warning("CUDA在当前环境中不可用")
            return False
        
        cuda_version = torch.version.cuda
        cudnn_version = torch.backends.cudnn.version()
        
        logger.info(f"CUDA版本: {cuda_version}")
        logger.info(f"cuDNN版本: {cudnn_version}")
        
        if cuda_version is None:
            logger.warning("无法检测到CUDA版本")
            return False
            
        # 检查CUDA版本是否兼容
        if not cuda_version.startswith("11.") and not cuda_version.startswith("12."):
            logger.warning(f"检测到CUDA版本 {cuda_version}，推荐使用CUDA 11.x 或 12.x")
        
        # 检查cuDNN是否可用
        if cudnn_version is None:
            logger.warning("cuDNN不可用，可能影响性能")
            return False
            
        # 检查CUDA库路径是否在系统PATH中
        paths = os.environ.get('PATH', '').split(os.pathsep)
        
        # 检查cublas库
        cublas_lib_found = any(os.path.exists(os.path.join(path, 'cublas64_12.dll')) for path in paths)
        if not cublas_lib_found:
            logger.warning("cublas64_12.dll未在PATH中找到")
            
        # 检查cudnn库
        cudnn_ops_lib_found = any(os.path.exists(os.path.join(path, 'cudnn_ops64_9.dll')) for path in paths)
        if not cudnn_ops_lib_found:
            logger.warning("cudnn_ops64_9.dll未在PATH中找到")
            
        if not cublas_lib_found or not cudnn_ops_lib_found:
            # 尝试添加默认的CUDA路径
            default_cuda_paths = [
                os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', 'cublas', 'bin'),
                os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', 'cudnn', 'bin'),
                os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python310', 'site-packages', 'nvidia', 'cudnn', 'bin'),
            ]
            
            for default_cuda_path in default_cuda_paths:
                if os.path.exists(default_cuda_path):
                    logger.info(f"添加CUDA路径到环境变量: {default_cuda_path}")
                    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + default_cuda_path
                    
                    # 检查库文件是否现在可以找到
                    if not cublas_lib_found:
                        cublas_lib_found = os.path.exists(os.path.join(default_cuda_path, 'cublas64_12.dll'))
                    if not cudnn_ops_lib_found:
                        cudnn_ops_lib_found = os.path.exists(os.path.join(default_cuda_path, 'cudnn_ops64_9.dll'))
                        
                    if cublas_lib_found and cudnn_ops_lib_found:
                        break
                        
            if not cublas_lib_found:
                logger.warning("cublas64_12.dll仍未找到")
            if not cudnn_ops_lib_found:
                logger.warning("cudnn_ops64_9.dll仍未找到")
            
        if not cublas_lib_found or not cudnn_ops_lib_found:
            logger.warning("CUDA库文件未在PATH中找到，请确保CUDA库在系统路径中")
            return False
            
        logger.info("CUDA和cuDNN环境检查通过")
        return True
    except ImportError:
        logger.warning("PyTorch未安装，CUDA功能不可用")
        return False
    except Exception as e:
        logger.error(f"CUDA环境检查时发生错误: {e}")
        return False

def check_ffmpeg():
    """检查FFmpeg是否安装并可用"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("FFmpeg检查通过")
            return True
        else:
            logger.warning("FFmpeg不可用")
            return False
    except Exception as e:
        logger.warning(f"FFmpeg检查失败: {e}")
        return False

def check_environment() -> List[str]:
    """检查所有环境依赖并返回问题列表"""
    issues = []
    
    if not check_cuda():
        issues.append("CUDA环境配置存在问题")
    
    if not check_ffmpeg():
        issues.append("FFmpeg未安装或不可用")
        
    if issues:
        logger.warning("环境检查发现问题: " + ", ".join(issues))
    else:
        logger.info("所有环境依赖检查通过")
        
    return issues