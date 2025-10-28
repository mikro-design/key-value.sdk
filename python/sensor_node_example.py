#!/usr/bin/env python3
"""
Sensor Node Simulator - Mixed Data Types Example

Demonstrates storing complex JSON with text, boolean, and numerical values.
Simulates a realistic sensor node with status, failures, and logs.

Features:
- Mixed data types: strings, numbers, booleans, arrays, nested objects
- Random failures and degraded states
- Error logs and event history
- Alarm conditions
- Network connectivity issues
- Battery status simulation

Requirements:
    pip install requests

Usage:
    python sensor_node_example.py --token YOUR-TOKEN
    python sensor_node_example.py --token YOUR-TOKEN --node-id sensor-lab-01 --interval 3
    python sensor_node_example.py --token YOUR-TOKEN --failure-rate 0.3
"""

import os
import sys
import time
import argparse
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")

# Possible failure scenarios
FAILURE_SCENARIOS = [
    {"type": "sensor_disconnected", "message": "Temperature sensor not responding", "severity": "critical"},
    {"type": "calibration_drift", "message": "Sensor calibration out of range", "severity": "warning"},
    {"type": "network_timeout", "message": "Failed to reach gateway", "severity": "error"},
    {"type": "low_battery", "message": "Battery level below 15%", "severity": "warning"},
    {"type": "memory_overflow", "message": "Data buffer overflow detected", "severity": "error"},
    {"type": "crc_error", "message": "Data integrity check failed", "severity": "error"},
    {"type": "temperature_alarm", "message": "Temperature exceeded threshold", "severity": "critical"},
]

# Status states
STATUS_STATES = ["online", "degraded", "offline", "maintenance"]


class SensorNodeSimulator:
    """Simulate a sensor node with realistic behavior including failures."""

    def __init__(self, node_id: str, failure_rate: float = 0.1):
        self.node_id = node_id
        self.failure_rate = failure_rate
        self.uptime_start = datetime.utcnow()
        self.total_samples = 0
        self.error_count = 0
        self.last_errors = []
        self.is_online = True
        self.battery_level = 100.0
        self.signal_strength = random.uniform(60, 100)

        # Sensor readings baseline
        self.temperature = 22.0
        self.humidity = 45.0
        self.pressure = 1013.25

    def simulate_step(self) -> Dict[str, Any]:
        """Simulate one time step and return node state."""
        self.total_samples += 1

        # Randomly trigger failures
        new_error = None
        if random.random() < self.failure_rate:
            failure = random.choice(FAILURE_SCENARIOS)
            new_error = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": failure["type"],
                "message": failure["message"],
                "severity": failure["severity"]
            }
            self.error_count += 1
            self.last_errors.append(new_error)
            # Keep only last 5 errors
            self.last_errors = self.last_errors[-5:]

        # Determine status based on recent errors
        if not self.is_online:
            status = "offline"
        elif any(e["severity"] == "critical" for e in self.last_errors[-3:]):
            status = "degraded"
        elif self.battery_level < 10:
            status = "degraded"
        else:
            status = "online"

        # Random connectivity issues
        if random.random() < 0.05:
            self.is_online = not self.is_online

        # Simulate battery drain
        self.battery_level = max(0, self.battery_level - random.uniform(0.1, 0.5))
        if self.battery_level <= 0:
            self.is_online = False
            status = "offline"

        # Simulate signal strength fluctuation
        self.signal_strength += random.uniform(-5, 5)
        self.signal_strength = max(0, min(100, self.signal_strength))

        # Generate sensor readings with some noise
        self.temperature += random.uniform(-0.5, 0.5)
        self.humidity += random.uniform(-1, 1)
        self.pressure += random.uniform(-2, 2)

        # Clamp values
        self.temperature = max(-40, min(85, self.temperature))
        self.humidity = max(0, min(100, self.humidity))
        self.pressure = max(950, min(1050, self.pressure))

        # Check alarm conditions
        temp_alarm = self.temperature > 35 or self.temperature < 5
        humidity_alarm = self.humidity > 80 or self.humidity < 20
        battery_alarm = self.battery_level < 15

        # Calculate uptime
        uptime_seconds = int((datetime.utcnow() - self.uptime_start).total_seconds())

        # Build the complete node state
        node_state = {
            # Identification
            "node_id": self.node_id,
            "firmware_version": "v2.4.1",
            "hardware_revision": "Rev C",

            # Status fields (text)
            "status": status,
            "location": "Lab Floor 2, Section B",

            # Boolean fields
            "is_online": self.is_online,
            "alarm_active": temp_alarm or humidity_alarm or battery_alarm,
            "maintenance_mode": False,
            "data_logging_enabled": True,

            # Numerical fields
            "uptime_seconds": uptime_seconds,
            "total_samples": self.total_samples,
            "error_count": self.error_count,
            "battery_level": round(self.battery_level, 1),
            "signal_strength_dbm": round(self.signal_strength, 1),

            # Sensor readings (nested object with mixed types)
            "sensors": {
                "temperature": {
                    "value": round(self.temperature, 2),
                    "unit": "°C",
                    "alarm": temp_alarm,
                    "threshold_min": 5,
                    "threshold_max": 35
                },
                "humidity": {
                    "value": round(self.humidity, 2),
                    "unit": "%",
                    "alarm": humidity_alarm,
                    "threshold_min": 20,
                    "threshold_max": 80
                },
                "pressure": {
                    "value": round(self.pressure, 2),
                    "unit": "hPa",
                    "alarm": False
                }
            },

            # Alarms object
            "alarms": {
                "temperature": temp_alarm,
                "humidity": humidity_alarm,
                "battery": battery_alarm,
                "connectivity": not self.is_online
            },

            # Error log (array of objects)
            "recent_errors": self.last_errors,

            # Network info
            "network": {
                "gateway_id": "gw-001",
                "ip_address": "192.168.1.42",
                "rssi": round(self.signal_strength, 1),
                "connected": self.is_online,
                "last_ping": datetime.utcnow().isoformat() + "Z"
            },

            # Diagnostics
            "diagnostics": {
                "memory_usage_percent": round(random.uniform(30, 70), 1),
                "cpu_usage_percent": round(random.uniform(10, 50), 1),
                "disk_usage_mb": round(random.uniform(100, 500), 2),
                "last_reboot": (datetime.utcnow() - timedelta(hours=uptime_seconds/3600)).isoformat() + "Z",
                "reboot_count": random.randint(0, 5)
            },

            # Timestamps
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        # Add current error to node state if one occurred
        if new_error:
            node_state["current_error"] = new_error

        return node_state


def store_data(token: str, data: Dict[str, Any]) -> Dict:
    """Store data to key-value store."""
    response = requests.post(
        f"{API_URL}/api/store",
        json={"data": data},
        headers={
            "Content-Type": "application/json",
            "X-KV-Token": token
        }
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Simulate sensor node with mixed data types",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")
    parser.add_argument("--node-id", default="sensor-node-01", help="Node identifier")
    parser.add_argument("--interval", type=float, default=5.0, help="Update interval in seconds")
    parser.add_argument("--failure-rate", type=float, default=0.1,
                       help="Probability of failure per iteration (0.0-1.0)")
    parser.add_argument("--iterations", type=int, default=None,
                       help="Number of iterations (infinite if not specified)")

    args = parser.parse_args()

    global API_URL
    API_URL = args.url

    print(f"=== Sensor Node Simulator ===")
    print(f"Node ID: {args.node_id}")
    print(f"Interval: {args.interval}s")
    print(f"Failure rate: {args.failure_rate * 100:.1f}%")
    print(f"Iterations: {args.iterations or 'infinite'}")
    print()

    simulator = SensorNodeSimulator(args.node_id, args.failure_rate)

    iteration = 0
    try:
        while args.iterations is None or iteration < args.iterations:
            iteration += 1

            # Generate node state
            state = simulator.simulate_step()

            # Store to key-value
            result = store_data(args.token, state)

            # Display summary
            status_icon = {
                "online": "✓",
                "degraded": "⚠",
                "offline": "✗",
                "maintenance": "🔧"
            }.get(state["status"], "?")

            alarm_indicator = "🚨" if state["alarm_active"] else "  "

            print(f"[{iteration:4d}] {status_icon} {state['status']:12s} | "
                  f"T:{state['sensors']['temperature']['value']:5.1f}°C "
                  f"H:{state['sensors']['humidity']['value']:5.1f}% "
                  f"P:{state['sensors']['pressure']['value']:7.1f}hPa | "
                  f"Batt:{state['battery_level']:5.1f}% "
                  f"Sig:{state['signal_strength_dbm']:5.1f} | "
                  f"{alarm_indicator} "
                  f"Errors:{state['error_count']} "
                  f"(v{result.get('version', 'N/A')})")

            # Show errors if they occurred
            if "current_error" in state:
                err = state["current_error"]
                print(f"      └─ [{err['severity'].upper()}] {err['type']}: {err['message']}")

            if args.iterations is None or iteration < args.iterations:
                time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\n✓ Stopped after {iteration} iterations")
        print(f"\n=== Final Statistics ===")
        print(f"Total samples: {simulator.total_samples}")
        print(f"Total errors: {simulator.error_count}")
        print(f"Error rate: {(simulator.error_count / simulator.total_samples * 100):.1f}%")
        print(f"Battery remaining: {simulator.battery_level:.1f}%")
        print(f"Status: {state['status']}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        if e.response:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
