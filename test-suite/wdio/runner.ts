import { Launcher } from '@wdio/cli';
import * as path from 'path';
import * as fs from 'fs';

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
      } catch (error) {
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
    const launcher = new Launcher(configPath);
    
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
    
  } catch (error) {
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