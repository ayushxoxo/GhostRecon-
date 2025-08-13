#!/usr/bin/env python3
"""
Automated Recon Pipeline Tool - Main Reconnaissance Script
Runs comprehensive reconnaissance on a target domain.
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

class ReconPipeline:
    def __init__(self, target: str):
        self.target = target
        self.output_dir = Path("output")
        self.screenshots_dir = Path("screenshots")
        self.js_out_dir = self.output_dir / "js_out"
        
        # Required tools
        self.required_tools = [
            "subfinder", "amass", "dnsx", "naabu", "httpx", 
            "nuclei", "gau", "unfurl", "ffuf", "gowitness", "curl"
        ]
        
        # Total steps
        self.total_steps = 21
        self.current_step = 0

    def log_step(self, step_name: str):
        """Log current step with progress indicator."""
        self.current_step += 1
        logger.info(f"[{self.current_step}/{self.total_steps}] Running {step_name}...")

    def run_command(self, command: List[str], output_file: Optional[str] = None, check: bool = True) -> Tuple[bool, str]:
        """Run a command and optionally save output to file."""
        try:
            if output_file:
                with open(output_file, 'w') as f:
                    result = subprocess.run(
                        command,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=check
                    )
                    return True, "Command executed successfully"
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=check
                )
                return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def run_shell_command(self, command: str, output_file: Optional[str] = None) -> Tuple[bool, str]:
        """Run a shell command using bash."""
        try:
            if output_file:
                with open(output_file, 'w') as f:
                    result = subprocess.run(
                        ["bash", "-c", command],
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=True
                    )
                    return True, "Command executed successfully"
            else:
                result = subprocess.run(
                    ["bash", "-c", command],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def check_tools(self) -> bool:
        """Check if all required tools are installed."""
        logger.info("[+] Checking required tools...")
        
        missing_tools = []
        for tool in self.required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
            else:
                logger.info(f"[✓] {tool} found")
        
        if missing_tools:
            logger.error(f"❌ Missing required tools: {', '.join(missing_tools)}")
            logger.error("Please run install.py first to install all required tools.")
            return False
        
        logger.info("[✓] All required tools are available")
        return True

    def create_directories(self) -> bool:
        """Create required directories."""
        logger.info("[+] Creating directories...")
        
        directories = [self.output_dir, self.screenshots_dir, self.js_out_dir]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"[✓] Created directory: {directory}/")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                return False
        
        return True

    def check_file_created(self, file_path: str) -> bool:
        """Check if a file was created and has content."""
        path = Path(file_path)
        if path.exists() and path.stat().st_size > 0:
            logger.info(f"[✓] {file_path} created successfully")
            return True
        else:
            logger.warning(f"[!] {file_path} is empty or not created")
            return False

    def run_recon(self) -> bool:
        """Main reconnaissance pipeline."""
        logger.info(f"🚀 Starting reconnaissance on: {self.target}")
        
        # Pre-flight checks
        if not self.check_tools():
            return False
        
        if not self.create_directories():
            return False
        
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"📸 Screenshots directory: {self.screenshots_dir}")
        
        # Step 1: Subfinder
        self.log_step("subfinder")
        success, output = self.run_command(
            ["subfinder", "-d", self.target, "-all", "-silent"],
            f"{self.output_dir}/01_subfinder.txt"
        )
        if not success:
            logger.error(f"Subfinder failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/01_subfinder.txt")
        
        # Step 2: Amass passive
        self.log_step("amass passive")
        success, output = self.run_command(
            ["amass", "enum", "-passive", "-d", self.target],
            f"{self.output_dir}/02_amass_passive.txt"
        )
        if not success:
            logger.error(f"Amass passive failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/02_amass_passive.txt")
        
        # Step 3: Merge & de-duplicate
        self.log_step("merge and de-duplicate subdomains")
        success, output = self.run_shell_command(
            f"cat {self.output_dir}/01_subfinder.txt {self.output_dir}/02_amass_passive.txt | sort -u",
            f"{self.output_dir}/03_subs_uniq.txt"
        )
        if not success:
            logger.error(f"Merge failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/03_subs_uniq.txt")
        
        # Step 4: DNS resolve
        self.log_step("DNS resolution")
        success, output = self.run_command(
            ["dnsx", "-l", f"{self.output_dir}/03_subs_uniq.txt", "-a", "-aaaa", "-cname", "-ns", "-resp"],
            f"{self.output_dir}/04_dnsx_resolved.txt"
        )
        if not success:
            logger.error(f"DNSx failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/04_dnsx_resolved.txt")
        
        # Step 5: Extract hosts
        self.log_step("extract resolved hosts")
        success, output = self.run_shell_command(
            f"awk '{{print $1}}' {self.output_dir}/04_dnsx_resolved.txt | sort -u",
            f"{self.output_dir}/05_hosts_resolved.txt"
        )
        if not success:
            logger.error(f"Host extraction failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/05_hosts_resolved.txt")
        
        # Step 6: Naabu top 1000 ports
        self.log_step("naabu top 1000 ports scan")
        success, output = self.run_command(
            ["naabu", "-list", f"{self.output_dir}/05_hosts_resolved.txt", "-p", "top-1000", "-rate", "2000"],
            f"{self.output_dir}/06_naabu_top1k.txt"
        )
        if not success:
            logger.error(f"Naabu top 1000 failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/06_naabu_top1k.txt")
        
        # Step 7: Naabu full TCP sweep
        self.log_step("naabu full TCP sweep")
        success, output = self.run_command(
            ["naabu", "-list", f"{self.output_dir}/05_hosts_resolved.txt", "-p", "-", "-rate", "500"],
            f"{self.output_dir}/07_naabu_full.txt"
        )
        if not success:
            logger.error(f"Naabu full sweep failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/07_naabu_full.txt")
        
        # Step 8: Merge open ports
        self.log_step("merge open ports")
        success, output = self.run_shell_command(
            f"cat {self.output_dir}/06_naabu_top1k.txt {self.output_dir}/07_naabu_full.txt | sort -u",
            f"{self.output_dir}/08_open_ports.txt"
        )
        if not success:
            logger.error(f"Port merge failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/08_open_ports.txt")
        
        # Step 9: HTTPx from subdomains
        self.log_step("httpx from subdomains")
        success, output = self.run_command(
            ["httpx", "-l", f"{self.output_dir}/03_subs_uniq.txt", "-status-code", "-title", "-tech-detect", "-follow-redirects"],
            f"{self.output_dir}/09_httpx_subs.txt"
        )
        if not success:
            logger.error(f"HTTPx subdomains failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/09_httpx_subs.txt")
        
        # Step 10: HTTPx from open ports
        self.log_step("httpx from open ports")
        success, output = self.run_command(
            ["httpx", "-l", f"{self.output_dir}/08_open_ports.txt", "-status-code", "-title", "-tech-detect", "-follow-redirects"],
            f"{self.output_dir}/10_httpx_ports.txt"
        )
        if not success:
            logger.error(f"HTTPx ports failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/10_httpx_ports.txt")
        
        # Step 11: Merge live URLs
        self.log_step("merge live URLs")
        success, output = self.run_shell_command(
            f"cat {self.output_dir}/09_httpx_subs.txt {self.output_dir}/10_httpx_ports.txt | awk '{{print $1}}' | sort -u",
            f"{self.output_dir}/11_live_urls.txt"
        )
        if not success:
            logger.error(f"URL merge failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/11_live_urls.txt")
        
        # Step 12: Gowitness screenshots
        self.log_step("gowitness screenshots")
        success, output = self.run_command([
            "gowitness", "file", "-f", f"{self.output_dir}/11_live_urls.txt", 
            "-t", "5", "--timeout", "10", "--log-level", "warn", 
            "--destination", "screenshots", "--json", "screenshots/gowitness.json"
        ])
        if not success:
            logger.error(f"Gowitness failed: {output}")
            return False
        logger.info("[✓] Screenshots captured")
        
        # Step 13: CNAME takeover candidates
        self.log_step("CNAME takeover candidates")
        success, output = self.run_shell_command(
            f"awk '/CNAME/ {{print $1,$5}}' {self.output_dir}/04_dnsx_resolved.txt",
            f"{self.output_dir}/12_cname_candidates.txt"
        )
        if not success:
            logger.error(f"CNAME extraction failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/12_cname_candidates.txt")
        
        # Step 14: Nuclei high-severity web scan
        self.log_step("nuclei high-severity web scan")
        success, output = self.run_command([
            "nuclei", "-l", f"{self.output_dir}/11_live_urls.txt", 
            "-severity", "critical,high,medium", "-rl", "50", "-c", "50"
        ], f"{self.output_dir}/13_nuclei_web.txt")
        if not success:
            logger.error(f"Nuclei web scan failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/13_nuclei_web.txt")
        
        # Step 15: Nuclei takeover scan
        self.log_step("nuclei takeover scan")
        success, output = self.run_command([
            "nuclei", "-t", "http/takeovers/", "-l", f"{self.output_dir}/03_subs_uniq.txt", 
            "-rl", "30", "-c", "30"
        ], f"{self.output_dir}/14_nuclei_takeover.txt")
        if not success:
            logger.error(f"Nuclei takeover scan failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/14_nuclei_takeover.txt")
        
        # Step 16: GAU historical endpoints
        self.log_step("GAU historical endpoints")
        success, output = self.run_command([
            "gau", "--providers", "wayback,otx,urlscan", self.target
        ], f"{self.output_dir}/15_gau.txt")
        if not success:
            logger.error(f"GAU failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/15_gau.txt")
        
        # Step 17: Extract params (unfurl)
        self.log_step("extract parameters")
        success, output = self.run_shell_command(
            f"cat {self.output_dir}/15_gau.txt | unfurl --unique keys",
            f"{self.output_dir}/16_params.txt"
        )
        if not success:
            logger.error(f"Parameter extraction failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/16_params.txt")
        
        # Step 18: FFUF directory fuzzing
        self.log_step("ffuf directory fuzzing")
        success, output = self.run_command([
            "ffuf", "-u", f"https://{self.target}/FUZZ", 
            "-w", "/usr/share/wordlists/dirb/common.txt",
            "-mc", "200,204,301,302,307,401,403", "-o", f"{self.output_dir}/17_ffuf_dirs.txt", "-of", "txt"
        ])
        if not success:
            logger.error(f"FFUF directory fuzzing failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/17_ffuf_dirs.txt")
        
        # Step 19: FFUF parameter fuzzing
        self.log_step("ffuf parameter fuzzing")
        success, output = self.run_command([
            "ffuf", "-u", f"https://{self.target}/search?FUZZ=test",
            "-w", f"{self.output_dir}/16_params.txt", "-mc", "all", "-o", f"{self.output_dir}/18_ffuf_params.txt", "-of", "txt"
        ])
        if not success:
            logger.error(f"FFUF parameter fuzzing failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/18_ffuf_params.txt")
        
        # Step 20: HTTPx JS scraping
        self.log_step("httpx JS scraping")
        success, output = self.run_command([
            "httpx", "-l", f"{self.output_dir}/11_live_urls.txt", 
            "-path", "discovery", "-store-response-dir", f"{self.output_dir}/js_out",
            "-match-regex", "\\.js($|\\?)"
        ], f"{self.output_dir}/19_js_endpoints.txt")
        if not success:
            logger.error(f"HTTPx JS scraping failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/19_js_endpoints.txt")
        
        # Step 21: Robots.txt
        self.log_step("robots.txt check")
        success, output = self.run_command([
            "curl", "-s", f"https://{self.target}/robots.txt"
        ], f"{self.output_dir}/20_robots.txt")
        if not success:
            logger.error(f"Robots.txt check failed: {output}")
            return False
        self.check_file_created(f"{self.output_dir}/20_robots.txt")
        
        logger.info("\n🎉 Recon complete! Results in ./output and ./screenshots")
        return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated Recon Pipeline Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 recon.py --target example.com
  python3 recon.py --target subdomain.example.com
        """
    )
    
    parser.add_argument(
        "--target", 
        required=True,
        help="Target domain to scan (e.g., example.com)"
    )
    
    args = parser.parse_args()
    
    # Validate target format
    if not args.target or '.' not in args.target:
        logger.error("❌ Invalid target format. Please provide a valid domain (e.g., example.com)")
        sys.exit(1)
    
    pipeline = ReconPipeline(args.target)
    
    try:
        success = pipeline.run_recon()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Reconnaissance interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
