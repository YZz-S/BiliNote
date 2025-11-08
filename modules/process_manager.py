#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程管理模块

功能：
- 启动和停止前端/后端进程
- 监控进程状态
- 管理进程生命周期
- 支持conda环境激活
"""

import subprocess
import psutil
import os
import signal
import threading
import time
from dataclasses import dataclass
from typing import Optional, Dict, List, Callable
from pathlib import Path

@dataclass
class ProcessStatus:
    """进程状态数据类"""
    pid: Optional[int] = None
    name: str = ""
    status: str = "stopped"  # 'running', 'stopped', 'error', 'starting'
    start_time: Optional[float] = None
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    port: Optional[int] = None
    command: str = ""
    error_message: str = ""

@dataclass
class ProcessResult:
    """进程操作结果"""
    success: bool
    pid: Optional[int] = None
    message: str = ""
    error: str = ""

class ProcessManager:
    """进程管理器"""
    
    def __init__(self):
        self.processes: Dict[str, ProcessStatus] = {
            'frontend': ProcessStatus(name='frontend'),
            'backend': ProcessStatus(name='backend')
        }
        self.process_objects: Dict[str, Optional[subprocess.Popen]] = {
            'frontend': None,
            'backend': None
        }
        self.monitoring_thread = None
        self.monitoring_active = False
        self.status_callbacks: List[Callable] = []
        
        # 项目路径
        self.project_root = Path.cwd()
        self.frontend_dir = self.project_root / "BillNote_frontend"
        self.backend_dir = self.project_root / "backend"
        
        # 启动监控线程
        self.start_monitoring()
        
    def add_status_callback(self, callback: Callable):
        """添加状态变化回调函数"""
        self.status_callbacks.append(callback)
        
    def _notify_status_change(self, service: str):
        """通知状态变化"""
        for callback in self.status_callbacks:
            try:
                callback(service, self.processes[service])
            except Exception as e:
                print(f"状态回调执行失败: {e}")
                
    def start_frontend(self) -> ProcessResult:
        """启动前端服务"""
        try:
            if self.is_process_running('frontend'):
                return ProcessResult(
                    success=False,
                    message="前端服务已在运行中"
                )
                
            # 检查前端目录是否存在
            if not self.frontend_dir.exists():
                return ProcessResult(
                    success=False,
                    error=f"前端目录不存在: {self.frontend_dir}"
                )
                
            # 检查package.json是否存在
            package_json = self.frontend_dir / "package.json"
            if not package_json.exists():
                return ProcessResult(
                    success=False,
                    error=f"package.json不存在: {package_json}"
                )
                
            # 更新状态为启动中
            self.processes['frontend'].status = 'starting'
            self.processes['frontend'].error_message = ""
            self._notify_status_change('frontend')
            
            # 构建启动命令
            if os.name == 'nt':  # Windows
                cmd = ['cmd', '/c', 'pnpm', 'dev']
            else:  # Unix/Linux
                cmd = ['pnpm', 'dev']
                
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.process_objects['frontend'] = process
            
            # 更新进程状态
            self.processes['frontend'].pid = process.pid
            self.processes['frontend'].status = 'running'
            self.processes['frontend'].start_time = time.time()
            self.processes['frontend'].command = ' '.join(cmd)
            self.processes['frontend'].port = 5173  # Vite默认端口
            
            self._notify_status_change('frontend')
            
            return ProcessResult(
                success=True,
                pid=process.pid,
                message="前端服务启动成功"
            )
            
        except Exception as e:
            self.processes['frontend'].status = 'error'
            self.processes['frontend'].error_message = str(e)
            self._notify_status_change('frontend')
            
            return ProcessResult(
                success=False,
                error=f"启动前端服务失败: {e}"
            )
            
    def start_backend(self, conda_env: Optional[str] = None) -> ProcessResult:
        """启动后端服务"""
        try:
            if self.is_process_running('backend'):
                return ProcessResult(
                    success=False,
                    message="后端服务已在运行中"
                )
                
            # 检查后端目录是否存在
            if not self.backend_dir.exists():
                return ProcessResult(
                    success=False,
                    error=f"后端目录不存在: {self.backend_dir}"
                )
                
            # 检查main.py是否存在
            main_py = self.backend_dir / "main.py"
            if not main_py.exists():
                return ProcessResult(
                    success=False,
                    error=f"main.py不存在: {main_py}"
                )
                
            # 更新状态为启动中
            self.processes['backend'].status = 'starting'
            self.processes['backend'].error_message = ""
            self._notify_status_change('backend')
            
            # 构建启动命令
            if conda_env and conda_env.strip():
                # 使用conda环境
                if os.name == 'nt':  # Windows
                    cmd = ['cmd', '/c', f'conda activate {conda_env} && python main.py']
                else:  # Unix/Linux
                    cmd = ['bash', '-c', f'source activate {conda_env} && python main.py']
            else:
                # 直接使用python
                cmd = ['python', 'main.py']
                
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=str(self.backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.process_objects['backend'] = process
            
            # 更新进程状态
            self.processes['backend'].pid = process.pid
            self.processes['backend'].status = 'running'
            self.processes['backend'].start_time = time.time()
            self.processes['backend'].command = ' '.join(cmd) if isinstance(cmd, list) else cmd
            self.processes['backend'].port = 8483  # 默认后端端口
            
            self._notify_status_change('backend')
            
            return ProcessResult(
                success=True,
                pid=process.pid,
                message="后端服务启动成功"
            )
            
        except Exception as e:
            self.processes['backend'].status = 'error'
            self.processes['backend'].error_message = str(e)
            self._notify_status_change('backend')
            
            return ProcessResult(
                success=False,
                error=f"启动后端服务失败: {e}"
            )
            
    def stop_process(self, service: str) -> bool:
        """停止指定服务"""
        try:
            if service not in self.process_objects:
                return False
                
            process = self.process_objects[service]
            if process is None:
                return True
                
            # 尝试优雅关闭
            if process.poll() is None:  # 进程仍在运行
                if os.name == 'nt':  # Windows
                    # 发送CTRL_BREAK_EVENT信号
                    try:
                        process.send_signal(signal.CTRL_BREAK_EVENT)
                        # 等待进程结束
                        process.wait(timeout=5)
                    except (subprocess.TimeoutExpired, OSError):
                        # 强制终止
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                else:  # Unix/Linux
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        
            self.process_objects[service] = None
            
            # 更新状态
            self.processes[service].pid = None
            self.processes[service].status = 'stopped'
            self.processes[service].start_time = None
            self.processes[service].cpu_percent = 0.0
            self.processes[service].memory_percent = 0.0
            self.processes[service].error_message = ""
            
            self._notify_status_change(service)
            
            return True
            
        except Exception as e:
            print(f"停止进程失败: {e}")
            return False
            
    def restart_process(self, service: str, conda_env: Optional[str] = None) -> ProcessResult:
        """重启指定服务"""
        # 先停止
        self.stop_process(service)
        
        # 等待一秒
        time.sleep(1)
        
        # 重新启动
        if service == 'frontend':
            return self.start_frontend()
        elif service == 'backend':
            return self.start_backend(conda_env)
        else:
            return ProcessResult(
                success=False,
                error=f"未知服务: {service}"
            )
            
    def is_process_running(self, service: str) -> bool:
        """检查进程是否正在运行"""
        process = self.process_objects.get(service)
        if process is None:
            return False
            
        return process.poll() is None
        
    def get_process_status(self, service: str) -> ProcessStatus:
        """获取进程状态"""
        return self.processes.get(service, ProcessStatus())
        
    def get_all_status(self) -> Dict[str, ProcessStatus]:
        """获取所有进程状态"""
        return self.processes.copy()
        
    def start_monitoring(self):
        """启动进程监控线程"""
        if self.monitoring_thread is not None and self.monitoring_thread.is_alive():
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """停止进程监控"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)
            
    def _monitor_processes(self):
        """监控进程状态（在后台线程中运行）"""
        while self.monitoring_active:
            try:
                for service in ['frontend', 'backend']:
                    self._update_process_stats(service)
                time.sleep(2)  # 每2秒更新一次
            except Exception as e:
                print(f"监控进程时发生错误: {e}")
                time.sleep(5)
                
    def _update_process_stats(self, service: str):
        """更新进程统计信息"""
        try:
            process_obj = self.process_objects.get(service)
            status = self.processes[service]
            
            if process_obj is None or process_obj.poll() is not None:
                # 进程不存在或已结束
                if status.status == 'running':
                    status.status = 'stopped'
                    status.pid = None
                    status.cpu_percent = 0.0
                    status.memory_percent = 0.0
                    self._notify_status_change(service)
                return
                
            # 获取进程信息
            try:
                psutil_process = psutil.Process(process_obj.pid)
                status.cpu_percent = psutil_process.cpu_percent()
                status.memory_percent = psutil_process.memory_percent()
                
                # 检查进程是否仍在运行
                if psutil_process.status() == psutil.STATUS_ZOMBIE:
                    status.status = 'stopped'
                    self.process_objects[service] = None
                    self._notify_status_change(service)
                    
            except psutil.NoSuchProcess:
                # 进程已不存在
                status.status = 'stopped'
                status.pid = None
                status.cpu_percent = 0.0
                status.memory_percent = 0.0
                self.process_objects[service] = None
                self._notify_status_change(service)
                
        except Exception as e:
            print(f"更新进程统计信息失败: {e}")
            
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        
        # 停止所有进程
        for service in ['frontend', 'backend']:
            try:
                self.stop_process(service)
            except Exception as e:
                print(f"清理进程 {service} 时发生错误: {e}")
                
    def get_port_info(self, port: int) -> Dict[str, any]:
        """获取端口占用信息"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    try:
                        process = psutil.Process(conn.pid) if conn.pid else None
                        return {
                            'occupied': True,
                            'pid': conn.pid,
                            'process_name': process.name() if process else 'Unknown',
                            'status': conn.status
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {
                            'occupied': True,
                            'pid': conn.pid,
                            'process_name': 'Unknown',
                            'status': conn.status
                        }
            return {'occupied': False}
        except Exception as e:
            print(f"检查端口占用失败: {e}")
            return {'occupied': False, 'error': str(e)}