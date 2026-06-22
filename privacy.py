#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

class PersistentPrivacyShield:
    def __init__(self, root):
        self.root = root
        self.root.title("Ironclad Stealth Guard v3.0")
        self.root.geometry("520x600")
        self.root.configure(bg="#0F111A")
        
        self.blacklist_dir = "/etc/modprobe.d"
        self.targets = {
            "Camera": {"mod": "uvcvideo", "dev": "/dev/video*", "conf": "camera_privacy.conf"},
            "Bluetooth": {"mod": "btusb", "dev": "/dev/input/event*", "conf": "bluetooth_privacy.conf"}
        }

        self.validate_environment()
        self.setup_ui()
        self.refresh_ui()

    def validate_environment(self):
        """Pre-flight check to ensure the system supports this tool."""
        missing = []
        for cmd in ["pkexec", "modprobe", "fuser"]:
            if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
                missing.append(cmd)
        
        if missing:
            messagebox.showerror("System Error", f"Missing critical components: {', '.join(missing)}\nAborting.")
            sys.exit(1)

    def get_blocker_info(self, dev_path):
        """Identifies the specific app preventing the hardware from being disabled."""
        if not dev_path or not any(os.path.exists(d) for d in [dev_path.replace('*', '0')]):
            return None
        try:
            # Get PIDs using the device
            pid_out = subprocess.check_output(["fuser", dev_path], stderr=subprocess.DEVNULL).decode().strip()
            if pid_out:
                pids = pid_out.split()
                # Get the names of the processes
                names = [subprocess.check_output(["ps", "-p", p, "-o", "comm="]).decode().strip() for p in pids]
                return ", ".join(set(names))
        except:
            return None
        return None

    def run_safe_cmd(self, cmd_string):
        """Centralized execution engine with environment syncing and logging."""
        env = os.environ.copy()
        env["DISPLAY"] = os.environ.get("DISPLAY", ":0")
        env["XAUTHORITY"] = os.environ.get("XAUTHORITY", "")
        
        full_cmd = ["pkexec", "bash", "-c", cmd_string]
        try:
            # We don't hide the output anymore to ensure the user sees error messages
            result = subprocess.run(full_cmd, check=True, env=env, capture_output=True, text=True)
            return True, ""
        except subprocess.CalledProcessError as e:
            # Catch 'Module Not Found' or 'Busy' error
            err_msg = e.stderr.strip() if e.stderr else "Unknown Authentication Error"
            return False, err_msg
        except Exception as e:
            return False, str(e)

    def is_blacklisted(self, conf_name):
        return os.path.exists(os.path.join(self.blacklist_dir, conf_name))

    def is_loaded(self, module):
        try:
            with open('/proc/modules', 'r') as f:
                return module in f.read()
        except:
            return False

    def toggle(self, label, module, dev, conf):
        loaded = self.is_loaded(module)
        conf_path = os.path.join(self.blacklist_dir, conf)
        
        # Phase 1: Pre-Check (Who is using it?)
        if loaded:
            blockers = self.get_blocker_info(dev)
            if blockers:
                ans = messagebox.askyesno("Device Busy", f"Apps currently using {label}: {blockers}.\n\nForce kill these apps and disable?")
                if not ans: return
                # Kill apps immediately to clear the lock
                self.run_safe_cmd(f"fuser -k {dev}")

        # Phase 2: Execution Logic
        if loaded:
            cmd = f"echo 'blacklist {module}' > {conf_path} && modprobe -rf {module}"
            action_desc = "Disable"
        else:
            cmd = f"rm -f {conf_path} && modprobe {module}"
            action_desc = "Enable"

        # Phase 3: Final Execution with Error Reporting
        success, error = self.run_safe_cmd(cmd)
        
        if success:
            # Re-verify the state directly in the kernel after action
            if self.is_loaded(module) == loaded:
                messagebox.showwarning("State Mismatch", f"Kernel command was sent but {label} did not {action_desc}.\nTry rebooting.")
            self.refresh_ui()
        else:
            # Detect the 'Fatal' Kernel Error
            if "not found" in error:
                messagebox.showerror("Kernel Out of Sync", f"Critical Error: {error}\n\nYour kernel was updated recently but you haven't rebooted. Reboot now to sync.")
            else:
                messagebox.showerror("Action Denied", f"System failed to {action_desc} hardware.\n\nDetails: {error}")

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#1A1C25", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="IRONCLAD PRIVACY GUARD", font=("Arial", 16, "bold"), 
                 bg="#1A1C25", fg="#00F2FF").pack(pady=25)

        self.content = tk.Frame(self.root, bg="#0F111A", padx=30, pady=20)
        self.content.pack(fill="both", expand=True)

    def refresh_ui(self):
        for widget in self.content.winfo_children(): widget.destroy()

        for label, data in self.targets.items():
            mod, dev, conf = data['mod'], data['dev'], data['conf']
            loaded = self.is_loaded(mod)
            blacklisted = self.is_blacklisted(conf)
            
            card = tk.Frame(self.content, bg="#1A1C25", padx=20, pady=25, 
                            highlightthickness=1, highlightbackground="#2D2F39")
            card.pack(fill="x", pady=10)

            txt_frame = tk.Frame(card, bg="#1A1C25")
            txt_frame.pack(side="left")

            tk.Label(txt_frame, text=label.upper(), font=("Arial", 12, "bold"), 
                     bg="#1A1C25", fg="white").pack(anchor="w")

            # Final status logic with persistent indicator
            if not loaded and blacklisted:
                status, color = "○ SECURE (BOOT PROTECTED)", "#00FF9D"
            elif loaded:
                status, color = "● EXPOSED (LIVE)", "#FF3366"
            else:
                status, color = "○ SECURE (TEMPORARY)", "#00F2FF"
            
            tk.Label(txt_frame, text=status, font=("Arial", 9, "bold"), 
                     bg="#1A1C25", fg=color).pack(anchor="w", pady=4)

            btn_text = "DISABLE" if loaded else "ENABLE"
            btn_color = "#FF3366" if loaded else "#00F2FF"
            
            tk.Button(card, text=btn_text, font=("Arial", 10, "bold"),
                      bg=btn_color, fg="#0F111A", width=12, relief="flat", cursor="hand2", 
                      command=lambda l=label, m=mod, d=dev, c=conf: self.toggle(l, m, d, c)).pack(side="right")

        tk.Label(self.root, text=f"Kernel: {os.uname().release} | Persistence Active", font=("Arial", 8), 
                 bg="#0F111A", fg="#454955").pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = PersistentPrivacyShield(root)
    root.mainloop()
