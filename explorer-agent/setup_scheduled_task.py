"""
定时任务设置脚本
为Windows或Linux设置每日自动运行探索任务
"""

import os
import sys
import subprocess
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def setup_windows_scheduled_task():
    """设置Windows定时任务"""

    # 获取脚本路径
    script_dir = Path(__file__).parent.absolute()
    python_script = script_dir / "automated_exploration.py"
    log_file = script_dir / "logs" / "scheduled_run.log"

    # 创建日志目录
    log_file.parent.mkdir(exist_ok=True)

    # 任务名称
    task_name = "ExplorerAgent_DailyExploration"

    # PowerShell命令
    ps_command = f'''
$action = New-ScheduledTaskAction -Execute "python" -Argument "{python_script}" -WorkingDirectory "{script_dir}"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
$principal = New-ScheduledTaskPrincipal -UserId "$ENV:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
'''

    print("=" * 80)
    print("设置Windows定时任务")
    print("=" * 80)
    print(f"\n任务名称: {task_name}")
    print(f"运行时间: 每天凌晨 2:00")
    print(f"脚本位置: {python_script}")
    print(f"工作目录: {script_dir}\n")

    print("正在创建任务...")
    print("注意: 需要管理员权限\n")

    try:
        # 保存PowerShell脚本到临时文件
        temp_ps = Path.cwd() / "temp_task_setup.ps1"
        with open(temp_ps, 'w', encoding='utf-8') as f:
            f.write(ps_command)

        # 执行PowerShell命令
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(temp_ps)],
            capture_output=True,
            text=True
        )

        # 删除临时文件
        temp_ps.unlink()

        if result.returncode == 0:
            print("✅ Windows定时任务创建成功!\n")
            print("你可以通过以下方式查看/修改任务:")
            print("1. 打开 '任务计划程序' (Task Scheduler)")
            print(f"2. 找到任务 '{task_name}'")
            print("3. 右键可以修改运行时间、查看历史等\n")

            # 显示手动运行命令
            print("或者手动运行:")
            print(f"  python {python_script}\n")
        else:
            print("❌ 创建任务失败:")
            print(result.stderr)
            print("\n请尝试手动设置:")
            print("1. 打开 '任务计划程序'")
            print("2. 创建基本任务")
            print(f"3. 程序或脚本: python")
            print(f"4. 参数: {python_script}")
            print(f"5. 起始于: {script_dir}\n")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n请手动设置定时任务:")
        print("1. 打开 '任务计划程序'")
        print("2. 创建基本任务")
        print(f"3. 程序: python")
        print(f"4. 参数: {python_script}")
        print(f"5. 起始于: {script_dir}")


def setup_linux_cron():
    """设置Linux cron定时任务"""

    script_dir = Path(__file__).parent.absolute()
    python_script = script_dir / "automated_exploration.py"
    log_file = script_dir / "logs" / "scheduled_run.log"

    log_file.parent.mkdir(exist_ok=True)

    print("=" * 80)
    print("设置Linux Cron定时任务")
    print("=" * 80)
    print(f"\n脚本位置: {python_script}")
    print(f"日志文件: {log_file}")
    print("运行时间: 每天凌晨 2:00\n")

    # Cron命令
    cron_command = f"0 2 * * * cd {script_dir} && /usr/bin/python3 {python_script} >> {log_file} 2>&1"

    print("请执行以下命令来设置cron任务:")
    print("\n1. 打开crontab:")
    print("   crontab -e")
    print("\n2. 添加以下行:")
    print(f"   {cron_command}")
    print("\n3. 保存退出\n")

    # 尝试自动添加
    try:
        # 获取当前crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        # 检查是否已存在
        if "automated_exploration.py" in current_cron:
            print("⚠️ Cron任务已存在，无需重复添加\n")
        else:
            # 添加新的cron任务
            new_cron = current_cron.strip() + "\n" + cron_command + "\n"
            subprocess.run(
                ["crontab", "-"],
                input=new_cron,
                text=True
            )
            print("✅ Cron任务已自动添加!\n")

    except Exception as e:
        print(f"⚠️ 自动添加失败: {e}")
        print("请按照上面的说明手动添加\n")

    print("查看cron任务:")
    print("  crontab -l")
    print("\n删除cron任务:")
    print("  crontab -e  # 然后删除对应行\n")


def show_manual_instructions():
    """显示手动运行说明"""
    script_dir = Path(__file__).parent.absolute()
    python_script = script_dir / "automated_exploration.py"

    print("=" * 80)
    print("手动运行说明")
    print("=" * 80)
    print("\n如果不使用定时任务，可以手动运行:\n")

    if sys.platform == 'win32':
        print("Windows:")
        print(f"  cd {script_dir}")
        print(f"  python {python_script}")
        print("\n或创建.bat文件:")
        print(f"  @echo off")
        print(f"  cd /d {script_dir}")
        print(f"  python {python_script}")
        print(f"  pause\n")
    else:
        print("Linux/Mac:")
        print(f"  cd {script_dir}")
        print(f"  python3 {python_script}")
        print("\n或创建shell脚本:")
        print(f"  #!/bin/bash")
        print(f"  cd {script_dir}")
        print(f"  python3 {python_script}\n")


def main():
    print("\n🕐 Explorer Agent - 定时任务设置")
    print("=" * 80)
    print()

    # 检测操作系统
    if sys.platform == 'win32':
        print("检测到Windows系统\n")

        print("请选择:")
        print("1. 自动创建Windows定时任务 (推荐)")
        print("2. 查看手动设置说明")
        print("3. 跳过\n")

        choice = input("请输入选项 (1-3): ").strip()

        if choice == "1":
            setup_windows_scheduled_task()
        elif choice == "2":
            show_manual_instructions()
        else:
            print("已跳过定时任务设置\n")
    else:
        print("检测到Linux/Mac系统\n")
        setup_linux_cron()
        show_manual_instructions()

    print("=" * 80)
    print("设置完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
