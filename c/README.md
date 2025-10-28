# C Examples for Key-Value Store

This repository contains C examples for interacting with the key-value web service. Perfect for embedded systems, IoT devices, and performance-critical applications.

## Features

- 🚀 **Lightweight** - Minimal dependencies (libcurl + json-c)
- ⚡ **Fast** - Native C performance
- 🔌 **Portable** - Works on Linux, macOS, embedded systems
- 🛠️ **Easy to integrate** - Simple, self-contained examples

## Requirements

### Libraries

- **libcurl** - HTTP client library
- **json-c** - JSON parser
- **gcc** or **clang** - C compiler

### Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y libcurl4-openssl-dev libjson-c-dev build-essential
```

**macOS (Homebrew):**
```bash
brew install curl json-c
```

**Fedora/RHEL:**
```bash
sudo dnf install libcurl-devel json-c-devel gcc
```

## Quick Start

```bash
# Build all examples
make

# Or build individually
gcc -o basic_example basic_example.c -lcurl -ljson-c
gcc -o ip_tracker ip_tracker.c -lcurl -ljson-c
gcc -o sensor_dashboard sensor_dashboard.c -lcurl -ljson-c -lm
```

## Examples

### 1. Basic Example (`basic_example.c`)

Demonstrates fundamental operations:
- Generate a memorable token
- Store JSON data
- Retrieve data

**Usage:**
```bash
./basic_example
```

**Output:**
```
=== Key-Value Store - Basic Example ===

1. Generating token...
   Token: capable-germinate-disbelief-survival-quantum

2. Storing data...
   Store response: {"success":true,"message":"Data stored successfully"}
   ✓ Data stored successfully

3. Retrieving data...
   Retrieved data:
   {
     "user": "alice",
     "settings": {
       "theme": "dark",
       "notifications": true
     },
     "scores": [95, 87, 92]
   }
   ✓ Data successfully retrieved!
```

### 2. IP Tracker (`ip_tracker.c`)

Track your external IP address - perfect for dynamic DNS, remote access, etc.

**Features:**
- Automatic external IP detection
- Change tracking with history
- Monitor mode for continuous updates
- Lightweight enough for embedded devices

**Usage:**

```bash
# Generate a token first (using basic_example or curl)
TOKEN="your-five-word-token"

# One-time IP update
./ip_tracker $TOKEN update
# Output:
# Current IP: 203.0.113.42
# ✓ IP unchanged

# Get stored IP data
./ip_tracker $TOKEN get
# Output:
# Stored IP data:
# {
#   "ip": "203.0.113.42",
#   "last_updated": "2025-01-14T09:30:00Z",
#   "changed": false,
#   "history": []
# }

# Continuous monitoring (check every 5 minutes)
./ip_tracker $TOKEN monitor 300
# Output:
# Starting IP monitor (checking every 300 seconds)
# Press Ctrl+C to stop
#
# [2025-01-14 09:30:00] IP unchanged: 203.0.113.42
# [2025-01-14 09:35:00] IP CHANGED!
#   Old: 203.0.113.42
#   New: 198.51.100.123
```

**Running as a Service (systemd):**

Create `/etc/systemd/system/ip-tracker.service`:
```ini
[Unit]
Description=IP Address Tracker
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/ip_tracker your-token monitor 300
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

### 3. Sensor Dashboard (`sensor_dashboard.c`)

Log sensor data for IoT and embedded systems.

**Features:**
- Temperature, humidity, pressure logging
- Automatic statistics (min, max, avg)
- Alert thresholds
- Monitor mode with configurable interval
- History tracking (last 100 readings)

**Usage:**

```bash
TOKEN="your-five-word-token"

# Log a single reading
./sensor_dashboard $TOKEN log 23.5 45.2
# Output:
# ✓ Reading logged
#   Temperature: 23.5°C
#   Humidity: 45.2%

# Log with pressure
./sensor_dashboard $TOKEN log 22.1 48.5 1013.25

# View current readings
./sensor_dashboard $TOKEN view
# Output:
# Current readings:
# {
#   "timestamp": "2025-01-14T09:30:00Z",
#   "temperature": 23.5,
#   "humidity": 45.2
# }

# View statistics
./sensor_dashboard $TOKEN stats
# Output:
# Statistics:
# {
#   "temperature": {
#     "min": 18.2,
#     "max": 28.7,
#     "avg": 23.4,
#     "count": 42
#   },
#   "humidity": {
#     "min": 35.1,
#     "max": 65.8,
#     "avg": 48.3,
#     "count": 42
#   },
#   "total_readings": 42
# }

# Monitor mode (read every 5 minutes)
./sensor_dashboard $TOKEN monitor 300
# Output:
# Starting sensor monitor (reading every 300 seconds)
# Note: Using simulated sensor data. Replace read_sensor() with real sensor code.
# Press Ctrl+C to stop
#
# [2025-01-14 09:30:00] Temp: 23.5°C, Humidity: 45.2%
# [2025-01-14 09:35:00] Temp: 31.2°C, Humidity: 52.1%
# ⚠️  High temperature: 31.2°C
```

**Integrating Real Sensors:**

Replace the `read_sensor()` function with actual sensor code:

```c
// Example for DHT22 sensor (using WiringPi on Raspberry Pi)
#include <wiringPi.h>
#include <dht.h>

void read_sensor(double *temp, double *humidity, double *pressure) {
    int result = dht_read(22, 4); // DHT22 on GPIO pin 4

    if (result == DHT_SUCCESS) {
        *temp = dht_getTemperature();
        *humidity = dht_getHumidity();
        *pressure = NAN; // DHT22 doesn't measure pressure
    } else {
        *temp = NAN;
        *humidity = NAN;
        *pressure = NAN;
    }
}
```

## Configuration

All examples default to `http://localhost:3000`. To change the API URL, edit the `API_URL` define in each source file:

```c
#define API_URL "https://your-domain.com"
```

Then recompile:
```bash
make clean
make
```

## Cross-Compilation

### For Raspberry Pi (from x86_64 Linux):

```bash
# Install cross-compiler
sudo apt-get install gcc-arm-linux-gnueabihf

# Cross-compile
arm-linux-gnueabihf-gcc -o ip_tracker ip_tracker.c \
    -lcurl -ljson-c \
    -I/usr/arm-linux-gnueabihf/include \
    -L/usr/arm-linux-gnueabihf/lib
```

### For OpenWRT/LEDE:

```bash
# Set up OpenWRT SDK first
make menuconfig  # Select your target
make

# Use OpenWRT toolchain
${STAGING_DIR}/bin/mipsel-openwrt-linux-gcc -o ip_tracker ip_tracker.c \
    -lcurl -ljson-c
```

## Embedded Systems Integration

### ESP32 (ESP-IDF):

1. Add to `main/CMakeLists.txt`:
```cmake
idf_component_register(SRCS "ip_tracker.c"
                       INCLUDE_DIRS "."
                       REQUIRES esp_http_client json)
```

2. Replace libcurl with `esp_http_client`
3. Replace json-c with `cJSON`

### Arduino (ESP8266/ESP32):

Use Arduino's HTTPClient and ArduinoJson libraries as alternatives.

## Performance

Benchmark on Raspberry Pi 3B+:
- **Memory usage**: ~200KB RSS
- **API call latency**: 50-150ms (depends on network)
- **CPU usage**: <1% during monitoring

## Security Notes

- **Basic examples**: Data stored unencrypted on server
- **HTTPS**: Use `https://` in API_URL for production
- **Embedded secrets**: Store tokens in secure storage (e.g., encrypted flash)
- **Rate limiting**: Free tier allows 10 requests/minute per IP

## Troubleshooting

**Compilation errors:**
```bash
# Missing libcurl
sudo apt-get install libcurl4-openssl-dev

# Missing json-c
sudo apt-get install libjson-c-dev
```

**Runtime errors:**
```bash
# Check API server is running
curl http://localhost:3000/api/health

# Test with verbose curl
curl -v http://localhost:3000/api/generate
```

**Cross-compilation issues:**
- Ensure target libraries (libcurl, json-c) are available for target architecture
- Use `ldd ./binary` to check dynamic library dependencies

## License

MIT

## Contributing

Contributions welcome! Please test on your target platform before submitting PRs.

---

**See also:**
- [Python examples](https://github.com/mikro-design/key-value.py) - High-level Python client
- [Main API](https://github.com/yourusername/key-value) - Key-value store service
