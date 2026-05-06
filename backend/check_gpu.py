"""
Script to check GPU availability and install PyTorch with CUDA support.
"""
import sys
import subprocess

def check_gpu():
    """Check if NVIDIA GPU is available."""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA is available!")
            print(f"   PyTorch version: {torch.__version__}")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                try:
                    print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
                except Exception:
                    print(f"   GPU {i}: (name not available)")
            return True
        else:
            print("❌ CUDA is not available")
            print("   Installing PyTorch with CUDA support...")
            install_cuda_torch()
            return False
    except ImportError:
        print("❌ PyTorch not installed")
        install_cuda_torch()
        return False

def install_cuda_torch():
    """Install PyTorch with CUDA support."""
    print("Installing PyTorch with CUDA support...")
    try:
        # Try to install PyTorch with CUDA 12.1
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu121"
        ])
        print("✅ PyTorch with CUDA installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PyTorch with CUDA: {e}")
        print("   Trying CPU version...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio"
        ])
        print("✅ PyTorch CPU version installed")

if __name__ == "__main__":
    check_gpu()
