import wave
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

def convert_to_binary(message):
    if type(message) == str:
        result = ''.join([format(ord(i), "08b") for i in message])
    elif type(message) == bytes or type(message) == np.ndarray:
        result = [format(i, "08b") for i in message]
    elif type(message) == int or type(message) == np.uint8:
        result = format(message, "08b")
    else:
        raise TypeError("Input type is not supported")
    return result

def image_encode():
    global image
    if 'image' not in globals():
        messagebox.showerror("Error", "Please select an image first")
        return
    secret_data = entry.get().strip()
    new_file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])   
    if not new_file:
        return
    number_of_bytes = (image.shape[0] * image.shape[1] * 3) // 8
    print("\nThe number of bytes that can be encoded in the image:", number_of_bytes)
    if number_of_bytes < len(secret_data):
        messagebox.showerror("Error", "Not enough space")
        return
    secret_data += '~!~!~'
    binary_data = convert_to_binary(secret_data)
    print("\n", binary_data)
    data_length = len(binary_data)
    position = 0
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            r, g, b = convert_to_binary(image[i, j])
            if position < data_length:
                image[i, j] = int(r[:-1] + binary_data[position], 2), int(g[:-1] + binary_data[position], 2), int(b[:-1] + binary_data[position], 2)
                position += 1
            if position >= data_length:
                break
        if position >= data_length:
            break
    image = image.astype(np.uint8)
    try:
        cv2.imwrite(new_file, image)
        messagebox.showinfo("Success", "Data encoded and saved successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save the image: {str(e)}")
def open_image():
    global image
    filename = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
    if filename:
        img = Image.open(filename)
        img.thumbnail((300, 300))  
        img = ImageTk.PhotoImage(img)
        panel.config(image=img)
        panel.image = img
        image = cv2.imread(filename)



def image_decode():
    global image1
    if 'image1' not in globals():
        messagebox.showerror("Error", "Please select an image first")
        return
    data_binary = ""
    for i in range(image1.shape[0]):
        for j in range(image1.shape[1]):
            r, g, b = convert_to_binary(image1[i, j])
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]
    total_bytes = [data_binary[i: i + 8] for i in range(0, len(data_binary), 8)]
    decoded_data = ""
    for byte in total_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "~!~!~":
            print("Decoded Message:", decoded_data[:-5])
            decoded_message_label.config(text="Decoded Message: " + decoded_data[:-5])
            messagebox.showinfo("Decoded Message", "The hidden message in the image is: " + decoded_data[:-5])
            return
def open_image_decode():
    global image1
    filename = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
    if filename:
        img1 = Image.open(filename)
        img1.thumbnail((300, 300))  
        img1 = ImageTk.PhotoImage(img1)
        panel.config(image=img1)
        panel.image1 = img1
        image1 = cv2.imread(filename)


def audio_encode():
    def encode():
        newfile = filedialog.askopenfilename(filetypes=[("Wave files", "*.wav")])
        song = wave.open(newfile, mode='rb')
        nframes = song.getnframes()
        frames = song.readframes(nframes)
        frame_list = list(frames)
        frame_bytes = bytearray(frame_list)

        data = text_entry.get("1.0", "end-1c")
        res = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))
        length = len(res)
        data = data + '~!~!~'

        result = []
        for c in data:
            bits = bin(ord(c))[2:].zfill(8)
            result.extend([int(b) for b in bits])

        j = 0
        for i in range(0, len(result), 1):
            res = bin(frame_bytes[j])[2:].zfill(8)
            if res[len(res) - 4] == str(result[i]):
                frame_bytes[j] = (frame_bytes[j] & 253)  # 253: 11111101
            else:
                frame_bytes[j] = (frame_bytes[j] & 253) | 2
                frame_bytes[j] = (frame_bytes[j] & 254) | result[i]
            j = j + 1

        frame_modified = bytes(frame_bytes)
        stegofile = filedialog.asksaveasfilename(defaultextension=".wav")
        with wave.open(stegofile, 'wb') as fd:
            fd.setparams(song.getparams())
            fd.writeframes(frame_modified)
        song.close()
        text_entry.delete("1.0", "end")
        text_entry.insert("1.0", "Data Encoded Successfully")

    # GUI setup
    encode_window = tk.Toplevel(root)
    encode_window.title("Encode Text into Audio")
    encode_window.geometry("400x200")

    text_label = tk.Label(encode_window, text="Enter the secret message:")
    text_label.pack()

    text_entry = tk.Text(encode_window, height=4, width=40)
    text_entry.pack()

    encode_button = tk.Button(encode_window, text="Encode", command=encode)
    encode_button.pack()

def audio_decode():
    def decode():
        newfile = filedialog.askopenfilename(filetypes=[("Wave files", "*.wav")])
        song = wave.open(newfile, mode='rb')

        nframes = song.getnframes()
        frames = song.readframes(nframes)
        frame_list = list(frames)
        frame_bytes = bytearray(frame_list)

        extracted = ""
        p = 0
        for i in range(len(frame_bytes)):
            if p == 1:
                break
            res = bin(frame_bytes[i])[2:].zfill(8)
            if res[len(res) - 2] == '0':
                extracted += res[len(res) - 4]
            else:
                extracted += res[len(res) - 1]

            all_bytes = [extracted[i: i + 8] for i in range(0, len(extracted), 8)]
            decoded_data = ""
            for byte in all_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "~!~!~":
                    decoded_message_label.config(text="Decoded Message: " + decoded_data[:-5])
                    p = 1
                    break
        song.close()

    # GUI setup
    decode_window = tk.Toplevel(root)
    decode_window.title("Decode Text from Audio")
    decode_window.geometry("400x200")

    decode_button = tk.Button(decode_window, text="Select Audio File", command=decode)
    decode_button.pack(pady=10)

    decoded_message_label = tk.Label(decode_window, text="")
    decoded_message_label.pack()

# Main Tkinter window
root = tk.Tk()
root.title("Steganography")
root.geometry("500x400")

tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Image Steganography')
tab_control.add(tab2, text='Audio Steganography')
tab_control.pack(expand=1, fill='both')

image_encode_frame = ttk.Frame(tab1)
image_decode_frame = ttk.Frame(tab1)
image_encode_frame.pack(fill='both', padx=10, pady=10)
image_decode_frame.pack(fill='both', padx=10, pady=10)
panel = tk.Label(root)
panel.pack(padx=10, pady=10)
upload_button = tk.Button(image_encode_frame, text="Upload Image", command=open_image)
upload_button.pack(padx=10, pady=5)
entry_label = tk.Label(image_encode_frame, text="Enter Message:")
entry_label.pack(padx=10, pady=5)
entry = tk.Entry(image_encode_frame)
entry.pack(padx=10, pady=5)
encode_button = tk.Button(image_encode_frame, text="Encode Message", command=image_encode)
encode_button.pack(padx=10, pady=5)
select_image_button = tk.Button(image_decode_frame, text="Select Image for Decoding", command=open_image_decode)
select_image_button.pack(padx=10, pady=5)
decoded_message_label = ttk.Label(image_decode_frame, text="")
decoded_message_label.pack(padx=10, pady=5)
decode_button = tk.Button(image_decode_frame, text="Decode Message", command=image_decode)
decode_button.pack(padx=10, pady=5)

# Audio Steganography GUI
audio_encode_frame = ttk.Frame(tab2)
audio_encode_frame.pack(fill='both', padx=10, pady=10)


# Audio Steganography button
encode_button_audio = tk.Button(audio_encode_frame, text="Encode Text into Audio", command=audio_encode)
encode_button_audio.pack(padx=10, pady=5)

decode_button_audio = tk.Button(audio_encode_frame, text="Decode Text from Audio", command=audio_decode)
decode_button_audio.pack(padx=10, pady=5)

root.mainloop()
