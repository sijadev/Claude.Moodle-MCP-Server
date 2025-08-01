# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.x.x   | :white_check_mark: |
| 2.x.x   | :x:                |
| 1.x.x   | :x:                |

## Security Considerations

### Administrative Tools (`tools/` directory)

The `tools/` directory contains administrative and setup scripts that are designed for:
- Local development environments
- Docker container management
- Database setup and configuration
- System administration tasks

These scripts intentionally use:
- `shell=True` in subprocess calls for Docker/database operations
- Hardcoded temporary paths for setup files
- Direct SQL queries for debugging/testing

**These are acceptable security practices for administrative tools** and should not be considered vulnerabilities in the production application code.

### Core Application Security

The core application code (`src/`, `config/`) follows security best practices:
- Environment variable configuration
- Secure hash usage with appropriate flags
- No hardcoded credentials in production code
- Proper input validation and sanitization

## Reporting a Vulnerability

If you discover a security vulnerability in the **core application code** (not administrative tools), please:

1. **Do NOT** create a public GitHub issue
2. Email security concerns to the maintainers
3. Include detailed steps to reproduce
4. Allow time for investigation and fixes

Security issues in administrative tools (`tools/` directory) are generally acceptable as these are development/deployment utilities.