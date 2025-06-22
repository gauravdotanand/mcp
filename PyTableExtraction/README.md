# Table Extraction using YOLO V8n

A Python-based solution for extracting table data from images using YOLO V8n object detection and OCR techniques.

## Features

- **YOLO V8n Integration**: Uses Ultralytics YOLO V8n for accurate table detection
- **Dual OCR Support**: Supports both EasyOCR and Tesseract for text extraction
- **Custom Model Training**: Tools to train your own YOLO model for table detection
- **Multiple Output Formats**: Extracts data to CSV format for easy analysis
- **Visualization**: Built-in visualization of detected tables
- **Batch Processing**: Process multiple images at once

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd PyTableExtraction
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Tesseract OCR** (optional, for Tesseract support):
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

## Quick Start

### Basic Usage

```python
from table_extractor import TableExtractor

# Initialize the extractor
extractor = TableExtractor(confidence_threshold=0.5)

# Extract tables from an image
image_path = "path/to/your/image.jpg"
tables_data = extractor.extract_all_tables(image_path, use_easyocr=True)

# Save results
for i, table_data in enumerate(tables_data):
    table_data.to_csv(f"extracted_table_{i+1}.csv", index=False)
    print(f"Table {i+1} shape: {table_data.shape}")
```

### Using a Custom YOLO Model

```python
# Initialize with your custom trained model
extractor = TableExtractor(
    model_path="path/to/your/custom_model.pt",
    confidence_threshold=0.6
)

# Extract tables
tables_data = extractor.extract_all_tables("image.jpg")
```

### Visualization

```python
# Detect tables and visualize
detections = extractor.detect_tables("image.jpg")
extractor.visualize_detections("image.jpg", detections, "output.jpg")
```

## Training Your Own Model

### 1. Prepare Your Dataset

Create the following directory structure:
```
table_detection_dataset/
├── train/
│   ├── images/
│   └── labels/
└── val/
    ├── images/
    └── labels/
```

### 2. Create Annotations

Each image should have a corresponding `.txt` file with YOLO format annotations:
```
0 0.5 0.3 0.8 0.6
0 0.2 0.7 0.4 0.3
```

Where:
- `0` = class ID for 'table'
- `0.5` = x_center (normalized)
- `0.3` = y_center (normalized)
- `0.8` = width (normalized)
- `0.6` = height (normalized)

### 3. Train the Model

```bash
python train_custom_model.py
```

Or use the training functions directly:

```python
from train_custom_model import train_custom_model, create_dataset_yaml

# Create dataset configuration
create_dataset_yaml("table_detection_dataset", "dataset.yaml")

# Train the model
results = train_custom_model("dataset.yaml", epochs=100)
```

## Advanced Usage

### Batch Processing

```python
import os
from table_extractor import TableExtractor

extractor = TableExtractor()

# Process all images in a directory
image_dir = "path/to/images"
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(image_dir, filename)
        tables_data = extractor.extract_all_tables(image_path)
        
        # Save results
        for i, table_data in enumerate(tables_data):
            output_file = f"{filename}_table_{i+1}.csv"
            table_data.to_csv(output_file, index=False)
```

### OCR Comparison

```python
# Compare EasyOCR vs Tesseract
easyocr_tables = extractor.extract_all_tables("image.jpg", use_easyocr=True)
tesseract_tables = extractor.extract_all_tables("image.jpg", use_easyocr=False)

print(f"EasyOCR: {len(easyocr_tables)} tables")
print(f"Tesseract: {len(tesseract_tables)} tables")
```

### Custom Preprocessing

```python
# Extract from specific bounding box
bbox = [100, 200, 500, 400]  # [x1, y1, x2, y2]
table_data = extractor.extract_table_data("image.jpg", bbox, use_easyocr=True)
```

## Configuration Options

### TableExtractor Parameters

- `model_path`: Path to custom YOLO model weights
- `confidence_threshold`: Minimum confidence for detections (default: 0.5)

### OCR Options

- `use_easyocr`: Use EasyOCR (True) or Tesseract (False)
- Confidence filtering for text extraction
- Custom preprocessing for better OCR results

## File Structure

```
PyTableExtraction/
├── table_extractor.py      # Main extraction class
├── example_usage.py        # Usage examples
├── train_custom_model.py   # Model training utilities
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Dependencies

- **ultralytics**: YOLO V8n implementation
- **opencv-python**: Image processing
- **numpy**: Numerical operations
- **pandas**: Data manipulation
- **easyocr**: OCR engine
- **pytesseract**: Tesseract OCR wrapper
- **matplotlib**: Visualization
- **Pillow**: Image handling

## Performance Tips

1. **GPU Acceleration**: Install PyTorch with CUDA support for faster inference
2. **Batch Processing**: Process multiple images together for efficiency
3. **Image Resolution**: Higher resolution images generally give better results
4. **Model Selection**: Use custom models trained on your specific data for better accuracy

## Troubleshooting

### Common Issues

1. **No tables detected**: Lower the confidence threshold or check image quality
2. **Poor OCR results**: Try different preprocessing or switch between EasyOCR/Tesseract
3. **Memory issues**: Reduce batch size or image resolution
4. **Model loading errors**: Ensure model file exists and is compatible

### Getting Help

- Check the example scripts for usage patterns
- Verify all dependencies are installed correctly
- Ensure Tesseract is properly installed if using Tesseract OCR
- Check image format and quality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLO V8n
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for OCR capabilities
- [Tesseract](https://github.com/tesseract-ocr/tesseract) for OCR engine 