import os
import requests
from pathlib import Path
from typing import List, Dict
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentUploader:
    def __init__(self, api_url: str = "http://localhost:8000/upload"):
        """
        Initialize the document uploader.
        
        Args:
            api_url (str): The URL of the upload endpoint
        """
        self.api_url = api_url
        self.successful_uploads: List[Dict] = []
        self.failed_uploads: List[Dict] = []

    def upload_document(self, file_path: str) -> bool:
        """
        Upload a single document to the vector database.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False

            if not file_path.lower().endswith('.pdf'):
                logger.error(f"Only PDF files are supported: {file_path}")
                return False

            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'application/pdf')}
                response = requests.post(self.api_url, files=files)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully processed {result['message']}")
                logger.info(f"Number of chunks added: {result['chunks_added']}")
                self.successful_uploads.append({
                    'file': file_path,
                    'chunks_added': result['chunks_added']
                })
                return True
            else:
                logger.error(f"Failed to upload {file_path}: {response.status_code}")
                logger.error(response.text)
                self.failed_uploads.append({
                    'file': file_path,
                    'error': f"Status code: {response.status_code}, Response: {response.text}"
                })
                return False

        except Exception as e:
            logger.error(f"Error uploading {file_path}: {str(e)}")
            self.failed_uploads.append({
                'file': file_path,
                'error': str(e)
            })
            return False

    def upload_directory(self, directory_path: str) -> None:
        """
        Upload all PDF files from a directory.
        
        Args:
            directory_path (str): Path to the directory containing PDF files
        """
        directory = Path(directory_path)
        if not directory.exists():
            logger.error(f"Directory not found: {directory_path}")
            return

        pdf_files = list(directory.glob('**/*.pdf'))
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return

        logger.info(f"Found {len(pdf_files)} PDF files to upload")
        
        for file_path in tqdm(pdf_files, desc="Uploading documents"):
            self.upload_document(str(file_path))

    def print_summary(self) -> None:
        """Print a summary of the upload process."""
        logger.info("\nUpload Summary:")
        logger.info(f"Total successful uploads: {len(self.successful_uploads)}")
        logger.info(f"Total failed uploads: {len(self.failed_uploads)}")
        
        if self.successful_uploads:
            logger.info("\nSuccessful uploads:")
            for upload in self.successful_uploads:
                logger.info(f"- {upload['file']} ({upload['chunks_added']} chunks)")
        
        if self.failed_uploads:
            logger.info("\nFailed uploads:")
            for upload in self.failed_uploads:
                logger.info(f"- {upload['file']}: {upload['error']}")

def main():
    """Main function to run the document uploader."""
    import argparse
    
    # Get the absolute path to the backend directory
    backend_dir = Path(__file__).parent.parent
    docs_dir = backend_dir / "docs_new"
    
    parser = argparse.ArgumentParser(description='Upload documents to the vector database')
    parser.add_argument('--path', default=str(docs_dir),
                      help=f'Path to a PDF file or directory containing PDF files (default: {docs_dir})')
    parser.add_argument('--api-url', default='http://localhost:8000/upload',
                      help='URL of the upload API endpoint')
    
    args = parser.parse_args()
    
    uploader = DocumentUploader(api_url=args.api_url)
    
    if os.path.isfile(args.path):
        uploader.upload_document(args.path)
    elif os.path.isdir(args.path):
        uploader.upload_directory(args.path)
    else:
        logger.error(f"Invalid path: {args.path}")
        return
    
    uploader.print_summary()

if __name__ == "__main__":
    main() 