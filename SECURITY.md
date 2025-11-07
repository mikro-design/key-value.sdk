# Security Policy

## Our Commitment

Security is a top priority for Key-Value. We're committed to protecting your data and maintaining the trust you place in our service.

---

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

### Contact

- **Email**: [security@key-value.co](mailto:security@key-value.co)
- **PGP Key**: Available at [key-value.co/pgp](https://key-value.co/pgp)

### What to Include

Please provide:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)

### Response Timeline

- **Initial response**: Within 24 hours
- **Confirmation**: Within 72 hours
- **Fix timeline**: Depends on severity (critical issues prioritized)
- **Disclosure**: Coordinated with reporter after fix is deployed

### Bug Bounty

We offer rewards for responsibly disclosed security issues:
- **Critical**: $500-$2,000
- **High**: $200-$500
- **Medium**: $50-$200
- **Low**: Public acknowledgment

---

## Security Practices

### Data Protection

#### Encryption
- **In Transit**: All API communication uses **TLS 1.3** with perfect forward secrecy
- **At Rest**: All data stored with **AES-256** encryption
- **Keys**: Hardware Security Modules (HSMs) for key management

#### Client-Side Encryption (Optional)
For sensitive data, we recommend client-side encryption before storage:

**Python Example**:
```python
from keyvalue import KeyValueClient
from cryptography.fernet import Fernet

# Generate key (store securely!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt before storing
client = KeyValueClient(token="your-token")
sensitive_data = {"password": "secret123"}
encrypted = cipher.encrypt(json.dumps(sensitive_data).encode())
client.store({"data": encrypted.decode()})

# Decrypt after retrieval
response = client.retrieve()
decrypted = cipher.decrypt(response['data']['data'].encode())
```

See [python/examples/encrypted_example.py](./python/examples/encrypted_example.py) for full implementation.

### Authentication

#### Token-Based Access
- **5-word tokens** generated using cryptographically secure randomness
- **Token entropy**: 2^64 combinations (18.4 quintillion possibilities)
- **Rate limiting**: Protection against brute-force attacks
- **No password requirements**: Tokens act as bearer credentials

#### Best Practices for Tokens
- Treat tokens like passwords (never commit to Git)
- Use environment variables: `export KV_TOKEN="your-token"`
- Rotate tokens periodically for sensitive applications
- Use different tokens for dev/staging/production

### Infrastructure Security

#### Hosting & Compliance
- Hosted on **AWS** with SOC2-compliant infrastructure
- **Multi-region redundancy** for high availability
- **DDoS protection** via Cloudflare
- **Automatic backups** every 6 hours with 30-day retention
- **Disaster recovery** plan with <4 hour RTO (Recovery Time Objective)

#### Monitoring & Detection
- 24/7 security monitoring and alerting
- Automated intrusion detection systems (IDS)
- Log aggregation and analysis
- Regular penetration testing by third-party security firms

### Access Control

#### Internal Access
- **Principle of least privilege** for all team members
- **Multi-factor authentication** (MFA) required for all staff
- **Audit logs** for all administrative actions
- **Background checks** for employees with data access

### Vulnerability Management

#### Security Audits
- **Annual penetration testing** by certified security professionals
- **Quarterly dependency audits** (npm, pip, cargo, Go modules)
- **Automated vulnerability scanning** on every deployment
- **CVE monitoring** for all infrastructure components

#### Patch Management
- **Critical vulnerabilities**: Patched within 24 hours
- **High severity**: Patched within 1 week
- **Medium/Low severity**: Patched in regular release cycle

### Secure Development

#### SDLC Security
- **Code review** required for all changes
- **Automated security testing** in CI/CD pipeline
- **Static analysis** (linting, type checking, security linters)
- **Dependency scanning** for known vulnerabilities
- **Secrets scanning** to prevent credential leaks

#### SDK Security
All SDKs follow security best practices:
- **Type safety** (TypeScript, Rust, Go) to prevent injection attacks
- **Input validation** for all API requests
- **No eval()** or unsafe code execution
- **Secure defaults** (HTTPS only, token validation)

---

## Data Privacy

### Data Handling

#### What We Store
- **Your data**: JSON payloads you store via the API
- **Metadata**: Timestamps, versions, IP addresses (for rate limiting)
- **No PII required**: No name, email, or personal info needed for free tier

#### What We DON'T Store
- **Passwords**: We don't have user passwords (token-based only)
- **Payment details**: Handled by Stripe (PCI-DSS compliant), we never see card numbers
- **Unencrypted sensitive data**: We recommend client-side encryption

### Data Retention

- **Active tokens**: Data retained while token is active
- **Expired tokens**: Deleted after TTL expiration
- **Deleted tokens**: Immediate deletion (soft delete for 7 days, then permanent)
- **Backups**: Retained for 30 days for disaster recovery

### Compliance

#### Regulations
- **GDPR** (EU General Data Protection Regulation): Compliant
- **CCPA** (California Consumer Privacy Act): Compliant
- **SOC2 Type II**: Certification in progress (expected Q2 2026)

#### Data Subject Rights
Under GDPR/CCPA, you have the right to:
- **Access**: Request a copy of your data
- **Rectification**: Correct inaccurate data
- **Erasure**: Delete your data ("right to be forgotten")
- **Portability**: Export your data in machine-readable format

Contact [privacy@key-value.co](mailto:privacy@key-value.co) for data requests.

### Data Location

- **Primary**: US East (AWS us-east-1)
- **Backups**: US West (AWS us-west-2) and EU (AWS eu-west-1)
- **Enterprise**: Custom data residency options available (US, EU, Asia)

---

## Rate Limiting & Abuse Prevention

### Rate Limits
- **Free tier**: 100 requests/minute per IP
- **Paid tiers**: Higher limits based on plan
- **Purpose**: Prevent abuse, ensure fair usage, DDoS protection

### Abuse Detection
We monitor for and block:
- Brute-force token guessing attempts
- Spam or malicious content storage
- Distributed attacks
- Cryptocurrency mining coordination
- Illegal content

### Consequences
- **First offense**: Warning email
- **Repeated abuse**: Temporary suspension (24 hours)
- **Severe abuse**: Permanent ban, law enforcement notification (if illegal)

---

## Incident Response

### In Case of Breach

If we detect or are notified of a security incident:

1. **Immediate containment** (within 1 hour)
2. **Root cause analysis** (within 24 hours)
3. **User notification** (within 72 hours, or sooner if required by law)
4. **Remediation** and security improvements
5. **Public disclosure** (after users notified and fix deployed)

### Status Page
- Real-time service status: [status.key-value.co](https://status.key-value.co)
- Incident notifications via email/SMS (opt-in)

---

## Self-Hosting Security

If you self-host Key-Value:

### Your Responsibilities
- **Keeping software updated** with security patches
- **Configuring firewalls** and network security
- **Managing TLS certificates**
- **Backup and disaster recovery**
- **Monitoring and intrusion detection**

### Our Support
- Security advisories published on GitHub Security tab
- CVE notifications for critical vulnerabilities
- Docker images with security best practices

---

## Third-Party Dependencies

### Dependency Management
- All dependencies audited before inclusion
- Automated scanning: `npm audit`, `pip check`, `cargo audit`, `go mod tidy`
- Dependabot enabled for automatic security updates
- Minimal dependencies (reduce attack surface)

### Major Dependencies
- **Python**: `requests`, `cryptography`
- **JavaScript**: `node-fetch` (or native fetch)
- **Go**: Standard library (minimal external deps)
- **Rust**: `tokio`, `serde`, `reqwest`
- **C**: `libcurl`, `json-c`

---

## Security Best Practices for Users

### For Developers

1. **Never commit tokens to Git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.token" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   export KV_TOKEN="your-five-word-token"
   ```

3. **Rotate tokens for production**
   - Generate new token
   - Update production environment
   - Delete old token

4. **Use client-side encryption for sensitive data**
   - See [python/examples/encrypted_example.py](./python/examples/encrypted_example.py)

5. **Validate data on retrieval**
   - Don't trust data implicitly
   - Validate types and schemas

6. **Rate limit your own apps**
   - Don't make unnecessary requests
   - Cache when possible
   - Use batch operations

### For IoT/Embedded Developers

1. **Secure token storage**
   - Use encrypted flash storage
   - Never hardcode in firmware
   - Consider hardware secure elements (e.g., ATECC608)

2. **Use HTTPS (TLS)**
   - Don't skip certificate validation
   - Use updated TLS libraries

3. **Update firmware regularly**
   - Include security patches
   - OTA update capability

4. **Network security**
   - Firewall embedded devices
   - Segment IoT network from main network

---

## Security Checklist

Before deploying to production:

- [ ] Tokens stored in environment variables (not in code)
- [ ] Using HTTPS URLs (not HTTP)
- [ ] Client-side encryption for sensitive data (optional but recommended)
- [ ] Rate limiting configured in your app
- [ ] Error handling for security responses (401, 403, 429)
- [ ] Monitoring and alerting configured
- [ ] Backup plan for token rotation
- [ ] Data validation on retrieval
- [ ] Tested on non-production environment first

---

## Contact & Resources

### Security Team
- **Email**: [security@key-value.co](mailto:security@key-value.co)
- **PGP Key**: [key-value.co/pgp](https://key-value.co/pgp)

### Resources
- [Security Best Practices Guide](https://key-value.co/docs/security)
- [Encryption Example](./python/examples/encrypted_example.py)
- [Status Page](https://status.key-value.co)
- [Privacy Policy](https://key-value.co/privacy)
- [Terms of Service](https://key-value.co/terms)

### Community
- [GitHub Security Advisories](https://github.com/mikro-design/key-value.sdk/security/advisories)
- [Discord Security Channel](https://discord.gg/keyvalue)

---

**Last Updated**: November 5, 2025

We review and update this security policy quarterly. Subscribe to our [security mailing list](https://key-value.co/security-updates) for notifications.
