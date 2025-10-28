/*
 * Sensor Dashboard in C
 *
 * Log sensor data (temperature, humidity, etc.) to the key-value store.
 * Perfect for embedded systems, IoT devices, Arduino, ESP32, etc.
 *
 * Compile:
 *   gcc -o sensor_dashboard sensor_dashboard.c -lcurl -ljson-c -lm
 *
 * Usage:
 *   ./sensor_dashboard <token> log <temp> <humidity>
 *   ./sensor_dashboard <token> view
 *   ./sensor_dashboard <token> stats
 *   ./sensor_dashboard <token> monitor <interval_seconds>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <math.h>
#include <curl/curl.h>
#include <json-c/json.h>

#ifndef API_URL
#define API_URL "https://key-value.co"
#endif
#define MAX_HISTORY 100

struct memory {
    char *response;
    size_t size;
};

static size_t write_callback(void *data, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct memory *mem = (struct memory *)userp;

    char *ptr = realloc(mem->response, mem->size + realsize + 1);
    if(ptr == NULL) return 0;

    mem->response = ptr;
    memcpy(&(mem->response[mem->size]), data, realsize);
    mem->size += realsize;
    mem->response[mem->size] = 0;

    return realsize;
}

void get_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *tm_info = gmtime(&now);
    strftime(buffer, size, "%Y-%m-%dT%H:%M:%SZ", tm_info);
}

struct json_object* get_stored_data(const char *token) {
    CURL *curl;
    CURLcode res;
    struct memory chunk = {0};
    struct json_object *data = NULL;

    curl = curl_easy_init();
    if(curl) {
        char url[256];
        snprintf(url, sizeof(url), "%s/api/retrieve", API_URL);

        struct curl_slist *headers = NULL;
        char token_header[512];
        snprintf(token_header, sizeof(token_header), "X-KV-Token: %s", token);
        headers = curl_slist_append(headers, token_header);

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);

        res = curl_easy_perform(curl);

        if(res == CURLE_OK && chunk.response) {
            struct json_object *parsed_json = json_tokener_parse(chunk.response);
            if(parsed_json) {
                struct json_object *data_obj;
                if(json_object_object_get_ex(parsed_json, "data", &data_obj)) {
                    data = json_object_get(data_obj);
                }
                json_object_put(parsed_json);
            }
        }

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        free(chunk.response);
    }

    return data;
}

int store_data(const char *token, struct json_object *data) {
    CURL *curl;
    CURLcode res;
    struct memory chunk = {0};
    int success = 0;

    curl = curl_easy_init();
    if(curl) {
        char url[256];
        snprintf(url, sizeof(url), "%s/api/store", API_URL);

        struct json_object *request = json_object_new_object();
        json_object_object_add(request, "data", json_object_get(data));

        const char *request_str = json_object_to_json_string(request);

        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        char token_header[512];
        snprintf(token_header, sizeof(token_header), "X-KV-Token: %s", token);
        headers = curl_slist_append(headers, token_header);

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_str);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);

        res = curl_easy_perform(curl);

        if(res == CURLE_OK) {
            long response_code;
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
            success = (response_code >= 200 && response_code < 300);
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        json_object_put(request);
        free(chunk.response);
    }

    return success;
}

void calculate_stats(struct json_object *history, const char *key,
                     double *min, double *max, double *avg, int *count) {
    *min = INFINITY;
    *max = -INFINITY;
    *avg = 0;
    *count = 0;

    int len = json_object_array_length(history);
    double sum = 0;

    for(int i = 0; i < len; i++) {
        struct json_object *reading = json_object_array_get_idx(history, i);
        struct json_object *value_obj;

        if(json_object_object_get_ex(reading, key, &value_obj)) {
            double value = json_object_get_double(value_obj);
            if(value < *min) *min = value;
            if(value > *max) *max = value;
            sum += value;
            (*count)++;
        }
    }

    if(*count > 0) {
        *avg = sum / *count;
    }
}

struct json_object* build_stats(struct json_object *history) {
    struct json_object *stats = json_object_new_object();

    const char *sensors[] = {"temperature", "humidity", "pressure"};
    for(int i = 0; i < 3; i++) {
        double min, max, avg;
        int count;

        calculate_stats(history, sensors[i], &min, &max, &avg, &count);

        if(count > 0) {
            struct json_object *sensor_stats = json_object_new_object();
            json_object_object_add(sensor_stats, "min", json_object_new_double(min));
            json_object_object_add(sensor_stats, "max", json_object_new_double(max));
            json_object_object_add(sensor_stats, "avg", json_object_new_double(avg));
            json_object_object_add(sensor_stats, "count", json_object_new_int(count));
            json_object_object_add(stats, sensors[i], sensor_stats);
        }
    }

    json_object_object_add(stats, "total_readings",
        json_object_new_int(json_object_array_length(history)));

    return stats;
}

void check_alerts(double temperature, double humidity) {
    if(temperature > 30.0) {
        printf("⚠️  High temperature: %.1f°C\n", temperature);
    } else if(temperature < 10.0) {
        printf("⚠️  Low temperature: %.1f°C\n", temperature);
    }

    if(humidity > 70.0) {
        printf("⚠️  High humidity: %.1f%%\n", humidity);
    } else if(humidity < 30.0) {
        printf("⚠️  Low humidity: %.1f%%\n", humidity);
    }
}

int log_reading(const char *token, double temperature, double humidity, double pressure) {
    /* Get existing data */
    struct json_object *data = get_stored_data(token);
    if(!data) {
        data = json_object_new_object();
    }

    /* Create new reading */
    char timestamp[64];
    get_timestamp(timestamp, sizeof(timestamp));

    struct json_object *reading = json_object_new_object();
    json_object_object_add(reading, "timestamp", json_object_new_string(timestamp));

    if(!isnan(temperature)) {
        json_object_object_add(reading, "temperature", json_object_new_double(temperature));
    }
    if(!isnan(humidity)) {
        json_object_object_add(reading, "humidity", json_object_new_double(humidity));
    }
    if(!isnan(pressure)) {
        json_object_object_add(reading, "pressure", json_object_new_double(pressure));
    }

    /* Get/create history */
    struct json_object *history;
    if(!json_object_object_get_ex(data, "history", &history)) {
        history = json_object_new_array();
        json_object_object_add(data, "history", history);
    }

    /* Add to history (keep last MAX_HISTORY) */
    int len = json_object_array_length(history);
    if(len >= MAX_HISTORY) {
        /* Remove oldest entries */
        struct json_object *new_history = json_object_new_array();
        for(int i = len - MAX_HISTORY + 1; i < len; i++) {
            json_object_array_add(new_history,
                json_object_get(json_object_array_get_idx(history, i)));
        }
        json_object_object_del(data, "history");
        history = new_history;
        json_object_object_add(data, "history", history);
    }

    json_object_array_add(history, reading);

    /* Update current and stats */
    json_object_object_add(data, "current", json_object_get(reading));

    struct json_object *stats = build_stats(history);
    json_object_object_add(data, "stats", stats);

    json_object_object_add(data, "last_updated", json_object_new_string(timestamp));

    /* Store */
    int success = store_data(token, data);

    json_object_put(data);

    return success;
}

void print_usage(const char *prog) {
    printf("Usage:\n");
    printf("  %s <token> log <temp> <humidity> [pressure]  - Log sensor reading\n", prog);
    printf("  %s <token> view                              - View current readings\n", prog);
    printf("  %s <token> stats                             - View statistics\n", prog);
    printf("  %s <token> monitor <secs>                    - Monitor continuously\n", prog);
}

/* Simulated sensor reading (replace with real sensor code) */
void read_sensor(double *temp, double *humidity, double *pressure) {
    /* Simulate sensor readings */
    *temp = 20.0 + ((double)rand() / RAND_MAX) * 10.0;
    *humidity = 40.0 + ((double)rand() / RAND_MAX) * 30.0;
    *pressure = 1000.0 + ((double)rand() / RAND_MAX) * 50.0;
}

int main(int argc, char *argv[]) {
    if(argc < 3) {
        print_usage(argv[0]);
        return 1;
    }

    const char *token = argv[1];
    const char *command = argv[2];

    srand(time(NULL));
    curl_global_init(CURL_GLOBAL_DEFAULT);

    if(strcmp(command, "log") == 0) {
        if(argc < 5) {
            fprintf(stderr, "Error: log requires temperature and humidity\n");
            print_usage(argv[0]);
            curl_global_cleanup();
            return 1;
        }

        double temp = atof(argv[3]);
        double humidity = atof(argv[4]);
        double pressure = (argc > 5) ? atof(argv[5]) : NAN;

        if(log_reading(token, temp, humidity, pressure)) {
            printf("✓ Reading logged\n");
            printf("  Temperature: %.1f°C\n", temp);
            printf("  Humidity: %.1f%%\n", humidity);
            if(!isnan(pressure)) {
                printf("  Pressure: %.1f hPa\n", pressure);
            }
        } else {
            fprintf(stderr, "Failed to log reading\n");
        }
    }
    else if(strcmp(command, "view") == 0) {
        struct json_object *data = get_stored_data(token);
        if(data) {
            struct json_object *current;
            if(json_object_object_get_ex(data, "current", &current)) {
                printf("Current readings:\n%s\n",
                    json_object_to_json_string_ext(current, JSON_C_TO_STRING_PRETTY));
            } else {
                printf("No readings yet\n");
            }
            json_object_put(data);
        } else {
            printf("No data stored yet\n");
        }
    }
    else if(strcmp(command, "stats") == 0) {
        struct json_object *data = get_stored_data(token);
        if(data) {
            struct json_object *stats;
            if(json_object_object_get_ex(data, "stats", &stats)) {
                printf("Statistics:\n%s\n",
                    json_object_to_json_string_ext(stats, JSON_C_TO_STRING_PRETTY));
            } else {
                printf("No statistics yet\n");
            }
            json_object_put(data);
        } else {
            printf("No data stored yet\n");
        }
    }
    else if(strcmp(command, "monitor") == 0) {
        if(argc < 4) {
            fprintf(stderr, "Error: monitor requires interval in seconds\n");
            print_usage(argv[0]);
            curl_global_cleanup();
            return 1;
        }

        int interval = atoi(argv[3]);
        printf("Starting sensor monitor (reading every %d seconds)\n", interval);
        printf("Note: Using simulated sensor data. Replace read_sensor() with real sensor code.\n");
        printf("Press Ctrl+C to stop\n\n");

        while(1) {
            double temp, humidity, pressure;
            read_sensor(&temp, &humidity, &pressure);

            if(log_reading(token, temp, humidity, pressure)) {
                time_t now = time(NULL);
                char timestr[64];
                strftime(timestr, sizeof(timestr), "%Y-%m-%d %H:%M:%S", localtime(&now));

                printf("[%s] Temp: %.1f°C, Humidity: %.1f%%\n", timestr, temp, humidity);
                check_alerts(temp, humidity);
            } else {
                fprintf(stderr, "Failed to log reading\n");
            }

            sleep(interval);
        }
    }
    else {
        fprintf(stderr, "Unknown command: %s\n", command);
        print_usage(argv[0]);
        curl_global_cleanup();
        return 1;
    }

    curl_global_cleanup();
    return 0;
}
