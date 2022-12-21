import pyautogui as auto
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import time


TITLE = "KeyInsert"
COUNTER = "Click Submit to start countdown"

def writez(text, main, targetFrame):
    print(text)
    timer = 3
    count = timer
    while count != 0:
        targetFrame.set("Countdown: {}".format(count))            
        print("Countdown: {}".format(count))
        main.update()
        time.sleep(1)
        count -= 1

    auto.typewrite(text, interval=0.1)
    print(text, "has been written")
    targetFrame.set("Text has been written!\nPlease click Submit to start again")


def main():

    resp = auto.confirm("What would you like to paste?\n[*] They are both funtionally the same. Just the multiline is nicer on the eyes", buttons=['Single Line', 'Multi Line',], title=TITLE)
    if resp == "Multi Line":
        root = tk.Tk()
        root.title(TITLE)
        testing = tk.StringVar()
        testing.set(COUNTER)

        frame_a = tk.Frame()
        entry = tk.Entry(master=frame_a, width=50)

        label_a = tk.Label(master=frame_a, text="Hey! This is the Multi lined KeyLogger Program!\n\nPlease insert the text you want to paste below\n\n")
        label_a.pack()

        entry.pack()
        
        ttk.Label(root, text="Hey! This is the Single lined KeyLogger Program!\n\nPlease insert the text you want to paste below\n\n",
                font=("Times New Roman", 15)).grid(column=0, row=0)
        ttk.Label(root, textvariable=testing, font=("Bold", 12)).grid(column=0, row=1)
        ttk.Label(root, text="Text to Paste:", font=("Bold", 12)).grid(column=0, row=2)
        ttk.Label(frame_a, text="Test")
        
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD,
                                            width=40, height=8,
                                            font=("Times New Roman", 15))
        
        sub_btn=tk.Button(root,text = 'Submit', command = lambda: writez(text_area.get("1.0", "end-1c"), root, testing))
        text_area.grid(column=0, row=2, pady=10, padx=10)
        sub_btn.grid(column=0, row=3, pady=10, padx=10)

        # placing cursor in text area
        text_area.focus()
        root.mainloop()

    if resp == "Single Line":
        window = tk.Tk()
        window.title(TITLE)

        testing = tk.StringVar()
        testing.set(COUNTER)

        frame_a = tk.Frame()
        frame_b = tk.Frame()

        entry = tk.Entry(master=frame_a, width=50)
        label_a = tk.Label(master=frame_a, text="Hey! This is the Single lined KeyLogger Program!\n\nPlease insert the text you want to paste below\n")
        frameC = tk.Label(master=frame_a, textvariable=testing)
        button = tk.Button(master=frame_b, text="Submit", command=lambda: writez(entry.get(), window, testing))

        label_a.pack()
        frameC.pack()
        entry.pack()
        button.pack()
        frame_a.pack()
        frame_b.pack()
        
        window.mainloop()

        
if __name__ == '__main__':
    main()
