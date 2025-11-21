#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing system dependencies..."
# Install Tesseract OCR and Poppler for PDF processing
apt-get update
apt-get install -y tesseract-ocr poppler-utils

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Build completed successfully!"
