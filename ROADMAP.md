# Roadmap

> Our vision for the future of Key-Value

This roadmap outlines our planned features and improvements. Timelines are estimates and may change based on user feedback and priorities.

**Last Updated**: November 5, 2025

---

## ✅ Completed (Recent)

### Q3-Q4 2025
- [x] **SDK Consolidation**: Merged all SDKs into monorepo for consistency
- [x] **Python SDK**: 11 production-ready examples (clipboard sync, IP tracker, sensors, etc.)
- [x] **JavaScript/TypeScript**: Full type safety and browser support
- [x] **Go SDK**: Idiomatic Go with goroutines support
- [x] **Rust SDK**: Memory-safe with tokio async
- [x] **C SDK**: Optimized for embedded systems (Raspberry Pi, ESP32, OpenWRT)
- [x] **Time-Series History**: Event log with classification and filtering
- [x] **Optimistic Concurrency**: PATCH with version-based conflict detection
- [x] **Batch Operations**: Up to 100 operations per request
- [x] **Schema Validation**: JSON Schema support across all SDKs

---

## 🚀 In Progress (Q4 2025 - Q1 2026)

### Priority 1: Foundation & Trust
**Goal**: Build confidence and stability for production use

- [ ] **SOC2 Type II Certification** (In progress, expected Q2 2026)
  - Third-party security audit
  - Compliance with enterprise requirements

- [ ] **CLI Tool (`kv`)** (In development)
  - `kv push`, `kv pull`, `kv ls`, `kv tail`, `kv delete`
  - Token management and configuration
  - Batch operations and scripting support
  - Cross-platform (Linux, macOS, Windows)

- [ ] **Web Dashboard** (In development)
  - Usage analytics and metrics
  - Token management
  - Data browser and editor
  - Webhook configuration
  - Team management (Pro/Enterprise)

- [ ] **Enhanced Documentation**
  - Interactive quickstart guide
  - Video tutorials for each SDK
  - Architecture diagrams
  - Best practices guide

### Priority 2: Developer Experience
**Goal**: Make Key-Value the easiest data backend to use

- [ ] **Improved Onboarding**
  - Interactive tutorial
  - Sample projects (templates)
  - Reduce time-to-first-value to < 2 minutes

- [ ] **VS Code Extension**
  - Token management
  - Data browsing
  - Code snippets for all SDKs

- [ ] **GitHub Actions Integration**
  - Deploy tokens with CI/CD
  - Automated testing with Key-Value

- [ ] **More Examples**
  - Next.js starter template
  - React hooks (`useKeyValue`)
  - Vue composables
  - Svelte stores

---

## 📅 Q1 2026: IoT & Embedded Focus

### Goal: Become the #1 data backend for IoT developers

- [ ] **Arduino Library** (C++ wrapper)
  - ESP32 and ESP8266 support
  - PlatformIO integration
  - Examples for common sensors (DHT22, BME280, etc.)

- [ ] **Home Assistant Integration**
  - Custom component for Home Assistant
  - Easy sensor data storage
  - Automation triggers

- [ ] **Node-RED Nodes**
  - `keyvalue-store` and `keyvalue-retrieve` nodes
  - Visual flow programming for IoT

- [ ] **Raspberry Pi Official Partner**
  - Featured in Raspberry Pi documentation
  - Pre-installed in Raspberry Pi OS (explore)
  - Case studies with Raspberry Pi projects

- [ ] **Edge Computing Support**
  - Multi-region replication
  - Geo-distributed storage
  - Cloudflare Workers integration

---

## 📅 Q2 2026: Enterprise & Teams

### Goal: Make Key-Value enterprise-ready

- [ ] **Teams & Organizations**
  - Role-based access control (RBAC)
  - Team workspaces
  - Shared tokens with permissions

- [ ] **SSO/SAML Authentication**
  - Google Workspace, Okta, Azure AD
  - SAML 2.0 support

- [ ] **Advanced Audit Logs**
  - Detailed action logs
  - Compliance reporting (GDPR, HIPAA)
  - Export to SIEM systems

- [ ] **Custom SLAs**
  - 99.9%, 99.95%, 99.99% uptime options
  - Financial credits for downtime
  - Dedicated account manager

- [ ] **Multi-Region Deployment**
  - US East, US West, EU, Asia data centers
  - Data residency compliance
  - Automatic failover

- [ ] **On-Premises Option**
  - Managed on-premises deployment
  - Air-gapped environments
  - Custom hardware support

---

## 📅 Q3 2026: AI & Intelligence

### Goal: Make data smarter with AI

- [ ] **Enhanced Event Classification**
  - Better AI models for event types
  - Custom classification training
  - Confidence scores and explanations

- [ ] **Anomaly Detection**
  - Automatic anomaly alerts
  - Machine learning-based detection
  - Custom threshold configuration

- [ ] **Predictive Analytics**
  - Forecast future values (time-series)
  - Trend analysis
  - Usage predictions

- [ ] **Natural Language Queries**
  - Ask questions about your data in plain English
  - "Show me all temperature readings above 30°C last week"

- [ ] **Vector Embeddings**
  - Store and search semantic data
  - Similar data recommendations
  - AI-powered search

---

## 📅 Q4 2026: Platform & Ecosystem

### Goal: Build a thriving ecosystem

- [ ] **Marketplace**
  - Community-contributed SDKs
  - Pre-built integrations
  - Templates and examples
  - Revenue sharing for creators

- [ ] **Webhooks & Integrations**
  - Zapier app
  - IFTTT applet
  - Make.com integration
  - Webhooks on data changes

- [ ] **Terraform Provider**
  - Infrastructure as code
  - Token management
  - Configuration automation

- [ ] **Kubernetes Operator**
  - Deploy Key-Value in Kubernetes
  - CRDs for tokens and configuration
  - Automatic scaling

- [ ] **GraphQL API**
  - Alternative to REST API
  - Efficient queries
  - Subscriptions for real-time updates

---

## 📅 2027: Vertical Solutions

### Goal: Package best examples into standalone SaaS products

- [ ] **IP Tracker SaaS** (from `ip_tracker.py`)
  - Hosted dashboard
  - Dynamic DNS alternative
  - Email/SMS alerts on IP changes

- [ ] **Clipboard Sync SaaS** (from `clipboard_sync.py`)
  - Universal clipboard across devices
  - Browser extensions (Chrome, Firefox)
  - Mobile apps (iOS, Android)

- [ ] **One-Time Secret SaaS** (from `one_time_secret.py`)
  - Password sharing tool
  - Self-destructing messages
  - Compliance tracking

- [ ] **Sensor Dashboard SaaS** (from `sensor_dashboard.py`)
  - No-code IoT monitoring
  - Pre-built sensor integrations
  - Custom dashboards and alerts

---

## 🌟 Future Exploration (2027+)

Ideas we're exploring but not yet committed to:

- [ ] **Mobile SDKs**: Swift (iOS), Kotlin (Android), Flutter/Dart
- [ ] **Desktop SDKs**: Electron integration, Tauri support
- [ ] **Blockchain Integration**: Decentralized storage option
- [ ] **Local-First**: CRDT support for offline-first apps
- [ ] **Database Adapters**: SQL interface for Key-Value data
- [ ] **Message Queue**: Pub/sub messaging on top of history API
- [ ] **Time-Series Database**: Optimized for sensor data
- [ ] **Object Storage**: Store files and media (not just JSON)

---

## 🗳️ Community Input

We want to build what YOU need! Vote on features or suggest new ones:

- **GitHub Discussions**: [github.com/mikro-design/key-value.sdk/discussions](https://github.com/mikro-design/key-value.sdk/discussions)
- **Discord**: [discord.gg/keyvalue](https://discord.gg/keyvalue)
- **Feature Requests**: Open an issue with the `enhancement` label

---

## 📊 Success Metrics

We measure progress against these goals:

### Q1 2026 Targets
- 1,000 active users/tokens
- 50+ community members
- 5+ IoT partnerships initiated
- SOC2 audit in progress

### Q2 2026 Targets
- 5,000 active users/tokens
- 100K API requests/month
- 20% MoM growth
- 5+ enterprise customers

### Q4 2026 Targets
- 25,000 active users/tokens
- 1M+ API requests/month
- $10K MRR
- Top 3 ranking for "memorable token API" search

---

## 💬 Stay Updated

- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
- **Blog**: [key-value.co/blog](https://key-value.co/blog)
- **Twitter**: [@keyvalue_co](https://twitter.com/keyvalue_co)
- **Email Newsletter**: [Subscribe](https://key-value.co/newsletter)

---

## 🤝 Contributing

Want to help build the future? See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to:
- Submit feature requests
- Contribute code
- Write documentation
- Report bugs
- Join the community

---

## ⚖️ Our Commitment

We're committed to:

1. **Transparency**: Open roadmap, open source, open communication
2. **Stability**: Grandfather pricing, 60-day notice for changes, free tier forever
3. **Quality**: Security first, thorough testing, excellent documentation
4. **Community**: Listen to users, respond to feedback, build together

**Key-Value is here to stay.** We're building for the long term, not a quick exit.

---

**Questions about the roadmap?** Email us at [hello@key-value.co](mailto:hello@key-value.co) or join our [Discord](https://discord.gg/keyvalue).
