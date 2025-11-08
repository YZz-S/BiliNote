#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BiliNote GUI启动器
主程序入口文件

功能：
- 提供可视化的项目启动和管理界面
- 支持前后端独立或联合启动
- 配置管理和状态监控
- 日志查看和系统检测
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time
from pathlib import Path

# 添加modules目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from process_manager import ProcessManager
    from config_manager import ConfigManager
    from log_monitor import LogMonitor
    from system_detector import SystemDetector
except ImportError as e:
    print(f"模块导入失败: {e}")
    print("请确保所有必要的模块文件都已创建")

class BiliNoteGUILauncher:
    """BiliNote GUI启动器主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_managers()
        self.create_widgets()
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("BiliNote GUI启动器 v1.0")
        self.root.geometry("1024x768")
        self.root.minsize(1024, 768)
        
        # 设置窗口图标（如果存在）
        icon_path = Path("doc/icon.svg")
        if icon_path.exists():
            try:
                # 注意：tkinter不直接支持SVG，这里只是示例
                # 实际使用中可能需要转换为ICO或PNG格式
                pass
            except Exception:
                pass
                
        # 居中显示窗口
        self.center_window()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_managers(self):
        """初始化各个管理器"""
        try:
            self.process_manager = ProcessManager()
            self.config_manager = ConfigManager()
            self.log_monitor = LogMonitor()
            self.system_detector = SystemDetector()
        except Exception as e:
            messagebox.showerror("初始化错误", f"管理器初始化失败: {e}")
            
    def create_widgets(self):
        """创建主界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧导航栏
        self.create_navigation(main_frame)
        
        # 创建右侧内容区域
        self.create_content_area(main_frame)
        
        # 创建底部状态栏
        self.create_status_bar()
        
        # 默认显示主控制台页面
        self.show_main_console()
        
    def create_navigation(self, parent):
        """创建左侧导航栏"""
        nav_frame = ttk.LabelFrame(parent, text="功能导航", padding=10)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 导航按钮
        nav_buttons = [
            ("主控制台", self.show_main_console),
            ("配置管理", self.show_config_management),
            ("日志监控", self.show_log_monitor),
            ("系统信息", self.show_system_info)
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ttk.Button(nav_frame, text=text, command=command, width=15)
            btn.pack(pady=5, fill=tk.X)
            self.nav_buttons[text] = btn
            
    def create_content_area(self, parent):
        """创建右侧内容区域"""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        """创建底部状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 添加时间显示
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=10, pady=5)
        self.update_time()
        
    def update_time(self):
        """更新时间显示"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def clear_content(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_main_console(self):
        """显示主控制台页面"""
        self.clear_content()
        self.update_nav_selection("主控制台")
        
        # 创建主控制台内容
        console_frame = ttk.Frame(self.content_frame)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 上半部分：启动控制
        control_frame = ttk.LabelFrame(console_frame, text="启动控制", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮框架
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        # 前端控制
        frontend_frame = ttk.LabelFrame(btn_frame, text="前端服务", padding=5)
        frontend_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.frontend_start_btn = ttk.Button(frontend_frame, text="启动前端", command=self.start_frontend)
        self.frontend_start_btn.pack(side=tk.LEFT, padx=2)
        
        self.frontend_stop_btn = ttk.Button(frontend_frame, text="停止前端", command=self.stop_frontend, state=tk.DISABLED)
        self.frontend_stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.frontend_status = ttk.Label(frontend_frame, text="已停止", foreground="red")
        self.frontend_status.pack(side=tk.RIGHT, padx=5)
        
        # 后端控制
        backend_frame = ttk.LabelFrame(btn_frame, text="后端服务", padding=5)
        backend_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.backend_start_btn = ttk.Button(backend_frame, text="启动后端", command=self.start_backend)
        self.backend_start_btn.pack(side=tk.LEFT, padx=2)
        
        self.backend_stop_btn = ttk.Button(backend_frame, text="停止后端", command=self.stop_backend, state=tk.DISABLED)
        self.backend_stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.backend_status = ttk.Label(backend_frame, text="已停止", foreground="red")
        self.backend_status.pack(side=tk.RIGHT, padx=5)
        
        # 一键启动
        quick_frame = ttk.Frame(control_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_all_btn = ttk.Button(quick_frame, text="一键启动全部", command=self.start_all)
        self.start_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_all_btn = ttk.Button(quick_frame, text="停止全部", command=self.stop_all)
        self.stop_all_btn.pack(side=tk.LEFT, padx=5)
        
        # 下半部分：状态监控和快速访问
        bottom_frame = ttk.Frame(console_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态监控
        status_frame = ttk.LabelFrame(bottom_frame, text="状态监控", padding=10)
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 创建状态表格
        columns = ('服务', '状态', 'PID', '端口', 'CPU%', '内存%')
        self.status_tree = ttk.Treeview(status_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=80)
            
        self.status_tree.pack(fill=tk.BOTH, expand=True)
        
        # 快速访问
        access_frame = ttk.LabelFrame(bottom_frame, text="快速访问", padding=10)
        access_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        ttk.Button(access_frame, text="打开前端页面", command=self.open_frontend).pack(fill=tk.X, pady=2)
        ttk.Button(access_frame, text="打开后端API", command=self.open_backend).pack(fill=tk.X, pady=2)
        ttk.Button(access_frame, text="打开项目目录", command=self.open_project_dir).pack(fill=tk.X, pady=2)
        ttk.Button(access_frame, text="刷新状态", command=self.refresh_status).pack(fill=tk.X, pady=2)
        
        # 启动状态更新
        self.update_status_display()
        self.schedule_status_update()
        
    def show_config_management(self):
        """显示配置管理页面"""
        self.clear_content()
        self.update_nav_selection("配置管理")
        
        config_frame = ttk.Frame(self.content_frame)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Notebook用于标签页
        notebook = ttk.Notebook(config_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 端口配置标签页
        port_frame = ttk.Frame(notebook)
        notebook.add(port_frame, text="端口配置")
        self.create_port_config_tab(port_frame)
        
        # .env文件编辑标签页
        env_frame = ttk.Frame(notebook)
        notebook.add(env_frame, text=".env文件编辑")
        self.create_env_editor_tab(env_frame)
        
        # 配置验证标签页
        validation_frame = ttk.Frame(notebook)
        notebook.add(validation_frame, text="配置验证")
        self.create_validation_tab(validation_frame)
        
    def show_log_monitor(self):
        """显示日志监控页面"""
        self.clear_content()
        self.update_nav_selection("日志监控")
        
        log_frame = ttk.Frame(self.content_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 控制面板
        control_panel = ttk.Frame(log_frame)
        control_panel.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(control_panel, text="日志级别:").pack(side=tk.LEFT, padx=5)
        self.log_level_var = tk.StringVar(value="全部")
        level_combo = ttk.Combobox(control_panel, textvariable=self.log_level_var, 
                                  values=["全部", "ERROR", "WARNING", "INFO", "DEBUG"], width=10)
        level_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_panel, text="清空日志", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_panel, text="导出日志", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_panel, text="刷新", command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域
        log_notebook = ttk.Notebook(log_frame)
        log_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 前端日志
        frontend_log_frame = ttk.Frame(log_notebook)
        log_notebook.add(frontend_log_frame, text="前端日志")
        self.create_log_display(frontend_log_frame, "frontend")
        
        # 后端日志
        backend_log_frame = ttk.Frame(log_notebook)
        log_notebook.add(backend_log_frame, text="后端日志")
        self.create_log_display(backend_log_frame, "backend")
        
        # 系统日志
        system_log_frame = ttk.Frame(log_notebook)
        log_notebook.add(system_log_frame, text="系统日志")
        self.create_log_display(system_log_frame, "system")
        
    def show_system_info(self):
        """显示系统信息页面"""
        self.clear_content()
        self.update_nav_selection("系统信息")
        
        system_frame = ttk.Frame(self.content_frame)
        system_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Notebook
        notebook = ttk.Notebook(system_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 依赖检查标签页
        deps_frame = ttk.Frame(notebook)
        notebook.add(deps_frame, text="依赖检查")
        self.create_dependencies_tab(deps_frame)
        
        # 系统资源标签页
        resources_frame = ttk.Frame(notebook)
        notebook.add(resources_frame, text="系统资源")
        self.create_resources_tab(resources_frame)
        
        # 项目结构标签页
        structure_frame = ttk.Frame(notebook)
        notebook.add(structure_frame, text="项目结构")
        self.create_structure_tab(structure_frame)
        
    def update_nav_selection(self, selected):
        """更新导航按钮选中状态"""
        for text, btn in self.nav_buttons.items():
            if text == selected:
                btn.configure(style="Selected.TButton")
            else:
                btn.configure(style="TButton")
                
    def update_status(self, message):
        """更新状态栏信息"""
        self.status_label.config(text=message)
        
    def run(self):
        """启动GUI应用程序"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            messagebox.showerror("运行错误", f"应用程序运行时发生错误: {e}")
            
    def on_closing(self):
        """程序关闭时的清理工作"""
        try:
            # 停止所有正在运行的进程
            if hasattr(self, 'process_manager'):
                self.process_manager.cleanup()
            if hasattr(self, 'log_monitor'):
                self.log_monitor.cleanup()
            if hasattr(self, 'system_detector'):
                self.system_detector.cleanup()
        except Exception as e:
            print(f"清理资源时发生错误: {e}")
        finally:
            self.root.destroy()
            
    # ==================== 主控制台功能 ====================
    
    def start_frontend(self):
        """启动前端服务"""
        try:
            result = self.process_manager.start_frontend()
            if result.success:
                self.update_status(f"前端启动成功 (PID: {result.pid})")
                self.frontend_start_btn.config(state=tk.DISABLED)
                self.frontend_stop_btn.config(state=tk.NORMAL)
                self.frontend_status.config(text="运行中", foreground="green")
                # 开始监控日志
                process_obj = self.process_manager.process_objects.get('frontend')
                if process_obj:
                    self.log_monitor.start_monitoring('frontend', process_obj)
            else:
                messagebox.showerror("启动失败", result.error or result.message)
        except Exception as e:
            messagebox.showerror("错误", f"启动前端失败: {e}")
            
    def stop_frontend(self):
        """停止前端服务"""
        try:
            if self.process_manager.stop_process('frontend'):
                self.update_status("前端已停止")
                self.frontend_start_btn.config(state=tk.NORMAL)
                self.frontend_stop_btn.config(state=tk.DISABLED)
                self.frontend_status.config(text="已停止", foreground="red")
                self.log_monitor.stop_monitoring('frontend')
            else:
                messagebox.showerror("错误", "停止前端失败")
        except Exception as e:
            messagebox.showerror("错误", f"停止前端失败: {e}")
            
    def start_backend(self):
        """启动后端服务"""
        try:
            # 获取conda环境名称
            conda_env = self.config_manager.get_config('CONDA_ENV_NAME')
            result = self.process_manager.start_backend(conda_env)
            if result.success:
                self.update_status(f"后端启动成功 (PID: {result.pid})")
                self.backend_start_btn.config(state=tk.DISABLED)
                self.backend_stop_btn.config(state=tk.NORMAL)
                self.backend_status.config(text="运行中", foreground="green")
                # 开始监控日志
                process_obj = self.process_manager.process_objects.get('backend')
                if process_obj:
                    self.log_monitor.start_monitoring('backend', process_obj)
            else:
                messagebox.showerror("启动失败", result.error or result.message)
        except Exception as e:
            messagebox.showerror("错误", f"启动后端失败: {e}")
            
    def stop_backend(self):
        """停止后端服务"""
        try:
            if self.process_manager.stop_process('backend'):
                self.update_status("后端已停止")
                self.backend_start_btn.config(state=tk.NORMAL)
                self.backend_stop_btn.config(state=tk.DISABLED)
                self.backend_status.config(text="已停止", foreground="red")
                self.log_monitor.stop_monitoring('backend')
            else:
                messagebox.showerror("错误", "停止后端失败")
        except Exception as e:
            messagebox.showerror("错误", f"停止后端失败: {e}")
            
    def start_all(self):
        """一键启动全部服务"""
        self.start_backend()
        time.sleep(2)  # 等待后端启动
        self.start_frontend()
        
    def stop_all(self):
        """停止全部服务"""
        self.stop_frontend()
        self.stop_backend()
        
    def open_frontend(self):
        """打开前端页面"""
        import webbrowser
        port = self.config_manager.get_config('VITE_FRONTEND_PORT', '5173')
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        
    def open_backend(self):
        """打开后端API页面"""
        import webbrowser
        port = self.config_manager.get_config('BACKEND_PORT', '8483')
        url = f"http://localhost:{port}/docs"
        webbrowser.open(url)
        
    def open_project_dir(self):
        """打开项目目录"""
        import subprocess
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', str(Path.cwd())])
        else:  # Unix/Linux
            subprocess.run(['xdg-open', str(Path.cwd())])
            
    def refresh_status(self):
        """刷新状态显示"""
        self.update_status_display()
        
    def update_status_display(self):
        """更新状态显示"""
        try:
            # 清空现有项目
            for item in self.status_tree.get_children():
                self.status_tree.delete(item)
                
            # 获取进程状态
            all_status = self.process_manager.get_all_status()
            
            for service, status in all_status.items():
                if service in ['frontend', 'backend']:
                    self.status_tree.insert('', 'end', values=(
                        service.title(),
                        status.status,
                        status.pid or 'N/A',
                        status.port or 'N/A',
                        f"{status.cpu_percent:.1f}" if status.cpu_percent else 'N/A',
                        f"{status.memory_percent:.1f}" if status.memory_percent else 'N/A'
                    ))
        except Exception as e:
            print(f"更新状态显示失败: {e}")
            
    def schedule_status_update(self):
        """定时更新状态"""
        self.update_status_display()
        self.root.after(5000, self.schedule_status_update)  # 每5秒更新一次
        
    # ==================== 配置管理功能 ====================
    
    def create_port_config_tab(self, parent):
        """创建端口配置标签页"""
        # 端口配置框架
        config_frame = ttk.LabelFrame(parent, text="端口配置", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 端口配置项
        port_configs = [
            ('BACKEND_PORT', '后端端口'),
            ('FRONTEND_PORT', '前端端口(Docker)'),
            ('VITE_FRONTEND_PORT', 'Vite开发端口')
        ]
        
        self.port_vars = {}
        row = 0
        
        for key, label in port_configs:
            ttk.Label(config_frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            
            var = tk.StringVar(value=self.config_manager.get_config(key, ''))
            self.port_vars[key] = var
            
            entry = ttk.Entry(config_frame, textvariable=var, width=10)
            entry.grid(row=row, column=1, padx=5, pady=5)
            
            # 端口检查按钮
            check_btn = ttk.Button(config_frame, text="检查", 
                                 command=lambda k=key: self.check_port(k))
            check_btn.grid(row=row, column=2, padx=5, pady=5)
            
            row += 1
            
        # 按钮框架
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="保存端口配置", command=self.save_port_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_port_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="验证配置", command=self.validate_port_config).pack(side=tk.LEFT, padx=5)
        
    def create_env_editor_tab(self, parent):
        """创建.env文件编辑标签页"""
        # 工具栏
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Button(toolbar, text="重新加载", command=self.reload_env_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="保存文件", command=self.save_env_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="重置为默认", command=self.reset_env_file).pack(side=tk.LEFT, padx=5)
        
        # 文本编辑器
        editor_frame = ttk.LabelFrame(parent, text=".env文件内容", padding=5)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建文本框和滚动条
        self.env_text = tk.Text(editor_frame, wrap=tk.NONE, font=('Consolas', 10))
        
        v_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.env_text.yview)
        h_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.env_text.xview)
        
        self.env_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.env_text.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)
        
        # 加载.env文件内容
        self.load_env_content()
        
    def create_validation_tab(self, parent):
        """创建配置验证标签页"""
        # 验证按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="验证配置", command=self.run_config_validation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空结果", command=self.clear_validation_results).pack(side=tk.LEFT, padx=5)
        
        # 验证结果显示
        result_frame = ttk.LabelFrame(parent, text="验证结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.validation_text = tk.Text(result_frame, wrap=tk.WORD, height=20)
        validation_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.validation_text.yview)
        self.validation_text.configure(yscrollcommand=validation_scroll.set)
        
        self.validation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        validation_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def check_port(self, port_key):
        """检查端口可用性"""
        try:
            port_str = self.port_vars[port_key].get()
            if not port_str:
                messagebox.showwarning("警告", "请先输入端口号")
                return
                
            port = int(port_str)
            result = self.system_detector.check_port_availability(port)
            
            if result['available']:
                messagebox.showinfo("端口检查", f"端口 {port} 可用")
            else:
                occupied_info = result.get('occupied_by', {})
                msg = f"端口 {port} 已被占用\n\n"
                msg += f"进程ID: {occupied_info.get('pid', 'Unknown')}\n"
                msg += f"进程名: {occupied_info.get('name', 'Unknown')}\n"
                msg += f"状态: {occupied_info.get('status', 'Unknown')}"
                messagebox.showwarning("端口占用", msg)
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的端口号")
        except Exception as e:
            messagebox.showerror("错误", f"检查端口失败: {e}")
            
    def save_port_config(self):
        """保存端口配置"""
        try:
            # 收集端口配置
            port_config = {}
            for key, var in self.port_vars.items():
                value = var.get().strip()
                if value:
                    port_config[key] = value
                    
            # 验证端口配置
            ports_to_validate = {}
            for key, value in port_config.items():
                try:
                    ports_to_validate[key] = int(value)
                except ValueError:
                    messagebox.showerror("错误", f"{key} 的端口号格式不正确: {value}")
                    return
                    
            validation_result = self.config_manager.validate_port_config(ports_to_validate)
            
            if not validation_result.is_valid:
                error_msg = "端口配置验证失败:\n\n" + "\n".join(validation_result.errors)
                messagebox.showerror("验证失败", error_msg)
                return
                
            # 显示警告（如果有）
            if validation_result.warnings:
                warning_msg = "配置警告:\n\n" + "\n".join(validation_result.warnings)
                if not messagebox.askyesno("配置警告", warning_msg + "\n\n是否继续保存？"):
                    return
                    
            # 保存配置
            for key, value in port_config.items():
                self.config_manager.set_config(key, value)
                
            if self.config_manager.save_config():
                messagebox.showinfo("成功", "端口配置已保存")
                self.update_status("端口配置已更新")
            else:
                messagebox.showerror("错误", "保存配置失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存端口配置失败: {e}")
            
    def reset_port_config(self):
        """重置端口配置"""
        for key, var in self.port_vars.items():
            default_value = self.config_manager.config_definitions.get(key, {}).get('default_value', '')
            var.set(default_value)
            
    def validate_port_config(self):
        """验证端口配置"""
        try:
            ports_to_validate = {}
            for key, var in self.port_vars.items():
                value = var.get().strip()
                if value:
                    try:
                        ports_to_validate[key] = int(value)
                    except ValueError:
                        messagebox.showerror("错误", f"{key} 的端口号格式不正确: {value}")
                        return
                        
            validation_result = self.config_manager.validate_port_config(ports_to_validate)
            
            msg = "端口配置验证结果:\n\n"
            
            if validation_result.is_valid:
                msg += "✓ 配置有效\n\n"
            else:
                msg += "✗ 配置无效\n\n错误：\n"
                msg += "\n".join(f"- {error}" for error in validation_result.errors)
                msg += "\n\n"
                
            if validation_result.warnings:
                msg += "警告：\n"
                msg += "\n".join(f"- {warning}" for warning in validation_result.warnings)
                
            messagebox.showinfo("验证结果", msg)
            
        except Exception as e:
            messagebox.showerror("错误", f"验证配置失败: {e}")
            
    def load_env_content(self):
        """加载.env文件内容"""
        try:
            env_file = Path('.env')
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.env_text.delete(1.0, tk.END)
                self.env_text.insert(1.0, content)
            else:
                self.env_text.delete(1.0, tk.END)
                self.env_text.insert(1.0, "# .env文件不存在\n# 请先创建配置文件")
        except Exception as e:
            messagebox.showerror("错误", f"加载.env文件失败: {e}")
            
    def reload_env_file(self):
        """重新加载.env文件"""
        self.config_manager.load_config()
        self.load_env_content()
        self.update_status(".env文件已重新加载")
        
    def save_env_file(self):
        """保存.env文件"""
        try:
            content = self.env_text.get(1.0, tk.END)
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 重新加载配置
            self.config_manager.load_config()
            messagebox.showinfo("成功", ".env文件已保存")
            self.update_status(".env文件已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存.env文件失败: {e}")
            
    def reset_env_file(self):
        """重置.env文件为默认配置"""
        if messagebox.askyesno("确认", "确定要重置.env文件为默认配置吗？\n\n当前配置将被覆盖！"):
            try:
                if self.config_manager.reset_to_default():
                    self.load_env_content()
                    messagebox.showinfo("成功", ".env文件已重置为默认配置")
                    self.update_status(".env文件已重置")
                else:
                    messagebox.showerror("错误", "重置.env文件失败")
            except Exception as e:
                messagebox.showerror("错误", f"重置.env文件失败: {e}")
                
    def run_config_validation(self):
        """运行配置验证"""
        try:
            self.validation_text.delete(1.0, tk.END)
            
            # 验证当前配置
            validation_result = self.config_manager.validate_config()
            
            result_text = "=== 配置验证结果 ===\n\n"
            
            if validation_result.is_valid:
                result_text += "✓ 配置验证通过\n\n"
            else:
                result_text += "✗ 配置验证失败\n\n"
                result_text += "错误列表：\n"
                for error in validation_result.errors:
                    result_text += f"  - {error}\n"
                result_text += "\n"
                
            if validation_result.warnings:
                result_text += "警告列表：\n"
                for warning in validation_result.warnings:
                    result_text += f"  - {warning}\n"
                result_text += "\n"
                
            # 添加配置项检查
            result_text += "=== 配置项检查 ===\n\n"
            config_definitions = self.config_manager.get_config_definitions()
            current_config = self.config_manager.get_all_config()
            
            for key, definition in config_definitions.items():
                current_value = current_config.get(key, '')
                result_text += f"{key}:\n"
                result_text += f"  当前值: {current_value or '(未设置)'}\n"
                result_text += f"  默认值: {definition.default_value}\n"
                result_text += f"  描述: {definition.description}\n"
                result_text += f"  必需: {'是' if definition.is_required else '否'}\n\n"
                
            self.validation_text.insert(1.0, result_text)
            
        except Exception as e:
            error_text = f"配置验证失败: {e}"
            self.validation_text.insert(1.0, error_text)
            
    def clear_validation_results(self):
        """清空验证结果"""
        self.validation_text.delete(1.0, tk.END)
        
    # ==================== 日志监控功能 ====================
    
    def create_log_display(self, parent, service):
        """创建日志显示区域"""
        # 创建文本框和滚动条
        log_text = tk.Text(parent, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 存储文本框引用
        if not hasattr(self, 'log_displays'):
            self.log_displays = {}
        self.log_displays[service] = log_text
        
        # 添加日志回调
        self.log_monitor.add_log_callback(self.on_log_update)
        
    def on_log_update(self, service, entry):
        """日志更新回调"""
        try:
            if hasattr(self, 'log_displays') and service in self.log_displays:
                log_text = self.log_displays[service]
                
                # 检查日志级别过滤
                if hasattr(self, 'log_level_var'):
                    selected_level = self.log_level_var.get()
                    if selected_level != "全部" and entry.level != selected_level:
                        return
                        
                # 格式化日志条目
                timestamp = entry.timestamp.strftime('%H:%M:%S')
                log_line = f"[{timestamp}] [{entry.level}] {entry.message}\n"
                
                # 添加到文本框
                log_text.insert(tk.END, log_line)
                
                # 根据日志级别设置颜色
                if entry.level == 'ERROR':
                    log_text.tag_add('error', f"end-{len(log_line)}c", 'end')
                    log_text.tag_config('error', foreground='red')
                elif entry.level == 'WARNING':
                    log_text.tag_add('warning', f"end-{len(log_line)}c", 'end')
                    log_text.tag_config('warning', foreground='orange')
                elif entry.level == 'DEBUG':
                    log_text.tag_add('debug', f"end-{len(log_line)}c", 'end')
                    log_text.tag_config('debug', foreground='gray')
                    
                # 自动滚动到底部
                log_text.see(tk.END)
                
                # 限制行数
                lines = log_text.get(1.0, tk.END).count('\n')
                if lines > 1000:
                    log_text.delete(1.0, '100.0')
                    
        except Exception as e:
            print(f"更新日志显示失败: {e}")
            
    def clear_logs(self):
        """清空日志"""
        try:
            if hasattr(self, 'log_displays'):
                for service, log_text in self.log_displays.items():
                    log_text.delete(1.0, tk.END)
                    self.log_monitor.clear_logs(service)
            self.update_status("日志已清空")
        except Exception as e:
            messagebox.showerror("错误", f"清空日志失败: {e}")
            
    def export_logs(self):
        """导出日志"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                title="导出日志"
            )
            
            if filename:
                # 这里可以选择导出哪个服务的日志
                service = "frontend"  # 默认导出前端日志
                if self.log_monitor.export_logs(service, filename):
                    messagebox.showinfo("成功", f"日志已导出到: {filename}")
                else:
                    messagebox.showerror("错误", "导出日志失败")
                    
        except Exception as e:
            messagebox.showerror("错误", f"导出日志失败: {e}")
            
    def refresh_logs(self):
        """刷新日志显示"""
        try:
            if hasattr(self, 'log_displays'):
                for service, log_text in self.log_displays.items():
                    log_text.delete(1.0, tk.END)
                    
                    # 重新加载日志
                    logs = self.log_monitor.get_logs(service, 100)  # 获取最近100条
                    for entry in logs:
                        self.on_log_update(service, entry)
                        
            self.update_status("日志已刷新")
        except Exception as e:
            messagebox.showerror("错误", f"刷新日志失败: {e}")
            
    # ==================== 系统信息功能 ====================
    
    def create_dependencies_tab(self, parent):
        """创建依赖检查标签页"""
        # 刷新按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="检查依赖", command=self.check_dependencies).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=self.refresh_dependencies).pack(side=tk.LEFT, padx=5)
        
        # 依赖列表
        deps_frame = ttk.LabelFrame(parent, text="依赖状态", padding=10)
        deps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ('名称', '状态', '版本', '路径', '描述')
        self.deps_tree = ttk.Treeview(deps_frame, columns=columns, show='headings')
        
        for col in columns:
            self.deps_tree.heading(col, text=col)
            
        self.deps_tree.column('名称', width=100)
        self.deps_tree.column('状态', width=80)
        self.deps_tree.column('版本', width=100)
        self.deps_tree.column('路径', width=200)
        self.deps_tree.column('描述', width=150)
        
        deps_scrollbar = ttk.Scrollbar(deps_frame, orient=tk.VERTICAL, command=self.deps_tree.yview)
        self.deps_tree.configure(yscrollcommand=deps_scrollbar.set)
        
        self.deps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        deps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始检查
        self.check_dependencies()
        
    def create_resources_tab(self, parent):
        """创建系统资源标签页"""
        # 刷新按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="刷新资源信息", command=self.refresh_resources).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="系统诊断", command=self.run_system_diagnosis).pack(side=tk.LEFT, padx=5)
        
        # 资源信息显示
        info_frame = ttk.LabelFrame(parent, text="系统资源", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.resources_text = tk.Text(info_frame, wrap=tk.WORD, height=20, font=('Consolas', 10))
        resources_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.resources_text.yview)
        self.resources_text.configure(yscrollcommand=resources_scroll.set)
        
        self.resources_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        resources_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始加载
        self.refresh_resources()
        
    def create_structure_tab(self, parent):
        """创建项目结构标签页"""
        # 刷新按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="检查项目结构", command=self.check_project_structure).pack(side=tk.LEFT, padx=5)
        
        # 结构检查结果
        structure_frame = ttk.LabelFrame(parent, text="项目结构检查", padding=10)
        structure_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ('项目', '状态', '说明')
        self.structure_tree = ttk.Treeview(structure_frame, columns=columns, show='headings')
        
        for col in columns:
            self.structure_tree.heading(col, text=col)
            
        self.structure_tree.column('项目', width=200)
        self.structure_tree.column('状态', width=100)
        self.structure_tree.column('说明', width=300)
        
        structure_scroll = ttk.Scrollbar(structure_frame, orient=tk.VERTICAL, command=self.structure_tree.yview)
        self.structure_tree.configure(yscrollcommand=structure_scroll.set)
        
        self.structure_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        structure_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始检查
        self.check_project_structure()
        
    def check_dependencies(self):
        """检查依赖"""
        try:
            # 清空现有项目
            for item in self.deps_tree.get_children():
                self.deps_tree.delete(item)
                
            dependencies = self.system_detector.check_dependencies()
            
            for dep in dependencies:
                status_text = "✓ 已安装" if dep.is_installed else "✗ 未安装"
                status_color = "green" if dep.is_installed else "red"
                
                item = self.deps_tree.insert('', 'end', values=(
                    dep.name,
                    status_text,
                    dep.version or 'N/A',
                    dep.install_path or 'N/A',
                    dep.description
                ))
                
                # 设置颜色标签
                if not dep.is_installed:
                    self.deps_tree.set(item, '状态', '✗ 未安装')
                    
        except Exception as e:
            messagebox.showerror("错误", f"检查依赖失败: {e}")
            
    def refresh_dependencies(self):
        """刷新依赖检查"""
        self.check_dependencies()
        self.update_status("依赖检查已刷新")
        
    def refresh_resources(self):
        """刷新系统资源信息"""
        try:
            self.resources_text.delete(1.0, tk.END)
            
            # 获取系统信息
            system_info = self.system_detector.get_system_info()
            resources = self.system_detector.get_system_resources()
            
            info_text = "=== 系统信息 ===\n\n"
            for key, value in system_info.items():
                info_text += f"{key}: {value}\n"
                
            info_text += "\n=== 系统资源 ===\n\n"
            info_text += f"CPU使用率: {resources.cpu_usage:.1f}%\n"
            info_text += f"内存使用率: {resources.memory_usage:.1f}%\n"
            info_text += f"内存总量: {resources.memory_total:.1f} GB\n"
            info_text += f"可用内存: {resources.memory_available:.1f} GB\n"
            info_text += f"磁盘使用率: {resources.disk_usage:.1f}%\n"
            info_text += f"磁盘总量: {resources.disk_total:.1f} GB\n"
            info_text += f"磁盘可用: {resources.disk_free:.1f} GB\n"
            info_text += f"网络状态: {'正常' if resources.network_status else '异常'}\n"
            info_text += f"系统运行时间: {resources.uptime/3600:.1f} 小时\n"
            
            self.resources_text.insert(1.0, info_text)
            
        except Exception as e:
            error_text = f"获取系统资源信息失败: {e}"
            self.resources_text.insert(1.0, error_text)
            
    def run_system_diagnosis(self):
        """运行系统诊断"""
        try:
            diagnosis = self.system_detector.diagnose_system()
            
            diag_text = "\n\n=== 系统诊断结果 ===\n\n"
            
            if diagnosis['errors']:
                diag_text += "❌ 错误：\n"
                for error in diagnosis['errors']:
                    diag_text += f"  - {error}\n"
                diag_text += "\n"
                
            if diagnosis['warnings']:
                diag_text += "⚠️ 警告：\n"
                for warning in diagnosis['warnings']:
                    diag_text += f"  - {warning}\n"
                diag_text += "\n"
                
            if diagnosis['suggestions']:
                diag_text += "💡 建议：\n"
                for suggestion in diagnosis['suggestions']:
                    diag_text += f"  - {suggestion}\n"
                diag_text += "\n"
                
            if not any(diagnosis.values()):
                diag_text += "✅ 系统状态良好，未发现问题\n"
                
            self.resources_text.insert(tk.END, diag_text)
            self.resources_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("错误", f"系统诊断失败: {e}")
            
    def check_project_structure(self):
        """检查项目结构"""
        try:
            # 清空现有项目
            for item in self.structure_tree.get_children():
                self.structure_tree.delete(item)
                
            structure = self.system_detector.check_project_structure()
            
            for name, exists in structure.items():
                status_text = "✓ 存在" if exists else "✗ 缺失"
                description = "正常" if exists else "需要检查"
                
                self.structure_tree.insert('', 'end', values=(
                    name,
                    status_text,
                    description
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"检查项目结构失败: {e}")

def main():
    """主函数"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 6):
            print("错误：需要Python 3.6或更高版本")
            sys.exit(1)
            
        # 检查是否在正确的目录中运行
        if not os.path.exists("backend") or not os.path.exists("BillNote_frontend"):
            print("错误：请在BiliNote项目根目录中运行此程序")
            sys.exit(1)
            
        # 创建并运行GUI应用程序
        app = BiliNoteGUILauncher()
        app.run()
        
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()