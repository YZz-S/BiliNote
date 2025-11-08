#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块测试脚本
用于验证GUI启动器的各个模块是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加modules目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from process_manager import ProcessManager
        print("✓ ProcessManager 导入成功")
    except ImportError as e:
        print(f"✗ ProcessManager 导入失败: {e}")
        return False
        
    try:
        from config_manager import ConfigManager
        print("✓ ConfigManager 导入成功")
    except ImportError as e:
        print(f"✗ ConfigManager 导入失败: {e}")
        return False
        
    try:
        from log_monitor import LogMonitor
        print("✓ LogMonitor 导入成功")
    except ImportError as e:
        print(f"✗ LogMonitor 导入失败: {e}")
        return False
        
    try:
        from system_detector import SystemDetector
        print("✓ SystemDetector 导入成功")
    except ImportError as e:
        print(f"✗ SystemDetector 导入失败: {e}")
        return False
        
    return True

def test_config_manager():
    """测试配置管理器"""
    print("\n=== 测试配置管理器 ===")
    
    try:
        from config_manager import ConfigManager
        
        config_manager = ConfigManager()
        print("✓ ConfigManager 实例化成功")
        
        # 测试配置读取
        all_config = config_manager.get_all_config()
        print(f"✓ 读取到 {len(all_config)} 个配置项")
        
        # 测试配置验证
        validation_result = config_manager.validate_config()
        print(f"✓ 配置验证完成，有效性: {validation_result.is_valid}")
        
        if validation_result.errors:
            print(f"  错误: {len(validation_result.errors)} 个")
        if validation_result.warnings:
            print(f"  警告: {len(validation_result.warnings)} 个")
            
        return True
        
    except Exception as e:
        print(f"✗ ConfigManager 测试失败: {e}")
        return False

def test_system_detector():
    """测试系统检测器"""
    print("\n=== 测试系统检测器 ===")
    
    try:
        from system_detector import SystemDetector
        
        detector = SystemDetector()
        print("✓ SystemDetector 实例化成功")
        
        # 测试依赖检查
        dependencies = detector.check_dependencies()
        print(f"✓ 检查到 {len(dependencies)} 个依赖")
        
        for dep in dependencies:
            status = "已安装" if dep.is_installed else "未安装"
            print(f"  {dep.name}: {status} ({dep.version})")
            
        # 测试系统资源
        resources = detector.get_system_resources()
        print(f"✓ 系统资源检查完成")
        print(f"  CPU使用率: {resources.cpu_usage:.1f}%")
        print(f"  内存使用率: {resources.memory_usage:.1f}%")
        
        # 测试项目结构
        structure = detector.check_project_structure()
        print(f"✓ 项目结构检查完成")
        
        missing_items = [name for name, exists in structure.items() if not exists]
        if missing_items:
            print(f"  缺失项目: {', '.join(missing_items)}")
        else:
            print("  项目结构完整")
            
        return True
        
    except Exception as e:
        print(f"✗ SystemDetector 测试失败: {e}")
        return False

def test_process_manager():
    """测试进程管理器"""
    print("\n=== 测试进程管理器 ===")
    
    try:
        from process_manager import ProcessManager
        
        process_manager = ProcessManager()
        print("✓ ProcessManager 实例化成功")
        
        # 测试进程状态获取
        all_status = process_manager.get_all_status()
        print(f"✓ 获取到 {len(all_status)} 个服务状态")
        
        for service, status in all_status.items():
            print(f"  {service}: {status.status}")
            
        # 测试端口检查
        port_info = process_manager.get_port_info(8483)
        if port_info.get('occupied'):
            print(f"  端口8483被占用: PID {port_info.get('pid')}")
        else:
            print("  端口8483可用")
            
        return True
        
    except Exception as e:
        print(f"✗ ProcessManager 测试失败: {e}")
        return False

def test_log_monitor():
    """测试日志监控器"""
    print("\n=== 测试日志监控器 ===")
    
    try:
        from log_monitor import LogMonitor
        
        log_monitor = LogMonitor()
        print("✓ LogMonitor 实例化成功")
        
        # 测试添加系统日志
        log_monitor.add_system_log("测试日志消息", "INFO")
        print("✓ 添加系统日志成功")
        
        # 测试获取日志
        logs = log_monitor.get_logs('system')
        print(f"✓ 获取到 {len(logs)} 条系统日志")
        
        # 测试日志统计
        stats = log_monitor.get_log_statistics('system')
        print(f"✓ 日志统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ LogMonitor 测试失败: {e}")
        return False

def test_gui_basic():
    """测试GUI基本功能"""
    print("\n=== 测试GUI基本功能 ===")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 创建测试窗口
        root = tk.Tk()
        root.title("GUI测试")
        root.geometry("300x200")
        
        # 添加测试组件
        label = ttk.Label(root, text="GUI组件测试成功")
        label.pack(pady=20)
        
        button = ttk.Button(root, text="关闭", command=root.destroy)
        button.pack(pady=10)
        
        print("✓ GUI组件创建成功")
        
        # 立即关闭窗口
        root.after(100, root.destroy)
        root.mainloop()
        
        print("✓ GUI事件循环测试成功")
        return True
        
    except Exception as e:
        print(f"✗ GUI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("BiliNote GUI启动器模块测试")
    print("=" * 50)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {Path.cwd()}")
    print()
    
    # 运行所有测试
    tests = [
        test_imports,
        test_config_manager,
        test_system_detector,
        test_process_manager,
        test_log_monitor,
        test_gui_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！GUI启动器准备就绪。")
        return True
    else:
        print("❌ 部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)