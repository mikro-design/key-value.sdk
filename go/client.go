// Package keyvalue provides a Go client for the Key-Value store API.
package keyvalue

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

const (
	// DefaultBaseURL is the default API endpoint
	DefaultBaseURL = "https://key-value.co"
	// DefaultTimeout is the default request timeout
	DefaultTimeout = 30 * time.Second
)

// Client is the Key-Value API client
type Client struct {
	BaseURL    string
	Token      string
	HTTPClient *http.Client
}

// NewClient creates a new Key-Value client
func NewClient(options ...Option) *Client {
	c := &Client{
		BaseURL: DefaultBaseURL,
		HTTPClient: &http.Client{
			Timeout: DefaultTimeout,
		},
	}

	for _, opt := range options {
		opt(c)
	}

	return c
}

// Option is a functional option for configuring the client
type Option func(*Client)

// WithBaseURL sets a custom base URL
func WithBaseURL(baseURL string) Option {
	return func(c *Client) {
		c.BaseURL = baseURL
	}
}

// WithToken sets the default token
func WithToken(token string) Option {
	return func(c *Client) {
		c.Token = token
	}
}

// WithHTTPClient sets a custom HTTP client
func WithHTTPClient(client *http.Client) Option {
	return func(c *Client) {
		c.HTTPClient = client
	}
}

// GenerateResponse represents the response from token generation
type GenerateResponse struct {
	Success bool   `json:"success"`
	Token   string `json:"token"`
}

// StoreResponse represents the response from storing data
type StoreResponse struct {
	Success   bool      `json:"success"`
	Message   string    `json:"message"`
	Size      int       `json:"size"`
	Tier      string    `json:"tier"`
	Version   int       `json:"version"`
	UpdatedAt time.Time `json:"updated_at"`
	ExpiresAt *time.Time `json:"expires_at"`
}

// RetrieveResponse represents the response from retrieving data
type RetrieveResponse struct {
	Success   bool            `json:"success"`
	Data      json.RawMessage `json:"data"`
	Version   int             `json:"version"`
	UpdatedAt time.Time       `json:"updated_at"`
	ExpiresAt *time.Time      `json:"expires_at"`
}

// DeleteResponse represents the response from deleting data
type DeleteResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

// HistoryEvent represents a single event in the history
type HistoryEvent struct {
	Seq            int             `json:"seq"`
	CreatedAt      time.Time       `json:"created_at"`
	ExpiresAt      *time.Time      `json:"expires_at"`
	ClassifiedType *string         `json:"classified_type"`
	NumericValue   *float64        `json:"numeric_value"`
	TextValue      *string         `json:"text_value"`
	Confidence     *float64        `json:"confidence"`
	Payload        json.RawMessage `json:"payload"`
}

// HistoryResponse represents the response from querying history
type HistoryResponse struct {
	Success bool           `json:"success"`
	Events  []HistoryEvent `json:"events"`
	Pagination struct {
		Limit   int     `json:"limit"`
		Before  *int    `json:"before"`
		Since   *string `json:"since"`
		HasMore bool    `json:"has_more"`
	} `json:"pagination"`
}

// PatchOperations defines patch operations
type PatchOperations struct {
	Set    map[string]interface{} `json:"set,omitempty"`
	Remove []string               `json:"remove,omitempty"`
}

// PatchResponse represents the response from a patch operation
type PatchResponse struct {
	Success   bool            `json:"success"`
	Version   int             `json:"version"`
	UpdatedAt time.Time       `json:"updated_at"`
	ExpiresAt *time.Time      `json:"expires_at"`
	Data      json.RawMessage `json:"data"`
	Size      int             `json:"size"`
	Tier      string          `json:"tier"`
}

// BatchOperation represents a single operation in a batch
type BatchOperation struct {
	Action  string              `json:"action"`
	Token   string              `json:"token"`
	Data    interface{}         `json:"data,omitempty"`
	TTL     *int                `json:"ttl,omitempty"`
	Patch   *PatchOperations    `json:"patch,omitempty"`
	Version *int                `json:"version,omitempty"`
}

// BatchResult represents the result of a single batch operation
type BatchResult struct {
	Success bool            `json:"success"`
	Token   string          `json:"token"`
	Action  string          `json:"action"`
	Data    json.RawMessage `json:"data,omitempty"`
	Version *int            `json:"version,omitempty"`
	Error   string          `json:"error,omitempty"`
}

// BatchResponse represents the response from a batch operation
type BatchResponse struct {
	Success bool          `json:"success"`
	Results []BatchResult `json:"results"`
	Summary struct {
		Total       int    `json:"total"`
		Succeeded   int    `json:"succeeded"`
		Failed      int    `json:"failed"`
		SuccessRate string `json:"successRate"`
	} `json:"summary"`
}

// Generate creates a new 5-word memorable token
func (c *Client) Generate(turnstileToken ...string) (*GenerateResponse, error) {
	var payload map[string]string
	if len(turnstileToken) > 0 {
		payload = map[string]string{"turnstileToken": turnstileToken[0]}
	}

	var resp GenerateResponse
	err := c.request("POST", "/api/generate", payload, nil, &resp)
	return &resp, err
}

// Store stores JSON data with a token
func (c *Client) Store(data interface{}, token string, ttl *int) (*StoreResponse, error) {
	if token == "" {
		token = c.Token
	}
	if token == "" {
		return nil, fmt.Errorf("token is required")
	}

	payload := map[string]interface{}{"data": data}
	if ttl != nil {
		payload["ttl"] = *ttl
	}

	headers := map[string]string{"X-KV-Token": token}

	var resp StoreResponse
	err := c.request("POST", "/api/store", payload, headers, &resp)
	return &resp, err
}

// Retrieve retrieves data for a token
func (c *Client) Retrieve(token string) (*RetrieveResponse, error) {
	if token == "" {
		token = c.Token
	}
	if token == "" {
		return nil, fmt.Errorf("token is required")
	}

	headers := map[string]string{"X-KV-Token": token}

	var resp RetrieveResponse
	err := c.request("GET", "/api/retrieve", nil, headers, &resp)
	return &resp, err
}

// Delete deletes data for a token
func (c *Client) Delete(token string) (*DeleteResponse, error) {
	if token == "" {
		token = c.Token
	}
	if token == "" {
		return nil, fmt.Errorf("token is required")
	}

	headers := map[string]string{"X-KV-Token": token}

	var resp DeleteResponse
	err := c.request("DELETE", "/api/delete", nil, headers, &resp)
	return &resp, err
}

// Patch applies atomic partial updates with optimistic concurrency
func (c *Client) Patch(version int, patch *PatchOperations, token string, ttl *int) (*PatchResponse, error) {
	if token == "" {
		token = c.Token
	}
	if token == "" {
		return nil, fmt.Errorf("token is required")
	}

	payload := map[string]interface{}{
		"version": version,
		"patch":   patch,
	}
	if ttl != nil {
		payload["ttl"] = *ttl
	}

	headers := map[string]string{"X-KV-Token": token}

	var resp PatchResponse
	err := c.request("PATCH", "/api/store", payload, headers, &resp)
	return &resp, err
}

// HistoryOptions defines options for querying history
type HistoryOptions struct {
	Limit  int
	Before *int
	Since  *string
	Type   *string
}

// History queries time-series event history
func (c *Client) History(token string, opts *HistoryOptions) (*HistoryResponse, error) {
	if token == "" {
		token = c.Token
	}
	if token == "" {
		return nil, fmt.Errorf("token is required")
	}

	params := url.Values{}
	if opts != nil {
		if opts.Limit > 0 {
			params.Set("limit", fmt.Sprintf("%d", opts.Limit))
		}
		if opts.Before != nil {
			params.Set("before", fmt.Sprintf("%d", *opts.Before))
		}
		if opts.Since != nil {
			params.Set("since", *opts.Since)
		}
		if opts.Type != nil {
			params.Set("type", *opts.Type)
		}
	}

	path := "/api/history"
	if len(params) > 0 {
		path += "?" + params.Encode()
	}

	headers := map[string]string{"X-KV-Token": token}

	var resp HistoryResponse
	err := c.request("GET", path, nil, headers, &resp)
	return &resp, err
}

// Batch executes multiple operations in a single request
func (c *Client) Batch(operations []BatchOperation) (*BatchResponse, error) {
	if len(operations) == 0 {
		return nil, fmt.Errorf("at least one operation is required")
	}
	if len(operations) > 100 {
		return nil, fmt.Errorf("maximum 100 operations per batch")
	}

	payload := map[string]interface{}{"operations": operations}

	var resp BatchResponse
	err := c.request("POST", "/api/batch", payload, nil, &resp)
	return &resp, err
}

// request is the internal HTTP request handler
func (c *Client) request(method, path string, body interface{}, headers map[string]string, result interface{}) error {
	var bodyReader io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request: %w", err)
		}
		bodyReader = bytes.NewReader(jsonData)
	}

	req, err := http.NewRequest(method, c.BaseURL+path, bodyReader)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		var errResp struct {
			Error string `json:"error"`
		}
		json.Unmarshal(respBody, &errResp)
		return &APIError{
			StatusCode: resp.StatusCode,
			Message:    errResp.Error,
		}
	}

	if err := json.Unmarshal(respBody, result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	return nil
}

// APIError represents an API error response
type APIError struct {
	StatusCode int
	Message    string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("API error %d: %s", e.StatusCode, e.Message)
}
