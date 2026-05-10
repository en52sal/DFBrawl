from PIL import Image
import os

# Folder where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create gray folder if it doesn't exist
gray_dir = os.path.join(script_dir, "gray")
os.makedirs(gray_dir, exist_ok=True)

# Loop through PNG files
for filename in os.listdir(script_dir):
    if filename.lower().endswith(".png"):
        input_path = os.path.join(script_dir, filename)
        output_path = os.path.join(gray_dir, filename)

        # Open image
        img = Image.open(input_path).convert("RGBA")

        # Split channels
        r, g, b, a = img.split()

        # Create grayscale version
        gray = Image.merge("RGB", (r, g, b)).convert("L")

        # Rebuild RGBA with original transparency
        final_img = Image.merge("RGBA", (gray, gray, gray, a))

        # Save
        final_img.save(output_path)

        print(f"Created: {output_path}")

print("Done.")