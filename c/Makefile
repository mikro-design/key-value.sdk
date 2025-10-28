# Makefile for Key-Value Store C Examples

CC = gcc
API_URL ?= https://key-value.co
CFLAGS = -Wall -Wextra -O2
CFLAGS += -DAPI_URL=\"$(API_URL)\"
LIBS = -lcurl -ljson-c -lm

EXAMPLES_DIR = examples
TARGETS = $(EXAMPLES_DIR)/basic_example $(EXAMPLES_DIR)/ip_tracker $(EXAMPLES_DIR)/sensor_dashboard

all: $(TARGETS)

$(EXAMPLES_DIR)/basic_example: $(EXAMPLES_DIR)/basic_example.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

$(EXAMPLES_DIR)/ip_tracker: $(EXAMPLES_DIR)/ip_tracker.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

$(EXAMPLES_DIR)/sensor_dashboard: $(EXAMPLES_DIR)/sensor_dashboard.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

clean:
	rm -f $(TARGETS)

install-deps:
	@echo "Installing dependencies (Ubuntu/Debian):"
	sudo apt-get update
	sudo apt-get install -y libcurl4-openssl-dev libjson-c-dev build-essential

test: all
	@echo "Running automated tests..."
	@echo "Note: Manual testing required for C examples"

.PHONY: all clean install-deps test
