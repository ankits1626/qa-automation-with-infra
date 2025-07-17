import { baseConfig } from './base.config';
import path from 'path';
const isCompiled = __filename.endsWith('.js');
const configExt = isCompiled ? 'js' : 'ts';
export const config = {
  ...baseConfig,
  
  //
  // AWS Device Farm Configuration
  //
  
  specs: [path.resolve(__dirname, `../../src/tests/**/*.${configExt}`)], // Relative path to compiled JS files
  hostname: '127.0.0.1',
  port: 4723,
  path: '/wd/hub',
  
  //
  // Device Farm Services (no local services needed)
  //
  services: [],
  
  //
  // Device Farm iOS Capabilities
  //
  capabilities: [
    {
      platformName: 'iOS',
      'appium:automationName': 'XCUITest',
      'appium:locale': 'en_US',
      'appium:language': 'en',
      'appium:newCommandTimeout': 240,
      'appium:shouldTerminateApp': true,
      'appium:noReset': false,
      'appium:fullReset': false,
      'appium:wdaLaunchTimeout': 60000,
      'appium:wdaConnectionTimeout': 60000,
    },
  ],

  //
  // Device Farm specific timeouts
  //
  waitforTimeout: 30000, // Longer timeouts for real devices
  connectionRetryTimeout: 180000, // 3 minutes for device connections
  connectionRetryCount: 3,

  //
  // Test execution settings for Device Farm
  //
  maxInstances: 1, // Device Farm runs one test at a time per device
  logLevel: 'info',

  //
  // Device Farm Hooks
  //
  beforeSession: function (config: any, capabilities: any, specs: any) {
    console.log('🔥 Starting AWS Device Farm session...');
    console.log(`📱 Platform: ${capabilities.platformName}`);
    console.log(`🤖 Automation: ${capabilities['appium:automationName']}`);
    console.log(`🌐 Language: ${capabilities['appium:language']}`);
  },

  before: function (capabilities: any, specs: any) {
    console.log('⚙️ Setting up Device Farm test environment...');
    console.log(`📋 Running ${specs.length} test file(s)`);
  },

  afterSession: function (config: any, capabilities: any, specs: any) {
    console.log('✅ AWS Device Farm session completed');
  },

  onComplete: function (exitCode: any, config: any, capabilities: any, results: any) {
    console.log('📊 Device Farm test execution summary:');
    console.log(`Exit code: ${exitCode}`);
    console.log('🏁 All Device Farm tests completed');
  }
};