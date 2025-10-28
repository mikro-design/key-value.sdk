#!/usr/bin/env node
/**
 * Basic Key-Value Store Example
 *
 * Demonstrates:
 * - Generating a token
 * - Storing JSON data
 * - Retrieving data
 * - Updating data
 */

import { KeyValueClient } from '../src/index'

async function main() {
  const client = new KeyValueClient({
    baseUrl: process.env.API_URL || 'https://key-value.co',
  })

  // Step 1: Generate a new token (or use existing)
  const token = process.env.KV_TOKEN

  if (!token) {
    console.log('=== Generating Token ===')
    const { token: newToken } = await client.generate()
    console.log(`Generated token: ${newToken}`)
    console.log('Save this token! Set KV_TOKEN environment variable to reuse it.\n')
    client.setToken(newToken)
  } else {
    console.log(`=== Using Existing Token ===`)
    console.log(`Token: ${token}\n`)
    client.setToken(token)
  }

  // Step 2: Store some data
  console.log('=== Storing Data ===')
  const myData = {
    user: 'alice',
    settings: {
      theme: 'dark',
      notifications: true,
    },
    scores: [95, 87, 92],
  }

  const storeResult = await client.store(myData)
  console.log(`✓ Data stored successfully`)
  console.log(`  Size: ${storeResult.size} bytes`)
  console.log(`  Version: ${storeResult.version}`)
  console.log(`  Tier: ${storeResult.tier}`)
  console.log(`  Updated: ${storeResult.updated_at}\n`)

  // Step 3: Retrieve the data
  console.log('=== Retrieving Data ===')
  const { data, version, updated_at, expires_at } = await client.retrieve()
  console.log(`Retrieved data:`, JSON.stringify(data, null, 2))
  console.log(`Version: ${version}`)
  console.log(`Updated: ${updated_at}`)
  console.log(`Expires: ${expires_at || 'Never'}\n`)

  // Verify data matches
  if (JSON.stringify(data) !== JSON.stringify(myData)) {
    throw new Error('Data mismatch!')
  }
  console.log('✓ Data verified!\n')

  // Step 4: Update the data
  console.log('=== Updating Data ===')
  const updatedData = {
    ...myData,
    settings: {
      ...myData.settings,
      theme: 'light',
    },
    last_updated: new Date().toISOString(),
  }

  await client.store(updatedData)
  const { data: retrieved, version: newVersion } = await client.retrieve()
  console.log(`✓ Data updated successfully`)
  console.log(`  New version: ${newVersion}`)
  console.log(`  Theme changed to: ${(retrieved as any).settings.theme}\n`)
}

main().catch(error => {
  console.error('Error:', error.message)
  if (error.status) {
    console.error(`HTTP ${error.status}`)
  }
  process.exit(1)
})
