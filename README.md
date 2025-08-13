# Automated Recon Pipeline Tool

A comprehensive automated reconnaissance pipeline tool designed specifically for Kali Linux that installs and manages popular security testing tools.

## 🚀 Quick Start

### Prerequisites
- **Kali Linux** (required - this tool is designed specifically for Kali Linux)
- Root privileges (for package installation)
- Internet connection

> **Note**: This tool will automatically detect if you're running on Kali Linux and will refuse to run on other systems.

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd recon-pipeline
   ```

2. **Run the installer:**
   ```bash
   # Normal installation (skips already installed tools)
   sudo python3 install.py
   
   # Force installation (reinstalls all tools)
   sudo python3 install.py --force
   ```

3. **Add Go tools to PATH (if not already done):**
   ```bash
   export PATH=$PATH:$HOME/go/bin
   # Or add to ~/.bashrc for persistence:
   echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
   source ~/.bashrc
   ```

## 📦 Installed Tools

### Go-based Tools
- **subfinder** - Subdomain discovery tool
- **amass** - Network mapping and attack surface discovery
- **dnsx** - Fast and multi-purpose DNS toolkit
- **naabu** - Port scanning tool
- **httpx** - Fast HTTP probe
- **nuclei** - Vulnerability scanner
- **gau** - Fetch known URLs from AlienVault's Open Threat Exchange
- **unfurl** - Parse and extract URLs
- **gowitness** - Web screenshot utility

### System Dependencies
- **golang-go** - Go programming language
- **git** - Version control system
- **curl** - Command line tool for transferring data
- **jq** - Lightweight command-line JSON processor
- **python3-pip** - Python package installer
- **chromium** - Web browser (for gowitness)
- **build-essential** - Compilation tools
- **pkg-config** - Helper tool for compiling

## 📁 Project Structure

```
recon-pipeline/
├── install.py                    # Python installer script
├── recon.py                      # Main recon script (coming soon)
├── README.md                     # This file
├── output/                       # Output directory
│   └── js_out/                   # JavaScript output
└── screenshots/                  # Screenshots directory
```

## 🔧 Installation Process

The installer performs the following steps:

1. **System Update** - Updates APT packages
2. **Dependencies** - Installs required system packages (skips if already installed)
3. **Go Environment** - Sets up Go and verifies installation
4. **Tool Installation** - Installs all Go-based security tools (skips if already installed)
5. **Templates Update** - Updates Nuclei vulnerability templates
6. **Directory Creation** - Creates output directories
7. **Verification** - Verifies all tools are installed correctly

### Force Installation

Use the `--force` flag to reinstall all tools even if they're already installed:

```bash
sudo python3 install.py --force
```

This is useful when:
- Tools are corrupted or not working properly
- You want to update to the latest versions
- Installation was interrupted and you want to start fresh

## ✅ Verification

After installation, you can verify tools are working:

```bash
# Check individual tools
subfinder --version
amass --version
nuclei --version
# ... etc

# Or run the verification again
sudo python3 install.py

# Show help
python3 install.py --help

## 🛠️ Troubleshooting

### Common Issues

1. **"Please run this script on a Kali Linux system"**
   - This tool is designed specifically for Kali Linux
   - It will not run on other Linux distributions or Windows
   - Use a Kali Linux virtual machine or live USB

2. **Permission Denied**
   - Ensure you're running with `sudo`
   - Check file permissions

3. **Go tools not found**
   - Add `$HOME/go/bin` to your PATH
   - Restart your terminal or run `source ~/.bashrc`

3. **APT package installation fails**
   - Update your system: `sudo apt update && sudo apt upgrade`
   - Check internet connection

4. **Go installation fails**
   - Ensure Go is properly installed: `go version`
   - Check GOPATH and GOROOT environment variables

5. **Recon script fails**
   - Ensure all tools are installed: `sudo python3 install.py`
   - Check if running on Kali Linux
   - Verify wordlists exist: `/usr/share/wordlists/dirb/common.txt`
   - Check internet connection for online tools

### Manual Installation

If the automated installer fails, you can install tools manually:

```bash
# Install Go tools individually
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/owasp-amass/amass/v4/...@latest
# ... etc

# Update Nuclei templates
nuclei -update-templates
```

## 📝 Usage

### Running Reconnaissance

The main reconnaissance script (`recon.py`) provides comprehensive automated scanning capabilities:

```bash
# Basic usage
python3 recon.py --target example.com

# Show help
python3 recon.py --help
```

### Reconnaissance Pipeline

The script runs 21 sequential steps:

1. **Subfinder** - Subdomain discovery
2. **Amass passive** - Passive subdomain enumeration
3. **Merge & de-duplicate** - Combine and clean subdomain lists
4. **DNS resolution** - Resolve subdomains with DNSx
5. **Extract hosts** - Extract resolved hostnames
6. **Naabu top 1000** - Port scan common ports
7. **Naabu full TCP** - Complete port sweep
8. **Merge open ports** - Combine port scan results
9. **HTTPx subdomains** - HTTP probing of subdomains
10. **HTTPx ports** - HTTP probing of open ports
11. **Merge live URLs** - Combine live web endpoints
12. **Gowitness screenshots** - Capture website screenshots
13. **CNAME takeover** - Identify takeover candidates
14. **Nuclei web scan** - High-severity vulnerability scan
15. **Nuclei takeover** - Subdomain takeover scan
16. **GAU historical** - Historical endpoint discovery
17. **Parameter extraction** - Extract URL parameters
18. **FFUF directories** - Directory fuzzing
19. **FFUF parameters** - Parameter fuzzing
20. **JavaScript scraping** - Extract JS endpoints
21. **Robots.txt** - Check robots.txt file

### Output Files

All important results are saved in numbered `.txt` files in the `output/` directory for easy reading and analysis:

- `01_subfinder.txt` - Subfinder results
- `02_amass_passive.txt` - Amass passive results
- `03_subs_uniq.txt` - Unique subdomains
- `04_dnsx_resolved.txt` - DNS resolution results
- `05_hosts_resolved.txt` - Resolved hostnames
- `06_naabu_top1k.txt` - Top 1000 ports scan
- `07_naabu_full.txt` - Full port sweep
- `08_open_ports.txt` - All open ports
- `09_httpx_subs.txt` - HTTP subdomain results
- `10_httpx_ports.txt` - HTTP port results
- `11_live_urls.txt` - Live web endpoints
- `12_cname_candidates.txt` - CNAME takeover candidates
- `13_nuclei_web.txt` - Web vulnerability scan
- `14_nuclei_takeover.txt` - Takeover scan results
- `15_gau.txt` - Historical endpoints
- `16_params.txt` - URL parameters
- `17_ffuf_dirs.txt` - Directory fuzzing results
- `18_ffuf_params.txt` - Parameter fuzzing results
- `19_js_endpoints.txt` - JavaScript endpoints
- `20_robots.txt` - Robots.txt content

### Screenshots

Website screenshots are saved in the `screenshots/` directory with metadata in `screenshots/gowitness.json`.

### JavaScript Files

JavaScript files discovered during scanning are saved in `output/js_out/`.

### Wordlists

The script uses the following wordlists (should be available on Kali Linux):
- `/usr/share/wordlists/dirb/common.txt` - For directory fuzzing

### Complete Workflow

1. **Install tools**: `sudo python3 install.py`
2. **Run reconnaissance**: `python3 recon.py --target example.com`
3. **Review results**: Check `output/` and `screenshots/` directories

### Example Output

```
[INFO] 🚀 Starting reconnaissance on: example.com
[INFO] [+] Checking required tools...
[INFO] [✓] subfinder found
[INFO] [✓] amass found
[INFO] [✓] dnsx found
...
[INFO] [+] Creating directories...
[INFO] [✓] Created directory: output/
[INFO] [✓] Created directory: screenshots/
[INFO] [✓] Created directory: output/js_out/
[INFO] [1/21] Running subfinder...
[INFO] [✓] output/01_subfinder.txt created successfully
[INFO] [2/21] Running amass passive...
[INFO] [✓] output/02_amass_passive.txt created successfully
...
[INFO] 🎉 Recon complete! Results in ./output and ./screenshots
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and authorized security testing purposes only. Always ensure you have proper authorization before scanning any systems or networks.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the installation logs
3. Open an issue with detailed error information
