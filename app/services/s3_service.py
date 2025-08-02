import boto3
import uuid
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError, NoCredentialsError
from app.config.settings import settings
from app.utils.logger import get_logger
import os
from datetime import datetime

logger = get_logger("s3-service")

class S3Service:
    """Service for S3 operations"""
    
    def __init__(self):
        """Initialize S3 client with LocalStack configuration"""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.AWS_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
            logger.info(f"S3 client initialized with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise
    
    async def create_bucket_if_not_exists(self) -> bool:
        """
        Create S3 bucket if it doesn't exist
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.debug(f"Bucket {self.bucket_name} already exists")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                    return True
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {self.bucket_name}: {str(create_error)}")
                    return False
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {str(e)}")
                return False
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename for S3 storage in tmp folder
        
        Args:
            original_filename: Original file name
            
        Returns:
            Unique filename with timestamp and UUID in tmp folder
        """
        
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Upload to tmp folder (with 7-day auto-delete lifecycle)
        return f"{settings.S3_TEMP_FOLDER}/{timestamp}_{unique_id}{ext}"
    
    async def upload_file(
        self, 
        file_obj: BinaryIO, 
        original_filename: str,
        content_type: str
    ) -> Optional[str]:
        """
        Upload file to S3
        
        Args:
            file_obj: File object to upload
            original_filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            S3 file path/key if successful, None otherwise
        """
        try:
            # Ensure bucket exists
            if not await self.create_bucket_if_not_exists():
                logger.error("Failed to ensure bucket exists")
                return None
            
            # Generate unique filename
            file_key = self.generate_unique_filename(original_filename)
            
            # Upload file
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'original_filename': original_filename
                    }
                }
            )
            
            logger.info(f"Successfully uploaded file: {file_key}")
            return file_key
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return None
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            return None
    
    def generate_presigned_url(self, file_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for file access
        
        Args:
            file_key: S3 file path/key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL if successful, None otherwise
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            logger.debug(f"Generated presigned URL for: {file_key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {file_key}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            return None

# Create instance for dependency injection
s3_service = S3Service()
