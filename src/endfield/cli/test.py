"""
System Information Monitor
Collects real-time system information including CPU, GPU, RAM usage.
"""

import platform
import psutil
from typing import Dict

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("Warning: GPUtil not installed. GPU monitoring will be disabled.")
    print("Install with: pip install gputil")


class SystemMonitor:
    """Monitor system resources and information."""
    
    def __init__(self):
        """Initialize the system monitor."""
        self.static_info = self._get_static_info()
    
    def _get_static_info(self) -> Dict[str, str]:
        """Get static system information that doesn't change."""
        return {
            "host": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
        }
    
    def get_cpu_usage(self) -> str:
        """Get current CPU usage percentage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return f"{cpu_percent:.1f}%"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_gpu_usage(self) -> str:
        """Get current GPU usage percentage."""
        if not GPU_AVAILABLE:
            return "N/A (GPUtil not installed)"
        
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return "No GPU detected"
            
            # Get the first GPU (most systems have one)
            gpu = gpus[0]
            return f"{gpu.load * 100:.1f}% ({gpu.name})"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_ram_usage(self) -> str:
        """Get current RAM usage."""
        try:
            memory = psutil.virtual_memory()
            used_gb = memory.used / (1024 ** 3)  # Convert to GB
            total_gb = memory.total / (1024 ** 3)
            percent = memory.percent
            return f"{used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.1f}%)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_all_info(self) -> Dict[str, str]:
        """Get all system information (static + dynamic)."""
        info = self.static_info.copy()
        info.update({
            "cpu": self.get_cpu_usage(),
            "gpu": self.get_gpu_usage(),
            "ram": self.get_ram_usage(),
        })
        return info


# Test the system monitor
if __name__ == "__main__":
    import time
    
    print("System Information Monitor")
    print("=" * 50)
    
    monitor = SystemMonitor()
    
    # Display static info
    static_info = monitor._get_static_info()
    print(f"\nStatic Information:")
    print(f"  Host: {static_info['host']}")
    print(f"  OS: {static_info['os']}")
    print(f"  Architecture: {static_info['arch']}")
    
    # Monitor dynamic info for 10 seconds
    print(f"\nDynamic Information (updating every 3 seconds):")
    print("-" * 50)
    
    for i in range(5):  # Run 5 times (15 seconds total)
        info = monitor.get_all_info()
        print(f"\nUpdate #{i+1}:")
        print(f"  CPU: {info['cpu']}")
        print(f"  GPU: {info['gpu']}")
        print(f"  RAM: {info['ram']}")
        
        if i < 4:  # Don't sleep after last iteration
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("Monitoring complete!")
