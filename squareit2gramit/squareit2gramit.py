from tkinter import Tk, Label, Button, filedialog, tix, ttk
from pathlib import Path
from PIL import Image
import os
import time
import threading
import queue


class GUI:
    def __init__(self, master):

        self.image_directory = None
        self.master = master
        master.title("Batch Square")

        self.label = Label(master, text="""
        Please select a directory that contains your images (JPEG only).
        This program will square it and save it in a folder called 'squared'
        within the directory you provided.

        For example:
        Your directory: C://Users/Bob/Pictures/MyImages
        The squared images will be placed inside C://Users/Bob/Pictures/MyImages/squared folder
        """)
        self.label.pack()

        self.choose_directory = Button(master, text="Choose a folder", command=self.choose_directory)
        self.choose_directory.pack()

        self.process_button = Button(master, text="Process", command=self.process,
            state='disabled')
        self.process_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.message = Label(master, text="")
        self.message.pack()

        self.progress = ttk.Progressbar(root, orient = 'horizontal', 
              length = 100, mode = 'determinate') 
        self.progress.pack() 


    def choose_directory(self):
        self.image_directory = filedialog.askdirectory()
        self.message.config(text=self.image_directory)
        self.process_button.config(state='normal')
    
    def process(self):
        if self.image_directory is None:
            return
        self.process_images()

    def process_images(self):
        source_path = Path(self.image_directory)
        output_path = source_path/'squared'
        try:
            os.mkdir(output_path)
        except FileExistsError:
            pass

        self.queue = queue.Queue()
        
        image_paths = list(source_path.glob('*.jpg'))
        
        self.progress['value'] = 0
        ThreadedTask(self.queue, image_paths, output_path).start()

        self.listen_to_queue()

    def listen_to_queue(self):
        try:
            msg = self.queue.get(0)
            print('message', msg)
            self.progress['value'] = int(msg)
            if msg == 100:
                self.message.config(text='Done')
                return
        except queue.Empty:
            pass  
        
        self.master.after(100, self.listen_to_queue)

class ThreadedTask(threading.Thread):
    def __init__(self, queue, image_paths, output_path):
        threading.Thread.__init__(self)
        self.image_paths = image_paths
        self.queue = queue
        self.output_path = output_path

    def run(self):
        for i, image_path in enumerate(self.image_paths):
            im = Image.open(image_path)
            side_length = max(im.size[0], im.size[1])

            new_im = Image.new("RGB", (side_length, side_length), color=(255,255,255))
            new_im.paste(im, ((side_length - im.size[0]) // 2,
                            (side_length - im.size[1]) // 2))
            new_im.save(self.output_path/image_path.name)

            self.queue.put((i+1) / len(self.image_paths) * 100)

root = Tk()
my_gui = GUI(root)
root.mainloop()