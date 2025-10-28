//! # Key-Value Rust Client
//!
//! Official Rust client for [Key-Value](https://key-value.co) - a secure key-value store
//! with memorable 5-word tokens.
//!
//! ## Example
//!
//! ```no_run
//! use keyvalue_client::{Client, Error};
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Error> {
//!     let client = Client::new("word-word-word-word-word");
//!
//!     let data = serde_json::json!({"temperature": 23.5});
//!     let response = client.store(&data, None).await?;
//!     println!("Stored with version {}", response.version);
//!
//!     let result = client.retrieve().await?;
//!     println!("Data: {:?}", result.data);
//!
//!     Ok(())
//! }
//! ```

use chrono::{DateTime, Utc};
use reqwest::{Client as HttpClient, StatusCode};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::time::Duration;
use thiserror::Error;

const DEFAULT_BASE_URL: &str = "https://key-value.co";
const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);

/// Client errors
#[derive(Error, Debug)]
pub enum Error {
    #[error("HTTP request failed: {0}")]
    Request(#[from] reqwest::Error),

    #[error("API error ({status}): {message}")]
    Api { status: StatusCode, message: String },

    #[error("Token is required")]
    MissingToken,

    #[error("Validation error: {0}")]
    Validation(String),
}

/// Key-Value API client
pub struct Client {
    base_url: String,
    token: Option<String>,
    http_client: HttpClient,
}

impl Client {
    /// Create a new client with a token
    pub fn new(token: impl Into<String>) -> Self {
        Self {
            base_url: DEFAULT_BASE_URL.to_string(),
            token: Some(token.into()),
            http_client: HttpClient::builder()
                .timeout(DEFAULT_TIMEOUT)
                .build()
                .expect("Failed to build HTTP client"),
        }
    }

    /// Create a client without a default token
    pub fn new_without_token() -> Self {
        Self {
            base_url: DEFAULT_BASE_URL.to_string(),
            token: None,
            http_client: HttpClient::builder()
                .timeout(DEFAULT_TIMEOUT)
                .build()
                .expect("Failed to build HTTP client"),
        }
    }

    /// Set the base URL
    pub fn with_base_url(mut self, url: impl Into<String>) -> Self {
        self.base_url = url.into();
        self
    }

    /// Set the default token
    pub fn set_token(&mut self, token: impl Into<String>) {
        self.token = Some(token.into());
    }

    /// Generate a new 5-word memorable token
    pub async fn generate(&self, turnstile_token: Option<&str>) -> Result<GenerateResponse, Error> {
        let mut payload = HashMap::new();
        if let Some(token) = turnstile_token {
            payload.insert("turnstileToken", token);
        }

        let resp = self.http_client
            .post(format!("{}/api/generate", self.base_url))
            .json(&payload)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    /// Store JSON data
    pub async fn store(&self, data: &Value, ttl: Option<i32>) -> Result<StoreResponse, Error> {
        let token = self.token.as_ref().ok_or(Error::MissingToken)?;

        let mut payload = serde_json::json!({"data": data});
        if let Some(ttl_value) = ttl {
            payload["ttl"] = serde_json::json!(ttl_value);
        }

        let resp = self.http_client
            .post(format!("{}/api/store", self.base_url))
            .header("X-KV-Token", token)
            .json(&payload)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    /// Retrieve data
    pub async fn retrieve(&self) -> Result<RetrieveResponse, Error> {
        let token = self.token.as_ref().ok_or(Error::MissingToken)?;

        let resp = self.http_client
            .get(format!("{}/api/retrieve", self.base_url))
            .header("X-KV-Token", token)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    /// Delete data
    pub async fn delete(&self) -> Result<DeleteResponse, Error> {
        let token = self.token.as_ref().ok_or(Error::MissingToken)?;

        let resp = self.http_client
            .delete(format!("{}/api/delete", self.base_url))
            .header("X-KV-Token", token)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    /// Apply atomic partial updates
    pub async fn patch(
        &self,
        version: i32,
        patch: &PatchOperations,
        ttl: Option<i32>,
    ) -> Result<PatchResponse, Error> {
        let token = self.token.as_ref().ok_or(Error::MissingToken)?;

        let mut payload = serde_json::json!({
            "version": version,
            "patch": patch,
        });
        if let Some(ttl_value) = ttl {
            payload["ttl"] = serde_json::json!(ttl_value);
        }

        let resp = self.http_client
            .patch(format!("{}/api/store", self.base_url))
            .header("X-KV-Token", token)
            .json(&payload)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    /// Query time-series history
    pub async fn history(&self, options: &HistoryOptions) -> Result<HistoryResponse, Error> {
        let token = self.token.as_ref().ok_or(Error::MissingToken)?;

        let mut url = format!("{}/api/history", self.base_url);
        let mut query = vec![];

        if let Some(limit) = options.limit {
            query.push(format!("limit={}", limit));
        }
        if let Some(before) = options.before {
            query.push(format!("before={}", before));
        }
        if let Some(since) = &options.since {
            query.push(format!("since={}", since));
        }
        if let Some(typ) = &options.type_filter {
            query.push(format!("type={}", typ));
        }

        if !query.is_empty() {
            url.push_str("?");
            url.push_str(&query.join("&"));
        }

        let resp = self.http_client
            .get(&url)
            .header("X-KV-Token", token)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    /// Execute batch operations
    pub async fn batch(&self, operations: Vec<BatchOperation>) -> Result<BatchResponse, Error> {
        if operations.is_empty() {
            return Err(Error::Validation("At least one operation required".to_string()));
        }
        if operations.len() > 100 {
            return Err(Error::Validation("Maximum 100 operations per batch".to_string()));
        }

        let payload = serde_json::json!({"operations": operations});

        let resp = self.http_client
            .post(format!("{}/api/batch", self.base_url))
            .json(&payload)
            .send()
            .await?;

        self.handle_response(resp).await
    }

    async fn handle_response<T: for<'de> Deserialize<'de>>(&self, resp: reqwest::Response) -> Result<T, Error> {
        let status = resp.status();

        if status.is_success() {
            Ok(resp.json().await?)
        } else {
            let error_body: ErrorResponse = resp.json().await.unwrap_or_else(|_| ErrorResponse {
                error: format!("HTTP {}", status),
            });
            Err(Error::Api {
                status,
                message: error_body.error,
            })
        }
    }
}

#[derive(Debug, Deserialize)]
struct ErrorResponse {
    error: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GenerateResponse {
    pub success: bool,
    pub token: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct StoreResponse {
    pub success: bool,
    pub message: String,
    pub size: i32,
    pub tier: String,
    pub version: i32,
    pub updated_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct RetrieveResponse {
    pub success: bool,
    pub data: Value,
    pub version: i32,
    pub updated_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct DeleteResponse {
    pub success: bool,
    pub message: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PatchOperations {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub set: Option<HashMap<String, Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub remove: Option<Vec<String>>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct PatchResponse {
    pub success: bool,
    pub version: i32,
    pub updated_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub data: Value,
    pub size: i32,
    pub tier: String,
}

#[derive(Debug, Default)]
pub struct HistoryOptions {
    pub limit: Option<i32>,
    pub before: Option<i32>,
    pub since: Option<String>,
    pub type_filter: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct HistoryEvent {
    pub seq: i32,
    pub created_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub classified_type: Option<String>,
    pub numeric_value: Option<f64>,
    pub text_value: Option<String>,
    pub confidence: Option<f64>,
    pub payload: Value,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct HistoryResponse {
    pub success: bool,
    pub events: Vec<HistoryEvent>,
    pub pagination: HistoryPagination,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct HistoryPagination {
    pub limit: i32,
    pub before: Option<i32>,
    pub since: Option<String>,
    pub has_more: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BatchOperation {
    pub action: String,
    pub token: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ttl: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub patch: Option<PatchOperations>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<i32>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct BatchResult {
    pub success: bool,
    pub token: String,
    pub action: String,
    pub data: Option<Value>,
    pub version: Option<i32>,
    pub error: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct BatchResponse {
    pub success: bool,
    pub results: Vec<BatchResult>,
    pub summary: BatchSummary,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct BatchSummary {
    pub total: i32,
    pub succeeded: i32,
    pub failed: i32,
    #[serde(rename = "successRate")]
    pub success_rate: String,
}
