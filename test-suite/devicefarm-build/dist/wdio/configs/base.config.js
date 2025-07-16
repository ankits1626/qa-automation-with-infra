"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.baseConfig = void 0;
const path = __importStar(require("path"));
exports.baseConfig = {
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
                outputFileFormat: function (options) {
                    return `junit-${options.cid}.xml`;
                }
            }
        ],
        [
            'mochawesome',
            {
                outputDir: './test-results',
                outputFileFormat: function (options) {
                    return `mochawesome-${options.cid}.json`;
                }
            }
        ]
    ],
    //
    // Hooks
    //
    onPrepare: function (config, capabilities) {
        console.log('Starting test execution...');
    },
    onComplete: function (exitCode, config, capabilities, results) {
        console.log('Test execution completed');
    },
    beforeSession: function (config, capabilities, specs) {
        console.log('Starting new session...');
    },
    afterSession: function (config, capabilities, specs) {
        console.log('Session ended');
    },
    beforeTest: function (test, context) {
        console.log(`Starting test: ${test.title}`);
    },
    afterTest: function (test, context, { error, result, duration, passed, retries }) {
        console.log(`Test ${test.title} ${passed ? 'PASSED' : 'FAILED'}`);
    }
};
