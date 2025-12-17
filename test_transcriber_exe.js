// test_transcriber_exe.js - Test using the PyInstaller executable
const { spawn } = require('child_process');
const path = require('path');

// Statistics tracking
const stats = {
  stable: 0,
  partial: 0,
  total: 0,
  segments: 0
};

// Collect final sentences from each segment
const finalSentences = [];

// Track current segment's latest stable text
let currentSegmentText = '';

console.log('='.repeat(60));
console.log('Testing Transcriber with PyInstaller EXE');
console.log('='.repeat(60));

// Path to the executable
const exePath = path.join(__dirname, 'dist', 'transcriber.exe');
console.log(`\nExecutable: ${exePath}`);

// Spawn the executable directly
const childProcess = spawn(exePath, [], {
  stdio: ['pipe', 'pipe', 'pipe']
});

// Handle stdout - JSON messages from the transcriber
childProcess.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  
  lines.forEach(line => {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        handleMessage(message);
      } catch (err) {
        // Non-JSON output (e.g., shutdown messages)
        if (!line.includes('shutting down')) {
          console.log('Raw:', line);
        }
      }
    }
  });
});

// Handle stderr - suppress debug logs, only show errors
childProcess.stderr.on('data', (data) => {
  const text = data.toString();
  // Only show actual errors, not INFO/DEBUG messages
  if (text.includes('ERROR') || text.includes('Exception') || text.includes('Traceback')) {
    console.error('Error:', text);
  }
});

// Helper to save current segment before exit
function saveCurrentSegment() {
  if (currentSegmentText.trim()) {
    stats.segments++;
    finalSentences.push(currentSegmentText.trim());
    currentSegmentText = '';
  }
}

// Handle process exit
childProcess.on('close', (code) => {
  // Save any pending segment that didn't get a final marker
  saveCurrentSegment();
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 SESSION SUMMARY');
  console.log('='.repeat(60));
  console.log(`Messages: ${stats.total} (${stats.stable} stable, ${stats.partial} partial)`);
  console.log(`Segments: ${stats.segments}`);

  // Display final transcription
  if (finalSentences.length > 0) {
    console.log('\n' + '='.repeat(60));
    console.log('📝 FINAL TRANSCRIPTION');
    console.log('='.repeat(60));
    
    if (finalSentences.length === 1) {
      console.log(`\n${finalSentences[0]}\n`);
    } else {
      // Show each segment
      finalSentences.forEach((sentence, i) => {
        console.log(`\n[${i + 1}] ${sentence}`);
      });
      
      // Combined
      console.log('\n' + '-'.repeat(60));
      console.log('Combined:', finalSentences.join(' '));
    }
    console.log('='.repeat(60));
  } else {
    console.log('\n(No speech detected)');
  }

  console.log(`\nExit code: ${code}`);
  process.exit(code);
});

// Handle process errors
childProcess.on('error', (err) => {
  console.error('Failed to start executable:', err);
  process.exit(1);
});

// Message handler
function handleMessage(message) {
  const { type, data } = message;

  switch (type) {
    case 'ready':
      console.log('\n✅ Ready');
      sendCommand('list_devices');
      break;

    case 'devices':
      console.log('\n📱 Audio Devices:');
      data.devices.forEach(device => {
        if (device.channels > 0) {
          console.log(`  [${device.index}] ${device.name} (${device.channels}ch, ${device.sampleRate}Hz)`);
        }
      });
      
      console.log('\n⚙️  Initializing device 34 (loopback)...');
      sendCommand('initialize', { deviceIndex: 34, model: 'tiny' });
      break;

    case 'initialized':
      console.log('✅ Initialized');
      sendCommand('start');
      break;

    case 'started':
      console.log('\n' + '═'.repeat(60));
      console.log('🎤 LISTENING (30s demo, Ctrl+C to stop)');
      console.log('═'.repeat(60));
      break;

    case 'speech_detected':
      console.log(`\n🗣️  Speech started`);
      break;

    case 'transcription':
      stats.total++;

      if (data.is_stable && !data.is_partial) {
        stats.stable++;
        currentSegmentText = data.text;
        // Show stable updates inline (overwrite style)
        process.stdout.write(`\r✅ ${data.text.substring(0, 70)}${data.text.length > 70 ? '...' : ''}`.padEnd(80));
      } else if (data.is_partial) {
        stats.partial++;
        // Don't show partials - too noisy
      }

      // When segment ends naturally
      if (data.is_final) {
        saveCurrentSegment();
        console.log('\n   └─ [SEGMENT COMPLETE]');
      }
      break;

    case 'status':
      // Suppress status messages
      break;

    case 'error':
      console.error(`\n❌ ${data.message}`);
      break;

    case 'stopped':
      console.log(`\n\n✅ Stopped`);
      break;

    default:
      // Ignore unknown messages
      break;
  }
}

// Send command to the process
function sendCommand(command, params = {}) {
  const message = JSON.stringify({ command, ...params }) + '\n';
  childProcess.stdin.write(message);
}

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\nStopping...');
  sendCommand('stop');
  setTimeout(() => {
    sendCommand('exit');
  }, 1000);
});

// Auto-stop after 30 seconds for demo
setTimeout(() => {
  console.log('\n\n⏱️  Demo time limit (30s)');
  sendCommand('stop');
  setTimeout(() => {
    sendCommand('exit');
  }, 1500);
}, 30000);

console.log('\nStarting...');
