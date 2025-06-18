import streamlit as st
from PIL import Image
import hashlib
import io
import random

# ===== Helper Functions =====

def password_to_key(password):
    hash_object = hashlib.sha256(password.encode())
    return int(hash_object.hexdigest(), 16) % 256

def process_image(img, key, method, mode):
    img = img.convert('RGB')
    pixels = img.load()
    width, height = img.size

    if method == "Additive":
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                if mode == 'Encrypt':
                    r, g, b = (r + key) % 256, (g + key) % 256, (b + key) % 256
                else:
                    r, g, b = (r - key) % 256, (g - key) % 256, (b - key) % 256
                pixels[x, y] = (r, g, b)

    elif method == "XOR":
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                r, g, b = r ^ key, g ^ key, b ^ key
                pixels[x, y] = (r, g, b)

    elif method == "Shuffle":
        coords = [(x, y) for x in range(width) for y in range(height)]
        random.seed(key)

        if mode == 'Encrypt':
            shuffled = coords[:]
            random.shuffle(shuffled)
            new_img = Image.new('RGB', img.size)
            for orig, shuf in zip(coords, shuffled):
                new_img.putpixel(shuf, pixels[orig])
            img = new_img

        elif mode == 'Decrypt':
            shuffled = coords[:]
            random.shuffle(shuffled)
            new_img = Image.new('RGB', img.size)
            for orig, shuf in zip(coords, shuffled):
                new_img.putpixel(orig, pixels[shuf])
            img = new_img

    return img


# ===== Streamlit UI =====

st.title("🔐 Image Encryptor / Decryptor")
st.markdown("Secure your images using simple pixel-based transformations with password-to-key conversion.")

uploaded_file = st.file_uploader("📤 Upload an image", type=["png", "jpg", "jpeg"])
password = st.text_input("🔑 Enter your password", type="password")
method = st.selectbox("Select encryption method", ["Additive", "XOR", "Shuffle"])
mode = st.radio("Choose action", ["Encrypt", "Decrypt"])

if uploaded_file and password:
    img = Image.open(uploaded_file)
    st.image(img, caption="Original Image", use_column_width=True)

    key = password_to_key(password)

    if st.button(f"{mode} Image"):
        result_img = process_image(img, key, method, mode)
        st.image(result_img, caption=f"{mode}ed Image", use_column_width=True)

        # Save in-memory for download
        buf = io.BytesIO()
        result_img.save(buf, format='PNG')
        byte_img = buf.getvalue()
        st.download_button(label="💾 Download Result",
                           data=byte_img,
                           file_name=f"{mode.lower()}ed_image.png",
                           mime="image/png")
