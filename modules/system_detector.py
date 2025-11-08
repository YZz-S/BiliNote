#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统检测模块

功能：
- 检查系统依赖
- 监控系统资源
- 环境验证
- 性能诊断
"""

import os
import sys
import platform
import subprocess
import shutil
import psutil
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DependencyStatus:
    """依赖状态"""
    name: str
    version: str
    is_installed: bool
    install_path: str
    required_version: str = ""
    description: str = ""
    install_command: str = ""

@dataclass
class SystemResources:
    """系统资源信息"""
    cpu_usage: float
    memory_usage: float
    memory_total: float
    memory_available: float
    disk_usage: float
    disk_total: float
    disk_free: float
    network_status: bool
    uptime: float

class SystemDetector:
    """系统检测器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.resource_history = []
        self.max_history = 100
        
        # 依赖定义
        self.dependencies = self._get_dependency_definitions()
        
    def _get_dependency_definitions(self) -> Dict[str, DependencyStatus]:
        """获取依赖定义"""
        return {
            'python': DependencyStatus(
                name='Python',
                version='',
                is_installed=False,
                install_path='',
                required_version='3.6+',
                description='Python解释器',
                install_command='从 https://python.org 下载安装'
            ),
            'node': DependencyStatus(
                name='Node.js',
                version='',
                is_installed=False,
                install_path='',
                required_version='14.0+',
                description='JavaScript运行时',
                install_command='从 https://nodejs.org 下载安装'
            ),
            'pnpm': DependencyStatus(
                name='pnpm',
                version='',
                is_installed=False,
                install_path='',
                required_version='6.0+',
                description='包管理器',
                install_command='npm install -g pnpm'
            ),
            'ffmpeg': DependencyStatus(
                name='FFmpeg',
                version='',
                is_installed=False,
                install_path='',
                required_version='4.0+',
                description='音视频处理工具',
                install_command='从 https://ffmpeg.org 下载安装'
            ),
            'conda': DependencyStatus(
                name='Conda',
                version='',
                is_installed=False,
                install_path='',
                required_version='',
                description='Python环境管理器（可选）',
                install_command='从 https://anaconda.com 下载安装'
            )
        }
        
    def check_dependencies(self) -> List[DependencyStatus]:
        """检查所有依赖"""
        results = []
        
        for dep_name, dep_info in self.dependencies.items():
            status = self._check_single_dependency(dep_name)
            results.append(status)
            
        return results
        
    def _check_single_dependency(self, name: str) -> DependencyStatus:
        """检查单个依赖"""
        dep = self.dependencies[name].copy() if name in self.dependencies else DependencyStatus(
            name=name, version='', is_installed=False, install_path=''
        )
        
        try:
            if name == 'python':
                dep.version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                dep.install_path = sys.executable
                dep.is_installed = True
                
            elif name == 'node':
                result = subprocess.run(['node', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    dep.version = result.stdout.strip().lstrip('v')
                    dep.install_path = shutil.which('node') or ''
                    dep.is_installed = True
                    
            elif name == 'pnpm':
                result = subprocess.run(['pnpm', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    dep.version = result.stdout.strip()
                    dep.install_path = shutil.which('pnpm') or ''
                    dep.is_installed = True
                    
            elif name == 'ffmpeg':
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # 解析FFmpeg版本
                    lines = result.stdout.split('\n')
                    if lines:
                        version_line = lines[0]
                        if 'version' in version_line:
                            parts = version_line.split()
                            for i, part in enumerate(parts):
                                if part == 'version' and i + 1 < len(parts):
                                    dep.version = parts[i + 1]
                                    break
                    dep.install_path = shutil.which('ffmpeg') or ''
                    dep.is_installed = True
                    
            elif name == 'conda':
                result = subprocess.run(['conda', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    dep.version = result.stdout.strip().replace('conda ', '')
                    dep.install_path = shutil.which('conda') or ''
                    dep.is_installed = True
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            dep.is_installed = False
            
        return dep
        
    def check_port_availability(self, port: int) -> Dict[str, any]:
        """检查端口可用性"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    try:
                        process = psutil.Process(conn.pid) if conn.pid else None
                        return {
                            'available': False,
                            'occupied_by': {
                                'pid': conn.pid,
                                'name': process.name() if process else 'Unknown',
                                'status': conn.status
                            }
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {
                            'available': False,
                            'occupied_by': {
                                'pid': conn.pid,
                                'name': 'Unknown',
                                'status': conn.status
                            }
                        }
            return {'available': True}
        except Exception as e:
            return {'available': False, 'error': str(e)}
            
    def get_system_resources(self) -> SystemResources:
        """获取系统资源信息"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息（项目根目录所在磁盘）
            disk = psutil.disk_usage(str(self.project_root))
            
            # 网络状态（简单检查）
            network_status = self._check_network_connectivity()
            
            # 系统运行时间
            uptime = time.time() - psutil.boot_time()
            
            return SystemResources(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                memory_total=memory.total / (1024**3),  # GB
                memory_available=memory.available / (1024**3),  # GB
                disk_usage=(disk.used / disk.total) * 100,
                disk_total=disk.total / (1024**3),  # GB
                disk_free=disk.free / (1024**3),  # GB
                network_status=network_status,
                uptime=uptime
            )
            
        except Exception as e:
            print(f"获取系统资源信息失败: {e}")
            return SystemResources(
                cpu_usage=0, memory_usage=0, memory_total=0, memory_available=0,
                disk_usage=0, disk_total=0, disk_free=0, network_status=False, uptime=0
            )
            
    def _check_network_connectivity(self) -> bool:
        """检查网络连接"""
        try:
            # 检查网络接口
            stats = psutil.net_if_stats()
            for interface, stat in stats.items():
                if stat.isup and interface != 'lo':  # 排除回环接口
                    return True
            return False
        except Exception:
            return False
            
    def check_project_structure(self) -> Dict[str, bool]:
        """检查项目结构"""
        required_paths = {
            'backend目录': self.project_root / 'backend',
            'frontend目录': self.project_root / 'BillNote_frontend',
            'backend/main.py': self.project_root / 'backend' / 'main.py',
            'frontend/package.json': self.project_root / 'BillNote_frontend' / 'package.json',
            '.env文件': self.project_root / '.env',
            'requirements.txt': self.project_root / 'backend' / 'requirements.txt'
        }
        
        results = {}
        for name, path in required_paths.items():
            results[name] = path.exists()
            
        return results
        
    def check_python_packages(self) -> List[Dict[str, str]]:
        """检查Python包依赖"""
        requirements_file = self.project_root / 'backend' / 'requirements.txt'
        if not requirements_file.exists():
            return []
            
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.readlines()
                
            package_status = []
            
            for line in requirements:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 解析包名和版本
                package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0]
                
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'show', package_name],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if result.returncode == 0:
                        # 解析版本信息
                        version = ''
                        for output_line in result.stdout.split('\n'):
                            if output_line.startswith('Version:'):
                                version = output_line.split(':', 1)[1].strip()
                                break
                                
                        package_status.append({
                            'name': package_name,
                            'required': line,
                            'installed_version': version,
                            'status': 'installed'
                        })
                    else:
                        package_status.append({
                            'name': package_name,
                            'required': line,
                            'installed_version': '',
                            'status': 'missing'
                        })
                        
                except subprocess.TimeoutExpired:
                    package_status.append({
                        'name': package_name,
                        'required': line,
                        'installed_version': '',
                        'status': 'timeout'
                    })
                    
            return package_status
            
        except Exception as e:
            print(f"检查Python包失败: {e}")
            return []
            
    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        try:
            return {
                '操作系统': platform.system(),
                '系统版本': platform.release(),
                '架构': platform.machine(),
                'Python版本': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'Python路径': sys.executable,
                '工作目录': str(self.project_root),
                '用户名': os.getenv('USERNAME', os.getenv('USER', 'Unknown')),
                '主机名': platform.node(),
                'CPU核心数': str(psutil.cpu_count()),
                '物理内存': f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
            }
        except Exception as e:
            print(f"获取系统信息失败: {e}")
            return {}
            
    def start_resource_monitoring(self, interval: int = 5):
        """开始资源监控"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_resources,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
    def stop_resource_monitoring(self):
        """停止资源监控"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)
            
    def _monitor_resources(self, interval: int):
        """监控资源（后台线程）"""
        while self.monitoring_active:
            try:
                resources = self.get_system_resources()
                
                # 添加时间戳
                resource_data = {
                    'timestamp': datetime.now(),
                    'cpu_usage': resources.cpu_usage,
                    'memory_usage': resources.memory_usage,
                    'disk_usage': resources.disk_usage
                }
                
                self.resource_history.append(resource_data)
                
                # 保持历史记录在限制范围内
                if len(self.resource_history) > self.max_history:
                    self.resource_history.pop(0)
                    
                time.sleep(interval)
                
            except Exception as e:
                print(f"资源监控错误: {e}")
                time.sleep(interval)
                
    def get_resource_history(self) -> List[Dict]:
        """获取资源历史记录"""
        return self.resource_history.copy()
        
    def diagnose_system(self) -> Dict[str, List[str]]:
        """系统诊断"""
        issues = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 检查依赖
        dependencies = self.check_dependencies()
        for dep in dependencies:
            if not dep.is_installed:
                if dep.name in ['Python', 'Node.js', 'pnpm']:
                    issues['errors'].append(f"缺少必需依赖: {dep.name}")
                else:
                    issues['warnings'].append(f"缺少可选依赖: {dep.name}")
                    
        # 检查项目结构
        structure = self.check_project_structure()
        for name, exists in structure.items():
            if not exists:
                if 'main.py' in name or 'package.json' in name:
                    issues['errors'].append(f"缺少关键文件: {name}")
                else:
                    issues['warnings'].append(f"缺少文件/目录: {name}")
                    
        # 检查系统资源
        resources = self.get_system_resources()
        if resources.memory_usage > 90:
            issues['warnings'].append(f"内存使用率过高: {resources.memory_usage:.1f}%")
        if resources.disk_usage > 90:
            issues['warnings'].append(f"磁盘使用率过高: {resources.disk_usage:.1f}%")
        if resources.cpu_usage > 90:
            issues['warnings'].append(f"CPU使用率过高: {resources.cpu_usage:.1f}%")
            
        # 提供建议
        if not resources.network_status:
            issues['suggestions'].append("检查网络连接")
        if resources.memory_total < 4:
            issues['suggestions'].append("建议增加内存以提升性能")
        if resources.disk_free < 1:
            issues['suggestions'].append("磁盘空间不足，建议清理")
            
        return issues
        
    def cleanup(self):
        """清理资源"""
        self.stop_resource_monitoring()
        self.resource_history.clear()