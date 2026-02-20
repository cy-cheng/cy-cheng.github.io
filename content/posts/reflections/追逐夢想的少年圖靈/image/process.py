import os
from PIL import Image
from pillow_heif import register_heif_opener

# Register the HEIF opener with Pillow
register_heif_opener()

def convert_heic_to_jpg(directory=".", quality=95):
    """
    Converts all HEIC files in the specified directory to JPG.
    """
    # Count for feedback
    converted_count = 0
    
    # List files in the directory
    files = [f for f in os.listdir(directory) if f.lower().endswith(".heic")]
    
    if not files:
        print("No HEIC files found in the directory.")
        return

    print(f"Found {len(files)} files. Starting conversion...")

    for filename in files:
        # Construct full file paths
        input_path = os.path.join(directory, filename)
        output_path = os.path.join(directory, os.path.splitext(filename)[0] + ".jpg")

        try:
            # Open the HEIC image
            image = Image.open(input_path)
            
            # Convert and save as JPG
            # Note: HEIC is often in 'RGBA' or 'P' mode; JPG requires 'RGB'
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            image.save(output_path, "JPEG", quality=quality)
            print(f"Converted: {filename} -> {os.path.basename(output_path)}")
            converted_count += 1
            
        except Exception as e:
            print(f"Failed to convert {filename}: {e}")

    print(f"\nFinished! Successfully converted {converted_count} files.")

if __name__ == "__main__":
    # You can specify a path here, e.g., convert_heic_to_jpg("/path/to/photos")
    convert_heic_to_jpg()
