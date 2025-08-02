#!/bin/bash

# Script to test S3 bucket and lifecycle policy

echo "🧪 Testing S3 bucket setup..."

# Check if LocalStack is running
if ! docker ps | grep -q fastapi_mvc_localstack; then
    echo "❌ LocalStack is not running. Please start it first:"
    echo "   docker-compose up -d localstack"
    exit 1
fi

echo "✅ LocalStack is running"

# Check bucket exists
echo "📦 Checking bucket exists..."
if docker exec fastapi_mvc_localstack awslocal s3 ls | grep -q mvp-dating-bucket-2025; then
    echo "✅ Bucket mvp-dating-bucket-2025 exists"
else
    echo "❌ Bucket mvp-dating-bucket-2025 not found"
    exit 1
fi

# Check tmp folder
echo "📁 Checking tmp folder..."
docker exec fastapi_mvc_localstack awslocal s3 ls s3://mvp-dating-bucket-2025/

# Check lifecycle policy
echo "🔄 Checking lifecycle policy..."
if docker exec fastapi_mvc_localstack awslocal s3api get-bucket-lifecycle-configuration --bucket mvp-dating-bucket-2025 &>/dev/null; then
    echo "✅ Lifecycle policy is configured"
    docker exec fastapi_mvc_localstack awslocal s3api get-bucket-lifecycle-configuration --bucket mvp-dating-bucket-2025
else
    echo "⚠️  Lifecycle policy not found or not configured"
fi

# Test upload a dummy file
echo "📤 Testing file upload..."
echo "This is a test file" > /tmp/test-upload.txt

if docker exec fastapi_mvc_localstack awslocal s3 cp /tmp/test-upload.txt s3://mvp-dating-bucket-2025/tmp/test-file.txt; then
    echo "✅ Test file uploaded successfully"
    
    # List files in tmp folder
    echo "📋 Files in tmp folder:"
    docker exec fastapi_mvc_localstack awslocal s3 ls s3://mvp-dating-bucket-2025/tmp/
    
    # Clean up test file
    docker exec fastapi_mvc_localstack awslocal s3 rm s3://mvp-dating-bucket-2025/tmp/test-file.txt
    echo "🧹 Test file cleaned up"
else
    echo "❌ Test file upload failed"
    exit 1
fi

# Clean up local test file
rm -f /tmp/test-upload.txt

echo ""
echo "🎉 S3 bucket test completed successfully!"
echo "📍 Bucket: s3://mvp-dating-bucket-2025/tmp/"
echo "🗓️  Lifecycle: Files auto-delete after 7 days"
