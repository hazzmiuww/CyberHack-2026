#!/usr/bin/env node

const { spawn } = require('child_process');
const os = require('os');

// Get network IP
function getNetworkIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Skip internal and non-IPv4 addresses
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '0.0.0.0';
}

const networkIP = getNetworkIP();
const port = process.env.PORT || 3000;

console.log('\n🚀 Starting Next.js development server...\n');

// Start Next.js dev server
const child = spawn('pnpm', ['run', 'dev:next'], {
  stdio: 'pipe',
  shell: true,
});

let serverStarted = false;

child.stdout.on('data', (data) => {
  const output = data.toString();
  
  // Detect when server is ready
  if (!serverStarted && (output.includes('Ready in') || output.includes('started server'))) {
    serverStarted = true;
    
    console.log('\n✓ Next.js server ready!\n');
    console.log('  ┌─────────────────────────────────────────────────┐');
    console.log('  │                                                 │');
    console.log(`  │  Local:    \x1b[36mhttp://localhost:${port}/qc-dashboard\x1b[0m     │`);
    console.log(`  │  Network:  \x1b[36mhttp://${networkIP}:${port}\x1b[0m            │`);
    console.log('  │                                                 │');
    console.log('  └─────────────────────────────────────────────────┘\n');
  }
  
  // Pass through other output (but filter out default Next.js URLs)
  if (!output.includes('Local:') && !output.includes('Network:')) {
    process.stdout.write(output);
  }
});

child.stderr.on('data', (data) => {
  process.stderr.write(data);
});

child.on('close', (code) => {
  process.exit(code);
});

// Handle Ctrl+C
process.on('SIGINT', () => {
  child.kill('SIGINT');
});
