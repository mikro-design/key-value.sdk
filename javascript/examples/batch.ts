#!/usr/bin/env node
/**
 * Batch Operations Example
 *
 * Demonstrates:
 * - Multiple operations in single request
 * - Store, retrieve, patch, delete in batch
 * - Error handling for individual operations
 */

import { KeyValueClient } from '../src/index'

async function main() {
  const client = new KeyValueClient()

  console.log('=== Batch Operations Example ===\n')

  // Generate 3 tokens
  console.log('Generating tokens...')
  const token1 = (await client.generate()).token
  const token2 = (await client.generate()).token
  const token3 = (await client.generate()).token
  console.log(`✓ Generated 3 tokens\n`)

  // Batch Example 1: Multiple stores
  console.log('=== Batch Store ===')
  const storeResult = await client.batch([
    {
      action: 'store',
      token: token1,
      data: { sensor: 'temp-1', value: 23.5 },
    },
    {
      action: 'store',
      token: token2,
      data: { sensor: 'temp-2', value: 24.1 },
    },
    {
      action: 'store',
      token: token3,
      data: { sensor: 'temp-3', value: 22.8 },
    },
  ])

  console.log(`Success rate: ${storeResult.summary.successRate}`)
  console.log(`Succeeded: ${storeResult.summary.succeeded}`)
  console.log(`Failed: ${storeResult.summary.failed}\n`)

  // Batch Example 2: Mixed operations
  console.log('=== Batch Mixed Operations ===')
  const mixedResult = await client.batch([
    {
      action: 'retrieve',
      token: token1,
    },
    {
      action: 'store',
      token: token2,
      data: { sensor: 'temp-2', value: 25.0, updated: true },
    },
    {
      action: 'retrieve',
      token: token3,
    },
  ])

  console.log('Results:')
  for (const result of mixedResult.results) {
    if (result.success) {
      console.log(`  ✓ ${result.action} on ${result.token.substring(0, 20)}...`)
      if (result.data) {
        console.log(`    Data: ${JSON.stringify(result.data)}`)
      }
    } else {
      console.log(`  ✗ ${result.action} failed: ${result.error}`)
    }
  }
  console.log()

  // Batch Example 3: Patch operations
  console.log('=== Batch Patch ===')

  // First get current versions
  const versions = await client.batch([
    { action: 'retrieve', token: token1 },
    { action: 'retrieve', token: token2 },
  ])

  const patchResult = await client.batch([
    {
      action: 'patch',
      token: token1,
      version: versions.results[0].version!,
      patch: { set: { 'value': 30.0 } },
    },
    {
      action: 'patch',
      token: token2,
      version: versions.results[1].version!,
      patch: { set: { 'value': 31.0 } },
    },
  ])

  console.log(`Patched ${patchResult.summary.succeeded} records\n`)

  // Batch Example 4: Cleanup
  console.log('=== Batch Delete ===')
  const deleteResult = await client.batch([
    { action: 'delete', token: token1 },
    { action: 'delete', token: token2 },
    { action: 'delete', token: token3 },
  ])

  console.log(`Deleted ${deleteResult.summary.succeeded} records`)
  console.log(`✓ Cleanup complete\n`)

  // Summary
  console.log('=== Summary ===')
  console.log('Batch operations allow you to:')
  console.log('  - Reduce HTTP overhead')
  console.log('  - Improve performance for bulk operations')
  console.log('  - Get atomic success/failure for each operation')
  console.log('  - Mix different operation types in one request')
}

main().catch(error => {
  console.error('Error:', error.message)
  if (error.status) {
    console.error(`HTTP ${error.status}`)
  }
  process.exit(1)
})
