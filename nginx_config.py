#!/usr/bin/env python3
import argparse
import os
import subprocess
from pathlib import Path

def create_nginx_config(server_name: str, proxy_pass: str) -> str:
    """Generate Nginx configuration content."""
    return f"""server {{
    listen 80;
    server_name {server_name};

    location / {{
        proxy_pass {proxy_pass};
        
        # Essential headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Cache control for static assets
        proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
        proxy_cache_bypass $http_upgrade;
    }}

    # Static file handling
    location /_next/static/ {{
        proxy_cache_valid 60m;
        proxy_pass {proxy_pass};
    }}
}}"""

def run_command(command: str) -> tuple[bool, str]:
    """Execute a shell command and return result."""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)

def save_config(content: str, filename: str, sites_path: str) -> tuple[bool, str]:
    """Save the configuration to a file and create symlink."""
    try:
        # Create sites-available directory if it doesn't exist
        available_path = os.path.join(sites_path, 'sites-available')
        enabled_path = os.path.join(sites_path, 'sites-enabled')
        os.makedirs(available_path, exist_ok=True)
        os.makedirs(enabled_path, exist_ok=True)

        # Save configuration file
        config_path = os.path.join(available_path, filename)
        with open(config_path, 'w') as f:
            f.write(content)

        # Create symlink
        symlink_path = os.path.join(enabled_path, filename)
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(config_path, symlink_path)

        return True, config_path
    except Exception as e:
        return False, str(e)

def test_and_reload_nginx() -> tuple[bool, str]:
    """Test Nginx configuration and reload if test passes."""
    # Test Nginx configuration
    success, result = run_command("nginx -t")
    if not success:
        return False, f"Nginx configuration test failed:\n{result}"

    # If test passes, reload Nginx
    success, result = run_command("systemctl reload nginx")
    if not success:
        return False, f"Nginx reload failed:\n{result}"

    return True, "Nginx configuration tested and reloaded successfully!"

def main():
    parser = argparse.ArgumentParser(
        description='Generate Nginx configuration for reverse proxy'
    )
    parser.add_argument(
        '--server-name',
        required=True,
        help='Server name (e.g., example.com)'
    )
    parser.add_argument(
        '--proxy-pass',
        required=True,
        help='Proxy pass URL (e.g., http://localhost:3002)'
    )
    parser.add_argument(
        '--output',
        default='site.conf',
        help='Output filename (default: site.conf)'
    )
    parser.add_argument(
        '--nginx-path',
        default='/etc/nginx',
        help='Nginx configuration directory (default: /etc/nginx)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print configuration without saving'
    )
    parser.add_argument(
        '--skip-reload',
        action='store_true',
        help='Skip testing and reloading Nginx'
    )

    args = parser.parse_args()

    # Generate configuration content
    config_content = create_nginx_config(args.server_name, args.proxy_pass)

    if args.dry_run:
        print("Generated configuration:")
        print("-" * 50)
        print(config_content)
        return

    # Save configuration
    success, result = save_config(config_content, args.output, args.nginx_path)

    if success:
        print(f"Configuration successfully created at: {result}")
        
        if not args.skip_reload:
            print("\nTesting and reloading Nginx configuration...")
            success, message = test_and_reload_nginx()
            if success:
                print("✓ Configuration test passed")
                print("✓ Nginx reloaded successfully")
            else:
                print("✗ Error:", message)
                print("\nPlease fix the configuration and run:")
                print("1. nginx -t")
                print("2. systemctl reload nginx")
    else:
        print(f"Error creating configuration: {result}")

if __name__ == "__main__":
    main()
