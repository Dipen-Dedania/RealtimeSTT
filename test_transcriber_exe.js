// test_transcriber_exe.js - Test using the PyInstaller executable
const { spawn } = require('child_process');
const path = require('path');

console.log('='.repeat(60));
console.log('Testing Transcriber with PyInstaller EXE');
console.log('='.repeat(60));

// Path to the executable
const exePath = path.join(__dirname, 'dist', 'transcriber.exe');
console.log(`\nExecutable: ${exePath}`);

// Spawn the executable directly (no python command needed)
const process = spawn(exePath, [], {
  stdio: ['pipe', 'pipe', 'pipe']
});

// Handle stdout - JSON messages from the transcriber
process.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  
  lines.forEach(line => {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        handleMessage(message);
      } catch (err) {
        console.log('Raw output:', line);
      }
    }
  });
});

// Handle stderr
process.stderr.on('data', (data) => {
  console.error('Error:', data.toString());
});

// Handle process exit
process.on('close', (code) => {
  console.log(`\nProcess exited with code ${code}`);
  process.exit(code);
});

// Handle process errors
process.on('error', (err) => {
  console.error('Failed to start executable:', err);
  process.exit(1);
});

// Message handler
function handleMessage(message) {
  const { type, data } = message;

  switch (type) {
    case 'ready':
      console.log('\n✅ Ready:', data.message);
      console.log('\nListing audio devices...');
      sendCommand('list_devices');
      break;

    case 'devices':
      console.log('\n📱 Available Audio Devices:');
      data.devices.forEach(device => {
        if (device.channels > 0) {
          console.log(`  [${device.index}] ${device.name} (${device.channels} channels, ${device.sampleRate}Hz)`);
        }
      });
      
      console.log('\nInitializing with device 34...');
      sendCommand('initialize', { deviceIndex: 34, model: 'tiny' });
      break;

    case 'initialized':
      console.log(`\n✅ Initialized:`, data);
      console.log('\nStarting transcription...');
      sendCommand('start');
      break;

    case 'started':
      console.log(`\n✅ ${data.message}`);
      console.log('\n🎤 Listening for speech... (Press Ctrl+C to stop)');
      console.log('-'.repeat(60));
      break;

    case 'speech_detected':
      console.log(`\n🗣️  ${data.message}`);
      break;

    case 'transcription':
      console.log(`\n📝 Transcription: ${data.text}`);
      break;

    case 'status':
      console.log(`ℹ️  ${data.message}`);
      break;

    case 'error':
      console.error(`\n❌ Error: ${data.message}`);
      break;

    case 'stopped':
      console.log(`\n✅ ${data.message}`);
      break;

    default:
      console.log(`Unknown message type: ${type}`, data);
  }
}

// Send command to the process
function sendCommand(command, params = {}) {
  const message = JSON.stringify({ command, ...params }) + '\n';
  process.stdin.write(message);
}

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\nShutting down...');
  sendCommand('exit');
  setTimeout(() => process.exit(0), 2000);
});

// Auto-stop after 30 seconds for demo
setTimeout(() => {
  console.log('\n\n⏱️  Demo time limit reached (30s)');
  console.log('Stopping transcription...');
  sendCommand('stop');
  setTimeout(() => {
    sendCommand('exit');
  }, 2000);
}, 30000);

console.log('\nStarting executable...');
