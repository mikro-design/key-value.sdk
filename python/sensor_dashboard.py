#!/usr/bin/env python3
"""
Sensor Dashboard

Log and track sensor data (temperature, humidity, etc.) from IoT devices.
Perfect for Raspberry Pi, Arduino, or any device with sensors.

Features:
- Log sensor readings with timestamps
- Store history (last N readings)
- Calculate statistics (min, max, avg)
- Support multiple sensors
- Alerting on threshold violations
- Works with various sensor types

Requirements:
    pip install requests
    # Optional for Raspberry Pi DHT sensors:
    # pip install adafruit-circuitpython-dht

Usage:
    # Log a single reading
    python sensor_dashboard.py --token YOUR-TOKEN log \
        --temp 23.5 --humidity 45.2

    # View current sensor data
    python sensor_dashboard.py --token YOUR-TOKEN view

    # View statistics
    python sensor_dashboard.py --token YOUR-TOKEN stats

    # Monitor mode (read from DHT22 sensor on Raspberry Pi)
    python sensor_dashboard.py --token YOUR-TOKEN monitor \
        --dht-pin 4 --interval 300

    # Monitor with custom sensor script
    python sensor_dashboard.py --token YOUR-TOKEN monitor \
        --command "python read_sensor.py" --interval 60
"""

import os
import requests
import json
import argparse
import sys
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")
MAX_HISTORY = 100  # Keep last 100 readings


class SensorDashboard:
    """Track sensor data over time."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def log_reading(
        self,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        pressure: Optional[float] = None,
        custom: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Log a sensor reading.

        Args:
            temperature: Temperature in Celsius
            humidity: Relative humidity %
            pressure: Pressure in hPa
            custom: Custom sensor readings

        Returns:
            Result with statistics
        """
        # Get existing data
        data = self._get_data()

        # Create reading
        reading = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if temperature is not None:
            reading["temperature"] = round(temperature, 2)
        if humidity is not None:
            reading["humidity"] = round(humidity, 2)
        if pressure is not None:
            reading["pressure"] = round(pressure, 2)
        if custom:
            reading["custom"] = custom

        # Add to history
        history = data.get("history", [])
        history.append(reading)

        # Keep only last MAX_HISTORY readings
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        # Update current reading and statistics
        data["current"] = reading
        data["history"] = history
        data["stats"] = self._calculate_stats(history)
        data["last_updated"] = reading["timestamp"]

        # Store
        response = requests.post(
            f"{self.base_url}/api/store",
            json={"data": data},
            headers={
                "Content-Type": "application/json",
                "X-KV-Token": self.token
            }
        )
        response.raise_for_status()

        return {
            "success": True,
            "reading": reading,
            "stats": data["stats"]
        }

    def get_current(self) -> Dict[str, Any]:
        """Get current sensor readings."""
        data = self._get_data()
        return data.get("current", {})

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get reading history."""
        data = self._get_data()
        history = data.get("history", [])
        if limit:
            return history[-limit:]
        return history

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        data = self._get_data()
        return data.get("stats", {})

    def monitor_dht(self, pin: int, interval: int = 300, sensor_type: str = "DHT22"):
        """
        Monitor DHT sensor on Raspberry Pi.

        Args:
            pin: GPIO pin number (BCM numbering)
            interval: Reading interval in seconds
            sensor_type: "DHT22" or "DHT11"
        """
        try:
            import board
            import adafruit_dht
        except ImportError:
            print("Error: adafruit-circuitpython-dht not installed")
            print("Install with: pip install adafruit-circuitpython-dht")
            sys.exit(1)

        # Initialize sensor
        pin_map = {
            4: board.D4, 17: board.D17, 18: board.D18,
            22: board.D22, 23: board.D23, 24: board.D24, 27: board.D27
        }

        if pin not in pin_map:
            print(f"Error: Pin {pin} not supported. Use: {list(pin_map.keys())}")
            sys.exit(1)

        if sensor_type == "DHT22":
            sensor = adafruit_dht.DHT22(pin_map[pin])
        else:
            sensor = adafruit_dht.DHT11(pin_map[pin])

        print(f"Starting {sensor_type} monitor on pin {pin} (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    temperature = sensor.temperature
                    humidity = sensor.humidity

                    if temperature is not None and humidity is not None:
                        result = self.log_reading(
                            temperature=temperature,
                            humidity=humidity
                        )

                        print(f"[{datetime.now()}] Temp: {temperature:.1f}°C, Humidity: {humidity:.1f}%")

                        # Check alerts
                        self._check_alerts(temperature, humidity)
                    else:
                        print(f"[{datetime.now()}] Failed to read sensor")

                except RuntimeError as e:
                    # DHT sensors sometimes fail to read
                    print(f"[{datetime.now()}] Sensor error: {e}")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            sensor.exit()

    def monitor_command(self, command: str, interval: int = 60):
        """
        Monitor using custom command.

        The command should output JSON with sensor readings:
        {"temperature": 23.5, "humidity": 45.2}

        Args:
            command: Command to execute
            interval: Reading interval in seconds
        """
        print(f"Starting monitor with command: {command}")
        print(f"Interval: {interval}s")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    # Execute command
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0:
                        # Parse JSON output
                        reading = json.loads(result.stdout)

                        # Log reading
                        log_result = self.log_reading(
                            temperature=reading.get("temperature"),
                            humidity=reading.get("humidity"),
                            pressure=reading.get("pressure"),
                            custom=reading.get("custom")
                        )

                        print(f"[{datetime.now()}] Logged: {reading}")

                        # Check alerts
                        if "temperature" in reading and "humidity" in reading:
                            self._check_alerts(reading["temperature"], reading["humidity"])
                    else:
                        print(f"[{datetime.now()}] Command failed: {result.stderr}")

                except json.JSONDecodeError:
                    print(f"[{datetime.now()}] Failed to parse command output")
                except subprocess.TimeoutExpired:
                    print(f"[{datetime.now()}] Command timeout")
                except Exception as e:
                    print(f"[{datetime.now()}] Error: {e}")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped")

    def _get_data(self) -> Dict[str, Any]:
        """Get stored data."""
        try:
            response = requests.get(
                f"{self.base_url}/api/retrieve",
                headers={"X-KV-Token": self.token}
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                return {}
            raise

    def _calculate_stats(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from history."""
        if not history:
            return {}

        stats = {}

        # Calculate for each sensor type
        for key in ["temperature", "humidity", "pressure"]:
            values = [r[key] for r in history if key in r]
            if values:
                stats[key] = {
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "avg": round(sum(values) / len(values), 2),
                    "last": round(values[-1], 2),
                    "count": len(values)
                }

        stats["total_readings"] = len(history)
        stats["first_reading"] = history[0]["timestamp"] if history else None
        stats["last_reading"] = history[-1]["timestamp"] if history else None

        return stats

    def _check_alerts(self, temperature: float, humidity: float):
        """Check for threshold violations."""
        alerts = []

        if temperature > 30:
            alerts.append(f"⚠️  High temperature: {temperature:.1f}°C")
        elif temperature < 10:
            alerts.append(f"⚠️  Low temperature: {temperature:.1f}°C")

        if humidity > 70:
            alerts.append(f"⚠️  High humidity: {humidity:.1f}%")
        elif humidity < 30:
            alerts.append(f"⚠️  Low humidity: {humidity:.1f}%")

        for alert in alerts:
            print(alert)


def main():
    parser = argparse.ArgumentParser(description="Sensor data dashboard")
    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a sensor reading")
    log_parser.add_argument("--temp", type=float, help="Temperature in Celsius")
    log_parser.add_argument("--humidity", type=float, help="Humidity %")
    log_parser.add_argument("--pressure", type=float, help="Pressure in hPa")

    # View command
    view_parser = subparsers.add_parser("view", help="View current readings")
    view_parser.add_argument("--history", type=int, help="Show last N readings")

    # Stats command
    subparsers.add_parser("stats", help="View statistics")

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor sensors")
    monitor_parser.add_argument("--interval", type=int, default=300, help="Interval in seconds")
    monitor_parser.add_argument("--dht-pin", type=int, help="DHT sensor GPIO pin (Raspberry Pi)")
    monitor_parser.add_argument("--dht-type", default="DHT22", choices=["DHT22", "DHT11"])
    monitor_parser.add_argument("--command", help="Custom command to read sensors (outputs JSON)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    dashboard = SensorDashboard(args.url, args.token)

    if args.command == "log":
        if not any([args.temp, args.humidity, args.pressure]):
            print("Error: Provide at least one sensor reading")
            sys.exit(1)

        result = dashboard.log_reading(
            temperature=args.temp,
            humidity=args.humidity,
            pressure=args.pressure
        )

        print("✓ Reading logged")
        print(f"\nCurrent: {json.dumps(result['reading'], indent=2)}")
        print(f"\nStats: {json.dumps(result['stats'], indent=2)}")

    elif args.command == "view":
        if args.history:
            history = dashboard.get_history(limit=args.history)
            print(f"Last {len(history)} readings:")
            print(json.dumps(history, indent=2))
        else:
            current = dashboard.get_current()
            if current:
                print("Current readings:")
                print(json.dumps(current, indent=2))
            else:
                print("No readings yet")

    elif args.command == "stats":
        stats = dashboard.get_stats()
        if stats:
            print("Statistics:")
            print(json.dumps(stats, indent=2))
        else:
            print("No data yet")

    elif args.command == "monitor":
        if args.dht_pin:
            dashboard.monitor_dht(args.dht_pin, args.interval, args.dht_type)
        elif args.command:
            dashboard.monitor_command(args.command, args.interval)
        else:
            print("Error: Provide --dht-pin or --command")
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
