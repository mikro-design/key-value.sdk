/*
 * Basic Key-Value Store Example in C
 *
 * Demonstrates basic operations:
 * - Store JSON data
 * - Retrieve data
 *
 * Compile:
 *   gcc -o basic_example basic_example.c -lcurl -ljson-c
 *
 * Usage:
 *   ./basic_example <token>
 *   # or set KV_TOKEN environment variable:
 *   # KV_TOKEN=your-token ./basic_example
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <json-c/json.h>

#ifndef API_URL
#define API_URL "https://key-value.co"
#endif
#define MAX_RESPONSE_SIZE 100000

/* Memory structure for curl response */
struct memory {
    char *response;
    size_t size;
};

/* Callback function for curl to write response */
static size_t write_callback(void *data, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct memory *mem = (struct memory *)userp;

    char *ptr = realloc(mem->response, mem->size + realsize + 1);
    if(ptr == NULL) {
        printf("Not enough memory (realloc returned NULL)\n");
        return 0;
    }

    mem->response = ptr;
    memcpy(&(mem->response[mem->size]), data, realsize);
    mem->size += realsize;
    mem->response[mem->size] = 0;

    return realsize;
}

/* Store data with a token */
int store_data(const char *token, const char *json_data) {
    CURL *curl;
    CURLcode res;
    struct memory chunk = {0};
    int success = 0;

    curl = curl_easy_init();
    if(curl) {
        char url[256];
        snprintf(url, sizeof(url), "%s/api/store", API_URL);

        /* Build request JSON */
        struct json_object *request = json_object_new_object();
        struct json_object *data_obj = json_tokener_parse(json_data);
        json_object_object_add(request, "data", data_obj);

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

            if(chunk.response && chunk.size > 0) {
                printf("Store response: %s\n", chunk.response);
            }
        } else {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        json_object_put(request);
        free(chunk.response);
    }

    return success;
}

/* Retrieve data for a token */
char* retrieve_data(const char *token) {
    CURL *curl;
    CURLcode res;
    struct memory chunk = {0};
    char *data_str = NULL;

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
            struct json_object *parsed_json;
            struct json_object *data_obj;

            parsed_json = json_tokener_parse(chunk.response);
            if(json_object_object_get_ex(parsed_json, "data", &data_obj)) {
                data_str = strdup(json_object_to_json_string_ext(data_obj, JSON_C_TO_STRING_PRETTY));
            }
            json_object_put(parsed_json);
        } else {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        free(chunk.response);
    }

    return data_str;
}

int main(int argc, char *argv[]) {
    curl_global_init(CURL_GLOBAL_DEFAULT);

    printf("=== Key-Value Store - Basic Example ===\n\n");

    const char *token_source = NULL;
    if(argc > 1 && argv[1] && strlen(argv[1]) > 0) {
        token_source = argv[1];
    } else {
        token_source = getenv("KV_TOKEN");
    }

    if(!token_source || strlen(token_source) == 0) {
        fprintf(stderr, "Token required. Pass it as the first argument or set KV_TOKEN.\n");
        curl_global_cleanup();
        return 1;
    }

    char *token = strdup(token_source);
    if(!token) {
        fprintf(stderr, "Failed to allocate memory for token\n");
        curl_global_cleanup();
        return 1;
    }

    printf("1. Using provided token...\n");
    printf("   Token: %s\n\n", token);

    /* Step 2: Store data */
    printf("2. Storing data...\n");
    const char *data = "{"
        "\"user\":\"alice\","
        "\"settings\":{"
            "\"theme\":\"dark\","
            "\"notifications\":true"
        "},"
        "\"scores\":[95,87,92]"
    "}";

    if(!store_data(token, data)) {
        fprintf(stderr, "Failed to store data\n");
        free(token);
        curl_global_cleanup();
        return 1;
    }
    printf("   ✓ Data stored successfully\n\n");

    /* Step 3: Retrieve data */
    printf("3. Retrieving data...\n");
    char *retrieved = retrieve_data(token);
    if(!retrieved) {
        fprintf(stderr, "Failed to retrieve data\n");
        free(token);
        curl_global_cleanup();
        return 1;
    }
    printf("   Retrieved data:\n%s\n\n", retrieved);
    printf("   ✓ Data successfully retrieved!\n");

    /* Cleanup */
    free(token);
    free(retrieved);
    curl_global_cleanup();

    return 0;
}
