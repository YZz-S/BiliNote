#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

功能：
- 读写.env文件
- 端口配置验证
- 环境变量管理
- 配置备份和恢复
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """配置验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class ConfigItem:
    """配置项"""
    key: str
    value: str
    description: str = ""
    is_required: bool = False
    data_type: str = "string"  # string, int, bool, path
    default_value: str = ""

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, env_file_path: Optional[str] = None):
        self.project_root = Path.cwd()
        self.env_file_path = Path(env_file_path) if env_file_path else self.project_root / ".env"
        self.env_example_path = self.project_root / ".env.example"
        self.backup_dir = self.project_root / "config_backups"
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
        # 配置项定义
        self.config_definitions = self._get_config_definitions()
        
        # 当前配置
        self.current_config: Dict[str, str] = {}
        self.load_config()
        
    def _get_config_definitions(self) -> Dict[str, ConfigItem]:
        """获取配置项定义"""
        return {
            'BACKEND_PORT': ConfigItem(
                key='BACKEND_PORT',
                value='8483',
                description='后端服务端口',
                is_required=True,
                data_type='int',
                default_value='8483'
            ),
            'FRONTEND_PORT': ConfigItem(
                key='FRONTEND_PORT', 
                value='3015',
                description='前端服务端口（Docker部署用）',
                is_required=False,
                data_type='int',
                default_value='3015'
            ),
            'VITE_FRONTEND_PORT': ConfigItem(
                key='VITE_FRONTEND_PORT',
                value='3015', 
                description='Vite前端开发服务器端口',
                is_required=False,
                data_type='int',
                default_value='3015'
            ),
            'BACKEND_HOST': ConfigItem(
                key='BACKEND_HOST',
                value='0.0.0.0',
                description='后端服务监听地址',
                is_required=False,
                data_type='string',
                default_value='0.0.0.0'
            ),
            'VITE_API_BASE_URL': ConfigItem(
                key='VITE_API_BASE_URL',
                value='http://127.0.0.1:8483',
                description='前端访问后端API的基础URL',
                is_required=True,
                data_type='string',
                default_value='http://127.0.0.1:8483'
            ),
            'VITE_SCREENSHOT_BASE_URL': ConfigItem(
                key='VITE_SCREENSHOT_BASE_URL',
                value='http://127.0.0.1:8483/static/screenshots',
                description='截图访问基础URL',
                is_required=False,
                data_type='string',
                default_value='http://127.0.0.1:8483/static/screenshots'
            ),
            'TRANSCRIBER_TYPE': ConfigItem(
                key='TRANSCRIBER_TYPE',
                value='fast-whisper',
                description='转写器类型',
                is_required=False,
                data_type='string',
                default_value='fast-whisper'
            ),
            'WHISPER_MODEL_SIZE': ConfigItem(
                key='WHISPER_MODEL_SIZE',
                value='base',
                description='Whisper模型大小',
                is_required=False,
                data_type='string',
                default_value='base'
            ),
            'CONDA_ENV_NAME': ConfigItem(
                key='CONDA_ENV_NAME',
                value='bilinote',
                description='Conda虚拟环境名称',
                is_required=False,
                data_type='string',
                default_value='bilinote'
            ),
            'FFMPEG_BIN_PATH': ConfigItem(
                key='FFMPEG_BIN_PATH',
                value='',
                description='FFmpeg可执行文件路径',
                is_required=False,
                data_type='path',
                default_value=''
            )
        }
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            self.current_config = {}
            
            if not self.env_file_path.exists():
                # 如果.env不存在，尝试从.env.example复制
                if self.env_example_path.exists():
                    shutil.copy2(self.env_example_path, self.env_file_path)
                else:
                    # 创建默认配置文件
                    self._create_default_config()
                    
            # 读取配置文件
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                        
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除值两端的引号
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                            
                        # 处理注释
                        if '#' in value:
                            value = value.split('#')[0].strip()
                            
                        self.current_config[key] = value
                        
            return True
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
            
    def save_config(self, config: Optional[Dict[str, str]] = None) -> bool:
        """保存配置文件"""
        try:
            if config is not None:
                self.current_config.update(config)
                
            # 创建备份
            self._create_backup()
            
            # 读取原文件内容以保持格式和注释
            original_lines = []
            if self.env_file_path.exists():
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    original_lines = f.readlines()
                    
            # 构建新的文件内容
            new_lines = []
            processed_keys = set()
            
            for line in original_lines:
                stripped_line = line.strip()
                
                # 保持空行和注释
                if not stripped_line or stripped_line.startswith('#'):
                    new_lines.append(line)
                    continue
                    
                # 处理配置行
                if '=' in stripped_line:
                    key = stripped_line.split('=')[0].strip()
                    if key in self.current_config:
                        # 更新现有配置
                        value = self.current_config[key]
                        comment = ''
                        
                        # 提取原有注释
                        if '#' in line:
                            comment = ' ' + line.split('#', 1)[1]
                        elif key in self.config_definitions:
                            comment = f' # {self.config_definitions[key].description}'
                            
                        new_lines.append(f"{key}={value}{comment}")
                        processed_keys.add(key)
                    else:
                        # 保持原有配置
                        new_lines.append(line)
                else:
                    new_lines.append(line)
                    
            # 添加新的配置项
            for key, value in self.current_config.items():
                if key not in processed_keys:
                    comment = ''
                    if key in self.config_definitions:
                        comment = f' # {self.config_definitions[key].description}'
                    new_lines.append(f"{key}={value}{comment}\n")
                    
            # 写入文件
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
            
    def get_config(self, key: str, default: str = "") -> str:
        """获取配置值"""
        return self.current_config.get(key, default)
        
    def set_config(self, key: str, value: str) -> bool:
        """设置配置值"""
        try:
            self.current_config[key] = str(value)
            return True
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
            
    def get_all_config(self) -> Dict[str, str]:
        """获取所有配置"""
        return self.current_config.copy()
        
    def validate_config(self, config: Optional[Dict[str, str]] = None) -> ValidationResult:
        """验证配置"""
        if config is None:
            config = self.current_config
            
        errors = []
        warnings = []
        
        # 检查必需的配置项
        for key, definition in self.config_definitions.items():
            if definition.is_required and key not in config:
                errors.append(f"缺少必需的配置项: {key}")
                
        # 验证端口配置
        port_configs = ['BACKEND_PORT', 'FRONTEND_PORT', 'VITE_FRONTEND_PORT']
        used_ports = []
        
        for port_key in port_configs:
            if port_key in config:
                try:
                    port = int(config[port_key])
                    if port < 1 or port > 65535:
                        errors.append(f"{port_key} 端口号无效: {port} (应在1-65535之间)")
                    elif port in used_ports:
                        errors.append(f"端口冲突: {port} 被多个服务使用")
                    else:
                        used_ports.append(port)
                        
                    # 检查常用端口
                    if port in [80, 443, 22, 21, 25, 53, 110, 143, 993, 995]:
                        warnings.append(f"{port_key} 使用了系统常用端口: {port}")
                        
                except ValueError:
                    errors.append(f"{port_key} 端口号格式错误: {config[port_key]}")
                    
        # 验证URL格式
        url_configs = ['VITE_API_BASE_URL', 'VITE_SCREENSHOT_BASE_URL']
        for url_key in url_configs:
            if url_key in config:
                url = config[url_key]
                if url and not (url.startswith('http://') or url.startswith('https://')):
                    warnings.append(f"{url_key} URL格式可能不正确: {url}")
                    
        # 验证路径配置
        path_configs = ['FFMPEG_BIN_PATH']
        for path_key in path_configs:
            if path_key in config and config[path_key]:
                path = Path(config[path_key])
                if not path.exists():
                    warnings.append(f"{path_key} 指定的路径不存在: {config[path_key]}")
                    
        # 验证转写器类型
        if 'TRANSCRIBER_TYPE' in config:
            valid_types = ['fast-whisper', 'bcut', 'kuaishou', 'mlx-whisper', 'groq']
            if config['TRANSCRIBER_TYPE'] not in valid_types:
                warnings.append(f"TRANSCRIBER_TYPE 值可能不正确: {config['TRANSCRIBER_TYPE']}")
                
        # 验证Whisper模型大小
        if 'WHISPER_MODEL_SIZE' in config:
            valid_sizes = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
            if config['WHISPER_MODEL_SIZE'] not in valid_sizes:
                warnings.append(f"WHISPER_MODEL_SIZE 值可能不正确: {config['WHISPER_MODEL_SIZE']}")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    def validate_port_config(self, ports: Dict[str, int]) -> ValidationResult:
        """验证端口配置"""
        errors = []
        warnings = []
        used_ports = []
        
        for name, port in ports.items():
            # 检查端口范围
            if port < 1 or port > 65535:
                errors.append(f"{name} 端口号无效: {port} (应在1-65535之间)")
                continue
                
            # 检查端口冲突
            if port in used_ports:
                errors.append(f"端口冲突: {port} 被多个服务使用")
            else:
                used_ports.append(port)
                
            # 检查系统端口
            if port < 1024:
                warnings.append(f"{name} 使用了系统保留端口: {port}")
                
            # 检查常用端口
            common_ports = {80: 'HTTP', 443: 'HTTPS', 22: 'SSH', 3306: 'MySQL', 5432: 'PostgreSQL'}
            if port in common_ports:
                warnings.append(f"{name} 使用了{common_ports[port]}常用端口: {port}")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    def _create_default_config(self):
        """创建默认配置文件"""
        try:
            default_content = [
                "# BiliNote 配置文件",
                "# 自动生成于 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "",
                "# 通用端口配置",
                "BACKEND_PORT=8483 # 后端端口",
                "FRONTEND_PORT=3015",
                "BACKEND_HOST=0.0.0.0 # 默认为 0.0.0.0，表示监听所有 IP 地址 不建议动",
                "APP_PORT=3015 # docker 部署时用",
                "",
                "# 前端访问后端用 (开发环境使用)",
                "VITE_API_BASE_URL=http://127.0.0.1:8483",
                "VITE_SCREENSHOT_BASE_URL=http://127.0.0.1:8483/static/screenshots",
                "VITE_FRONTEND_PORT=3015",
                "",
                "# 生产环境配置",
                "ENV=production",
                "STATIC=/static",
                "OUT_DIR=./static/screenshots",
                "NOTE_OUTPUT_DIR=note_results",
                "IMAGE_BASE_URL=/static/screenshots",
                "DATA_DIR=data",
                "",
                "# FFMPEG 配置",
                "FFMPEG_BIN_PATH=",
                "",
                "# transcriber 相关配置",
                "TRANSCRIBER_TYPE=fast-whisper # fast-whisper/bcut/kuaishou/mlx-whisper(仅Apple平台)/groq",
                "WHISPER_MODEL_SIZE=base",
                "",
                "GROQ_TRANSCRIBER_MODEL=whisper-large-v3-turbo # groq提供的faster-whisper 默认为 whisper-large-v3-turbo",
                "",
                "# Conda虚拟环境配置",
                "CONDA_ENV_NAME=bilinote # conda虚拟环境名称，如果为空则跳过虚拟环境设置",
                ""
            ]
            
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(default_content))
                
        except Exception as e:
            print(f"创建默认配置文件失败: {e}")
            
    def _create_backup(self) -> bool:
        """创建配置文件备份"""
        try:
            if not self.env_file_path.exists():
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f".env.backup_{timestamp}"
            
            shutil.copy2(self.env_file_path, backup_file)
            
            # 只保留最近10个备份
            backups = sorted(self.backup_dir.glob(".env.backup_*"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
                    
            return True
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            return False
            
    def restore_from_backup(self, backup_file: str) -> bool:
        """从备份恢复配置"""
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                return False
                
            shutil.copy2(backup_path, self.env_file_path)
            self.load_config()
            return True
            
        except Exception as e:
            print(f"从备份恢复失败: {e}")
            return False
            
    def get_backups(self) -> List[str]:
        """获取备份文件列表"""
        try:
            backups = sorted(self.backup_dir.glob(".env.backup_*"), reverse=True)
            return [backup.name for backup in backups]
        except Exception as e:
            print(f"获取备份列表失败: {e}")
            return []
            
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self._create_backup()
            self._create_default_config()
            self.load_config()
            return True
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False
            
    def get_config_definitions(self) -> Dict[str, ConfigItem]:
        """获取配置项定义"""
        return self.config_definitions.copy()