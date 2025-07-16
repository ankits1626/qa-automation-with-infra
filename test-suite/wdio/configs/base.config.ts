import * as path from 'path';

export const baseConfig = {
  //
  // Test Configuration
  //
  runner: 'local',

  //
  // Test Files
  //
  specs: [
    path.join(__dirname, '../../src/tests/**/*.test.ts'),
    path.join(__dirname, '../../src/tests/**/*.spec.ts')
  ],
  exclude: [
    // 'path/to/excluded/files'
  ],

  //
  // Capabilities
  //
  maxInstances: 1,
  capabilities: [],

  //
  // Test Configuration
  //
  logLevel: 'info',
  bail: 0,
  waitforTimeout: 15000,
  connectionRetryTimeout: 180000,
  connectionRetryCount: 5,

  //
  // Test Framework
  //
  framework: 'mocha',
  mochaOpts: {
    ui: 'bdd',
    timeout: 60000
  },

  //
  // Test Reporters
  //
  reporters: [
    'spec',
    [
      'junit',
      {
        outputDir: './test-results',
        outputFileFormat: function (options: any) {
          return `junit-${options.cid}.xml`;
        }
      }
    ],
    [
      'mochawesome',
      {
        outputDir: './test-results',
        outputFileFormat: function (options: any) {
          return `mochawesome-${options.cid}.json`;
        }
      }
    ]
  ],

  //
  // Hooks
  //
  onPrepare: function (config: any, capabilities: any) {
    console.log('Starting test execution...');
  },

  onComplete: function (exitCode: any, config: any, capabilities: any, results: any) {
    console.log('Test execution completed');
  },

  beforeSession: function (config: any, capabilities: any, specs: any) {
    console.log('Starting new session...');
  },

  afterSession: function (config: any, capabilities: any, specs: any) {
    console.log('Session ended');
  },

  beforeTest: function (test: any, context: any) {
    console.log(`Starting test: ${test.title}`);
  },

  afterTest: function (test: any, context: any, { error, result, duration, passed, retries }: any) {
    console.log(`Test ${test.title} ${passed ? 'PASSED' : 'FAILED'}`);
  }
};