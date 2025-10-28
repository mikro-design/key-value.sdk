use keyvalue_client::{Client, Error};
use std::env;

#[tokio::main]
async fn main() -> Result<(), Error> {
    // Get token from environment or generate
    let token = env::var("KV_TOKEN").ok();

    let mut client = if let Some(token) = token {
        println!("=== Using Existing Token ===");
        println!("Token: {}\n", token);
        Client::new(token)
    } else {
        println!("=== Generating Token ===");
        let client_temp = Client::new_without_token();
        let resp = client_temp.generate(None).await?;
        println!("Generated token: {}", resp.token);
        println!("Save this! Set KV_TOKEN environment variable to reuse.\n");
        Client::new(resp.token)
    };

    // Store data
    println!("=== Storing Data ===");
    let data = serde_json::json!({
        "user": "alice",
        "settings": {
            "theme": "dark",
            "notifications": true
        },
        "scores": [95, 87, 92]
    });

    let store_resp = client.store(&data, None).await?;
    println!("✓ Data stored successfully");
    println!("  Size: {} bytes", store_resp.size);
    println!("  Version: {}", store_resp.version);
    println!("  Tier: {}\n", store_resp.tier);

    // Retrieve data
    println!("=== Retrieving Data ===");
    let retrieve_resp = client.retrieve().await?;
    println!("Retrieved data: {}", serde_json::to_string_pretty(&retrieve_resp.data)?);
    println!("Version: {}", retrieve_resp.version);
    println!("Updated: {}\n", retrieve_resp.updated_at);

    println!("✓ Success!");

    Ok(())
}
