#!/usr/bin/env node
/**
 * PATCH Operations Example
 *
 * Demonstrates:
 * - Atomic partial updates with optimistic concurrency
 * - Setting nested fields with dot notation
 * - Removing fields
 * - Handling version conflicts
 */

import { KeyValueClient } from '../src/index'

async function main() {
  const token = process.env.KV_TOKEN
  if (!token) {
    console.error('Error: KV_TOKEN environment variable required')
    console.error('Usage: KV_TOKEN=your-token node examples/patch.ts')
    process.exit(1)
  }

  const client = new KeyValueClient({ token })

  // Initialize with some data
  console.log('=== Initializing Data ===')
  const initialData = {
    profile: {
      name: 'Alice',
      email: 'alice@example.com',
      age: 30,
    },
    stats: {
      loginCount: 0,
      lastLogin: null,
    },
    preferences: {
      theme: 'dark',
      language: 'en',
    },
  }

  await client.store(initialData)
  const { version: v1 } = await client.retrieve()
  console.log(`✓ Initial data stored (version ${v1})\n`)

  // PATCH Example 1: Set nested fields
  console.log('=== Example 1: Set Nested Fields ===')
  const result1 = await client.patch({
    version: v1,
    patch: {
      set: {
        'stats.loginCount': 1,
        'stats.lastLogin': new Date().toISOString(),
        'profile.age': 31,
      },
    },
  })
  console.log(`✓ Updated fields (version ${result1.version})`)
  console.log(`  Login count: ${result1.data.stats.loginCount}`)
  console.log(`  Age: ${result1.data.profile.age}\n`)

  // PATCH Example 2: Remove fields
  console.log('=== Example 2: Remove Fields ===')
  const result2 = await client.patch({
    version: result1.version,
    patch: {
      remove: ['preferences.language'],
    },
  })
  console.log(`✓ Removed language preference (version ${result2.version})`)
  console.log(`  Preferences:`, result2.data.preferences, '\n')

  // PATCH Example 3: Combined operations
  console.log('=== Example 3: Combined Set + Remove ===')
  const result3 = await client.patch({
    version: result2.version,
    patch: {
      set: {
        'profile.verified': true,
        'stats.loginCount': 2,
      },
      remove: ['profile.age'],
    },
  })
  console.log(`✓ Combined operations (version ${result3.version})`)
  console.log(`  Profile:`, result3.data.profile, '\n')

  // PATCH Example 4: Conflict detection
  console.log('=== Example 4: Conflict Detection ===')
  try {
    // Try to use an old version
    await client.patch({
      version: v1, // Old version!
      patch: {
        set: { 'profile.name': 'Bob' },
      },
    })
    console.error('ERROR: Should have detected version conflict!')
  } catch (error: any) {
    if (error.status === 409) {
      console.log(`✓ Conflict detected correctly`)
      console.log(`  Error: ${error.message}\n`)
    } else {
      throw error
    }
  }

  // PATCH Example 5: Concurrent counter (retry logic)
  console.log('=== Example 5: Concurrent Counter with Retry ===')

  async function incrementCounter(retries = 3): Promise<number> {
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const { version, data } = await client.retrieve()
        const currentCount = data.stats?.loginCount || 0

        const result = await client.patch({
          version,
          patch: {
            set: { 'stats.loginCount': currentCount + 1 },
          },
        })

        return result.data.stats.loginCount
      } catch (error: any) {
        if (error.status === 409 && attempt < retries) {
          console.log(`  Conflict on attempt ${attempt + 1}, retrying...`)
          continue
        }
        throw error
      }
    }
    throw new Error('Max retries exceeded')
  }

  const newCount = await incrementCounter()
  console.log(`✓ Counter incremented to: ${newCount}`)
  console.log(`  (With automatic conflict retry)\n`)

  // Show final state
  console.log('=== Final State ===')
  const { data: final, version: finalVersion } = await client.retrieve()
  console.log(`Version: ${finalVersion}`)
  console.log(`Data:`, JSON.stringify(final, null, 2))
}

main().catch(error => {
  console.error('Error:', error.message)
  if (error.status) {
    console.error(`HTTP ${error.status}`)
  }
  process.exit(1)
})
