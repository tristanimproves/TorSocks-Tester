# Tor Proxy Tester

A powerful and flexible tool for testing Tor proxy connectivity with customizable speed, concurrency, and target options.

## Features

- 🎯 **Preset URLs**: Quick access to common test sites (Google, GitHub, Wikipedia, etc.)
- ⚡ **Performance Presets**: Conservative, Moderate, Aggressive, and Stress modes
- 🔧 **Full Customization**: Configure workers, delays, timeouts independently
- 📊 **Real-time Statistics**: Live updates with success rates and request/sec
- 🛑 **Graceful Shutdown**: Clean exit with complete statistics
- 🔍 **Verbose Mode**: Detailed logging for debugging
- ⏱️ **Timeout Control**: Separate connection and total timeouts

## Installation

```bash
# Install required dependencies
pip install aiohttp aiohttp-socks

# Make the script executable
chmod +x tor_tester.py
```

## Quick Start

```bash
# Basic test with default settings
python tor_tester.py --url https://example.com

# Test using a preset URL
python tor_tester.py --url google

# Use a performance preset
python tor_tester.py --url torproject --preset moderate

# Custom configuration
python tor_tester.py --url github --concurrency 20 --delay 0.5
```

## Usage

```
python tor_tester.py [OPTIONS]

Required:
  --url URL              Target URL or preset name

Optional:
  --preset PRESET        Performance preset (conservative/moderate/aggressive/stress)
  -c, --concurrency N    Number of concurrent workers (default: 10)
  -d, --delay SECONDS    Delay between batches (default: 1.0)
  -p, --proxy URL        Proxy URL (default: socks5://127.0.0.1:9050)
  -m, --max-requests N   Maximum number of requests (default: unlimited)
  -v, --verbose          Show detailed output for each request
  --connect-timeout N    Connection timeout in seconds (default: 5)
  --total-timeout N      Total request timeout in seconds (default: 10)
  --list-presets         List available presets
  --list-urls            List available test URLs
```

## Presets

### Performance Presets

| Preset       | Workers | Delay | Description                    |
|--------------|---------|-------|--------------------------------|
| conservative | 3       | 3.0s  | Low load for sensitive testing |
| moderate     | 10      | 1.5s  | Balanced performance           |
| aggressive   | 25      | 0.5s  | High load testing              |
| stress       | 50      | 0s    | Maximum load                   |

### Test URLs

| Preset       | URL                              |
|--------------|----------------------------------|
| google       | https://www.google.com/          |
| cloudflare   | https://www.cloudflare.com/      |
| torproject   | https://www.torproject.org/      |
| checkip      | https://checkip.amazonaws.com/   |
| ipify        | https://api.ipify.org/           |
| duckduckgo   | https://duckduckgo.com/          |
| wikipedia    | https://www.wikipedia.org/       |
| github       | https://github.com/              |

## Examples

### List Available Options

```bash
# See all preset URLs
python tor_tester.py --list-urls

# See all performance presets
python tor_tester.py --list-presets
```

### Basic Testing

```bash
# Test Google with default settings
python tor_tester.py --url google

# Test custom URL with moderate preset
python tor_tester.py --url https://example.com --preset moderate
```

### Custom Configurations

```bash
# Fast testing: 30 workers, 0.2s delay
python tor_tester.py --url torproject --concurrency 30 --delay 0.2

# Limited test: 100 requests total
python tor_tester.py --url github --max-requests 100

# Verbose output for debugging
python tor_tester.py --url google --verbose
```

### Different Proxy Configurations

```bash
# Use custom Tor port
python tor_tester.py --url google --proxy socks5://127.0.0.1:9150

# Use HTTP proxy
python tor_tester.py --url google --proxy http://127.0.0.1:8118

# Remote proxy
python tor_tester.py --url google --proxy socks5://proxy.example.com:1080
```

### Timeout Configurations

```bash
# Fast timeout for quick testing
python tor_tester.py --url google --connect-timeout 3 --total-timeout 5

# Patient timeout for slow connections
python tor_tester.py --url torproject --connect-timeout 10 --total-timeout 30
```

### Combined Examples

```bash
# Stress test with 50 workers, no delay, 500 requests
python tor_tester.py --url cloudflare --preset stress --max-requests 500

# Conservative long-running test with verbose output
python tor_tester.py --url torproject --preset conservative --verbose

# Custom aggressive test with specific timeouts
python tor_tester.py --url github \
  --concurrency 40 \
  --delay 0.1 \
  --max-requests 1000 \
  --connect-timeout 3 \
  --total-timeout 8
```

## Output

The tool provides real-time statistics:

```
╔══════════════════════════════════════════════════════════════════════╗
║                          Tor Proxy Tester                            ║
╠══════════════════════════════════════════════════════════════════════╣
║ URL:         https://www.google.com/                                 ║
║ Proxy:       socks5://127.0.0.1:9050                                 ║
║ Workers:     10                                                      ║
║ Delay:       1.0s                                                    ║
║ Max Requests: Unlimited                                              ║
╚══════════════════════════════════════════════════════════════════════╝

Press Ctrl+C to stop

[45s] ✓ 423 | ✗ 12 | ⏱ 5 | Total: 440 | Rate: 9.78/s | Success: 96.1%

======================================================================
FINAL STATISTICS
======================================================================
Total Requests:    440
Successful:        423 (96.14%)
Failed:            12
Timeouts:          5
Duration:          45.00s
Requests/sec:      9.78
======================================================================
```

## Statistics Explained

- **✓ Successful**: Requests that completed successfully (HTTP 200-399)
- **✗ Failed**: Requests that failed due to errors (connection refused, etc.)
- **⏱ Timeout**: Requests that exceeded the timeout period
- **Rate**: Requests per second (total requests / elapsed time)
- **Success**: Percentage of successful requests

## Tips

1. **Start Conservative**: Begin with the `conservative` preset to ensure your Tor setup works
2. **Monitor Resources**: High concurrency can consume significant bandwidth and memory
3. **Respect Rate Limits**: Some sites may block or throttle aggressive testing
4. **Use Verbose Mode**: Add `-v` when debugging connection issues
5. **Set Max Requests**: Use `-m` to limit testing and avoid excessive load
6. **Adjust Timeouts**: Tor can be slow; increase timeouts for more reliable results

## Troubleshooting

### "Connection refused" errors
- Ensure Tor is running: `systemctl status tor` or check Tor Browser
- Verify proxy port (default: 9050 for Tor daemon, 9150 for Tor Browser)
- Check firewall settings

### High failure rate
- Reduce concurrency (`-c 5` or use `conservative` preset)
- Increase timeouts (`--total-timeout 20`)
- Add delay between batches (`-d 2.0`)

### "Timeout" errors
- Increase timeouts: `--connect-timeout 10 --total-timeout 20`
- Reduce concurrency to avoid overwhelming Tor circuits
- Check your internet connection speed

## Security Note

This tool is for testing your own Tor setup. Do not use it to:
- Attack or stress-test websites you don't own
- Bypass rate limits or access restrictions
- Generate excessive traffic that could harm services

## Requirements

- Python 3.7+
- aiohttp
- aiohttp-socks
- Tor service running (default port 9050)

## License

This tool is provided as-is for legitimate testing purposes only.
