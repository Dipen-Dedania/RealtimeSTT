// TranscriberService.js - Complete working implementation
const { spawn } = require('child_process');
const path = require('path');
const EventEmitter = require('events');

class TranscriberService extends EventEmitter {
  constructor(pythonScriptPath, pythonCommand = 'python') {
    super();
    this.scriptPath = pythonScriptPath;
    this.pythonCommand = pythonCommand;
    this.process = null;
    this.isInitialized = false;
    this.isRunning = false;
    
    // Auto-detect if this is an executable or Python script
    this.isExecutable = pythonScriptPath.endsWith('.exe') || 
                        pythonScriptPath.endsWith('.app') || 
                        !pythonScriptPath.includes('.');
  }

  /**
   * Start the transcriber process
   */
  start() {
    if (this.process) {
      console.warn('[Transcriber] Already started');
      return;
    }

    if (this.isExecutable) {
      console.log(`[Transcriber] Starting executable: ${this.scriptPath}`);
      // Spawn executable directly
      this.process = spawn(this.scriptPath, [], {
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } else {
      console.log(`[Transcriber] Starting Python script: ${this.scriptPath}`);
      // Spawn via Python interpreter
      this.process = spawn(this.pythonCommand, [this.scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe'] // stdin, stdout, stderr
      });
    }

    // Handle stdout - where JSON messages come from
    this.process.stdout.on('data', (data) => {
      const lines = data.toString().split('\n');
      
      lines.forEach(line => {
        if (line.trim()) {
          try {
            const message = JSON.parse(line);
            this.handleMessage(message);
          } catch (err) {
            console.warn('[Transcriber] Failed to parse:', line);
          }
        }
      });
    });

    // Handle stderr - for debugging
    this.process.stderr.on('data', (data) => {
      console.error('[Transcriber Error]:', data.toString());
      this.emit('error', { message: data.toString() });
    });

    // Handle process exit
    this.process.on('close', (code) => {
      console.log(`[Transcriber] Process exited with code ${code}`);
      this.process = null;
      this.isInitialized = false;
      this.isRunning = false;
      this.emit('closed', { code });
    });

    // Handle process errors
    this.process.on('error', (err) => {
      console.error('[Transcriber] Failed to start:', err);
      this.emit('error', { message: err.message });
    });
  }

  /**
   * Handle incoming messages from Python
   */
  handleMessage(message) {
    const { type, data, timestamp } = message;

    console.log(`[Transcriber] ${type}:`, data);

    switch (type) {
      case 'ready':
        this.emit('ready', data);
        break;

      case 'initialized':
        this.isInitialized = true;
        this.emit('initialized', data);
        break;

      case 'started':
        this.isRunning = true;
        this.emit('started', data);
        break;

      case 'stopped':
        this.isRunning = false;
        this.emit('stopped', data);
        break;

      case 'transcription':
        // This is the actual transcribed text!
        this.emit('transcription', data);
        break;

      case 'speech_detected':
        this.emit('speech_detected', data);
        break;

      case 'devices':
        this.emit('devices', data);
        break;

      case 'status':
        this.emit('status', data);
        break;

      case 'error':
        this.emit('error', data);
        break;

      case 'warning':
        this.emit('warning', data);
        break;

      default:
        console.warn('[Transcriber] Unknown message type:', type);
    }
  }

  /**
   * Send a command to the Python process
   */
  sendCommand(command, params = {}) {
    if (!this.process) {
      throw new Error('Transcriber not started');
    }

    const message = JSON.stringify({ command, ...params }) + '\n';
    this.process.stdin.write(message);
  }

  /**
   * Initialize the transcriber with device and model
   */
  initialize(deviceIndex = 34, model = 'tiny') {
    console.log(`[Transcriber] Initializing with device ${deviceIndex}, model ${model}`);
    this.sendCommand('initialize', { deviceIndex, model });
  }

  /**
   * Start transcription
   */
  startTranscription() {
    console.log('[Transcriber] Starting transcription');
    this.sendCommand('start');
  }

  /**
   * Stop transcription
   */
  stopTranscription() {
    console.log('[Transcriber] Stopping transcription');
    this.sendCommand('stop');
  }

  /**
   * List available audio devices
   */
  listDevices() {
    console.log('[Transcriber] Listing devices');
    this.sendCommand('list_devices');
  }

  /**
   * Terminate the transcriber process
   */
  terminate() {
    if (this.process) {
      console.log('[Transcriber] Terminating process');
      this.sendCommand('exit');
      
      // Force kill after 2 seconds if not closed gracefully
      setTimeout(() => {
        if (this.process) {
          console.log('[Transcriber] Force killing process');
          this.process.kill('SIGTERM');
        }
      }, 2000);
    }
  }
}

module.exports = TranscriberService;

// Example usage:
/*
const TranscriberService = require('./TranscriberService');
const path = require('path');

// Option 1: Use Python script (recommended for development)
const transcriber = new TranscriberService(
  path.join(__dirname, 'electron_transcriber.py'),
  'python'  // or 'python3' on some systems
);

// Option 2: Use PyInstaller executable (if you have one working)
// const transcriber = new TranscriberService(
//   path.join(__dirname, 'dist', 'transcriber.exe')
// );

transcriber.on('ready', () => {
  console.log('Transcriber is ready!');
  transcriber.initialize(34, 'tiny');
});

transcriber.on('initialized', (data) => {
  console.log('Initialized:', data);
  transcriber.startTranscription();
});

transcriber.on('transcription', (data) => {
  console.log('Transcription:', data.text);
});

transcriber.on('error', (data) => {
  console.error('Error:', data.message);
});

transcriber.start();

// Clean up on exit
process.on('SIGINT', () => {
  transcriber.terminate();
  process.exit(0);
});
*/
