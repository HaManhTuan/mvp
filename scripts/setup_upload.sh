#!/bin/bash

# Script to setup and run the upload module

echo "Setting up upload module..."

# Install dependencies
echo "Installing boto3 and botocore..."
poetry add boto3 botocore

# Start LocalStack (if not running)
echo "Starting LocalStack S3..."
docker-compose up -d localstack

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
sleep 10

# Create S3 bucket
echo "Creating S3 bucket..."
docker exec fastapi_mvc_localstack awslocal s3 mb s3://mvp-dating-bucket-2025

# Create tmp folder and setup lifecycle policy (7-day auto-delete)
echo "Setting up tmp folder with lifecycle policy..."
docker exec fastapi_mvc_localstack awslocal s3api put-object --bucket mvp-dating-bucket-2025 --key tmp/

# Create lifecycle configuration for tmp folder
cat > /tmp/lifecycle.json << EOF
{
    "Rules": [
        {
            "ID": "DeleteTmpFilesAfter7Days",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "tmp/"
            },
            "Expiration": {
                "Days": 7
            }
        }
    ]
}
EOF

# Apply lifecycle policy
docker exec fastapi_mvc_localstack awslocal s3api put-bucket-lifecycle-configuration \
    --bucket mvp-dating-bucket-2025 \
    --lifecycle-configuration file:///tmp/lifecycle.json

# List buckets to verify
echo "Verifying bucket creation..."
docker exec fastapi_mvc_localstack awslocal s3 ls

# Verify lifecycle policy
echo "Verifying lifecycle policy..."
docker exec fastapi_mvc_localstack awslocal s3api get-bucket-lifecycle-configuration --bucket mvp-dating-bucket-2025

echo "Upload module setup complete!"
echo ""
echo "✅ S3 Bucket: mvp-dating-bucket-2025"
echo "✅ Temp Folder: tmp/ (auto-delete after 7 days)"
echo "✅ Lifecycle Policy: Active"
echo ""
echo "Available endpoints:"
echo "  POST /api/v1/upload/image - Upload image and get URL"
echo "  GET  /api/v1/upload/url/{file_key} - Get new URL for existing file"
echo ""
echo "Example usage:"
echo "  curl -X POST http://localhost:8000/api/v1/upload/image \\"
echo "       -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "       -F 'file=@your_image.jpg'"
echo ""
echo "Files will be uploaded to: s3://mvp-dating-bucket-2025/tmp/"
echo "Auto-cleanup: Files older than 7 days will be automatically deleted"
