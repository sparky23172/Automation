import pyautogui as auto
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import time


def writez(text):
    print(text)
    timer = 3
    count = timer
    while count != 0:
        print("Countdown: {}".format(count))
        time.sleep(1)
        count -= 1
    auto.typewrite(text, interval=0.1)
    print(text, "has been written")


def main():

    resp = auto.confirm("What would you like to paste?\n[*] They are both funtionally the same. Just the multiline is nicer on the eyes", buttons=['Single Line', 'Multi Line',])

    if resp == "Multi Line":
        root = tk.Tk()
        frame_a = tk.Frame()
        entry = tk.Entry(master=frame_a, width=50)

        label_a = tk.Label(master=frame_a, text="Hey! This is the Single lined KeyLogger Program!\n\nPlease insert the text you want to paste below\n\n")
        label_a.pack()

        entry.pack()
  
        root.title("ScrolledText Widget Example")
        
        ttk.Label(root, text="Hey! This is the Single lined KeyLogger Program!\n\nPlease insert the text you want to paste below\n\n",
                font=("Times New Roman", 15)).grid(column=0, row=0)
        ttk.Label(root, text="Text to Paste:", font=("Bold", 12)).grid(column=0, row=1)
        ttk.Label(frame_a, text="Test")
        
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD,
                                            width=40, height=8,
                                            font=("Times New Roman", 15))
        
        sub_btn=tk.Button(root,text = 'Submit', command = lambda: writez(text_area.get("1.0", "end-1c")))
        text_area.grid(column=0, row=2, pady=10, padx=10)
        sub_btn.grid(column=0, row=3, pady=10, padx=10)

        
        # placing cursor in text area
        text_area.focus()
        root.mainloop()

    if resp == "Single Line":
        window = tk.Tk()

        frame_a = tk.Frame()
        entry = tk.Entry(master=frame_a, width=50)

        label_a = tk.Label(master=frame_a, text="Hey! This is the Single lined KeyLogger Program!\n\nPlease insert the text you want to paste below\n\n")
        label_a.pack()

        entry.pack()

        frame_b = tk.Frame()
        button = tk.Button(master=frame_b, text="Paste Text", command=lambda: writez(entry.get()))
        button.pack()

        frame_a.pack()
        frame_b.pack()

        window.mainloop()

        
if __name__ == '__main__':
    main()
