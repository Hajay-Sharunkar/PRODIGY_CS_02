import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import random
import os

class ImageEncryptor:
    def __init__(self, key):
        self.key = key

    def encrypt(self, img, method):
        return self._process_image(img, method, mode='encrypt')

    def decrypt(self, img, method):
        return self._process_image(img, method, mode='decrypt')

    def _process_image(self, img, method, mode):
        img = img.convert('RGB')
        pixels = img.load()
        width, height = img.size

        if method == "Additive":
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    k = self.key
                    if mode == 'encrypt':
                        r, g, b = (r + k) % 256, (g + k) % 256, (b + k) % 256
                    else:
                        r, g, b = (r - k) % 256, (g - k) % 256, (b - k) % 256
                    pixels[x, y] = (r, g, b)

        elif method == "XOR":
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    k = self.key
                    r, g, b = r ^ k, g ^ k, b ^ k
                    pixels[x, y] = (r, g, b)

        elif method == "Shuffle":
            coords = [(x, y) for x in range(width) for y in range(height)]
            random.seed(self.key)

            if mode == 'encrypt':
                shuffled = coords[:]
                random.shuffle(shuffled)
                new_img = Image.new('RGB', img.size)
                for orig, shuffled_coord in zip(coords, shuffled):
                    new_img.putpixel(shuffled_coord, pixels[orig])
                img = new_img

            elif mode == 'decrypt':
                shuffled = coords[:]
                random.shuffle(shuffled)
                new_img = Image.new('RGB', img.size)
                for orig, shuffled_coord in zip(coords, shuffled):
                    new_img.putpixel(orig, pixels[shuffled_coord])
                img = new_img

        return img


def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        try:
            img = Image.open(file_path)
            key = int(key_entry.get())
            method = method_var.get()
            encryptor = ImageEncryptor(key)

            if operation_var.get() == "Encrypt":
                new_img = encryptor.encrypt(img, method)
                save_image(new_img, f"encrypted_{method.lower()}_" + os.path.basename(file_path))
            else:
                new_img = encryptor.decrypt(img, method)
                save_image(new_img, f"decrypted_{method.lower()}_" + os.path.basename(file_path))

        except Exception as e:
            messagebox.showerror("Error", f"Could not process image:\n{e}")


def save_image(img, name):
    save_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=name,
                                             filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
    if save_path:
        img.save(save_path)
        messagebox.showinfo("Success", f"Image saved to:\n{save_path}")


# === GUI ===
app = tk.Tk()
app.title("🔐 Advanced Image Encryptor")
app.geometry("420x300")
app.resizable(False, False)

tk.Label(app, text="Enter encryption key (integer):").pack(pady=5)
key_entry = tk.Entry(app)
key_entry.pack(pady=5)

operation_var = tk.StringVar(value="Encrypt")
tk.Radiobutton(app, text="Encrypt", variable=operation_var, value="Encrypt").pack()
tk.Radiobutton(app, text="Decrypt", variable=operation_var, value="Decrypt").pack()

tk.Label(app, text="Select Encryption Method:").pack(pady=5)
method_var = tk.StringVar(value="Additive")
methods = ["Additive", "XOR", "Shuffle"]
tk.OptionMenu(app, method_var, *methods).pack()

tk.Button(app, text="Choose Image & Run", command=open_image, bg="#4CAF50", fg="white").pack(pady=20)

app.mainloop()
