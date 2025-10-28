/*
 * IP Tracker in C
 *
 * Track your external IP address and store it in the key-value store.
 * Useful for dynamic IP monitoring on embedded devices, routers, etc.
 *
 * Compile:
 *   gcc -o ip_tracker ip_tracker.c -lcurl -ljson-c
 *
 * Usage:
 *   ./ip_tracker <token> update
 *   ./ip_tracker <token> get
 *   ./ip_tracker <token> monitor <interval_seconds>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <curl/curl.h>
#include <json-c/json.h>

#ifndef API_URL
#define API_URL "https://key-value.co"
#endif
#define IP_CHECK_SERVICE "https://api.ipify.org?format=json"

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

/* Get current UTC timestamp in ISO format */
void get_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *tm_info = gmtime(&now);
    strftime(buffer, size, "%Y-%m-%dT%H:%M:%SZ", tm_info);
}

/* Get external IP address */
char* get_external_ip(void) {
    CURL *curl;
    CURLcode res;
    struct memory chunk = {0};
    char *ip = NULL;

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, IP_CHECK_SERVICE);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);

        res = curl_easy_perform(curl);

        if(res == CURLE_OK && chunk.response) {
            struct json_object *parsed_json;
            struct json_object *ip_obj;

            parsed_json = json_tokener_parse(chunk.response);
            if(json_object_object_get_ex(parsed_json, "ip", &ip_obj)) {
                ip = strdup(json_object_get_string(ip_obj));
            }
            json_object_put(parsed_json);
        }

        curl_easy_cleanup(curl);
        free(chunk.response);
    }

    return ip;
}

/* Retrieve stored IP data */
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
                    data = json_object_get(data_obj); /* Increase ref count */
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

/* Store IP data */
int store_ip_data(const char *token, struct json_object *data) {
    CURL *curl;
    CURLcode res;
    struct memory chunk = {0};
    int success = 0;

    curl = curl_easy_init();
    if(curl) {
        char url[256];
        snprintf(url, sizeof(url), "%s/api/store", API_URL);

        /* Build request */
        struct json_object *request = json_object_new_object();
        json_object_object_add(request, "data", json_object_get(data));

        const char *request_str = json_object_to_json_string(request);

        /* Set headers */
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

/* Update IP and return if changed */
int update_ip(const char *token, char **current_ip, char **previous_ip) {
    /* Get current external IP */
    char *ip = get_external_ip();
    if(!ip) {
        fprintf(stderr, "Failed to get external IP\n");
        return -1;
    }

    *current_ip = ip;

    /* Get stored data */
    struct json_object *stored = get_stored_data(token);
    *previous_ip = NULL;

    if(stored) {
        struct json_object *ip_obj;
        if(json_object_object_get_ex(stored, "ip", &ip_obj)) {
            *previous_ip = strdup(json_object_get_string(ip_obj));
        }
    }

    /* Check if changed */
    int changed = (*previous_ip == NULL || strcmp(ip, *previous_ip) != 0);

    /* Build new data */
    char timestamp[64];
    get_timestamp(timestamp, sizeof(timestamp));

    struct json_object *data = json_object_new_object();
    json_object_object_add(data, "ip", json_object_new_string(ip));
    json_object_object_add(data, "last_updated", json_object_new_string(timestamp));
    json_object_object_add(data, "changed", json_object_new_boolean(changed));

    if(*previous_ip) {
        json_object_object_add(data, "previous_ip", json_object_new_string(*previous_ip));
    }

    /* Add history */
    struct json_object *history = json_object_new_array();
    if(stored) {
        struct json_object *old_history;
        if(json_object_object_get_ex(stored, "history", &old_history)) {
            /* Copy up to last 9 entries */
            int len = json_object_array_length(old_history);
            int start = (len > 9) ? len - 9 : 0;
            for(int i = start; i < len; i++) {
                json_object_array_add(history, json_object_get(json_object_array_get_idx(old_history, i)));
            }
        }
    }

    /* Add previous IP to history if changed */
    if(changed && *previous_ip && stored) {
        struct json_object *history_entry = json_object_new_object();
        json_object_object_add(history_entry, "ip", json_object_new_string(*previous_ip));

        struct json_object *old_timestamp;
        if(json_object_object_get_ex(stored, "last_updated", &old_timestamp)) {
            json_object_object_add(history_entry, "timestamp",
                json_object_new_string(json_object_get_string(old_timestamp)));
        }

        json_object_array_add(history, history_entry);
    }

    json_object_object_add(data, "history", history);

    /* Store */
    int success = store_ip_data(token, data);

    if(stored) json_object_put(stored);
    json_object_put(data);

    return success ? (changed ? 1 : 0) : -1;
}

void print_usage(const char *prog) {
    printf("Usage:\n");
    printf("  %s <token> update          - Update IP once\n", prog);
    printf("  %s <token> get             - Get stored IP data\n", prog);
    printf("  %s <token> monitor <secs>  - Monitor IP continuously\n", prog);
}

int main(int argc, char *argv[]) {
    if(argc < 3) {
        print_usage(argv[0]);
        return 1;
    }

    const char *token = argv[1];
    const char *command = argv[2];

    curl_global_init(CURL_GLOBAL_DEFAULT);

    if(strcmp(command, "update") == 0) {
        char *current_ip = NULL, *previous_ip = NULL;
        int result = update_ip(token, &current_ip, &previous_ip);

        if(result >= 0) {
            printf("Current IP: %s\n", current_ip);
            if(result == 1) {
                printf("Previous IP: %s\n", previous_ip);
                printf("✓ IP has changed - updated in store\n");
            } else {
                printf("✓ IP unchanged\n");
            }
        }

        free(current_ip);
        free(previous_ip);
    }
    else if(strcmp(command, "get") == 0) {
        struct json_object *data = get_stored_data(token);
        if(data) {
            printf("Stored IP data:\n%s\n",
                json_object_to_json_string_ext(data, JSON_C_TO_STRING_PRETTY));
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
        printf("Starting IP monitor (checking every %d seconds)\n", interval);
        printf("Press Ctrl+C to stop\n\n");

        while(1) {
            char *current_ip = NULL, *previous_ip = NULL;
            int result = update_ip(token, &current_ip, &previous_ip);

            time_t now = time(NULL);
            char timestr[64];
            strftime(timestr, sizeof(timestr), "%Y-%m-%d %H:%M:%S", localtime(&now));

            if(result == 1) {
                printf("[%s] IP CHANGED!\n", timestr);
                printf("  Old: %s\n", previous_ip);
                printf("  New: %s\n", current_ip);
            } else if(result == 0) {
                printf("[%s] IP unchanged: %s\n", timestr, current_ip);
            } else {
                printf("[%s] Error updating IP\n", timestr);
            }

            free(current_ip);
            free(previous_ip);

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
