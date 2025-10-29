use keyvalue_client::{BatchOperation, Client, Error};
use serde_json::json;
use std::env;

#[tokio::main]
async fn main() -> Result<(), Error> {
    // Get token from environment or generate
    let token = env::var("KV_TOKEN").ok();

    let client = if let Some(token) = token {
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

    // Create batch operations
    println!("=== Batch Operations ===");

    // Generate additional tokens for batch operations
    let client_temp = Client::new_without_token();
    let token1 = client_temp.generate(None).await?.token;
    let token2 = client_temp.generate(None).await?.token;
    let token3 = client_temp.generate(None).await?.token;

    println!("Generated tokens for batch operations:");
    println!("  Token 1: {}", token1);
    println!("  Token 2: {}", token2);
    println!("  Token 3: {}\n", token3);

    let operations = vec![
        BatchOperation {
            action: "store".to_string(),
            token: token1.clone(),
            data: Some(json!({"type": "user", "name": "Alice"})),
            ttl: None,
            patch: None,
            version: None,
        },
        BatchOperation {
            action: "store".to_string(),
            token: token2.clone(),
            data: Some(json!({"type": "user", "name": "Bob"})),
            ttl: None,
            patch: None,
            version: None,
        },
        BatchOperation {
            action: "store".to_string(),
            token: token3.clone(),
            data: Some(json!({"type": "user", "name": "Charlie"})),
            ttl: None,
            patch: None,
            version: None,
        },
    ];

    let batch_resp = client.batch(operations).await?;

    println!("Batch Results:");
    println!("  Total operations: {}", batch_resp.summary.total);
    println!("  Succeeded: {}", batch_resp.summary.succeeded);
    println!("  Failed: {}", batch_resp.summary.failed);
    println!("  Success rate: {}\n", batch_resp.summary.success_rate);

    println!("Individual results:");
    for result in &batch_resp.results {
        if result.success {
            println!("  ✓ {} on {} (version: {})",
                result.action,
                result.token,
                result.version.unwrap_or(0)
            );
        } else {
            println!("  ✗ {} on {}: {}",
                result.action,
                result.token,
                result.error.as_deref().unwrap_or("unknown error")
            );
        }
    }

    // Retrieve one of the stored values
    println!("\n=== Retrieving Data ===");
    let mut client1 = Client::new(token1);
    let retrieve_resp = client1.retrieve().await?;
    println!("Retrieved from {}: {}",
        token1,
        serde_json::to_string_pretty(&retrieve_resp.data)?
    );

    println!("\n✓ Batch operations completed!");

    Ok(())
}
