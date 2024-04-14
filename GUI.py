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
    filename = filedialog.askopenfilename(title="Select Image")
    if filename:
        image = cv2.imread(filename)
        secret_data = entry.get()
        if not secret_data:
            output_text.set("Data is Empty")
            return
        try:
            number_of_bytes = (image.shape[0] * image.shape[1] * 3) // 8
            if number_of_bytes < len(secret_data):
                output_text.set("Not enough space")
                return

            secret_data += '~!~!~'
            binary_data = convert_to_binary(secret_data)

            position = 0
            for i in image:
                for pixel in i:
                    r, g, b = convert_to_binary(pixel)
                    if position < len(binary_data):
                        pixel[0] = int(r[:-1] + binary_data[position], 2)
                        position += 1
                    if position < len(binary_data):
                        pixel[1] = int(g[:-1] + binary_data[position], 2)
                        position += 1
                    if position < len(binary_data):
                        pixel[2] = int(b[:-1] + binary_data[position], 2)
                        position += 1
                    if position >= len(binary_data):
                        break
            new_filename = filedialog.asksaveasfilename(title="Save Image As")
            if new_filename:
                cv2.imwrite(new_filename, image)
                output_text.set("Data encoded successfully")
        except Exception as e:
            output_text.set(str(e))
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
    filename = filedialog.askopenfilename(title="Select Image")
    if filename:
        image = cv2.imread(filename)
        data_binary = ""
        for i in image:
            for pixel in i:
                r, g, b = convert_to_binary(pixel)
                data_binary += r[-1]
                data_binary += g[-1]
                data_binary += b[-1]
                total_bytes = [data_binary[i: i + 8] for i in range(0, len(data_binary), 8)]
                decoded_data = ""
                for byte in total_bytes:
                    decoded_data += chr(int(byte, 2))
                    if decoded_data[-5:] == "~!~!~":
                        output_text.set("The data hidden in the image is: " + decoded_data[:-5])
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
    encode_tab3 = tk.Toplevel(root)
    encode_tab3.title("Encode Text into Audio")
    encode_tab3.geometry("400x200")

    text_label = tk.Label(encode_tab3, text="Enter the secret message:")
    text_label.pack()

    text_entry = tk.Text(encode_tab3, height=4, width=40)
    text_entry.pack()

    encode_button = tk.Button(encode_tab3, text="Encode", command=encode)
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
    decode_tab3 = tk.Toplevel(root)
    decode_tab3.title("Decode Text from Audio")
    decode_tab3.geometry("400x200")

    decode_button = tk.Button(decode_tab3, text="Select Audio File", command=decode)
    decode_button.pack(pady=10)

    decoded_message_label = tk.Label(decode_tab3, text="")
    decoded_message_label.pack()


def embed(frame, secret_message):
    if len(secret_message) == 0: 
        raise ValueError('Secret message is empty')

    secret_message += '~!~!~'
    binary_data = convert_to_binary(secret_message)
    length_data = len(binary_data)
    index_data = 0
    for i in frame:
        for pixel in i:
            r, g, b = convert_to_binary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
    return frame
    

def video_encode():
    file_path = file_path_var.get()
    if file_path == "":
        tk.messagebox.showerror("Error", "Please select a video file.")
        return

    output_path = output_path_var.get()
    if output_path == "":
        tk.messagebox.showerror("Error", "Please select an output path.")
        return

    secret_message = secret_message_var.get()
    frame_number = frame_number_var.get()
    if not frame_number.isdigit() or int(frame_number) <= 0:
        tk.messagebox.showerror("Error", "Invalid frame number.")
        return

    try:
        cap = cv2.VideoCapture(file_path)
        vidcap = cv2.VideoCapture(file_path)
    except:
        tk.messagebox.showerror("Error", "Failed to open video file.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))
    size = (frame_width, frame_height)
    out = cv2.VideoWriter(output_path, fourcc, 25.0, size)
    max_frame = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame += 1
    cap.release()
    print("Total number of Frames in the selected Video:", max_frame)
    frame_number = int(frame_number)
    if frame_number > max_frame:
        tk.messagebox.showerror("Error", "Invalid frame number.")
        return

    frame_count = 0
    while vidcap.isOpened():
        frame_count += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_count == frame_number:
            frame_ = embed(frame, secret_message)
            out.write(frame_)
        else:
            out.write(frame)
    out.release()
    print("\nData encoded successfully.")
    tk.messagebox.showinfo("Success", "Data encoded successfully.")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
    file_path_var.set(file_path)

def browse_output_path():
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Video files", "*.mp4")])
    output_path_var.set(output_path)

# Main Tkinter tab3
root = tk.Tk()
root.title("Steganography")
root.geometry("600x600")

tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Image Steganography')
tab_control.add(tab2, text='Audio Steganography')
tab_control.add(tab3, text='Video Steganography')
tab_control.pack(expand=1, fill='both')

image_encode_frame = ttk.Frame(tab1)
image_decode_frame = ttk.Frame(tab1)
image_encode_frame.pack(fill='both', padx=10, pady=10)
image_decode_frame.pack(fill='both', padx=10, pady=10)
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

entry_label = tk.Label(image_encode_frame, text="Enter Message:")
entry_label.pack(padx=10, pady=5)
entry = tk.Entry(image_encode_frame)
entry.pack(padx=10, pady=5)
encode_button = tk.Button(image_encode_frame, text="Encode Message", command=image_encode)
encode_button.pack(padx=10, pady=5)


decoded_message_label = ttk.Label(image_decode_frame, text="")
decoded_message_label.pack(padx=10, pady=5)
decode_button = tk.Button(image_decode_frame, text="Decode Message", command=image_decode)
decode_button.pack(padx=10, pady=5)

output_text = tk.StringVar()
output_label = tk.Label(image_decode_frame, textvariable=output_text)
output_label.pack(pady=10)


audio_encode_frame = ttk.Frame(tab2)
audio_encode_frame.pack(fill='both', padx=10, pady=10)
encode_button_audio = tk.Button(audio_encode_frame, text="Encode Text into Audio", command=audio_encode)
encode_button_audio.pack(padx=10, pady=5)
decode_button_audio = tk.Button(audio_encode_frame, text="Decode Text from Audio", command=audio_decode)
decode_button_audio.pack(padx=10, pady=5)


file_path_var = tk.StringVar()
frame_number_var = tk.StringVar()
secret_message_var = tk.StringVar()
output_path_var = tk.StringVar()

video_label = tk.Label(tab3, text="Select Video File:")
video_label.grid(row=0, column=0, padx=10, pady=10)

video_entry = tk.Entry(tab3, textvariable=file_path_var, width=40)
video_entry.grid(row=0, column=1, padx=10, pady=10)

browse_button = tk.Button(tab3, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=10)

frame_label = tk.Label(tab3, text="Enter Frame Number:")
frame_label.grid(row=1, column=0, padx=10, pady=10)

frame_entry = tk.Entry(tab3, textvariable=frame_number_var, width=10)
frame_entry.grid(row=1, column=1, padx=10, pady=10)

message_label = tk.Label(tab3, text="Enter Secret Message:")
message_label.grid(row=2, column=0, padx=10, pady=10)

message_entry = tk.Entry(tab3, textvariable=secret_message_var, width=40)
message_entry.grid(row=2, column=1, padx=10, pady=10)

output_label = tk.Label(tab3, text="Select Output Path:")
output_label.grid(row=3, column=0, padx=10, pady=10)

output_entry = tk.Entry(tab3, textvariable=output_path_var, width=40)
output_entry.grid(row=3, column=1, padx=10, pady=10)

output_button = tk.Button(tab3, text="Save As", command=browse_output_path)
output_button.grid(row=3, column=2, padx=10, pady=10)

encode_button = tk.Button(tab3, text="Encode", command=video_encode)
encode_button.grid(row=4, column=1, padx=10, pady=10)




root.mainloop()
