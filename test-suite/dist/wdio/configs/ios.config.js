"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
const base_config_1 = require("./base.config");
exports.config = {
    ...base_config_1.baseConfig,
    //
    // iOS Simulator Configuration
    //
    port: 4723,
    //
    // Capabilities
    //
    capabilities: [
        {
            "platformName": "iOS",
            "appium:deviceName": "iPhone 16 Pro",
            "appium:app": "/Users/ankit/Library/Developer/Xcode/DerivedData/MyTestApp-cmttkdapkxdbisggiawasvasbdpe/Build/Products/Debug-iphonesimulator/MyTestApp.app",
            "appium:locale": "en_US",
            "appium:showXcodeLog": false,
            "appium:automationName": "xcuitest"
        }
    ],
    //
    // Services
    //
    services: [
    // Disable Appium service - we'll run it manually
    ],
    // Add additional delay before starting tests
    beforeSession: async function (config, capabilities, specs) {
        console.log('Starting iOS simulator session...');
        console.log(`Device: ${capabilities['appium:deviceName']}`);
        console.log(`Platform Version: ${capabilities['appium:platformVersion']}`);
        // Wait for Appium to be fully ready
        console.log('⏳ Waiting for Appium to be ready...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        console.log('✅ Proceeding with test execution...');
    },
    //
    // iOS-specific timeouts
    //
    waitforTimeout: 15000,
    connectionRetryTimeout: 90000,
    //
    // Hooks - iOS specific
    //
    before: function (capabilities, specs) {
        console.log('Setting up iOS test environment...');
        // Add any iOS-specific setup here
    },
    afterSession: function (config, capabilities, specs) {
        console.log('iOS simulator session ended');
    }
};
