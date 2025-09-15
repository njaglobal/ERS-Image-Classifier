from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch, io


# Lazy globals
blip_processor = None
blip_model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def get_blip():
    """Load BLIP only when needed, and cache it"""
    global blip_processor, blip_model
    if blip_processor is None or blip_model is None:
        print("🔄 Loading BLIP captioning model...")
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        ).to(device)
        print("✅ BLIP loaded")
    return blip_processor, blip_model


def generate_caption(image_bytes: bytes) -> str:
    try:
        processor, model = get_blip()
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = processor(pil_img, return_tensors="pt").to(device)
        out = model.generate(**inputs, max_length=50)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption[0].upper() + caption[1:] if caption else "No caption available"
    except Exception as e:
        return f"Captioning failed: {e}"
