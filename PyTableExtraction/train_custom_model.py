#!/usr/bin/env python3
"""
Script to train a custom YOLO V8n model for table detection.
"""

import os
import yaml
from ultralytics import YOLO
import shutil
from pathlib import Path

def create_dataset_structure(dataset_path: str):
    """
    Create the required directory structure for YOLO training.
    
    Args:
        dataset_path (str): Path to the dataset directory
    """
    # Create main directories
    os.makedirs(dataset_path, exist_ok=True)
    os.makedirs(os.path.join(dataset_path, "train", "images"), exist_ok=True)
    os.makedirs(os.path.join(dataset_path, "train", "labels"), exist_ok=True)
    os.makedirs(os.path.join(dataset_path, "val", "images"), exist_ok=True)
    os.makedirs(os.path.join(dataset_path, "val", "labels"), exist_ok=True)
    
    print(f"Created dataset structure at {dataset_path}")

def create_dataset_yaml(dataset_path: str, output_path: str = "dataset.yaml"):
    """
    Create the dataset.yaml file required for YOLO training.
    
    Args:
        dataset_path (str): Path to the dataset directory
        output_path (str): Path to save the dataset.yaml file
    """
    dataset_config = {
        'path': os.path.abspath(dataset_path),
        'train': 'train/images',
        'val': 'val/images',
        'nc': 1,  # Number of classes (1 for table)
        'names': ['table']  # Class names
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    print(f"Created dataset configuration at {output_path}")

def train_custom_model(dataset_yaml_path: str, epochs: int = 100, imgsz: int = 640):
    """
    Train a custom YOLO V8n model for table detection.
    
    Args:
        dataset_yaml_path (str): Path to the dataset.yaml file
        epochs (int): Number of training epochs
        imgsz (int): Input image size
    """
    # Load the base YOLO V8n model
    model = YOLO('yolov8n.pt')
    
    # Train the model
    print(f"Starting training with {epochs} epochs...")
    results = model.train(
        data=dataset_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=16,
        name='table_detection_model',
        patience=20,  # Early stopping patience
        save=True,
        device='auto'  # Use available device (CPU/GPU)
    )
    
    print("Training completed!")
    print(f"Best model saved at: {results.save_dir}")
    
    return results

def validate_model(model_path: str, dataset_yaml_path: str):
    """
    Validate the trained model on the validation set.
    
    Args:
        model_path (str): Path to the trained model
        dataset_yaml_path (str): Path to the dataset.yaml file
    """
    # Load the trained model
    model = YOLO(model_path)
    
    # Validate the model
    print("Validating model...")
    results = model.val(data=dataset_yaml_path)
    
    print("Validation completed!")
    print(f"mAP50: {results.box.map50:.4f}")
    print(f"mAP50-95: {results.box.map:.4f}")
    
    return results

def convert_annotations_to_yolo(input_annotations_dir: str, output_labels_dir: str, 
                              image_width: int, image_height: int):
    """
    Convert annotations from various formats to YOLO format.
    
    Args:
        input_annotations_dir (str): Directory containing input annotations
        output_labels_dir (str): Directory to save YOLO format labels
        image_width (int): Width of the images
        image_height (int): Height of the images
    """
    os.makedirs(output_labels_dir, exist_ok=True)
    
    # This is a placeholder function - you'll need to implement the conversion
    # based on your annotation format (COCO, Pascal VOC, etc.)
    
    print("Annotation conversion function - implement based on your format")
    print("YOLO format: <class> <x_center> <y_center> <width> <height>")
    print("All values should be normalized between 0 and 1")

def prepare_dataset_from_images(images_dir: str, annotations_dir: str, 
                               dataset_path: str, train_split: float = 0.8):
    """
    Prepare dataset from images and annotations.
    
    Args:
        images_dir (str): Directory containing images
        annotations_dir (str): Directory containing annotations
        dataset_path (str): Path to create the dataset
        train_split (float): Fraction of data to use for training
    """
    import random
    
    # Create dataset structure
    create_dataset_structure(dataset_path)
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = []
    
    for file in os.listdir(images_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    # Shuffle and split
    random.shuffle(image_files)
    split_idx = int(len(image_files) * train_split)
    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]
    
    # Copy files to train and val directories
    for file in train_files:
        # Copy image
        src_img = os.path.join(images_dir, file)
        dst_img = os.path.join(dataset_path, "train", "images", file)
        shutil.copy2(src_img, dst_img)
        
        # Copy corresponding annotation
        base_name = os.path.splitext(file)[0]
        src_ann = os.path.join(annotations_dir, f"{base_name}.txt")
        dst_ann = os.path.join(dataset_path, "train", "labels", f"{base_name}.txt")
        if os.path.exists(src_ann):
            shutil.copy2(src_ann, dst_ann)
    
    for file in val_files:
        # Copy image
        src_img = os.path.join(images_dir, file)
        dst_img = os.path.join(dataset_path, "val", "images", file)
        shutil.copy2(src_img, dst_img)
        
        # Copy corresponding annotation
        base_name = os.path.splitext(file)[0]
        src_ann = os.path.join(annotations_dir, f"{base_name}.txt")
        dst_ann = os.path.join(dataset_path, "val", "labels", f"{base_name}.txt")
        if os.path.exists(src_ann):
            shutil.copy2(src_ann, dst_ann)
    
    print(f"Dataset prepared: {len(train_files)} training, {len(val_files)} validation images")

def main():
    """
    Main function to train a custom table detection model.
    """
    print("Custom YOLO V8n Table Detection Model Training")
    print("=" * 50)
    
    # Configuration
    dataset_path = "table_detection_dataset"
    dataset_yaml_path = "dataset.yaml"
    epochs = 100
    imgsz = 640
    
    # Step 1: Create dataset structure
    print("Step 1: Creating dataset structure...")
    create_dataset_structure(dataset_path)
    
    # Step 2: Create dataset configuration
    print("Step 2: Creating dataset configuration...")
    create_dataset_yaml(dataset_path, dataset_yaml_path)
    
    # Step 3: Prepare your dataset
    # Uncomment and modify the following lines based on your data format:
    # images_dir = "path/to/your/images"
    # annotations_dir = "path/to/your/annotations"
    # prepare_dataset_from_images(images_dir, annotations_dir, dataset_path)
    
    # Step 4: Train the model
    print("Step 3: Training the model...")
    try:
        results = train_custom_model(dataset_yaml_path, epochs, imgsz)
        
        # Step 5: Validate the model
        print("Step 4: Validating the model...")
        best_model_path = os.path.join(results.save_dir, "weights", "best.pt")
        validate_model(best_model_path, dataset_yaml_path)
        
        print(f"\nTraining completed successfully!")
        print(f"Best model saved at: {best_model_path}")
        print(f"You can now use this model with the TableExtractor class:")
        print(f"extractor = TableExtractor(model_path='{best_model_path}')")
        
    except Exception as e:
        print(f"Training failed: {e}")
        print("Please ensure you have prepared your dataset correctly.")

def example_annotation_format():
    """
    Example showing the required annotation format for YOLO training.
    """
    print("YOLO Annotation Format Example:")
    print("=" * 30)
    print("Each image should have a corresponding .txt file with the same name.")
    print("Format: <class_id> <x_center> <y_center> <width> <height>")
    print("All values should be normalized between 0 and 1.")
    print()
    print("Example annotation file (image1.txt):")
    print("0 0.5 0.3 0.8 0.6")
    print("0 0.2 0.7 0.4 0.3")
    print()
    print("Where:")
    print("- 0 = class ID for 'table'")
    print("- 0.5 = x_center (center x-coordinate of bounding box)")
    print("- 0.3 = y_center (center y-coordinate of bounding box)")
    print("- 0.8 = width (width of bounding box)")
    print("- 0.6 = height (height of bounding box)")
    print()
    print("You can use tools like LabelImg or CVAT to create these annotations.")

if __name__ == "__main__":
    main()
    
    # Uncomment to see annotation format example
    # example_annotation_format() 