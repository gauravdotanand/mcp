#!/usr/bin/env python3
"""
Test script for table extraction functionality.
"""

import os
import sys
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from table_extractor import TableExtractor

def create_sample_table_image(output_path: str = "sample_table.jpg", 
                             width: int = 800, height: int = 600):
    """
    Create a sample table image for testing.
    
    Args:
        output_path (str): Path to save the sample image
        width (int): Image width
        height (int): Image height
    """
    # Create a white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Define table data
    table_data = [
        ["Name", "Age", "City", "Salary"],
        ["John Doe", "30", "New York", "$50,000"],
        ["Jane Smith", "25", "Los Angeles", "$45,000"],
        ["Bob Johnson", "35", "Chicago", "$60,000"],
        ["Alice Brown", "28", "Houston", "$55,000"]
    ]
    
    # Table dimensions
    cell_width = 150
    cell_height = 40
    start_x = 100
    start_y = 100
    
    # Draw table
    for i, row in enumerate(table_data):
        for j, cell in enumerate(row):
            x = start_x + j * cell_width
            y = start_y + i * cell_height
            
            # Draw cell border
            draw.rectangle([x, y, x + cell_width, y + cell_height], 
                         outline='black', width=2)
            
            # Draw text
            text_bbox = draw.textbbox((x + 5, y + 5), cell, font=font)
            draw.text((x + 5, y + 5), cell, fill='black', font=font)
    
    # Save the image
    image.save(output_path)
    print(f"Sample table image created: {output_path}")
    
    return output_path

def test_table_detection():
    """
    Test table detection functionality.
    """
    print("Testing table detection...")
    
    # Create sample image
    sample_image = create_sample_table_image()
    
    # Initialize extractor
    extractor = TableExtractor(confidence_threshold=0.3)
    
    # Test detection
    detections = extractor.detect_tables(sample_image)
    print(f"Detected {len(detections)} tables")
    
    # Visualize detections
    extractor.visualize_detections(sample_image, detections, "test_detections.jpg")
    
    return detections, sample_image

def test_table_extraction():
    """
    Test table extraction functionality.
    """
    print("Testing table extraction...")
    
    # Create sample image
    sample_image = create_sample_table_image()
    
    # Initialize extractor
    extractor = TableExtractor(confidence_threshold=0.3)
    
    # Test extraction with EasyOCR
    print("Testing EasyOCR extraction...")
    easyocr_tables = extractor.extract_all_tables(sample_image, use_easyocr=True)
    
    # Test extraction with Tesseract
    print("Testing Tesseract extraction...")
    tesseract_tables = extractor.extract_all_tables(sample_image, use_easyocr=False)
    
    # Save results
    for i, table_data in enumerate(easyocr_tables):
        table_data.to_csv(f"test_easyocr_table_{i+1}.csv", index=False)
        print(f"EasyOCR Table {i+1}: {table_data.shape}")
    
    for i, table_data in enumerate(tesseract_tables):
        table_data.to_csv(f"test_tesseract_table_{i+1}.csv", index=False)
        print(f"Tesseract Table {i+1}: {table_data.shape}")
    
    return easyocr_tables, tesseract_tables

def test_custom_bbox_extraction():
    """
    Test extraction from custom bounding box.
    """
    print("Testing custom bounding box extraction...")
    
    # Create sample image
    sample_image = create_sample_table_image()
    
    # Initialize extractor
    extractor = TableExtractor()
    
    # Define custom bounding box (covers the table area)
    bbox = [100, 100, 700, 300]  # [x1, y1, x2, y2]
    
    # Extract from custom bbox
    table_data = extractor.extract_table_data(sample_image, bbox, use_easyocr=True)
    
    if not table_data.empty:
        table_data.to_csv("test_custom_bbox_table.csv", index=False)
        print(f"Custom bbox extraction successful: {table_data.shape}")
        print("Extracted data:")
        print(table_data)
    else:
        print("Custom bbox extraction failed")
    
    return table_data

def test_preprocessing():
    """
    Test image preprocessing functionality.
    """
    print("Testing image preprocessing...")
    
    # Create sample image
    sample_image = create_sample_table_image()
    
    # Initialize extractor
    extractor = TableExtractor()
    
    # Load image
    import cv2
    image = cv2.imread(sample_image)
    
    # Test preprocessing
    processed = extractor._preprocess_table_image(image)
    
    # Save processed image
    cv2.imwrite("test_preprocessed.jpg", processed)
    print("Preprocessed image saved: test_preprocessed.jpg")
    
    return processed

def run_all_tests():
    """
    Run all tests.
    """
    print("Running Table Extraction Tests")
    print("=" * 40)
    
    try:
        # Test 1: Table detection
        print("\n1. Testing table detection...")
        detections, sample_image = test_table_detection()
        
        # Test 2: Table extraction
        print("\n2. Testing table extraction...")
        easyocr_tables, tesseract_tables = test_table_extraction()
        
        # Test 3: Custom bbox extraction
        print("\n3. Testing custom bounding box extraction...")
        custom_table = test_custom_bbox_extraction()
        
        # Test 4: Preprocessing
        print("\n4. Testing image preprocessing...")
        processed_image = test_preprocessing()
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        print(f"Generated files:")
        print("- sample_table.jpg (sample image)")
        print("- test_detections.jpg (detection visualization)")
        print("- test_preprocessed.jpg (preprocessed image)")
        print("- test_easyocr_table_*.csv (EasyOCR results)")
        print("- test_tesseract_table_*.csv (Tesseract results)")
        print("- test_custom_bbox_table.csv (custom bbox results)")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def cleanup_test_files():
    """
    Clean up test files.
    """
    test_files = [
        "sample_table.jpg",
        "test_detections.jpg", 
        "test_preprocessed.jpg",
        "test_easyocr_table_1.csv",
        "test_tesseract_table_1.csv",
        "test_custom_bbox_table.csv"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed: {file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_test_files()
    else:
        run_all_tests() 