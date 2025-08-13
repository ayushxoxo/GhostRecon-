# Reconnaissance Output Files

All important results from the reconnaissance pipeline are saved as `.txt` files for easy reading and analysis.

## 📁 Output Directory Structure

```
output/
├── 01_subfinder.txt              # Subfinder subdomain discovery results
├── 02_amass_passive.txt          # Amass passive enumeration results
├── 03_subs_uniq.txt              # Merged and de-duplicated subdomains
├── 04_dnsx_resolved.txt          # DNS resolution results (A, AAAA, CNAME, NS records)
├── 05_hosts_resolved.txt         # Extracted resolved hostnames
├── 06_naabu_top1k.txt            # Top 1000 ports scan results
├── 07_naabu_full.txt             # Full TCP port sweep results
├── 08_open_ports.txt             # Merged open ports list
├── 09_httpx_subs.txt             # HTTP probing results from subdomains
├── 10_httpx_ports.txt            # HTTP probing results from open ports
├── 11_live_urls.txt              # Merged live web endpoints
├── 12_cname_candidates.txt       # CNAME takeover candidates
├── 13_nuclei_web.txt             # High-severity vulnerability scan results
├── 14_nuclei_takeover.txt        # Subdomain takeover scan results
├── 15_gau.txt                    # Historical endpoints from GAU
├── 16_params.txt                 # Extracted URL parameters
├── 17_ffuf_dirs.txt              # Directory fuzzing results
├── 18_ffuf_params.txt            # Parameter fuzzing results
├── 19_js_endpoints.txt           # JavaScript endpoints discovered
├── 20_robots.txt                 # Robots.txt file content
└── js_out/                       # JavaScript files directory
    └── [js_files]                # Individual JavaScript files

screenshots/
├── gowitness.json                # Screenshot metadata
└── [screenshot_files]            # Website screenshots
```

## 📋 File Descriptions

### Subdomain Discovery (01-03)
- **01_subfinder.txt**: Raw subdomain discovery results from Subfinder
- **02_amass_passive.txt**: Passive subdomain enumeration results from Amass
- **03_subs_uniq.txt**: Clean, de-duplicated list of all discovered subdomains

### DNS Resolution (04-05)
- **04_dnsx_resolved.txt**: DNS records (A, AAAA, CNAME, NS) for all subdomains
- **05_hosts_resolved.txt**: List of hostnames that successfully resolved

### Port Scanning (06-08)
- **06_naabu_top1k.txt**: Common ports (top 1000) scan results
- **07_naabu_full.txt**: Complete TCP port sweep results
- **08_open_ports.txt**: Combined list of all open ports

### HTTP Probing (09-11)
- **09_httpx_subs.txt**: HTTP responses from subdomain probing
- **10_httpx_ports.txt**: HTTP responses from port-based probing
- **11_live_urls.txt**: Final list of live web endpoints

### Security Analysis (12-14)
- **12_cname_candidates.txt**: Potential CNAME takeover targets
- **13_nuclei_web.txt**: Web vulnerability scan findings
- **14_nuclei_takeover.txt**: Subdomain takeover vulnerabilities

### Historical & Parameter Discovery (15-16)
- **15_gau.txt**: Historical URLs from various sources
- **16_params.txt**: Unique URL parameters extracted

### Fuzzing Results (17-18)
- **17_ffuf_dirs.txt**: Directory fuzzing discoveries
- **18_ffuf_params.txt**: Parameter fuzzing results

### Additional Discovery (19-20)
- **19_js_endpoints.txt**: JavaScript files and endpoints
- **20_robots.txt**: Robots.txt file content

## 🔍 Analysis Priority

### High Priority Files (Start Here)
1. **03_subs_uniq.txt** - Complete subdomain list
2. **11_live_urls.txt** - Live web endpoints
3. **13_nuclei_web.txt** - Security vulnerabilities
4. **15_gau.txt** - Historical endpoints

### Medium Priority Files
1. **04_dnsx_resolved.txt** - DNS information
2. **12_cname_candidates.txt** - Takeover opportunities
3. **16_params.txt** - URL parameters
4. **17_ffuf_dirs.txt** - Hidden directories

### Additional Analysis
1. **js_out/** - JavaScript files for manual analysis
2. **screenshots/** - Visual reconnaissance
3. **20_robots.txt** - Disallowed paths

## 📊 File Formats

All output files are in **plain text format** (`.txt`) for:
- ✅ Easy reading and analysis
- ✅ Simple text processing
- ✅ Compatibility with any text editor
- ✅ Quick grep/search operations
- ✅ No special tools required to view

## 🚀 Quick Analysis Commands

```bash
# Count total subdomains
wc -l output/03_subs_uniq.txt

# Count live URLs
wc -l output/11_live_urls.txt

# Check for vulnerabilities
grep -i "critical\|high" output/13_nuclei_web.txt

# Find interesting parameters
cat output/16_params.txt | grep -E "(admin|login|user|id|token)"

# Check for takeover opportunities
cat output/12_cname_candidates.txt
```
