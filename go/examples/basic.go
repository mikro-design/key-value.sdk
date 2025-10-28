package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	kv "github.com/mikro-design/key-value.sdk/go"
)

func main() {
	// Get token from environment or generate new one
	token := os.Getenv("KV_TOKEN")

	client := kv.NewClient()

	if token == "" {
		fmt.Println("=== Generating Token ===")
		resp, err := client.Generate()
		if err != nil {
			log.Fatal(err)
		}
		token = resp.Token
		fmt.Printf("Generated token: %s\n", token)
		fmt.Println("Save this! Set KV_TOKEN environment variable to reuse.\n")
	} else {
		fmt.Println("=== Using Existing Token ===")
		fmt.Printf("Token: %s\n\n", token)
	}

	client.Token = token

	// Store data
	fmt.Println("=== Storing Data ===")
	data := map[string]interface{}{
		"user": "alice",
		"settings": map[string]interface{}{
			"theme":         "dark",
			"notifications": true,
		},
		"scores": []int{95, 87, 92},
	}

	storeResp, err := client.Store(data, "", nil)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("✓ Data stored successfully\n")
	fmt.Printf("  Size: %d bytes\n", storeResp.Size)
	fmt.Printf("  Version: %d\n", storeResp.Version)
	fmt.Printf("  Tier: %s\n\n", storeResp.Tier)

	// Retrieve data
	fmt.Println("=== Retrieving Data ===")
	retrieveResp, err := client.Retrieve("")
	if err != nil {
		log.Fatal(err)
	}

	var retrievedData map[string]interface{}
	json.Unmarshal(retrieveResp.Data, &retrievedData)

	fmt.Printf("Retrieved data: %+v\n", retrievedData)
	fmt.Printf("Version: %d\n", retrieveResp.Version)
	fmt.Printf("Updated: %s\n\n", retrieveResp.UpdatedAt)

	fmt.Println("✓ Success!")
}
