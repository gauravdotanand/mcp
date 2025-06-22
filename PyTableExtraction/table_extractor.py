import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import easyocr
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import os
from typing import List, Dict, Tuple, Optional
import logging
from sklearn.cluster import AgglomerativeClustering

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableExtractor:
    """
    A class to extract table data from images using YOLO V8n custom model.
    """
    
    def __init__(self, model_path: str = None, confidence_threshold: float = 0.5):
        """
        Initialize the TableExtractor.
        
        Args:
            model_path (str): Path to the custom YOLO V8n model weights (.pt file)
            confidence_threshold (float): Confidence threshold for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.reader = None
        
        # Initialize YOLO model
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
            logger.info(f"Loaded custom YOLO model from {model_path}")
        else:
            # Load default YOLO V8n model
            self.model = YOLO('yolov8n.pt')
            logger.info("Loaded default YOLO V8n model")
        
        # Initialize EasyOCR for text extraction
        try:
            self.reader = easyocr.Reader(['en'])
            logger.info("Initialized EasyOCR reader")
        except Exception as e:
            logger.warning(f"Could not initialize EasyOCR: {e}")
            self.reader = None
    
    def detect_tables(self, image_path: str) -> List[Dict]:
        """
        Detect tables in the image using multiple approaches.
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            List[Dict]: List of detected table bounding boxes with confidence scores
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            detections = []
            
            # Method 1: Try YOLO detection first
            yolo_detections = self._detect_with_yolo(image)
            if yolo_detections:
                detections.extend(yolo_detections)
                logger.info(f"YOLO detected {len(yolo_detections)} tables")
            
            # Method 2: If no YOLO detections, use contour-based detection
            if not detections:
                contour_detections = self._detect_with_contours(image)
                if contour_detections:
                    detections.extend(contour_detections)
                    logger.info(f"Contour detection found {len(contour_detections)} potential tables")
            
            # Method 3: If still no detections, use the entire image as a table
            if not detections:
                full_image_detection = self._detect_full_image_as_table(image)
                if full_image_detection:
                    detections.append(full_image_detection)
                    logger.info("Using entire image as table region")
            
            logger.info(f"Total detected regions: {len(detections)}")
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting tables: {e}")
            return []
    
    def _detect_with_yolo(self, image: np.ndarray) -> List[Dict]:
        """
        Detect tables using YOLO model.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List[Dict]: YOLO detections
        """
        try:
            # Run YOLO detection with lower confidence threshold for testing
            results = self.model(image, conf=0.1)  # Lower threshold to catch more objects
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]
                        
                        # Accept any detection with reasonable confidence
                        if confidence > 0.1:  # Very low threshold for testing
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(confidence),
                                'class_id': class_id,
                                'class_name': class_name,
                                'method': 'yolo'
                            })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
            return []
    
    def _detect_with_contours(self, image: np.ndarray) -> List[Dict]:
        """
        Detect table-like regions using contour analysis.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List[Dict]: Contour-based detections
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            min_area = 1000  # Minimum area to consider as table
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate aspect ratio
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Filter based on reasonable table-like proportions
                    if 0.5 < aspect_ratio < 3.0 and w > 100 and h > 50:
                        detections.append({
                            'bbox': [x, y, x + w, y + h],
                            'confidence': 0.5,  # Default confidence for contour detection
                            'class_id': -1,
                            'class_name': 'table_contour',
                            'method': 'contour'
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in contour detection: {e}")
            return []
    
    def _detect_full_image_as_table(self, image: np.ndarray) -> Dict:
        """
        Use the entire image as a table region when no other detection works.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            Dict: Full image detection
        """
        height, width = image.shape[:2]
        return {
            'bbox': [0, 0, width, height],
            'confidence': 0.3,  # Low confidence since it's a fallback
            'class_id': -1,
            'class_name': 'full_image',
            'method': 'fallback'
        }
    
    def extract_table_data(self, image_path: str, bbox: List[int], 
                          use_easyocr: bool = True) -> pd.DataFrame:
        """
        Extract table data from a specific bounding box region.
        
        Args:
            image_path (str): Path to the input image
            bbox (List[int]): Bounding box coordinates [x1, y1, x2, y2]
            use_easyocr (bool): Whether to use EasyOCR (True) or Tesseract (False)
            
        Returns:
            pd.DataFrame: Extracted table data
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Crop the table region
            x1, y1, x2, y2 = bbox
            table_region = image[y1:y2, x1:x2]
            
            # Preprocess the table region
            processed_image = self._preprocess_table_image(table_region)
            
            # Extract text using OCR
            if use_easyocr and self.reader:
                table_data = self._extract_with_easyocr(processed_image)
            else:
                table_data = self._extract_with_tesseract(processed_image)
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return pd.DataFrame()
    
    def _preprocess_table_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the table image for better OCR results.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Preprocessed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Try multiple preprocessing approaches
            processed_images = []
            
            # Approach 1: Adaptive thresholding
            thresh1 = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            processed_images.append(thresh1)
            
            # Approach 2: Otsu thresholding
            _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(thresh2)
            
            # Approach 3: Simple thresholding
            _, thresh3 = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            processed_images.append(thresh3)
            
            # Approach 4: Inverted image (sometimes helps with light text on dark background)
            thresh4 = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
            )
            processed_images.append(thresh4)
            
            # Return the first approach for now, but we could try all of them
            result = processed_images[0]
            
            # Apply morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
            
            # Save the preprocessed image for debugging
            cv2.imwrite("debug_preprocessed.jpg", result)
            logger.info(f"Saved preprocessed image for debugging")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            # Return original grayscale if preprocessing fails
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _extract_with_easyocr(self, image: np.ndarray) -> pd.DataFrame:
        """
        Extract text using EasyOCR.
        
        Args:
            image (np.ndarray): Preprocessed image
            
        Returns:
            pd.DataFrame: Extracted table data
        """
        try:
            logger.info(f"Starting EasyOCR extraction on image of shape {image.shape}")
            
            # Run EasyOCR
            results = self.reader.readtext(image)
            logger.info(f"EasyOCR found {len(results)} text regions")
            
            # Extract text and positions
            text_data = []
            for i, (bbox, text, confidence) in enumerate(results):
                logger.info(f"Text {i+1}: '{text}' (confidence: {confidence:.2f})")
                if confidence > 0.1:  # Very low confidence threshold for testing
                    # Calculate center point of the text
                    center_x = (bbox[0][0] + bbox[2][0]) / 2
                    center_y = (bbox[0][1] + bbox[2][1]) / 2
                    
                    text_data.append({
                        'text': text.strip(),
                        'x': center_x,
                        'y': center_y,
                        'confidence': confidence
                    })
            
            logger.info(f"Filtered to {len(text_data)} text items with confidence > 0.1")
            
            # Convert to DataFrame and organize into table structure
            if text_data:
                df = pd.DataFrame(text_data)
                logger.info(f"Created DataFrame with {len(df)} rows")
                return self._organize_into_table(df)
            else:
                logger.warning("No text data found with sufficient confidence")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error with EasyOCR extraction: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _extract_with_tesseract(self, image: np.ndarray) -> pd.DataFrame:
        """
        Extract text using Tesseract OCR.
        
        Args:
            image (np.ndarray): Preprocessed image
            
        Returns:
            pd.DataFrame: Extracted table data
        """
        try:
            logger.info(f"Starting Tesseract extraction on image of shape {image.shape}")
            
            # Configure Tesseract for table extraction
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()-/$% '
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            logger.info(f"Tesseract raw text: {text[:200]}...")
            
            # Extract data with bounding boxes
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Process the extracted data
            text_data = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 5:  # Very low confidence threshold
                    text_item = data['text'][i].strip()
                    if text_item:
                        logger.info(f"Tesseract text {i+1}: '{text_item}' (confidence: {data['conf'][i]})")
                        text_data.append({
                            'text': text_item,
                            'x': data['left'][i] + data['width'][i] // 2,
                            'y': data['top'][i] + data['height'][i] // 2,
                            'confidence': int(data['conf'][i]) / 100
                        })
            
            logger.info(f"Tesseract found {len(text_data)} text items")
            
            # Convert to DataFrame and organize into table structure
            if text_data:
                df = pd.DataFrame(text_data)
                logger.info(f"Created DataFrame with {len(df)} rows")
                return self._organize_into_table(df)
            else:
                logger.warning("No text data found with Tesseract")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error with Tesseract extraction: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _organize_into_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Organize extracted text data into a proper table structure using clustering for rows and columns.
        
        Args:
            df (pd.DataFrame): DataFrame with text and position data
            
        Returns:
            pd.DataFrame: Organized table data
        """
        try:
            if df.empty:
                return df
            
            # Sort by y-coordinate (rows) then x-coordinate (columns)
            df_sorted = df.sort_values(['y', 'x']).reset_index(drop=True)
            
            # --- Row Clustering ---
            y_coords = df_sorted['y'].values.reshape(-1, 1)
            # Estimate number of rows by finding large gaps in y
            y_diffs = np.diff(np.sort(df_sorted['y'].values))
            y_gap_threshold = max(20, np.percentile(y_diffs, 80))
            row_labels = [0]
            for diff in y_diffs:
                if diff > y_gap_threshold:
                    row_labels.append(row_labels[-1] + 1)
                else:
                    row_labels.append(row_labels[-1])
            df_sorted['row_group'] = row_labels
            n_rows = df_sorted['row_group'].nunique()
            
            # --- Column Clustering ---
            x_coords = df_sorted['x'].values.reshape(-1, 1)
            x_diffs = np.diff(np.sort(df_sorted['x'].values))
            x_gap_threshold = max(30, np.percentile(x_diffs, 80))
            col_labels = [0]
            for diff in x_diffs:
                if diff > x_gap_threshold:
                    col_labels.append(col_labels[-1] + 1)
                else:
                    col_labels.append(col_labels[-1])
            # Assign col_group by sorting within each row
            df_sorted = df_sorted.sort_values(['row_group', 'x']).reset_index(drop=True)
            col_group = []
            for _, group in df_sorted.groupby('row_group'):
                x_vals = group['x'].values
                x_diffs = np.diff(np.sort(x_vals))
                col_labels = [0]
                for diff in x_diffs:
                    if diff > x_gap_threshold:
                        col_labels.append(col_labels[-1] + 1)
                    else:
                        col_labels.append(col_labels[-1])
                col_group.extend(col_labels)
            df_sorted['col_group'] = col_group
            n_cols = max(col_group) + 1 if col_group else 1
            
            # --- Build Table ---
            table = [['' for _ in range(n_cols)] for _ in range(n_rows)]
            for _, row in df_sorted.iterrows():
                r = int(row['row_group'])
                c = int(row['col_group'])
                if table[r][c]:
                    table[r][c] += ' ' + row['text']
                else:
                    table[r][c] = row['text']
            
            # Convert to DataFrame
            table_df = pd.DataFrame(table)
            # Use first row as header if it looks like a header
            if n_rows > 1 and all(len(str(x)) > 0 for x in table[0]):
                table_df.columns = [str(x) for x in table[0]]
                table_df = table_df.drop(index=0).reset_index(drop=True)
            else:
                table_df.columns = [f'Column_{i+1}' for i in range(n_cols)]
            
            return table_df
        except Exception as e:
            logger.error(f"Error organizing table data: {e}")
            import traceback
            traceback.print_exc()
            return df
    
    def visualize_detections(self, image_path: str, detections: List[Dict], 
                           save_path: Optional[str] = None) -> None:
        """
        Visualize the detected tables on the image.
        
        Args:
            image_path (str): Path to the input image
            detections (List[Dict]): List of detected table bounding boxes
            save_path (Optional[str]): Path to save the visualization
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Draw bounding boxes
            for i, detection in enumerate(detections):
                bbox = detection['bbox']
                confidence = detection['confidence']
                method = detection.get('method', 'unknown')
                
                # Choose color based on detection method
                if method == 'yolo':
                    color = (0, 255, 0)  # Green for YOLO
                elif method == 'contour':
                    color = (255, 0, 0)  # Blue for contour
                else:
                    color = (0, 0, 255)  # Red for fallback
                
                # Draw rectangle
                cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                
                # Add label
                label = f"{method.upper()} {i+1}: {confidence:.2f}"
                cv2.putText(image, label, (bbox[0], bbox[1] - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Display or save the image
            if save_path:
                cv2.imwrite(save_path, image)
                logger.info(f"Visualization saved to {save_path}")
            else:
                # Convert BGR to RGB for matplotlib
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                plt.figure(figsize=(12, 8))
                plt.imshow(image_rgb)
                plt.title("Table Detections")
                plt.axis('off')
                plt.show()
                
        except Exception as e:
            logger.error(f"Error visualizing detections: {e}")
    
    def extract_all_tables(self, image_path: str, use_easyocr: bool = True) -> List[pd.DataFrame]:
        """
        Extract all tables from an image.
        
        Args:
            image_path (str): Path to the input image
            use_easyocr (bool): Whether to use EasyOCR (True) or Tesseract (False)
            
        Returns:
            List[pd.DataFrame]: List of extracted table data
        """
        # Detect tables
        detections = self.detect_tables(image_path)
        
        if not detections:
            logger.warning("No tables detected in the image")
            return []
        
        # Extract data from each detected table
        tables_data = []
        for i, detection in enumerate(detections):
            logger.info(f"Extracting data from region {i+1} (method: {detection.get('method', 'unknown')})")
            table_data = self.extract_table_data(image_path, detection['bbox'], use_easyocr)
            if not table_data.empty:
                tables_data.append(table_data)
                logger.info(f"Successfully extracted region {i+1} with {len(table_data)} rows")
            else:
                logger.warning(f"Failed to extract data from region {i+1}")
        
        return tables_data

    def extract_all_tables_json(self, image_path: str, use_easyocr: bool = True):
        """
        Extract all tables from an image and return them in JSON format with headers and rows.
        Args:
            image_path (str): Path to the input image
            use_easyocr (bool): Whether to use EasyOCR (True) or Tesseract (False)
        Returns:
            List[Dict]: List of tables, each as {'header': [...], 'rows': [[...], ...]}
        """
        tables = self.extract_all_tables(image_path, use_easyocr=use_easyocr)
        tables_json = []
        for table in tables:
            if table.empty:
                continue
            header = list(table.columns)
            rows = table.values.tolist()
            tables_json.append({'header': header, 'rows': rows})
        return tables_json 