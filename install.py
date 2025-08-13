#!/usr/bin/env python3
"""
Automated Recon Pipeline Tool - Installer Script
Installs all required tools and dependencies for the recon pipeline.
"""

import os
import sys
import subprocess
import shutil
import logging
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ReconInstaller:
    def __init__(self):
        self.go_tools = [
            ("subfinder", "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"),
            ("amass", "github.com/owasp-amass/amass/v4/...@latest"),
            ("dnsx", "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"),
            ("naabu", "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"),
            ("httpx", "github.com/projectdiscovery/httpx/cmd/httpx@latest"),
            ("nuclei", "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"),
            ("gau", "github.com/lc/gau/v2/cmd/gau@latest"),
            ("unfurl", "github.com/tomnomnom/unfurl@latest"),
            ("gowitness", "github.com/jaeles-project/gowitness@latest")
        ]
        
        self.apt_packages = [
            "golang-go",
            "git",
            "curl",
            "jq",
            "python3-pip",
            "chromium",
            "build-essential",
            "pkg-config"
        ]
        
        self.directories = [
            "output",
            "output/js_out",
            "screenshots"
        ]

    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None

    def get_tool_version(self, tool_name: str) -> Optional[str]:
        """Get version of an installed tool."""
        version_flags = ["--version", "-version", "-v", "version"]
        
        for flag in version_flags:
            success, output = self.run_command([tool_name, flag], check=False)
            if success and output.strip():
                # Extract version from output (common patterns)
                lines = output.strip().split('\n')
                for line in lines:
                    if 'version' in line.lower() or 'v' in line:
                        # Try to extract version number
                        import re
                        version_match = re.search(r'v?\d+\.\d+\.?\d*', line)
                        if version_match:
                            return version_match.group()
                return output.strip()[:50] + "..." if len(output.strip()) > 50 else output.strip()
        return None

    def update_system_packages(self) -> bool:
        """Update system packages using apt."""
        logger.info("[+] Updating APT packages...")
        
        commands = [
            ["apt", "update"],
            ["apt", "upgrade", "-y"]
        ]
        
        for cmd in commands:
            success, output = self.run_command(cmd)
            if not success:
                logger.error(f"Failed to run: {' '.join(cmd)}")
                logger.error(f"Error: {output}")
                return False
        
        logger.info("[✓] System packages updated successfully")
        return True

    def check_apt_package_installed(self, package: str) -> bool:
        """Check if an APT package is installed."""
        success, output = self.run_command(["dpkg", "-l", package], check=False)
        return success and package in output

    def force_install_apt_packages(self) -> bool:
        """Force install APT packages (reinstall if already installed)."""
        logger.info("[+] Force installing APT packages...")
        
        # Force install all packages
        logger.info(f"[+] Force installing packages: {', '.join(self.apt_packages)}")
        success, output = self.run_command(["apt", "install", "-y", "--reinstall"] + self.apt_packages)
        if not success:
            logger.error(f"Failed to install APT packages: {output}")
            return False
        
        logger.info("[✓] APT packages force installed successfully")
        return True

    def install_apt_packages(self) -> bool:
        """Install required APT packages."""
        logger.info("[+] Installing dependencies...")
        
        # Check which packages are missing
        missing_packages = []
        for package in self.apt_packages:
            if not self.check_apt_package_installed(package):
                missing_packages.append(package)
                logger.info(f"[+] {package} not found, will install")
            else:
                logger.info(f"[✓] {package} already installed")
        
        if not missing_packages:
            logger.info("[✓] All APT packages are already installed")
            return True
        
        # Install missing packages
        logger.info(f"[+] Installing missing packages: {', '.join(missing_packages)}")
        success, output = self.run_command(["apt", "install", "-y"] + missing_packages)
        if not success:
            logger.error(f"Failed to install APT packages: {output}")
            return False
        
        logger.info("[✓] APT packages installed successfully")
        return True

    def setup_go_environment(self) -> bool:
        """Setup Go environment and ensure GOPATH is configured."""
        logger.info("[+] Setting up Go environment...")
        
        # Check if Go is installed
        if not self.check_command_exists("go"):
            logger.error("Go is not installed. Please install it first.")
            return False
        
        # Get Go version
        success, output = self.run_command(["go", "version"])
        if success:
            logger.info(f"[✓] {output.strip()}")
        
        # Ensure GOPATH is set
        home = os.path.expanduser("~")
        go_path = os.path.join(home, "go")
        go_bin = os.path.join(go_path, "bin")
        
        # Create go directory if it doesn't exist
        Path(go_path).mkdir(exist_ok=True)
        Path(go_bin).mkdir(exist_ok=True)
        
        # Check if go/bin is in PATH
        current_path = os.environ.get('PATH', '')
        if go_bin not in current_path:
            logger.warning(f"[!] {go_bin} is not in PATH. Please add it to your PATH:")
            logger.warning(f"    export PATH=$PATH:{go_bin}")
            logger.warning(f"    Or add to ~/.bashrc: echo 'export PATH=$PATH:{go_bin}' >> ~/.bashrc")
        
        return True

    def force_install_go_tools(self) -> bool:
        """Force install Go-based tools (reinstall if already installed)."""
        logger.info("[+] Force installing Go-based tools...")
        
        for tool_name, tool_path in self.go_tools:
            logger.info(f"[+] Force installing {tool_name}...")
            
            # Force install (go install will overwrite existing)
            success, output = self.run_command(["go", "install", "-v", tool_path])
            if not success:
                logger.error(f"Failed to install {tool_name}: {output}")
                return False
            
            # Verify installation
            version = self.get_tool_version(tool_name)
            if version:
                logger.info(f"[✓] Installed {tool_name} {version}")
            else:
                logger.warning(f"[!] {tool_name} installed but version check failed")
        
        return True

    def install_go_tools(self) -> bool:
        """Install Go-based tools."""
        logger.info("[+] Installing Go-based tools...")
        
        for tool_name, tool_path in self.go_tools:
            # Check if tool is already installed
            existing_version = self.get_tool_version(tool_name)
            if existing_version:
                logger.info(f"[✓] {tool_name} {existing_version} already installed")
                continue
            
            logger.info(f"[+] Installing {tool_name}...")
            
            # Force install (remove existing if any)
            logger.info(f"[+] Force installing {tool_name}...")
            success, output = self.run_command(["go", "install", "-v", tool_path])
            if not success:
                logger.error(f"Failed to install {tool_name}: {output}")
                return False
            
            # Verify installation
            version = self.get_tool_version(tool_name)
            if version:
                logger.info(f"[✓] Installed {tool_name} {version}")
            else:
                logger.warning(f"[!] {tool_name} installed but version check failed")
        
        return True

    def update_nuclei_templates(self) -> bool:
        """Update Nuclei templates."""
        logger.info("[+] Updating Nuclei templates...")
        
        success, output = self.run_command(["nuclei", "-update-templates"])
        if not success:
            logger.error(f"Failed to update Nuclei templates: {output}")
            return False
        
        logger.info("[✓] Nuclei templates updated successfully")
        return True

    def create_directories(self) -> bool:
        """Create required directories."""
        logger.info("[+] Creating directories...")
        
        for directory in self.directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"[✓] Created directory: {directory}/")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                return False
        
        return True

    def verify_installations(self) -> bool:
        """Verify all tools are installed correctly."""
        logger.info("[+] Verifying installations...")
        
        all_good = True
        
        for tool_name, _ in self.go_tools:
            version = self.get_tool_version(tool_name)
            if version:
                logger.info(f"[✓] {tool_name}: {version}")
            else:
                logger.error(f"[✗] {tool_name}: Not found or version check failed")
                all_good = False
        
        # Check other tools
        other_tools = ["ffuf", "curl", "jq", "git"]
        for tool in other_tools:
            if self.check_command_exists(tool):
                version = self.get_tool_version(tool)
                if version:
                    logger.info(f"[✓] {tool}: {version}")
                else:
                    logger.info(f"[✓] {tool}: Installed")
            else:
                logger.warning(f"[!] {tool}: Not found in PATH")
        
        return all_good

    def check_kali_linux(self) -> bool:
        """Check if running on Kali Linux."""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'kali' in content:
                    return True
        except FileNotFoundError:
            pass
        
        # Alternative check for Kali
        try:
            with open('/etc/issue', 'r') as f:
                content = f.read().lower()
                if 'kali' in content:
                    return True
        except FileNotFoundError:
            pass
        
        return False

    def install(self, force: bool = False) -> bool:
        """Main installation method."""
        logger.info("🚀 Starting Automated Recon Pipeline Installation...")
        
        if force:
            logger.info("🔧 Force installation mode enabled - will reinstall all tools")
        
        # Check if running on Kali Linux
        if not self.check_kali_linux():
            logger.error("❌ This tool is designed specifically for Kali Linux")
            logger.error("Please run this script on a Kali Linux system")
            return False
        
        # Check if running as root (required for apt operations)
        if os.geteuid() != 0:
            logger.error("This script must be run as root (use sudo)")
            return False
        
        steps = [
            ("Update system packages", self.update_system_packages),
        ]
        
        # Choose APT installation method based on force flag
        if force:
            steps.append(("Force install APT packages", self.force_install_apt_packages))
        else:
            steps.append(("Install APT packages", self.install_apt_packages))
        
        steps.append(("Setup Go environment", self.setup_go_environment))
        
        # Choose Go tools installation method based on force flag
        if force:
            steps.append(("Force install Go tools", self.force_install_go_tools))
        else:
            steps.append(("Install Go tools", self.install_go_tools))
        
        steps.extend([
            ("Update Nuclei templates", self.update_nuclei_templates),
            ("Create directories", self.create_directories),
            ("Verify installations", self.verify_installations)
        ])
        
        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")
            if not step_func():
                logger.error(f"❌ Installation failed at: {step_name}")
                return False
        
        logger.info("\n🎉 Installation complete!")
        logger.info("💡 Next steps:")
        logger.info("   1. Add $HOME/go/bin to your PATH if not already done")
        logger.info("   2. Run: export PATH=$PATH:$HOME/go/bin")
        logger.info("   3. Or add to ~/.bashrc: echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc")
        logger.info("   4. Start building your recon pipeline!")
        
        return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated Recon Pipeline Tool - Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 install.py          # Normal installation
  sudo python3 install.py --force  # Force reinstall all tools
        """
    )
    
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force reinstall all tools (even if already installed)"
    )
    
    args = parser.parse_args()
    
    installer = ReconInstaller()
    
    try:
        success = installer.install(force=args.force)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
