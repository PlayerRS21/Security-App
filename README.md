# 🛡️ Security-App - Ironclad Privacy Guard

A powerful Linux privacy protection tool that gives you control over your hardware's access permissions. Disable camera, Bluetooth, and other sensitive hardware devices with a sleek, intuitive GUI.

## 📋 Overview

**Ironclad Privacy Guard** is a system-level privacy application designed for Linux users who want granular control over their hardware devices. It provides both temporary and persistent (boot-protected) device disabling capabilities through an easy-to-use graphical interface.

### Key Features

- **Hardware Device Control**: Safely disable/enable camera and Bluetooth devices
- **Persistent Protection**: Boot-protected device blacklisting that survives system reboots
- **Smart Process Detection**: Identifies which applications are using your devices
- **Safe Kernel Synchronization**: Handles kernel module operations with error recovery
- **Modern UI**: Dark-themed, responsive interface with real-time status indicators
- **Privilege Escalation**: Uses `pkexec` for secure administrator operations
- **Live Status Feedback**: Visual indicators show device state (EXPOSED/SECURE)

## 🚀 Getting Started

### Prerequisites

- **OS**: Linux (Fedora, Ubuntu, Debian, or other distributions)
- **Python**: Python 3.6 or higher
- **Required System Commands**:
  - `pkexec` - PolicyKit authorization tool
  - `modprobe` - Kernel module management
  - `fuser` - File and process identification
  - `ps` - Process status monitoring

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/PlayerRS21/Security-App.git
   cd Security-App
   ```

2. **Verify Prerequisites**
   The application will automatically check for required system commands on startup. Ensure you have:
   ```bash
   which pkexec
   which modprobe
   which fuser
   ```

3. **Make Executable** (Optional)
   ```bash
   chmod +x privacy.py
   ```

### Usage

Run the application with:

```bash
python3 privacy.py
```

Or directly:
```bash
./privacy.py
```

#### Granting Permissions

When prompted, authenticate with your administrator password. The application uses `pkexec` for secure privilege escalation.

## 🎨 User Interface

### Main Window
- **Title**: Ironclad Privacy Guard v3.0
- **Theme**: Dark mode with cyan and red accents
- **Window Size**: 520x600 pixels

### Device Cards

Each device has a card displaying:
- **Device Name**: CAMERA or BLUETOOTH
- **Status Indicator**:
  - 🔴 **EXPOSED (LIVE)** - Device is active and accessible
  - 🔵 **SECURE (TEMPORARY)** - Device is disabled for this session
  - 🟢 **SECURE (BOOT PROTECTED)** - Device is disabled and blacklisted
- **Control Button**: ENABLE or DISABLE action button

### Actions

**Disable a Device**:
1. Click the DISABLE button for the target device
2. If applications are using the device, you'll be prompted to force-kill them
3. Confirm the action
4. Device is immediately disabled and optionally blacklisted

**Enable a Device**:
1. Click the ENABLE button
2. Confirm the action
3. Device becomes available again

## ⚙️ Technical Details

### Architecture

```
PersistentPrivacyShield
├── validate_environment()      # Pre-flight system checks
├── setup_ui()                  # Initialize GUI
├── toggle()                    # Main device control logic
├── run_safe_cmd()             # Safe command execution with error handling
├── is_loaded()                # Check kernel module status
├── is_blacklisted()           # Check persistence configuration
├── get_blocker_info()         # Identify apps using devices
└── refresh_ui()               # Update UI with current states
```

### Supported Devices

| Device | Module | Device Path | Config File |
|--------|--------|-------------|------------|
| Camera | `uvcvideo` | `/dev/video*` | `camera_privacy.conf` |
| Bluetooth | `btusb` | `/dev/input/event*` | `bluetooth_privacy.conf` |

### Kernel Module Operations

The tool manages kernel modules through:
- **Disabling**: Creates blacklist config + unloads module
- **Enabling**: Removes blacklist config + reloads module
- **Verification**: Checks `/proc/modules` to confirm state

### Configuration Files

Persistent settings are stored in `/etc/modprobe.d/`:
- `camera_privacy.conf` - Blacklist configuration for camera
- `bluetooth_privacy.conf` - Blacklist configuration for Bluetooth

## 🔐 Security Considerations

⚠️ **Administrator Access Required**
- This tool requires root/administrator privileges to modify kernel modules
- Uses PolicyKit (`pkexec`) for secure privilege escalation
- All commands are executed through validated bash sessions

### Safety Features

1. **Pre-Flight Checks**: Validates system has required commands
2. **Process Detection**: Shows which apps are using devices before disabling
3. **Error Handling**: Clear error messages for kernel sync issues
4. **State Verification**: Confirms kernel state after operations
5. **User Confirmation**: Prompts before force-killing applications

## 🐛 Troubleshooting

### "Missing critical components" Error
**Problem**: `pkexec`, `modprobe`, or `fuser` not found  
**Solution**: Install PolicyKit and ensure modprobe/fuser are in your PATH
```bash
# For Debian/Ubuntu
sudo apt install policykit-1

# For Fedora
sudo dnf install polkit
```

### "Kernel Out of Sync" Error
**Problem**: Kernel was updated but system hasn't rebooted  
**Solution**: Reboot your system to sync with the new kernel
```bash
sudo reboot
```

### "State Mismatch" Warning
**Problem**: Command was sent but device state didn't change  
**Solution**: 
- Verify no applications are using the device
- Check system logs: `dmesg | tail -20`
- Try rebooting

### Authentication Denied
**Problem**: Password authentication fails or times out  
**Solution**: 
- Ensure your user is in the sudoers group
- Try running with explicit sudo: `sudo python3 privacy.py`

## 📁 Project Structure

```
Security-App/
├── README.md              # This file
├── privacy.py            # Main application file
└── .gitignore            # Git ignore rules
```

## 🔄 How It Works

### Device Disable Workflow
1. **Detection**: Checks if module is loaded in kernel
2. **Pre-Check**: Identifies blocking processes using `fuser`
3. **User Prompt**: Asks if should kill blocking apps
4. **Execution**: 
   - Creates blacklist config in `/etc/modprobe.d/`
   - Unloads module with `modprobe -rf`
5. **Verification**: Confirms state changed in `/proc/modules`
6. **Feedback**: Updates UI with new status

### Persistence
- Blacklist configs survive reboots
- On next boot, kernel loads without these modules
- User can still re-enable by removing blacklist

## 📝 Code Example

```python
# Check device status
if app.is_loaded("uvcvideo"):
    print("Camera module is active")

if app.is_blacklisted("camera_privacy.conf"):
    print("Camera is boot-protected")

# Toggle device
app.toggle("Camera", "uvcvideo", "/dev/video*", "camera_privacy.conf")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/PlayerRS21/Security-App.git
cd Security-App

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Run tests or modifications
python3 privacy.py
```

## 📄 License

This project is currently unlicensed. Please contact the repository owner for licensing information.

## 👤 Author

**PlayerRS21** - [GitHub Profile](https://github.com/PlayerRS21)

## 🌟 Support

If you encounter any issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review system logs with `dmesg` or `journalctl`
3. Open an [Issue](https://github.com/PlayerRS21/Security-App/issues) on GitHub

## ⭐ Show Your Support

If this project helped you, please consider giving it a star! ⭐

---

**Last Updated**: 2026  
**Version**: 3.0
