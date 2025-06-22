#!/usr/bin/env python3
"""
Example usage of the TableExtractor class for extracting table data from images.
"""

import os
import pandas as pd
from table_extractor import TableExtractor

def main():
    """
    Main function demonstrating table extraction capabilities.
    """
    
    # Initialize the table extractor
    # You can specify a custom YOLO model path if you have one trained for table detection
    # extractor = TableExtractor(model_path='path/to/your/custom_model.pt', confidence_threshold=0.5)
    
    # For this example, we'll use the default YOLO V8n model
    extractor = TableExtractor(confidence_threshold=0.5)
    
    # Example 1: Extract tables from a single image
    image_path = "sample_image.jpg"  # Replace with your image path
    
    if os.path.exists(image_path):
        print(f"Processing image: {image_path}")
        
        # Detect tables in the image
        detections = extractor.detect_tables(image_path)
        print(f"Detected {len(detections)} tables")
        
        # Visualize the detections
        extractor.visualize_detections(image_path, detections, "detections_visualization.jpg")
        
        # Extract all tables from the image
        tables_data = extractor.extract_all_tables(image_path, use_easyocr=True)
        
        # Save extracted tables to CSV files
        for i, table_data in enumerate(tables_data):
            if not table_data.empty:
                output_file = f"extracted_table_{i+1}.csv"
                table_data.to_csv(output_file, index=False)
                print(f"Saved table {i+1} to {output_file}")
                print(f"Table {i+1} shape: {table_data.shape}")
                print(f"Table {i+1} preview:")
                print(table_data.head())
                print("-" * 50)
    else:
        print(f"Image file {image_path} not found. Please provide a valid image path.")
    
    # Example 2: Process multiple images in a directory
    def process_directory(directory_path):
        """
        Process all images in a directory.
        
        Args:
            directory_path (str): Path to directory containing images
        """
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} not found.")
            return
        
        # Supported image formats
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        
        # Get all image files in the directory
        image_files = []
        for file in os.listdir(directory_path):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(directory_path, file))
        
        if not image_files:
            print(f"No image files found in {directory_path}")
            return
        
        print(f"Found {len(image_files)} images to process")
        
        # Process each image
        for image_file in image_files:
            print(f"\nProcessing: {image_file}")
            
            try:
                # Extract tables
                tables_data = extractor.extract_all_tables(image_file, use_easyocr=True)
                
                # Save results
                base_name = os.path.splitext(os.path.basename(image_file))[0]
                for i, table_data in enumerate(tables_data):
                    if not table_data.empty:
                        output_file = f"{base_name}_table_{i+1}.csv"
                        table_data.to_csv(output_file, index=False)
                        print(f"  Saved table {i+1} to {output_file}")
                
            except Exception as e:
                print(f"  Error processing {image_file}: {e}")
    
    # Uncomment the line below to process a directory of images
    # process_directory("path/to/your/image/directory")

def example_with_custom_model():
    """
    Example showing how to use a custom YOLO model trained specifically for table detection.
    """
    # Path to your custom YOLO V8n model trained on table detection dataset
    custom_model_path = "path/to/your/custom_table_detection_model.pt"
    
    if os.path.exists(custom_model_path):
        # Initialize with custom model
        extractor = TableExtractor(
            model_path=custom_model_path,
            confidence_threshold=0.6  # Higher confidence for custom model
        )
        
        # Process image
        image_path = "sample_image.jpg"
        if os.path.exists(image_path):
            tables_data = extractor.extract_all_tables(image_path, use_easyocr=True)
            
            # Save results
            for i, table_data in enumerate(tables_data):
                if not table_data.empty:
                    output_file = f"custom_model_table_{i+1}.csv"
                    table_data.to_csv(output_file, index=False)
                    print(f"Saved table {i+1} using custom model to {output_file}")
    else:
        print("Custom model not found. Please provide a valid path to your trained model.")

def example_ocr_comparison():
    """
    Example comparing EasyOCR vs Tesseract OCR for table extraction.
    """
    extractor = TableExtractor()
    image_path = "sample_image.jpg"
    
    if os.path.exists(image_path):
        # Detect tables
        detections = extractor.detect_tables(image_path)
        
        if detections:
            # Extract using EasyOCR
            print("Extracting with EasyOCR...")
            easyocr_tables = extractor.extract_all_tables(image_path, use_easyocr=True)
            
            # Extract using Tesseract
            print("Extracting with Tesseract...")
            tesseract_tables = extractor.extract_all_tables(image_path, use_easyocr=False)
            
            # Compare results
            print(f"EasyOCR extracted {len(easyocr_tables)} tables")
            print(f"Tesseract extracted {len(tesseract_tables)} tables")
            
            # Save both results for comparison
            for i, (easyocr_table, tesseract_table) in enumerate(zip(easyocr_tables, tesseract_tables)):
                easyocr_table.to_csv(f"easyocr_table_{i+1}.csv", index=False)
                tesseract_table.to_csv(f"tesseract_table_{i+1}.csv", index=False)
                print(f"Saved comparison tables {i+1}")

if __name__ == "__main__":
    print("Table Extraction Example")
    print("=" * 50)
    
    # Run the main example
    main()
    
    # Uncomment the lines below to run additional examples
    # example_with_custom_model()
    # example_ocr_comparison()
    
    print("\nExample completed!") 