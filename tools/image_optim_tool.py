from PIL import Image

def optimize_image(image_path: str, size=(224, 224)) -> Image.Image:
    '''
    Resize image for CLIP model input while maintaining aspect ratio.
    Converts to RGB and applies high-quality antialiasing.
    '''
    try:
        image = Image.open(image_path).convert("RGB")
        optimized_image = image.copy()
        optimized_image.thumbnail(size, Image.LANCZOS)
        return optimized_image
    except Exception as e:
        raise RuntimeError(f"Failed to process image '{image_path}': {e}")
