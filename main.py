from PIL import Image
import os
from pillow_heif import register_heif_opener

# Register HEIC/HEIF support
register_heif_opener()

# Canvas settings
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350
VERTICAL_PADDING = 32
HORIZONTAL_PADDING = 114

def resize_and_center_image(input_path, output_path):
    """Resize image to fit canvas with padding and center it."""
    # Open the original image
    img = Image.open(input_path)
    
    # Calculate maximum dimensions with padding
    max_width = CANVAS_WIDTH - (2 * HORIZONTAL_PADDING)
    max_height = CANVAS_HEIGHT - (2 * VERTICAL_PADDING)
    
    # Calculate scaling factor to fit within bounds
    width_ratio = max_width / img.width
    height_ratio = max_height / img.height
    scale_factor = min(width_ratio, height_ratio)
    
    # Calculate new dimensions
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    
    # Resize image
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Create white canvas
    canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), 'white')
    
    # Calculate position to center the image
    x = (CANVAS_WIDTH - new_width) // 2
    y = (CANVAS_HEIGHT - new_height) // 2
    
    # Paste resized image onto canvas
    canvas.paste(img_resized, (x, y))
    
    # Save as JPEG
    canvas.save(output_path, 'JPEG', quality=95)
    print(f"Processed: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")

def process_folder(input_folder, output_folder):
    """Process all images in the input folder."""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Supported image formats
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.heic', '.heif')
    
    # Process each image in the folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_folder, filename)
            
            # Change extension to .jpg for output
            output_filename = os.path.splitext(filename)[0] + '.jpg'
            output_path = os.path.join(output_folder, output_filename)
            
            try:
                resize_and_center_image(input_path, output_path)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    # Set your input and output folder paths here
    input_folder = "test_images"  # Change this to your input folder path
    output_folder = "output_images"  # Change this to your output folder path
    
    process_folder(input_folder, output_folder)