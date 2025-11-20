// test_transcriber.js - Simple test of the TranscriberService
const TranscriberService = require('./TranscriberService');
const path = require('path');

console.log('='.repeat(60));
console.log('Testing Transcriber Service');
console.log('='.repeat(60));

// Create transponder service
const transcriber = new TranscriberService(
  path.join(__dirname, 'electron_transcriber.py'),
  'python'
);

// Set up event handlers
transcriber.on('ready', (data) => {
  console.log('\n✅ Ready:', data.message);
  console.log('\nListing audio devices...');
  transcriber.listDevices();
});

transcriber.on('devices', (data) => {
  console.log('\n📱 Available Audio Devices:');
  data.devices.forEach(device => {
    if (device.channels > 0) {
      console.log(`  [${device.index}] ${device.name} (${device.channels} channels, ${device.sampleRate}Hz)`);
    }
  });
  
  console.log('\nInitializing with device 34...');
  transcriber.initialize(34, 'tiny');
});

transcriber.on('initialized', (data) => {
  console.log(`\n✅ Initialized:`, data);
  console.log('\nStarting transcription...');
  transcriber.startTranscription();
});

transcriber.on('started', (data) => {
  console.log(`\n✅ ${data.message}`);
  console.log('\n🎤 Listening for speech... (Press Ctrl+C to stop)');
  console.log('-'.repeat(60));
});

transcriber.on('speech_detected', (data) => {
  console.log(`\n🗣️  ${data.message}`);
});

transcriber.on('transcription', (data) => {
  console.log(`\n📝 Transcription: ${data.text}`);
});

transcriber.on('status', (data) => {
  console.log(`ℹ️  ${data.message}`);
});

transcriber.on('error', (data) => {
  console.error(`\n❌ Error: ${data.message}`);
});

transcriber.on('closed', (data) => {
  console.log(`\n👋 Process closed with code ${data.code}`);
  process.exit(0);
});

// Start the transcriber
console.log('\nStarting Python transcriber process...');
transcriber.start();

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\nShutting down...');
  transcriber.terminate();
  setTimeout(() => process.exit(0), 2000);
});

// Auto-stop after 30 seconds for demo
setTimeout(() => {
  console.log('\n\n⏱️  Demo time limit reached (30s)');
  console.log('Stopping transcription...');
  transcriber.stopTranscription();
  setTimeout(() => {
    transcriber.terminate();
  }, 2000);
}, 30000);
