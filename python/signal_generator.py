#!/usr/bin/env python3
"""
Signal Generator for Sensor Data

Generate and store realistic sensor signals to the key-value store.
Perfect for testing time-series features, history API, and dashboards.

Features:
- Multiple signal types: sine, random walk, step, noise, sawtooth, spike, exponential decay
- Simple mode: single sensor value
- Complex mode: multiple sensors with correlations
- 10+ sensor types with convenient aliases (e.g., temp → temperature)
- Configurable sample interval (every N seconds)
- Overwrites existing data with fresh sensor readings
- Continuous streaming or fixed iterations
- Token remains in dashboard (only data is replaced)

Requirements:
    pip install requests numpy

Usage:
    # Simple sine wave temperature sensor (can use 'temp' alias)
    python signal_generator.py --token YOUR-TOKEN simple --type temp --signal sine

    # Complex multi-sensor system (using aliases)
    python signal_generator.py --token YOUR-TOKEN complex --sensors temp,hum,press

    # Random walk with noise, sample every 5 seconds
    python signal_generator.py --token YOUR-TOKEN simple --type cpu --signal random_walk --interval 5

    # Clear existing data, then generate 100 samples
    python signal_generator.py --token YOUR-TOKEN simple --type temp --clear --iterations 100
"""

import os
import sys
import time
import json
import argparse
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
import random
import math

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")

# Sensor configurations with realistic ranges
SENSOR_CONFIGS = {
    "temperature": {
        "unit": "°C",
        "min": -40,
        "max": 85,
        "baseline": 22.0,
        "noise": 0.5,
        "description": "Temperature sensor"
    },
    "humidity": {
        "unit": "%",
        "min": 0,
        "max": 100,
        "baseline": 45.0,
        "noise": 2.0,
        "description": "Relative humidity"
    },
    "pressure": {
        "unit": "hPa",
        "min": 950,
        "max": 1050,
        "baseline": 1013.25,
        "noise": 5.0,
        "description": "Atmospheric pressure"
    },
    "cpu": {
        "unit": "%",
        "min": 0,
        "max": 100,
        "baseline": 35.0,
        "noise": 5.0,
        "description": "CPU utilization"
    },
    "memory": {
        "unit": "%",
        "min": 0,
        "max": 100,
        "baseline": 60.0,
        "noise": 3.0,
        "description": "Memory usage"
    },
    "voltage": {
        "unit": "V",
        "min": 0,
        "max": 12,
        "baseline": 5.0,
        "noise": 0.1,
        "description": "Voltage reading"
    },
    "light": {
        "unit": "lux",
        "min": 0,
        "max": 100000,
        "baseline": 500,
        "noise": 50,
        "description": "Light intensity"
    },
    "co2": {
        "unit": "ppm",
        "min": 300,
        "max": 5000,
        "baseline": 450,
        "noise": 20,
        "description": "CO2 concentration"
    },
    "vibration": {
        "unit": "g",
        "min": 0,
        "max": 10,
        "baseline": 0.1,
        "noise": 0.05,
        "description": "Vibration intensity"
    },
    "power": {
        "unit": "W",
        "min": 0,
        "max": 5000,
        "baseline": 250,
        "noise": 50,
        "description": "Power consumption"
    }
}

# Sensor name aliases for convenience
SENSOR_ALIASES = {
    "temp": "temperature",
    "hum": "humidity",
    "press": "pressure",
    "mem": "memory",
    "volt": "voltage",
    "vib": "vibration",
    "pwr": "power"
}


def resolve_sensor_name(name: str) -> str:
    """Resolve sensor name, expanding aliases."""
    name = name.strip().lower()
    return SENSOR_ALIASES.get(name, name)


def parse_sensor_spec(spec: str) -> tuple:
    """Parse sensor specification like 'temp:amp=10:freq=0.2:offset=25'.

    Returns:
        (sensor_name, params_dict)
    """
    parts = spec.split(':')
    sensor_name = parts[0].strip()
    params = {}

    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            # Convert to float
            try:
                params[key] = float(value.strip())
            except ValueError:
                print(f"Warning: Invalid parameter value '{value}' for '{key}', skipping")

    return sensor_name, params


class SignalGenerator:
    """Generate various signal types for testing."""

    def __init__(self, sensor_type: str):
        self.config = SENSOR_CONFIGS.get(sensor_type, SENSOR_CONFIGS["temperature"])
        self.baseline = self.config["baseline"]
        self.noise_level = self.config["noise"]
        self.step = 0
        self.random_walk_value = self.baseline

    def sine(self, frequency: float = 0.1, amplitude: float = None, offset: float = None) -> float:
        """Sine wave signal."""
        if amplitude is None:
            amplitude = (self.config["max"] - self.config["min"]) * 0.2
        baseline = offset if offset is not None else self.baseline
        value = baseline + amplitude * math.sin(2 * math.pi * frequency * self.step)
        self.step += 1
        return self._add_noise(value)

    def random_walk(self, step_size: float = None) -> float:
        """Random walk signal."""
        if step_size is None:
            step_size = self.noise_level * 2
        self.random_walk_value += random.uniform(-step_size, step_size)
        # Keep within bounds
        self.random_walk_value = max(self.config["min"],
                                     min(self.config["max"], self.random_walk_value))
        return self._add_noise(self.random_walk_value)

    def step(self, step_interval: int = 20) -> float:
        """Step function signal."""
        step_count = self.step // step_interval
        amplitude = (self.config["max"] - self.config["min"]) * 0.3
        value = self.baseline + amplitude * (1 if step_count % 2 == 0 else -1)
        self.step += 1
        return self._add_noise(value)

    def sawtooth(self, period: int = 50) -> float:
        """Sawtooth wave signal."""
        amplitude = (self.config["max"] - self.config["min"]) * 0.4
        value = self.baseline + amplitude * (2 * (self.step % period) / period - 1)
        self.step += 1
        return self._add_noise(value)

    def noise(self) -> float:
        """Pure noise signal."""
        value = random.uniform(self.config["min"], self.config["max"])
        return value

    def spike(self, spike_probability: float = 0.05) -> float:
        """Random spikes on baseline."""
        if random.random() < spike_probability:
            spike_amplitude = (self.config["max"] - self.baseline) * 0.8
            value = self.baseline + spike_amplitude
        else:
            value = self.baseline
        self.step += 1
        return self._add_noise(value)

    def exponential_decay(self, initial: float = None, decay_rate: float = 0.95) -> float:
        """Exponential decay from initial value to baseline."""
        if initial is None:
            initial = self.config["max"]
        value = self.baseline + (initial - self.baseline) * (decay_rate ** self.step)
        self.step += 1
        return self._add_noise(value)

    def _add_noise(self, value: float) -> float:
        """Add gaussian noise to value."""
        noisy_value = value + random.gauss(0, self.noise_level)
        # Clamp to valid range
        return max(self.config["min"], min(self.config["max"], noisy_value))

    def reset(self):
        """Reset generator state."""
        self.step = 0
        self.random_walk_value = self.baseline


class SensorDataPublisher:
    """Publish sensor data to key-value store."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.sample_count = 0

    def store(self, data: Dict[Any, Any], use_patch: bool = False,
              version: Optional[int] = None) -> Dict:
        """Store data using POST or PATCH."""
        if use_patch and version is not None:
            # Use PATCH for incremental updates
            response = requests.patch(
                f"{self.base_url}/api/store",
                json={
                    "version": version,
                    "patch": {
                        "set": data
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "X-KV-Token": self.token
                }
            )
        else:
            # Use POST for full replace
            response = requests.post(
                f"{self.base_url}/api/store",
                json={"data": data},
                headers={
                    "Content-Type": "application/json",
                    "X-KV-Token": self.token
                }
            )
        response.raise_for_status()
        return response.json()

    def retrieve(self) -> Dict[Any, Any]:
        """Retrieve current data."""
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            headers={"X-KV-Token": self.token}
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def get_history(self, limit: int = 50) -> Dict:
        """Get event history."""
        response = requests.get(
            f"{self.base_url}/api/history",
            params={"limit": limit},
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def delete(self) -> Dict:
        """Delete all data for this token."""
        response = requests.delete(
            f"{self.base_url}/api/delete",
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()


def simple_sensor_mode(args):
    """Generate simple single-sensor data."""
    # Resolve sensor name (expand aliases)
    sensor_type = resolve_sensor_name(args.type)

    if sensor_type not in SENSOR_CONFIGS:
        print(f"Error: Unknown sensor type '{args.type}'")
        print(f"Available sensors: {', '.join(sorted(SENSOR_CONFIGS.keys()))}")
        print(f"Aliases: {', '.join(f'{k}→{v}' for k, v in sorted(SENSOR_ALIASES.items()))}")
        sys.exit(1)

    print(f"=== Simple Sensor Mode ===")
    print(f"Sensor type: {sensor_type}")
    print(f"Signal: {args.signal}")
    print(f"Interval: {args.interval}s")
    print(f"Iterations: {args.iterations or 'infinite'}")
    print()

    generator = SignalGenerator(sensor_type)
    publisher = SensorDataPublisher(API_URL, args.token)
    config = SENSOR_CONFIGS[sensor_type]

    # Delete existing data before starting
    print("Deleting existing data...")
    try:
        publisher.delete()
        print("✓ Data deleted\n")
    except requests.HTTPError as e:
        if e.response and e.response.status_code == 404:
            print("✓ No existing data\n")
        else:
            print(f"⚠ Warning: Could not delete data: {e}\n")

    # Get signal generation function
    signal_func = getattr(generator, args.signal, generator.sine)

    iteration = 0
    try:
        while args.iterations is None or iteration < args.iterations:
            iteration += 1

            # Generate sensor reading
            value = signal_func()

            # Prepare data payload
            data = {
                "sensor_type": sensor_type,
                "value": round(value, 2),
                "unit": config["unit"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "signal": args.signal
            }

            # Store data
            result = publisher.store(data)

            # Display
            print(f"[{iteration:4d}] {sensor_type}: {value:7.2f} {config['unit']} "
                  f"(version: {result.get('version', 'N/A')})")

            if args.iterations is None or iteration < args.iterations:
                time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\n✓ Stopped after {iteration} iterations")


def complex_sensor_mode(args):
    """Generate complex multi-sensor data with correlations."""
    # Parse sensor specifications (e.g., "temp:amp=10:freq=0.2,hum:amp=15,press")
    sensor_specs = [s.strip() for s in args.sensors.split(',')]
    resolved_sensors = {}
    sensor_params = {}

    for spec in sensor_specs:
        sensor_name, params = parse_sensor_spec(spec)
        resolved = resolve_sensor_name(sensor_name)

        if resolved not in SENSOR_CONFIGS:
            print(f"Error: Unknown sensor type '{sensor_name}'")
            print(f"Available sensors: {', '.join(sorted(SENSOR_CONFIGS.keys()))}")
            print(f"Aliases: {', '.join(f'{k}→{v}' for k, v in sorted(SENSOR_ALIASES.items()))}")
            sys.exit(1)

        resolved_sensors[resolved] = sensor_name
        sensor_params[resolved] = params

    print(f"=== Complex Multi-Sensor Mode ===")
    print(f"Sensors: {', '.join(resolved_sensors.keys())}")
    print(f"Signal: {args.signal}")
    print(f"Interval: {args.interval}s")
    print(f"Iterations: {args.iterations or 'infinite'}")

    # Display custom parameters
    for sensor, params in sensor_params.items():
        if params:
            param_str = ', '.join(f"{k}={v}" for k, v in params.items())
            print(f"  {sensor}: {param_str}")
    print()

    # Create generator for each sensor
    generators = {sensor: SignalGenerator(sensor) for sensor in resolved_sensors.keys()}
    publisher = SensorDataPublisher(API_URL, args.token)

    # Delete existing data before starting
    print("Deleting existing data...")
    try:
        publisher.delete()
        print("✓ Data deleted\n")
    except requests.HTTPError as e:
        if e.response and e.response.status_code == 404:
            print("✓ No existing data\n")
        else:
            print(f"⚠ Warning: Could not delete data: {e}\n")

    iteration = 0
    current_version = None

    try:
        while args.iterations is None or iteration < args.iterations:
            iteration += 1

            # Generate readings for all sensors
            readings = {}
            for sensor, generator in generators.items():
                signal_func = getattr(generator, args.signal, generator.sine)

                # Get custom parameters for this sensor
                params = sensor_params.get(sensor, {})

                # Map common parameter names
                kwargs = {}
                if 'amp' in params or 'amplitude' in params:
                    kwargs['amplitude'] = params.get('amp', params.get('amplitude'))
                if 'freq' in params or 'frequency' in params:
                    kwargs['frequency'] = params.get('freq', params.get('frequency'))
                if 'offset' in params:
                    kwargs['offset'] = params['offset']

                # Call signal function with custom parameters
                value = signal_func(**kwargs)
                config = SENSOR_CONFIGS[sensor]

                readings[sensor] = {
                    "value": round(value, 2),
                    "unit": config["unit"],
                    "description": config["description"]
                }

            # Prepare data payload
            data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "signal_type": args.signal,
                "sensors": readings,
                "system_status": "online",
                "sample_count": iteration
            }

            # Add some derived metrics
            if "temperature" in readings and "humidity" in readings:
                # Heat index approximation
                t = readings["temperature"]["value"]
                h = readings["humidity"]["value"]
                heat_index = t + 0.5 * (h / 100) * (t - 14)
                data["heat_index"] = round(heat_index, 2)

            # Store data
            result = publisher.store(data)
            current_version = result.get("version")

            # Display
            display_parts = []
            for sensor, reading in readings.items():
                display_parts.append(f"{sensor}: {reading['value']:.1f}{reading['unit']}")

            print(f"[{iteration:4d}] {' | '.join(display_parts)} "
                  f"(v{current_version})")

            if args.iterations is None or iteration < args.iterations:
                time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\n✓ Stopped after {iteration} iterations")

        # Show summary
        print("\n=== Summary ===")
        try:
            current = publisher.retrieve()
            if current:
                print(f"Final version: {current.get('version')}")
                print(f"Last updated: {current.get('updated_at')}")
                print(f"Total samples: {iteration}")
        except:
            pass


def show_history(args):
    """Display sensor history."""
    publisher = SensorDataPublisher(API_URL, args.token)

    print("=== Fetching History ===")
    history = publisher.get_history(limit=args.limit)

    events = history.get("events", [])
    print(f"Found {len(events)} events\n")

    for event in events:
        timestamp = event.get("created_at", "")
        seq = event.get("seq", "")
        classified = event.get("classified_type", "")
        numeric = event.get("numeric_value", "")

        payload = event.get("payload", {})
        if isinstance(payload, dict):
            data = payload.get("data", {})
            if isinstance(data, dict) and "value" in data:
                print(f"[{seq:4d}] {timestamp[:19]} | {data.get('sensor_type', '?')}: "
                      f"{data.get('value')} {data.get('unit', '')} "
                      f"(type: {classified or 'unclassified'})")
            elif isinstance(data, dict) and "sensors" in data:
                sensor_count = len(data.get("sensors", {}))
                print(f"[{seq:4d}] {timestamp[:19]} | {sensor_count} sensors "
                      f"(iteration: {data.get('iteration', '?')})")
            else:
                print(f"[{seq:4d}] {timestamp[:19]} | {payload.get('type', 'store')}")
        else:
            print(f"[{seq:4d}] {timestamp[:19]}")

    pagination = history.get("pagination", {})
    if pagination.get("has_more"):
        print(f"\nMore events available (use --limit to see more)")


def main():
    global API_URL

    parser = argparse.ArgumentParser(
        description="Generate sensor signals for key-value store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple temperature sine wave (default: every 2 seconds)
  python signal_generator.py --token YOUR-TOKEN simple --type temperature --signal sine

  # CPU usage random walk, sample every 10 seconds
  python signal_generator.py --token YOUR-TOKEN simple --type cpu --signal random_walk --interval 10

  # Multi-sensor system using aliases (data cleared automatically)
  python signal_generator.py --token YOUR-TOKEN complex --sensors temp,hum,press

  # Multi-sensor with custom sine parameters per sensor
  python signal_generator.py --token YOUR-TOKEN complex --sensors temp:amp=10:freq=0.2,hum:amp=15:offset=50,press

  # Generate exactly 100 samples then stop
  python signal_generator.py --token YOUR-TOKEN simple --type voltage --iterations 100

  # Run 50 iterations with 1 second interval
  python signal_generator.py --token YOUR-TOKEN simple --type cpu --iterations 50 --interval 1

  # View history
  python signal_generator.py --token YOUR-TOKEN history --limit 100
        """
    )

    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="mode", help="Operating mode")

    # Simple sensor mode
    simple_parser = subparsers.add_parser("simple", help="Single sensor signal")
    simple_parser.add_argument(
        "--type",
        choices=list(SENSOR_CONFIGS.keys()),
        default="temperature",
        help="Sensor type"
    )
    simple_parser.add_argument(
        "--signal",
        choices=["sine", "random_walk", "step", "sawtooth", "noise", "spike", "exponential_decay"],
        default="sine",
        help="Signal type"
    )
    simple_parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Sample interval in seconds"
    )
    simple_parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Number of iterations (infinite if not specified)"
    )

    # Complex sensor mode
    complex_parser = subparsers.add_parser("complex", help="Multi-sensor signal")
    complex_parser.add_argument(
        "--sensors",
        default="temperature,humidity,pressure",
        help="Comma-separated sensor specs. Format: sensor[:param=value]... "
             "Example: temp:amp=10:freq=0.2,hum:amp=15:offset=50,press. "
             "Parameters: amp/amplitude, freq/frequency, offset"
    )
    complex_parser.add_argument(
        "--signal",
        choices=["sine", "random_walk", "step", "sawtooth", "noise"],
        default="random_walk",
        help="Signal type for all sensors"
    )
    complex_parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Sample interval in seconds"
    )
    complex_parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Number of iterations (infinite if not specified)"
    )

    # History mode
    history_parser = subparsers.add_parser("history", help="View sensor history")
    history_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of events to retrieve"
    )

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return

    # Update global API_URL if provided
    if args.url:
        API_URL = args.url

    if args.mode == "simple":
        simple_sensor_mode(args)
    elif args.mode == "complex":
        complex_sensor_mode(args)
    elif args.mode == "history":
        show_history(args)


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
