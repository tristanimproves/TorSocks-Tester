#!/usr/bin/env python3
import asyncio
import signal
import argparse
import sys
from aiohttp_socks import ProxyConnector
import aiohttp
import time
from typing import Dict, Optional

STOP = False

PRESETS = {
    "conservative": {
        "concurrency": 3,
        "delay": 3.0,
        "description": "Low load - 3 workers, 3s delay"
    },
    "moderate": {
        "concurrency": 10,
        "delay": 1.5,
        "description": "Medium load - 10 workers, 1.5s delay"
    },
    "aggressive": {
        "concurrency": 25,
        "delay": 0.5,
        "description": "High load - 25 workers, 0.5s delay"
    },
    "stress": {
        "concurrency": 50,
        "delay": 0,
        "description": "Extreme load - 50 workers, no delay"
    }
}

TEST_URLS = {
    "google": "https://www.google.com/",
    "cloudflare": "https://www.cloudflare.com/",
    "torproject": "https://www.torproject.org/",
    "checkip": "https://checkip.amazonaws.com/",
    "ipify": "https://api.ipify.org/",
    "duckduckgo": "https://duckduckgo.com/",
    "wikipedia": "https://www.wikipedia.org/",
    "github": "https://github.com/",
}


def shutdown():
    """Handle graceful shutdown"""
    global STOP
    STOP = True
    print("\n\nStopping gracefully... (please wait for current tasks to complete)")


signal.signal(signal.SIGINT, lambda s, f: shutdown())
signal.signal(signal.SIGTERM, lambda s, f: shutdown())


async def worker(
    session: aiohttp.ClientSession,
    url: str,
    sem: asyncio.Semaphore,
    stats: Dict[str, int],
    verbose: bool = False
) -> None:
    """Single worker that makes one request"""
    async with sem:
        try:
            async with session.get(url) as resp:
                status = resp.status
                stats["ok"] += 1
                if verbose:
                    print(f"✓ Success: {status} - {url[:50]}")
        except asyncio.TimeoutError:
            stats["timeout"] += 1
            if verbose:
                print(f"✗ Timeout: {url[:50]}")
        except Exception as e:
            stats["fail"] += 1
            if verbose:
                print(f"✗ Failed: {type(e).__name__} - {url[:50]}")


async def async_get_loop(
    url: str,
    concurrency: int = 10,
    delay: float = 1,
    proxy: str = "socks5://127.0.0.1:9050",
    max_requests: Optional[int] = None,
    verbose: bool = False,
    connect_timeout: int = 5,
    total_timeout: int = 10
) -> Dict[str, int]:
    """Main testing loop"""
    global STOP
    
    sem = asyncio.Semaphore(concurrency)
    stats = {"ok": 0, "fail": 0, "timeout": 0, "total": 0}
    start_time = time.time()
    
    connector = ProxyConnector.from_url(proxy)
    
    timeout = aiohttp.ClientTimeout(
        total=total_timeout,
        connect=connect_timeout,
        sock_read=total_timeout - connect_timeout
    )
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:
        
        print(f"╔{'═' * 70}╗")
        print(f"║ {'Tor Proxy Tester':^68} ║")
        print(f"╠{'═' * 70}╣")
        print(f"║ URL:         {url[:55]:<55} ║")
        print(f"║ Proxy:       {proxy:<55} ║")
        print(f"║ Workers:     {concurrency:<55} ║")
        print(f"║ Delay:       {delay}s{'':<52}  ║")
        print(f"║ Max Requests: {str(max_requests or 'Unlimited'):<54} ║")
        print(f"╚{'═' * 70}╝")
        print("\nPress Ctrl+C to stop\n")
        
        iteration = 0
        while not STOP:
            iteration += 1
            
            tasks = [
                worker(session, url, sem, stats, verbose)
                for _ in range(concurrency)
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            stats["total"] += concurrency
            elapsed = time.time() - start_time
            req_per_sec = stats["total"] / elapsed if elapsed > 0 else 0
            success_rate = (stats["ok"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            print(
                f"[{int(elapsed)}s] "
                f"✓ {stats['ok']} | "
                f"✗ {stats['fail']} | "
                f"⏱ {stats['timeout']} | "
                f"Total: {stats['total']} | "
                f"Rate: {req_per_sec:.2f}/s | "
                f"Success: {success_rate:.1f}%",
                end="\r",
                flush=True
            )
            
            if max_requests and stats["total"] >= max_requests:
                print("\n\nMaximum requests reached!")
                break
            
            if delay > 0 and not STOP:
                await asyncio.sleep(delay)
        
        elapsed = time.time() - start_time
        req_per_sec = stats["total"] / elapsed if elapsed > 0 else 0
        success_rate = (stats["ok"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        print("\n\n" + "=" * 70)
        print("FINAL STATISTICS")
        print("=" * 70)
        print(f"Total Requests:    {stats['total']}")
        print(f"Successful:        {stats['ok']} ({success_rate:.2f}%)")
        print(f"Failed:            {stats['fail']}")
        print(f"Timeouts:          {stats['timeout']}")
        print(f"Duration:          {elapsed:.2f}s")
        print(f"Requests/sec:      {req_per_sec:.2f}")
        print("=" * 70)
        
        return stats


def list_presets():
    """Display available presets"""
    print("\nAvailable presets:")
    print("-" * 60)
    for name, config in PRESETS.items():
        print(f"  {name:15} - {config['description']}")
    print("-" * 60)


def list_test_urls():
    """Display available test URLs"""
    print("\nAvailable test URLs:")
    print("-" * 60)
    for name, url in TEST_URLS.items():
        print(f"  {name:15} - {url}")
    print("-" * 60)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Test Tor proxy connectivity with configurable options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://example.com
  %(prog)s --preset moderate --url google
  %(prog)s --url torproject --concurrency 20 --delay 0.5
  %(prog)s --list-presets
  %(prog)s --list-urls
        """
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="Target URL or preset name (use --list-urls to see options)"
    )
    
    parser.add_argument(
        "--preset",
        type=str,
        choices=PRESETS.keys(),
        help="Use a preset configuration (see --list-presets)"
    )
    
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        help="Number of concurrent workers (default: 10)"
    )
    
    parser.add_argument(
        "-d", "--delay",
        type=float,
        help="Delay between batches in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "-p", "--proxy",
        type=str,
        default="socks5://127.0.0.1:9050",
        help="Proxy URL (default: socks5://127.0.0.1:9050)"
    )
    
    parser.add_argument(
        "-m", "--max-requests",
        type=int,
        help="Maximum number of requests to send (default: unlimited)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output for each request"
    )
    
    parser.add_argument(
        "--connect-timeout",
        type=int,
        default=5,
        help="Connection timeout in seconds (default: 5)"
    )
    
    parser.add_argument(
        "--total-timeout",
        type=int,
        default=10,
        help="Total request timeout in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available presets and exit"
    )
    
    parser.add_argument(
        "--list-urls",
        action="store_true",
        help="List available test URLs and exit"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    if args.list_presets:
        list_presets()
        sys.exit(0)
    
    if args.list_urls:
        list_test_urls()
        sys.exit(0)
    
    if not args.url:
        print("Error: --url is required")
        print("Use --list-urls to see available preset URLs")
        sys.exit(1)
    
    url = TEST_URLS.get(args.url, args.url)
    
    concurrency = args.concurrency or 10
    delay = args.delay if args.delay is not None else 1.0
    
    if args.preset:
        preset = PRESETS[args.preset]
        if args.concurrency is None:
            concurrency = preset["concurrency"]
        if args.delay is None:
            delay = preset["delay"]
    
    try:
        asyncio.run(
            async_get_loop(
                url=url,
                concurrency=concurrency,
                delay=delay,
                proxy=args.proxy,
                max_requests=args.max_requests,
                verbose=args.verbose,
                connect_timeout=args.connect_timeout,
                total_timeout=args.total_timeout
            )
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
