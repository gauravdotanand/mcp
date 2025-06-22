#!/usr/bin/env python3
"""
Simple demo script for table extraction using YOLO V8n.
"""

import os
import sys
from table_extractor import TableExtractor

def main():
    """
    Main demo function.
    """
    print("Table Extraction Demo using YOLO V8n")
    print("=" * 40)
    
    # Check if image path is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use default sample image or ask user
        image_path = input("Enter the path to your image (or press Enter to use sample): ").strip()
        if not image_path:
            print("Please provide an image path to test the system.")
            print("Usage: python demo.py <image_path>")
            return
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return
    
    try:
        # Initialize the table extractor
        print("Initializing TableExtractor...")
        extractor = TableExtractor(confidence_threshold=0.5)
        
        # Step 1: Detect tables
        print(f"\n1. Detecting tables in '{image_path}'...")
        detections = extractor.detect_tables(image_path)
        
        if not detections:
            print("No tables detected. Try lowering the confidence threshold.")
            return
        
        print(f"Found {len(detections)} table(s)")
        
        # Step 2: Visualize detections
        print("\n2. Creating visualization...")
        output_viz = "detection_visualization.jpg"
        extractor.visualize_detections(image_path, detections, output_viz)
        print(f"Visualization saved as '{output_viz}'")
        
        # Step 3: Extract table data
        print("\n3. Extracting table data...")
        print("Using EasyOCR for text extraction...")
        tables_data = extractor.extract_all_tables(image_path, use_easyocr=True)
        
        if not tables_data:
            print("No table data extracted. Trying with Tesseract...")
            tables_data = extractor.extract_all_tables(image_path, use_easyocr=False)
        
        # Step 4: Save results
        if tables_data:
            print(f"\n4. Saving {len(tables_data)} table(s)...")
            for i, table_data in enumerate(tables_data):
                if not table_data.empty:
                    output_file = f"extracted_table_{i+1}.csv"
                    table_data.to_csv(output_file, index=False)
                    print(f"Table {i+1} saved as '{output_file}'")
                    print(f"  Shape: {table_data.shape}")
                    print(f"  Preview:")
                    print(table_data.head())
                    print("-" * 30)
        else:
            print("No table data could be extracted.")
        
        print("\nDemo completed successfully!")
        print("Generated files:")
        print(f"- {output_viz} (detection visualization)")
        for i in range(len(tables_data)):
            print(f"- extracted_table_{i+1}.csv (table data)")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()

def quick_test():
    """
    Quick test with a sample image.
    """
    print("Running quick test...")
    
    # Create a simple test image
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple table image with better contrast
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a better font
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        # Draw a simple table with better spacing
        table_data = [
            ["Product", "Price", "Stock", "Category"],
            ["Laptop", "$999", "50", "Electronics"],
            ["Mouse", "$25", "100", "Accessories"],
            ["Keyboard", "$75", "30", "Accessories"],
            ["Monitor", "$299", "25", "Electronics"]
        ]
        
        # Table dimensions
        cell_width = 180
        cell_height = 60
        start_x = 50
        start_y = 50
        
        # Draw table with better contrast
        for i, row in enumerate(table_data):
            for j, cell in enumerate(row):
                x = start_x + j * cell_width
                y = start_y + i * cell_height
                
                # Draw cell border with thicker lines
                draw.rectangle([x, y, x + cell_width, y + cell_height], 
                             outline='black', width=3)
                
                # Draw text with better positioning
                text_bbox = draw.textbbox((x + 10, y + 15), cell, font=font)
                draw.text((x + 10, y + 15), cell, fill='black', font=font)
        
        test_image = "quick_test_table.jpg"
        img.save(test_image, quality=95)
        
        print(f"Created test image: {test_image}")
        
        # Run demo with test image
        sys.argv = [sys.argv[0], test_image]
        main()
        
    except ImportError:
        print("PIL not available. Please install Pillow for quick test.")
    except Exception as e:
        print(f"Quick test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick-test":
        quick_test()
    else:
        main() 