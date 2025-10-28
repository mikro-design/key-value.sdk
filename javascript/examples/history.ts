#!/usr/bin/env node
/**
 * History API Example
 *
 * Demonstrates:
 * - Querying event history
 * - Pagination
 * - Time-based filtering
 * - Analyzing event patterns
 */

import { KeyValueClient } from '../src/index'

async function main() {
  const token = process.env.KV_TOKEN
  if (!token) {
    console.error('Error: KV_TOKEN environment variable required')
    console.error('Usage: KV_TOKEN=your-token node examples/history.ts')
    process.exit(1)
  }

  const client = new KeyValueClient({ token })

  // Generate some test data
  console.log('=== Generating Test Data ===')
  for (let i = 0; i < 5; i++) {
    await client.store({
      iteration: i,
      temperature: 20 + Math.random() * 10,
      humidity: 40 + Math.random() * 20,
      timestamp: new Date().toISOString(),
    })
    console.log(`  Event ${i + 1} stored`)
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  console.log('✓ Test data generated\n')

  // Query recent history
  console.log('=== Recent History (Last 10 Events) ===')
  const history1 = await client.history({ limit: 10 })

  console.log(`Total events: ${history1.events.length}`)
  console.log(`Has more: ${history1.pagination.has_more}`)
  console.log('\nEvents:')

  for (const event of history1.events.slice(0, 5)) {
    console.log(`\n  Seq ${event.seq}:`)
    console.log(`    Type: ${event.classified_type || 'unclassified'}`)
    console.log(`    Value: ${event.numeric_value}`)
    console.log(`    Created: ${event.created_at}`)
    if (event.payload?.data) {
      console.log(`    Data: temp=${event.payload.data.temperature?.toFixed(1)}°C, hum=${event.payload.data.humidity?.toFixed(1)}%`)
    }
  }

  // Pagination example
  if (history1.events.length > 0) {
    console.log('\n\n=== Pagination Example ===')
    const oldestSeq = history1.events[history1.events.length - 1].seq
    const history2 = await client.history({ limit: 3, before: oldestSeq })
    console.log(`Events before seq ${oldestSeq}: ${history2.events.length}`)
    console.log(`Has more: ${history2.pagination.has_more}`)
  }

  // Time-based filtering
  console.log('\n\n=== Time-Based Filtering ===')
  const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString()
  const recentHistory = await client.history({ since: fiveMinutesAgo })
  console.log(`Events in last 5 minutes: ${recentHistory.events.length}`)

  // Statistics
  console.log('\n\n=== Event Statistics ===')
  const allHistory = await client.history({ limit: 200 })

  const temperatures = allHistory.events
    .filter(e => e.numeric_value !== null)
    .map(e => e.numeric_value!)

  if (temperatures.length > 0) {
    const avg = temperatures.reduce((a, b) => a + b, 0) / temperatures.length
    const min = Math.min(...temperatures)
    const max = Math.max(...temperatures)

    console.log(`Total events with numeric data: ${temperatures.length}`)
    console.log(`Average value: ${avg.toFixed(2)}`)
    console.log(`Min: ${min.toFixed(2)}`)
    console.log(`Max: ${max.toFixed(2)}`)
  }

  // Event type distribution
  const typeDistribution = new Map<string, number>()
  for (const event of allHistory.events) {
    const type = event.classified_type || 'unclassified'
    typeDistribution.set(type, (typeDistribution.get(type) || 0) + 1)
  }

  console.log('\nEvent Type Distribution:')
  for (const [type, count] of typeDistribution.entries()) {
    console.log(`  ${type}: ${count}`)
  }
}

main().catch(error => {
  console.error('Error:', error.message)
  if (error.status) {
    console.error(`HTTP ${error.status}`)
  }
  process.exit(1)
})
