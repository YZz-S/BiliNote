#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的GUI启动器启动脚本
用于测试和演示
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

def create_demo_gui():
    """创建演示GUI"""
    root = tk.Tk()
    root.title("BiliNote GUI启动器 - 演示版")
    root.geometry("800x600")
    
    # 主框架
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 标题
    title_label = ttk.Label(main_frame, text="BiliNote GUI启动器", font=('Arial', 16, 'bold'))
    title_label.pack(pady=10)
    
    # 状态信息
    status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding=10)
    status_frame.pack(fill=tk.X, pady=10)
    
    # 检查项目结构
    project_checks = [
        ("后端目录", Path("backend").exists()),
        ("前端目录", Path("BillNote_frontend").exists()),
        ("主程序文件", Path("backend/main.py").exists()),
        ("前端配置", Path("BillNote_frontend/package.json").exists()),
        (".env文件", Path(".env").exists())
    ]
    
    for i, (name, exists) in enumerate(project_checks):
        status_text = "✓ 正常" if exists else "✗ 缺失"
        color = "green" if exists else "red"
        
        label = ttk.Label(status_frame, text=f"{name}: {status_text}")
        label.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
        
    # 功能按钮
    button_frame = ttk.LabelFrame(main_frame, text="功能演示", padding=10)
    button_frame.pack(fill=tk.X, pady=10)
    
    def show_info():
        info_text = """
BiliNote GUI启动器功能：

✓ 项目启动控制
  - 独立启动前端/后端服务
  - 一键启动全部服务
  - 实时状态监控

✓ 配置管理
  - 端口配置和验证
  - .env文件可视化编辑
  - 配置项验证和诊断

✓ 日志监控
  - 实时日志查看
  - 日志级别过滤
  - 错误诊断和导出

✓ 系统信息
  - 依赖检查
  - 系统资源监控
  - 项目结构验证
"""
        messagebox.showinfo("功能介绍", info_text)
        
    def check_dependencies():
        """检查依赖"""
        import subprocess
        import shutil
        
        deps = {
            'Python': sys.executable,
            'Node.js': shutil.which('node'),
            'pnpm': shutil.which('pnpm'),
            'FFmpeg': shutil.which('ffmpeg')
        }
        
        result_text = "依赖检查结果:\n\n"
        
        for name, path in deps.items():
            if path:
                try:
                    if name == 'Python':
                        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                    elif name == 'Node.js':
                        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
                        version = result.stdout.strip() if result.returncode == 0 else "未知"
                    elif name == 'pnpm':
                        result = subprocess.run(['pnpm', '--version'], capture_output=True, text=True, timeout=5)
                        version = result.stdout.strip() if result.returncode == 0 else "未知"
                    elif name == 'FFmpeg':
                        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
                        version = "已安装" if result.returncode == 0 else "未知"
                    else:
                        version = "已安装"
                        
                    result_text += f"✓ {name}: {version}\n"
                except:
                    result_text += f"⚠ {name}: 检查失败\n"
            else:
                result_text += f"✗ {name}: 未安装\n"
                
        messagebox.showinfo("依赖检查", result_text)
        
    def launch_full_gui():
        """启动完整GUI"""
        try:
            root.destroy()
            # 导入并启动完整GUI
            sys.path.append('modules')
            from gui_launcher import BiliNoteGUILauncher
            app = BiliNoteGUILauncher()
            app.run()
        except Exception as e:
            messagebox.showerror("启动失败", f"启动完整GUI失败:\n{e}")
            
    # 按钮布局
    ttk.Button(button_frame, text="功能介绍", command=show_info).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="检查依赖", command=check_dependencies).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="启动完整GUI", command=launch_full_gui).pack(side=tk.LEFT, padx=5)
    
    # 说明文本
    info_frame = ttk.LabelFrame(main_frame, text="使用说明", padding=10)
    info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    info_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
    info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=info_text.yview)
    info_text.configure(yscrollcommand=info_scroll.set)
    
    instructions = """
欢迎使用BiliNote GUI启动器！

这是一个为BiliNote AI视频笔记项目设计的图形化启动和管理工具。

主要功能：
• 项目启动控制：可视化启动前端和后端服务
• 配置管理：端口配置、.env文件编辑
• 日志监控：实时查看服务运行日志
• 系统信息：依赖检查、资源监控

使用步骤：
1. 点击"检查依赖"确保所需软件已安装
2. 点击"启动完整GUI"打开主界面
3. 在主界面中可以启动前后端服务
4. 使用配置管理调整端口等设置
5. 通过日志监控查看运行状态

注意事项：
• 请确保在BiliNote项目根目录中运行
• 首次使用前请检查.env配置文件
• 如遇问题可查看系统信息页面的诊断结果
"""
    
    info_text.insert(1.0, instructions)
    info_text.config(state=tk.DISABLED)
    
    info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 底部状态栏
    status_bar = ttk.Frame(root)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    status_label = ttk.Label(status_bar, text=f"工作目录: {Path.cwd()}")
    status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    return root

def main():
    """主函数"""
    try:
        # 检查是否在正确的目录
        if not (Path("backend").exists() and Path("BillNote_frontend").exists()):
            print("警告：未在BiliNote项目根目录中运行")
            
        # 创建并运行演示GUI
        root = create_demo_gui()
        root.mainloop()
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()