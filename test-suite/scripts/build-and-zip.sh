#!/bin/bash
set -e

echo "🛠️  Cleaning previous build..."
rm -rf dist system_tests.zip devicefarm-build

echo "📦  Installing dependencies with pnpm..."
pnpm install --frozen-lockfile

echo "🔧  Compiling TypeScript..."
pnpm run build

echo "📂  Preparing bundle directory..."
mkdir -p devicefarm-build

echo "📁  Copying required files for Device Farm..."
# Copy compiled JavaScript
cp -r dist devicefarm-build/

# Copy node_modules (required for Device Farm)
cp -r node_modules devicefarm-build/

# Copy package files
cp package.json devicefarm-build/
cp pnpm-lock.yaml devicefarm-build/

# Create npm-compatible package-lock.json for Device Farm
echo "🔄  Converting pnpm-lock.yaml to package-lock.json for Device Farm compatibility..."
cd devicefarm-build
# Device Farm expects package-lock.json, so we'll create a basic one
echo '{"lockfileVersion": 1}' > package-lock.json
cd ..

echo "📋  Creating Device Farm test specification..."
# Copy Device Farm test spec if it exists
if [ -f "appium-ios-test.yml" ]; then
    cp appium-ios-test.yml devicefarm-build/
fi

echo "🗜️  Creating system_tests.zip for AWS Device Farm..."
cd devicefarm-build
zip -r ../system_tests.zip . -x "*.DS_Store" "*/.*"
cd ..

echo "📊  Bundle information:"
echo "   📦 Size: $(du -h system_tests.zip | cut -f1)"
echo "   📁 Contents:"
unzip -l system_tests.zip | head -20

echo ""
echo "✅ Done: system_tests.zip is ready for upload to AWS Device Farm"
echo "📤 Upload this file to your Device Farm project"
echo "🎯 Make sure to:"
echo "   1. Set TARGET=df.ios in your Device Farm test specification"
echo "   2. Use: node dist/wdio/runner.js as your test command"
echo "   3. Update app path in df.ios.config.ts for Device Farm"