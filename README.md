# Nginx Configuration Generator
A command-line tool for generating and managing Nginx reverse proxy configurations.

## Overview
This Python script automates the creation and deployment of Nginx reverse proxy configurations. It handles the creation of configuration files, symlinks, testing of the configuration, and reloading of the Nginx service.

## Prerequisites
- Python 3.6 or higher
- Nginx installed on the system
- Sudo/root privileges for file operations and service management

## Installation
1. Download the script:
```bash
wget https://raw.githubusercontent.com/yourusername/nginx-config-generator/main/nginx_config.py
```

2. Make it executable:
```bash
chmod +x nginx_config.py
```

3. Optionally, move to your PATH:
```bash
sudo mv nginx_config.py /usr/local/bin/nginx-config
```

## Usage

### Basic Command Syntax
```bash
sudo python3 nginx_config.py --server-name DOMAIN --proxy-pass URL [OPTIONS]
```

### Required Arguments
- `--server-name`: The domain name or server name (e.g., example.com)
- `--proxy-pass`: The URL to proxy requests to (e.g., http://localhost:3002)

### Optional Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--output` | site.conf | Output filename for the configuration |
| `--nginx-path` | /etc/nginx | Path to Nginx configuration directory |
| `--dry-run` | False | Preview configuration without saving |
| `--skip-reload` | False | Skip testing and reloading Nginx |

### Example Commands

1. Basic configuration:
```bash
sudo python3 nginx_config.py \
    --server-name example.com \
    --proxy-pass http://localhost:3002
```

2. Custom configuration name and path:
```bash
sudo python3 nginx_config.py \
    --server-name example.com \
    --proxy-pass http://localhost:3002 \
    --output myapp.conf \
    --nginx-path /opt/nginx
```

3. Preview configuration without saving:
```bash
python3 nginx_config.py \
    --server-name example.com \
    --proxy-pass http://localhost:3002 \
    --dry-run
```

4. Skip automatic Nginx reload:
```bash
sudo python3 nginx_config.py \
    --server-name example.com \
    --proxy-pass http://localhost:3002 \
    --skip-reload
```

## Generated Configuration Details

### Default Configuration Template
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3002;
        
        # Essential headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Cache control for static assets
        proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
        proxy_cache_bypass $http_upgrade;
    }

    # Static file handling
    location /_next/static/ {
        proxy_cache_valid 60m;
        proxy_pass http://localhost:3002;
    }
}
```

### Features
- HTTP reverse proxy configuration
- Headers for proper proxy functioning
- Cache control for static assets
- Optimized static file handling for Next.js applications

## File Locations
- Configurations are saved in: `{nginx_path}/sites-available/`
- Symlinks are created in: `{nginx_path}/sites-enabled/`

## Automatic Operations
1. Creates necessary directories if they don't exist
2. Generates the configuration file
3. Creates/updates symlink
4. Tests Nginx configuration (`nginx -t`)
5. Reloads Nginx service (`systemctl reload nginx`)

## Error Handling
The script includes error handling for:
- File permission issues
- Invalid Nginx configurations
- Service reload failures
- Directory creation problems

## Exit Codes
- 0: Success
- Non-zero: Various error conditions (standard Python error codes)

## Troubleshooting

### Common Issues

1. Permission Denied
```bash
Error creating configuration: Permission denied: '/etc/nginx/sites-available/site.conf'
```
Solution: Run the script with sudo privileges

2. Nginx Test Failed
```bash
✗ Error: Nginx configuration test failed
```
Solution: Check the generated configuration for syntax errors

3. Reload Failed
```bash
✗ Error: Nginx reload failed
```
Solution: Check Nginx service status and logs

### Debug Steps
1. Use `--dry-run` to verify configuration
2. Check file permissions
3. Verify Nginx service status
4. Review Nginx error logs

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
MIT License - Feel free to use and modify this script for your needs.
