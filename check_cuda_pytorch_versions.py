import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    print("Python版本:")
    print(f"  {sys.version}")
    print(f"  版本号: {platform.python_version()}")
    print()

def check_cuda_version():
    """检查CUDA版本"""
    print("CUDA版本:")
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if "release" in line.lower():
                    print(f"  {line.strip()}")
                    break
        else:
            print("  CUDA Toolkit未安装或nvcc命令不可用")
            print(f"  错误信息: {result.stderr}")
    except FileNotFoundError:
        print("  未找到CUDA Toolkit (nvcc命令不可用)")
    except subprocess.TimeoutExpired:
        print("  检查CUDA版本超时")
    except Exception as e:
        print(f"  检查CUDA版本时出错: {e}")
    print()

def check_pytorch_and_cudnn():
    """检查PyTorch和cuDNN版本"""
    print("PyTorch和cuDNN版本:")
    try:
        import torch
        print(f"  PyTorch版本: {torch.__version__}")
        print(f"  CUDA可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"  GPU型号: {torch.cuda.get_device_name(0)}")
            print(f"  显存容量: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f} GB")
            if hasattr(torch.version, 'cuda'):
                print(f"  PyTorch编译使用的CUDA版本: {torch.version.cuda}")
            else:
                print("  无法确定PyTorch编译使用的CUDA版本")
                
            if torch.backends.cudnn.is_available():
                print(f"  cuDNN版本: {torch.backends.cudnn.version()}")
            else:
                print("  cuDNN不可用")
        else:
            print("  CUDA不可用，仅使用CPU")
            
    except ImportError:
        print("  未安装PyTorch")
    except Exception as e:
        print(f"  检查PyTorch/cuDNN时出错: {e}")
    print()

def check_nvidia_driver():
    """检查NVIDIA驱动"""
    print("NVIDIA驱动信息:")
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            # 查找包含驱动版本的行
            for line in lines[:10]:  # 检查前10行
                if "Driver Version" in line:
                    print(f"  {line.strip()}")
                    break
            else:
                print("  找不到驱动版本信息")
        else:
            print("  NVIDIA驱动未安装或nvidia-smi命令不可用")
    except FileNotFoundError:
        print("  未找到NVIDIA驱动 (nvidia-smi命令不可用)")
    except subprocess.TimeoutExpired:
        print("  检查NVIDIA驱动超时")
    except Exception as e:
        print(f"  检查NVIDIA驱动时出错: {e}")
    print()

def main():
    print("=" * 60)
    print("CUDA、Python、PyTorch和cuDNN版本检查工具")
    print("=" * 60)
    print()
    
    check_python_version()
    check_cuda_version()
    check_nvidia_driver()
    check_pytorch_and_cudnn()
    
    print("=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()