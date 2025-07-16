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
const cli_1 = require("@wdio/cli");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
/**
 * Dynamic WebdriverIO Configuration Runner
 * Loads configuration based on TARGET environment variable
 *
 * Usage:
 * TARGET=ios ts-node wdio/runner.ts
 * TARGET=df.ios node dist/wdio/runner.js
 */
async function runTests() {
    try {
        console.log('🚀 Starting WebdriverIO test execution...');
        console.log('');
        const target = process.env.TARGET;
        if (!target) {
            console.error('❌ TARGET environment variable is required');
            console.log('📋 Available targets:');
            console.log('   TARGET=ios - Local iOS simulator testing');
            console.log('   TARGET=df.ios - AWS Device Farm iOS testing');
            console.log('');
            console.log('💡 Example usage:');
            console.log('   TARGET=ios ts-node wdio/runner.ts');
            process.exit(1);
        }
        console.log(`🎯 Loading configuration for target: ${target}`);
        // Determine if we're running from source (TypeScript) or compiled (JavaScript)
        const isCompiledMode = __filename.endsWith('.js');
        const configDir = isCompiledMode
            ? path.join(__dirname, 'configs')
            : path.join(__dirname, 'configs');
        const configFileName = `${target}.config`;
        const configExtension = isCompiledMode ? '.js' : '.ts';
        const configPath = path.join(configDir, configFileName + configExtension);
        console.log(`📁 Looking for config at: ${configPath}`);
        // Check if config file exists
        if (!fs.existsSync(configPath)) {
            console.error(`❌ Configuration file not found: ${configPath}`);
            console.log('📋 Available configurations:');
            // List available config files
            try {
                const files = fs.readdirSync(configDir);
                const configFiles = files
                    .filter(file => file.endsWith('.config.ts') || file.endsWith('.config.js'))
                    .map(file => file.replace(/\.config\.(ts|js)$/, ''));
                configFiles.forEach(config => {
                    console.log(`   TARGET=${config}`);
                });
            }
            catch (error) {
                console.log('   No configuration files found');
            }
            process.exit(1);
        }
        console.log('✅ Configuration loaded successfully');
        // Change to project root directory so WebdriverIO can find test files
        const projectRoot = path.resolve(__dirname, '..');
        console.log(`📂 Changing to project root: ${projectRoot}`);
        process.chdir(projectRoot);
        console.log(`📍 Current working directory: ${process.cwd()}`);
        // Debug: Check if test file exists
        const testFile = path.join(process.cwd(), 'src/tests/setup/framework.test.ts');
        console.log(`🔍 Looking for test file at: ${testFile}`);
        console.log(`📁 Test file exists: ${fs.existsSync(testFile)}`);
        // Add delay to ensure proper timing
        console.log('⏱️  Allowing time for environment setup...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        // Create WebdriverIO launcher with the config file path
        const launcher = new cli_1.Launcher(configPath);
        // Handle command line arguments (e.g., --spec)
        const args = process.argv.slice(2);
        if (args.length > 0) {
            console.log(`🎯 Running with arguments: ${args.join(' ')}`);
        }
        // Run the tests
        const exitCode = await launcher.run();
        console.log('');
        console.log(`🏁 Test execution completed with exit code: ${exitCode}`);
        process.exit(exitCode);
    }
    catch (error) {
        console.error('❌ Test execution failed:', error);
        process.exit(1);
    }
}
// Execute if this file is run directly
if (require.main === module) {
    runTests().catch((error) => {
        console.error('❌ Unexpected error:', error);
        process.exit(1);
    });
}
