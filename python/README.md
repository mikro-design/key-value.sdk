# Python Examples for Key-Value Store

This folder contains Python examples demonstrating how to use the key-value web service.

## Requirements

```bash
# Basic requirements
pip install requests

# For encryption examples
pip install cryptography

# For clipboard sync
pip install pyperclip

# For webhook receiver
pip install flask

# For signal generator
pip install numpy

# For Raspberry Pi DHT sensors (optional)
pip install adafruit-circuitpython-dht
```

## Tokens

All examples assume you have already created a token via the key-value.co dashboard (or your own deployment). The scripts never delete tokens; they only store or overwrite data. Export your token before running scripts, or pass it explicitly:

```bash
export KV_TOKEN="your-five-word-token"
# or
python basic_example.py --token your-five-word-token
```

## Examples

### 1. Basic Example (`basic_example.py`)

Demonstrates basic operations with your pre-generated token:
- Store JSON data
- Retrieve data with version tracking
- Update data
- Display version and timestamp info

**Usage:**
```bash
# Provide your token via CLI flag or KV_TOKEN environment variable
python basic_example.py --token YOUR-FIVE-WORD-TOKEN
# or
KV_TOKEN=YOUR-FIVE-WORD-TOKEN python basic_example.py
```

### 2. Encrypted Example (`encrypted_example.py`)

Shows client-side encryption for sensitive data:
- Encrypt data before sending to server
- Store encrypted payload
- Decrypt on retrieval
- Server cannot read your data

**Usage:**
```bash
python encrypted_example.py --token YOUR-FIVE-WORD-TOKEN
```

### 3. IP Tracker (`ip_tracker.py`)

A practical service to track your external IP address:
- Detects your public IP automatically
- Stores with timestamp and history
- Monitor mode for continuous tracking
- Useful for dynamic IPs

**Usage:**

```bash
# Obtain a token first
TOKEN="your-five-word-token"

# One-time IP update
python ip_tracker.py --token $TOKEN update

# Continuous monitoring (check every 5 minutes)
python ip_tracker.py --token $TOKEN monitor --interval 300

# Get stored IP data
python ip_tracker.py --token $TOKEN get
```

**Systemd Service Example:**

Create `/etc/systemd/system/ip-tracker.service`:

```ini
[Unit]
Description=IP Address Tracker
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/examples/python
ExecStart=/usr/bin/python3 ip_tracker.py --token your-token --url https://your-domain.com monitor --interval 300
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ip-tracker
sudo systemctl start ip-tracker
sudo systemctl status ip-tracker
```

### 4. Clipboard Sync (`clipboard_sync.py`) ⭐

Sync clipboard content between devices - super useful for daily workflows!

**Features:**
- Copy text on one device, paste on another
- Monitor mode for automatic sync
- Cross-platform (Linux, macOS, Windows)
- Push or pull modes

**Usage:**

```bash
TOKEN="your-five-word-token"

# Push local clipboard to cloud
python clipboard_sync.py --token $TOKEN push

# Pull cloud clipboard to local
python clipboard_sync.py --token $TOKEN pull

# Auto-sync mode (push on local clipboard change)
python clipboard_sync.py --token $TOKEN monitor --interval 2

# Auto-pull mode (pull when cloud clipboard changes)
python clipboard_sync.py --token $TOKEN monitor --mode pull --interval 5

# Check status
python clipboard_sync.py --token $TOKEN status
```

**Workflow Example:**
```bash
# On computer A:
echo "Important command: docker ps -a" | xclip -selection c
python clipboard_sync.py --token $TOKEN push

# On computer B:
python clipboard_sync.py --token $TOKEN pull
# Now paste - the text is in your clipboard!
```

### 5. One-Time Secret (`one_time_secret.py`) ⭐

Share passwords and API keys securely - they self-destruct after being read once.

**Features:**
- Auto-invalidate after first read
- Optional password protection
- Expiration time (TTL)
- Client-side encryption

**Usage:**

```bash
# Create a one-time secret
python one_time_secret.py create "Database password: MySecretPass123" --token YOUR-FIVE-WORD-TOKEN

# With password protection
python one_time_secret.py create "API Key: sk_live_123" --token YOUR-FIVE-WORD-TOKEN --prompt-password

# With expiration (1 hour = 3600 seconds)
python one_time_secret.py create "Temp token" --token YOUR-FIVE-WORD-TOKEN --ttl 3600

# Read a secret
python one_time_secret.py read your-five-word-token

# Read with password
python one_time_secret.py read your-five-word-token --prompt-password
```

**Real-world Example:**
```bash
# Share SSH private key temporarily
python one_time_secret.py create "$(cat ~/.ssh/id_rsa)" --token YOUR-FIVE-WORD-TOKEN --password MyPass --ttl 1800

# Send token to colleague via Slack/email
# They read it once, then it's gone forever
```

### 6. Sensor Dashboard (`sensor_dashboard.py`) ⭐

Track IoT sensor data - perfect for Raspberry Pi projects!

**Features:**
- Log temperature, humidity, pressure
- Automatic statistics (min, max, avg)
- Alert thresholds
- DHT22/DHT11 sensor support
- Custom sensor commands

**Usage:**

```bash
TOKEN="your-five-word-token"

# Manual logging
python sensor_dashboard.py --token $TOKEN log --temp 23.5 --humidity 45.2

# View current readings
python sensor_dashboard.py --token $TOKEN view

# View statistics
python sensor_dashboard.py --token $TOKEN stats

# View history
python sensor_dashboard.py --token $TOKEN view --history 10

# Raspberry Pi - Monitor DHT22 sensor on GPIO pin 4
python sensor_dashboard.py --token $TOKEN monitor --dht-pin 4 --interval 300

# Custom sensor command (outputs JSON)
python sensor_dashboard.py --token $TOKEN monitor \
  --command "python read_my_sensor.py" --interval 60
```

**Custom Sensor Script Example:**

Create `read_my_sensor.py`:
```python
#!/usr/bin/env python3
import json
import random

# Read your actual sensor here
temperature = random.uniform(20, 25)
humidity = random.uniform(40, 60)

print(json.dumps({
    "temperature": temperature,
    "humidity": humidity
}))
```

### 7. Webhook Receiver (`webhook_receiver.py`) ⭐

Catch webhooks from GitHub, Stripe, etc. without deploying a server!

**Features:**
- Local webhook receiver
- Store and view payloads
- Works with any webhook provider
- Great for debugging

**Usage:**

```bash
TOKEN="your-five-word-token"

# Start webhook server
python webhook_receiver.py --token $TOKEN serve --port 5000

# Expose to internet with ngrok (in another terminal)
ngrok http 5000

# Configure your webhook provider to send to:
# https://your-ngrok-url/webhook/YOUR-TOKEN

# View received webhooks
python webhook_receiver.py --token $TOKEN list

# View specific webhook
python webhook_receiver.py --token $TOKEN view 0

# Send test webhook
python webhook_receiver.py --token $TOKEN test
```

**Example with GitHub:**
1. Start receiver: `python webhook_receiver.py --token $TOKEN serve`
2. Expose with ngrok: `ngrok http 5000`
3. Go to GitHub repo → Settings → Webhooks
4. Add webhook URL: `https://abc123.ngrok.io/webhook/YOUR-TOKEN`
5. Push to repo and see webhooks appear!

### 8. PATCH Example (`patch_example.py`) ⭐

Demonstrates atomic partial updates with optimistic concurrency control.

**Features:**
- Atomic updates with version-based conflict detection
- Set nested fields using dot notation
- Remove fields
- Concurrent writer simulation
- Conflict resolution with retry logic

**Usage:**

```bash
TOKEN="your-five-word-token"

# Basic PATCH operations
python patch_example.py --token $TOKEN demo

# Concurrent counter (5 writers competing)
python patch_example.py --token $TOKEN counter --writers 5

# Complex nested object updates
python patch_example.py --token $TOKEN nested
```

**Key Concepts:**

The PATCH endpoint uses optimistic concurrency - each request includes a `version` number:
- If version matches, update succeeds and version increments
- If version doesn't match, returns 409 Conflict
- Client must fetch latest version and retry

**Example:**
```python
# Get current data and version
response = client.retrieve()
version = response['version']  # e.g., 5

# Update nested field
result = client.patch(
    version=5,
    set_fields={"profile.name": "Alice", "stats.count": 42}
)
# Success: new version is 6

# Another client tries to update with old version
result = client.patch(
    version=5,  # Outdated!
    set_fields={"profile.email": "alice@example.com"}
)
# Fails with 409 Conflict - must retry with version 6
```

### 9. History Example (`history_example.py`) ⭐

Query and analyze the complete time-series event log for a token.

**Features:**
- Query event history with filters
- Pagination support
- Filter by event type and time range
- Generate test data
- Analyze patterns and statistics
- Export history to JSON

**Usage:**

```bash
TOKEN="your-five-word-token"

# Generate test data (20 events)
python history_example.py --token $TOKEN generate --count 20

# View recent history
python history_example.py --token $TOKEN view

# View with filters
python history_example.py --token $TOKEN view --limit 10 --type store

# View events since a specific time
python history_example.py --token $TOKEN view --since 2025-10-20T00:00:00Z

# Paginate through results
python history_example.py --token $TOKEN view --limit 50 --before 100

# Analyze all history (statistics)
python history_example.py --token $TOKEN analyze

# Export to JSON file
python history_example.py --token $TOKEN export --output history.json
```

**History API Response:**
```json
{
  "success": true,
  "events": [
    {
      "seq": 5,
      "created_at": "2025-10-23T12:00:00Z",
      "expires_at": null,
      "classified_type": "sensor_reading",
      "numeric_value": 23.5,
      "text_value": null,
      "confidence": 0.95,
      "payload": {
        "type": "store",
        "data": {"temperature": 23.5}
      }
    }
  ],
  "pagination": {
    "limit": 50,
    "before": null,
    "since": null,
    "has_more": false
  }
}
```

### 10. Delete Example (`delete_example.py`)

Demonstrates how to permanently delete stored data.

**Features:**
- Delete with confirmation prompt
- View data before deleting
- Verify deletion
- Complete lifecycle demo (create → update → delete)
- Cleanup utility for test data

**Usage:**

```bash
TOKEN="your-five-word-token"

# Simple delete
python delete_example.py --token $TOKEN delete

# Delete with confirmation
python delete_example.py --token $TOKEN delete --confirm

# Show data before deleting
python delete_example.py --token $TOKEN delete --show --confirm

# Full lifecycle demo
python delete_example.py --token $TOKEN lifecycle

# Cleanup test/expired data
python delete_example.py --token $TOKEN cleanup --yes
```

**Lifecycle Demo:**
Shows complete workflow:
1. Create initial data
2. Verify creation
3. Update data
4. Delete data
5. Verify deletion (returns 404)
6. Attempt second delete (fails with 404)

### 11. Signal Generator (`signal_generator.py`) ⭐

Generate realistic sensor signals for testing time-series features and dashboards.

**Features:**
- Multiple signal types: sine, random walk, step, sawtooth, noise, spike, exponential decay
- 10+ sensor types: temperature, humidity, pressure, CPU, memory, voltage, light, CO2, vibration, power
- Simple mode: single sensor
- Complex mode: multi-sensor systems with correlations
- Configurable sample interval (every N seconds)
- **Overwrites existing data** with fresh sensor readings (token stays in dashboard)
- View history of generated signals
- Perfect for testing the history API

**Usage:**

```bash
TOKEN="your-five-word-token"

# Simple sine wave temperature sensor (default: every 2 seconds)
python signal_generator.py --token $TOKEN simple --type temperature --signal sine

# CPU usage random walk, sample every 10 seconds
python signal_generator.py --token $TOKEN simple --type cpu --signal random_walk --interval 10

# Generate 100 samples then stop (using alias 'temp')
python signal_generator.py --token $TOKEN simple --type temp --signal sine --iterations 100

# Run 50 samples with 1 second interval
python signal_generator.py --token $TOKEN simple --type cpu --iterations 50 --interval 1

# Complex multi-sensor system (using aliases)
python signal_generator.py --token $TOKEN complex --sensors temp,hum,press

# IoT device simulation, sample every 10 seconds
python signal_generator.py --token $TOKEN complex --sensors cpu,mem,temp --interval 10

# View generated history
python signal_generator.py --token $TOKEN history --limit 100
```

**Key Options:**
- `--interval N` - Sample every N seconds (default: 2s for simple, 5s for complex)
- `--iterations N` - Generate exactly N samples then stop (default: infinite, run until Ctrl+C)
- `--signal TYPE` - Choose signal pattern (sine, random_walk, step, etc.)

**Important:** The signal generator **overwrites existing data** for the token with each sample. Your token remains visible in the dashboard, but the data is replaced with fresh sensor readings. The version number starts from the last state and increments with each update.

**Available Sensor Types:**
- `temperature` (alias: `temp`) - Temperature in °C (-40 to 85°C)
- `humidity` (alias: `hum`) - Relative humidity (0-100%)
- `pressure` (alias: `press`) - Atmospheric pressure (950-1050 hPa)
- `cpu` - CPU utilization (0-100%)
- `memory` (alias: `mem`) - Memory usage (0-100%)
- `voltage` (alias: `volt`) - Voltage reading (0-12V)
- `light` - Light intensity (0-100000 lux)
- `co2` - CO2 concentration (300-5000 ppm)
- `vibration` (alias: `vib`) - Vibration intensity (0-10g)
- `power` (alias: `pwr`) - Power consumption (0-5000W)

**Available Signal Types:**
- `sine` - Smooth sinusoidal wave
- `random_walk` - Brownian motion, realistic sensor drift
- `step` - Step function, simulates on/off states
- `sawtooth` - Linear ramp up/down
- `noise` - Pure random noise
- `spike` - Random spikes on baseline
- `exponential_decay` - Decay from peak to baseline

**Real-world Examples:**

```bash
# Simulated HVAC temperature sensor
python signal_generator.py --token $TOKEN simple --type temperature --signal random_walk --interval 60

# Server monitoring (CPU + Memory)
python signal_generator.py --token $TOKEN complex --sensors cpu,memory,temperature --interval 30

# Environmental monitoring station
python signal_generator.py --token $TOKEN complex --sensors temperature,humidity,pressure,light,co2 --interval 300

# Power monitoring with spikes
python signal_generator.py --token $TOKEN simple --type power --signal spike --interval 1
```

## Configuration

All examples default to the hosted service at `https://key-value.co`. To point at another deployment:

1. Set an environment variable before running: `export API_URL=https://your-domain.com`
2. (Optional) For scripts with CLI support, pass `--url https://your-domain.com`

## Security Notes

- **Basic Example**: Data is stored unencrypted on the server
- **Encrypted Example**: Data is encrypted client-side; server never sees plaintext
- **IP Tracker**: Stores public IP (not sensitive), but you can combine with encryption
- **Clipboard Sync**: Clipboard content is stored as-is; use encryption for sensitive data
- **One-Time Secret**: Uses client-side encryption with password-based key derivation
- **Sensor Dashboard**: Sensor data typically not sensitive, stored unencrypted
- **Webhook Receiver**: Webhook payloads stored unencrypted; inspect before sharing tokens
- **PATCH Example**: Demonstrates version tracking and conflict resolution
- **History Example**: Shows time-series event log, useful for debugging
- **Delete Example**: Permanent deletion - use with caution
- **Signal Generator**: Test data only, not sensitive

## Common Issues

**Rate Limiting:**
- Free tier: 10 requests/minute per IP
- If you hit limits, wait and retry

**Connection Errors:**
- Ensure the API server is running
- Check the API_URL is correct
- Verify network connectivity

**Token Not Found:**
- Token must be stored before retrieval
- Tokens are case-sensitive
- Use exact 5-word token from generation
