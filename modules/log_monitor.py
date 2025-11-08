#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志监控模块

功能：
- 实时日志查看
- 日志搜索和过滤
- 日志导出
- 错误诊断
"""

import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable, Iterator
from dataclasses import dataclass
from collections import deque
import subprocess

@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: str  # 'INFO', 'WARNING', 'ERROR', 'DEBUG'
    message: str
    source: str  # 'frontend', 'backend', 'system'
    raw_line: str = ""

class LogMonitor:
    """日志监控器"""
    
    def __init__(self, max_lines: int = 1000):
        self.max_lines = max_lines
        self.logs: Dict[str, deque] = {
            'frontend': deque(maxlen=max_lines),
            'backend': deque(maxlen=max_lines),
            'system': deque(maxlen=max_lines)
        }
        
        # 监控线程
        self.monitoring_threads: Dict[str, Optional[threading.Thread]] = {
            'frontend': None,
            'backend': None
        }
        self.monitoring_active = False
        
        # 回调函数
        self.log_callbacks: List[Callable] = []
        
        # 进程对象引用（用于读取实时输出）
        self.process_objects: Dict[str, Optional[subprocess.Popen]] = {
            'frontend': None,
            'backend': None
        }
        
        # 日志级别映射
        self.level_patterns = {
            'ERROR': [r'error', r'错误', r'failed', r'失败', r'exception', r'异常'],
            'WARNING': [r'warning', r'warn', r'警告', r'deprecated', r'已弃用'],
            'INFO': [r'info', r'信息', r'started', r'启动', r'running', r'运行'],
            'DEBUG': [r'debug', r'调试', r'trace', r'跟踪']
        }
        
    def add_log_callback(self, callback: Callable):
        """添加日志回调函数"""
        self.log_callbacks.append(callback)
        
    def _notify_log_update(self, service: str, entry: LogEntry):
        """通知日志更新"""
        for callback in self.log_callbacks:
            try:
                callback(service, entry)
            except Exception as e:
                print(f"日志回调执行失败: {e}")
                
    def start_monitoring(self, service: str, process_obj: Optional[subprocess.Popen] = None):
        """开始监控指定服务的日志"""
        if service not in self.monitoring_threads:
            return False
            
        # 停止现有监控
        self.stop_monitoring(service)
        
        # 设置进程对象
        if process_obj:
            self.process_objects[service] = process_obj
            
        # 启动监控线程
        self.monitoring_active = True
        thread = threading.Thread(
            target=self._monitor_service_logs,
            args=(service,),
            daemon=True
        )
        thread.start()
        self.monitoring_threads[service] = thread
        
        return True
        
    def stop_monitoring(self, service: str):
        """停止监控指定服务的日志"""
        if service in self.monitoring_threads and self.monitoring_threads[service]:
            thread = self.monitoring_threads[service]
            if thread.is_alive():
                # 线程会在下次检查时自动退出
                pass
            self.monitoring_threads[service] = None
            
    def stop_all_monitoring(self):
        """停止所有日志监控"""
        self.monitoring_active = False
        for service in self.monitoring_threads:
            self.stop_monitoring(service)
            
    def _monitor_service_logs(self, service: str):
        """监控服务日志（在后台线程中运行）"""
        try:
            process = self.process_objects.get(service)
            if not process:
                return
                
            # 监控stdout和stderr
            while self.monitoring_active and process.poll() is None:
                try:
                    # 读取stdout
                    if process.stdout:
                        line = process.stdout.readline()
                        if line:
                            self._process_log_line(service, line.strip())
                            
                    # 读取stderr
                    if process.stderr:
                        line = process.stderr.readline()
                        if line:
                            self._process_log_line(service, line.strip(), is_error=True)
                            
                    time.sleep(0.1)  # 避免过度占用CPU
                    
                except Exception as e:
                    self.add_system_log(f"读取{service}日志时发生错误: {e}", 'ERROR')
                    break
                    
        except Exception as e:
            self.add_system_log(f"监控{service}日志失败: {e}", 'ERROR')
            
    def _process_log_line(self, service: str, line: str, is_error: bool = False):
        """处理日志行"""
        if not line.strip():
            return
            
        # 解析日志级别
        level = self._detect_log_level(line)
        if is_error and level == 'INFO':
            level = 'ERROR'
            
        # 创建日志条目
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=line,
            source=service,
            raw_line=line
        )
        
        # 添加到日志队列
        self.logs[service].append(entry)
        
        # 通知回调
        self._notify_log_update(service, entry)
        
    def _detect_log_level(self, line: str) -> str:
        """检测日志级别"""
        line_lower = line.lower()
        
        # 按优先级检查（ERROR > WARNING > DEBUG > INFO）
        for level, patterns in self.level_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line_lower):
                    return level
                    
        return 'INFO'  # 默认级别
        
    def add_system_log(self, message: str, level: str = 'INFO'):
        """添加系统日志"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            source='system',
            raw_line=message
        )
        
        self.logs['system'].append(entry)
        self._notify_log_update('system', entry)
        
    def get_logs(self, service: str, limit: Optional[int] = None) -> List[LogEntry]:
        """获取指定服务的日志"""
        if service not in self.logs:
            return []
            
        logs = list(self.logs[service])
        if limit:
            logs = logs[-limit:]
            
        return logs
        
    def get_recent_logs(self, service: str, minutes: int = 10) -> List[LogEntry]:
        """获取最近几分钟的日志"""
        if service not in self.logs:
            return []
            
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        recent_logs = []
        
        for entry in self.logs[service]:
            if entry.timestamp.timestamp() >= cutoff_time:
                recent_logs.append(entry)
                
        return recent_logs
        
    def search_logs(self, service: str, keyword: str, level: Optional[str] = None) -> List[LogEntry]:
        """搜索日志"""
        if service not in self.logs:
            return []
            
        results = []
        keyword_lower = keyword.lower()
        
        for entry in self.logs[service]:
            # 检查级别过滤
            if level and entry.level != level:
                continue
                
            # 检查关键词
            if keyword_lower in entry.message.lower():
                results.append(entry)
                
        return results
        
    def get_error_logs(self, service: str, limit: int = 50) -> List[LogEntry]:
        """获取错误日志"""
        if service not in self.logs:
            return []
            
        error_logs = []
        for entry in self.logs[service]:
            if entry.level == 'ERROR':
                error_logs.append(entry)
                
        return error_logs[-limit:] if limit else error_logs
        
    def export_logs(self, service: str, filepath: str, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> bool:
        """导出日志到文件"""
        try:
            if service not in self.logs:
                return False
                
            logs_to_export = []
            
            for entry in self.logs[service]:
                # 时间过滤
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                    
                logs_to_export.append(entry)
                
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {service.upper()} 日志导出\n")
                f.write(f"# 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 日志条数: {len(logs_to_export)}\n\n")
                
                for entry in logs_to_export:
                    timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp_str}] [{entry.level}] {entry.message}\n")
                    
            return True
            
        except Exception as e:
            self.add_system_log(f"导出日志失败: {e}", 'ERROR')
            return False
            
    def clear_logs(self, service: str) -> bool:
        """清空指定服务的日志"""
        try:
            if service in self.logs:
                self.logs[service].clear()
                self.add_system_log(f"已清空{service}日志")
                return True
            return False
        except Exception as e:
            self.add_system_log(f"清空日志失败: {e}", 'ERROR')
            return False
            
    def get_log_statistics(self, service: str) -> Dict[str, int]:
        """获取日志统计信息"""
        if service not in self.logs:
            return {}
            
        stats = {
            'total': 0,
            'ERROR': 0,
            'WARNING': 0,
            'INFO': 0,
            'DEBUG': 0
        }
        
        for entry in self.logs[service]:
            stats['total'] += 1
            stats[entry.level] = stats.get(entry.level, 0) + 1
            
        return stats
        
    def diagnose_errors(self, service: str) -> List[Dict[str, str]]:
        """诊断常见错误"""
        error_logs = self.get_error_logs(service)
        diagnoses = []
        
        # 常见错误模式和解决方案
        error_patterns = {
            r'port.*already.*in.*use|address.*already.*in.*use': {
                'problem': '端口被占用',
                'solution': '检查端口配置，或停止占用端口的进程'
            },
            r'module.*not.*found|no.*module.*named': {
                'problem': '缺少Python模块',
                'solution': '安装缺少的依赖包：pip install <模块名>'
            },
            r'command.*not.*found|is.*not.*recognized': {
                'problem': '命令未找到',
                'solution': '检查相关程序是否已安装并添加到PATH环境变量'
            },
            r'permission.*denied|access.*denied': {
                'problem': '权限不足',
                'solution': '检查文件权限或以管理员身份运行'
            },
            r'connection.*refused|connection.*failed': {
                'problem': '连接失败',
                'solution': '检查网络连接和服务是否正常运行'
            },
            r'file.*not.*found|no.*such.*file': {
                'problem': '文件未找到',
                'solution': '检查文件路径是否正确，确保文件存在'
            }
        }
        
        for entry in error_logs[-10:]:  # 只检查最近10条错误
            message_lower = entry.message.lower()
            
            for pattern, diagnosis in error_patterns.items():
                if re.search(pattern, message_lower):
                    diagnoses.append({
                        'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'error_message': entry.message,
                        'problem': diagnosis['problem'],
                        'solution': diagnosis['solution']
                    })
                    break
                    
        return diagnoses
        
    def get_realtime_logs(self, service: str) -> Iterator[LogEntry]:
        """获取实时日志流"""
        if service not in self.logs:
            return
            
        # 返回现有日志
        for entry in self.logs[service]:
            yield entry
            
        # 这里可以实现实时流，但在GUI应用中通常通过回调处理
        
    def cleanup(self):
        """清理资源"""
        self.stop_all_monitoring()
        
        # 清空所有日志
        for service in self.logs:
            self.logs[service].clear()
            
        # 清空回调
        self.log_callbacks.clear()