import tensorflow as tf
import os

# Globals
interpreter = None
input_details = None
output_details = None
class_labels = None

MODEL_PATH = "models/final_model_latest.tflite"
LABELS_PATH = "models/labels_full.txt"


def get_model():
    """Load TFLite model + labels lazily, cache for reuse"""
    global interpreter, input_details, output_details, class_labels

    if interpreter is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"❌ Model file not found: {MODEL_PATH}")
        if not os.path.exists(LABELS_PATH):
            raise FileNotFoundError(f"❌ Labels file not found: {LABELS_PATH}")

        # Load labels
        with open(LABELS_PATH, "r") as f:
            class_labels = [line.strip() for line in f.readlines()]

        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        print(f"✅ TFLite model loaded ({MODEL_PATH})")
        print(f"📋 Classes: {class_labels}")

    return interpreter, input_details, output_details, class_labels


def reset_model():
    """Force reload on next prediction (e.g., after sync)."""
    global interpreter, input_details, output_details, class_labels
    interpreter = None
    input_details = None
    output_details = None
    class_labels = None
    print("🔄 Model reset — will reload on next predict")