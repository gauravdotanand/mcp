#!/usr/bin/env python3
"""
Demo script for extracting table data in JSON format.
"""

import json
import sys
from table_extractor import TableExtractor

def main():
    """
    Main function to demonstrate JSON extraction.
    """
    print("Table Extraction JSON Demo")
    print("=" * 30)
    
    # Check if image path is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter the path to your image: ").strip()
        if not image_path:
            print("Please provide an image path.")
            return
    
    try:
        # Initialize the extractor
        print("Initializing TableExtractor...")
        extractor = TableExtractor(confidence_threshold=0.5)
        
        # Extract tables in JSON format
        print(f"Extracting tables from '{image_path}'...")
        tables_json = extractor.extract_all_tables_json(image_path, use_easyocr=True)
        
        if not tables_json:
            print("No tables found or extracted.")
            return
        
        # Display results
        print(f"\nFound {len(tables_json)} table(s):")
        
        for i, table in enumerate(tables_json):
            print(f"\nTable {i+1}:")
            print(f"Headers: {table['header']}")
            print(f"Rows: {len(table['rows'])}")
            print("Data:")
            for j, row in enumerate(table['rows']):
                print(f"  Row {j+1}: {row}")
        
        # Save to JSON file
        output_file = "extracted_tables.json"
        with open(output_file, 'w') as f:
            json.dump(tables_json, f, indent=2)
        
        print(f"\nJSON data saved to '{output_file}'")
        
        # Also save individual tables
        for i, table in enumerate(tables_json):
            table_file = f"table_{i+1}.json"
            with open(table_file, 'w') as f:
                json.dump(table, f, indent=2)
            print(f"Table {i+1} saved to '{table_file}'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def quick_test():
    """
    Quick test with sample image.
    """
    print("Running quick JSON test...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        # Draw a table
        table_data = [
            ["Name", "Age", "City", "Salary"],
            ["John Doe", "30", "New York", "$50,000"],
            ["Jane Smith", "25", "Los Angeles", "$45,000"],
            ["Bob Johnson", "35", "Chicago", "$60,000"]
        ]
        
        cell_width = 180
        cell_height = 60
        start_x = 50
        start_y = 50
        
        for i, row in enumerate(table_data):
            for j, cell in enumerate(row):
                x = start_x + j * cell_width
                y = start_y + i * cell_height
                draw.rectangle([x, y, x + cell_width, y + cell_height], 
                             outline='black', width=3)
                draw.text((x + 10, y + 15), cell, fill='black', font=font)
        
        test_image = "json_test_table.jpg"
        img.save(test_image, quality=95)
        
        print(f"Created test image: {test_image}")
        
        # Run JSON extraction
        sys.argv = [sys.argv[0], test_image]
        main()
        
    except Exception as e:
        print(f"Quick test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick-test":
        quick_test()
    else:
        main() 