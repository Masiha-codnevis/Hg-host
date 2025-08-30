#!/usr/bin/env python3
import platform
import subprocess
import os
import sys

def run_command(command, sudo=False):
    """اجرا کردن دستورات شل با مدیریت خطاها"""
    try:
        if sudo:
            command = f"sudo {command}"
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"خطا در اجرای دستور {command}: {e.stderr}")
        sys.exit(1)

def detect_os():
    """تشخیص سیستم‌عامل"""
    os_type = platform.system().lower()
    if os_type == "linux":
        distro = platform.linux_distribution()[0].lower() if hasattr(platform, 'linux_distribution') else run_command("cat /etc/os-release").lower()
        if "ubuntu" in distro or "debian" in distro:
            return "debian"
        elif "centos" in distro or "rhel" in distro or "fedora" in distro:
            return "redhat"
        else:
            return "unknown"
    return "unknown"

def install_tmate(os_type):
    """نصب tmate بر اساس نوع سیستم‌عامل"""
    print(f"سیستم‌عامل تشخیص داده‌شده: {os_type}")
    if os_type == "debian":
        print("به‌روزرسانی بسته‌ها و نصب tmate در سیستم‌های مبتنی بر دبیان...")
        run_command("apt update", sudo=True)
        run_command("apt install -y tmate", sudo=True)
    elif os_type == "redhat":
        print("نصب tmate در سیستم‌های مبتنی بر Red Hat...")
        run_command("yum install -y epel-release", sudo=True)
        run_command("yum install -y tmate", sudo=True)
    else:
        print("سیستم‌عامل پشتیبانی‌نشده است. لطفاً tmate را به صورت دستی نصب کنید.")
        sys.exit(1)

def start_tmate():
    """اجرای tmate و گرفتن لینک SSH"""
    try:
        print("اجرای tmate...")
        # اجرای tmate در پس‌زمینه و گرفتن خروجی
        process = subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.wait(timeout=5)  # منتظر آماده شدن tmate
        
        # گرفتن لینک SSH
        ssh_link = run_command("tmate -S /tmp/tmate.sock display -p '#{tmate_ssh}'")
        print(f"لینک SSH برای اتصال: {ssh_link.strip()}")
        return ssh_link.strip()
    except Exception as e:
        print(f"خطا در اجرای tmate: {e}")
        sys.exit(1)

def main():
    # تشخیص سیستم‌عامل
    os_type = detect_os()
    if os_type == "unknown":
        print("نمی‌توان سیستم‌عامل را تشخیص داد.")
        sys.exit(1)
    
    # نصب tmate
    install_tmate(os_type)
    
    # اجرای tmate و نمایش لینک SSH
    ssh_link = start_tmate()
    
    # نگه داشتن اسکریپت تا وقتی کاربر بخواد (برای نگه داشتن جلسه tmate)
    print("برای خروج Ctrl+C را فشار دهید...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nخروج از برنامه و بستن جلسه tmate...")
        run_command("tmate -S /tmp/tmate.sock kill-session")

if __name__ == "__main__":
    main()
