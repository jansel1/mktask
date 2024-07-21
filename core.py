import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from subprocess import Popen, PIPE
import os, random

import pygments.lexer
import pygments.lexers
from chlorophyll import CodeView
import pygments.lexers.shell

import pyperclip, time, re
import keyboard, threading


class MKTask:
    def __init__(self):
        self.window = tk.Tk()
        self.style = ttk.Style()
        self.scriptloc = f".\\Scripts\\Code.bat"

        style = self.style
        window = self.window

        try:
            try:
                window.iconbitmap("MkTask.ico")
            except: 
                try:
                    window.iconbitmap("./src/MkTask.ico")
                except:
                    pass
        except: pass

        window.title("MKTask")

        window.geometry("850x650") # y x
        window.configure(bg="#1f1f1f")

        window.minsize(250, 250)

    def run(self, input):
        self.out_text.delete(1.0, tk.END)

        txt = "@echo off\n" # Turns this off if you want echo on

        txt += input.get(1.0, tk.END)

        with open(self.scriptloc, "w") as f:
            f.write(txt)

        if "pause" in txt: self.out_text.insert(1.0, "UNSUPPORTED COMMAND: pause: This command WILL crash MkTask. "); return

        if txt == None: txt = ""

        proc = Popen(
            f"cmd.exe /c {self.scriptloc}",
            cwd=os.getcwd(),
            stdout=PIPE,
            stderr=PIPE,
            shell=True
        )

        stdout, stderr = proc.communicate()

        output = stdout.decode('utf-8')
        output_E = stderr.decode('utf-8')
        
        if output_E in [None, '']: output_E = 'No logs...\n'
        if output in [None, '']: output_E = "Could not fetch a response or program did not provide any.\n"
        #if txt in None: output_E = "Please write!"

        output_E += stderr.decode('utf-8')

            
        self.out_text.configure(state="normal")
        self.out_text.insert(1.0, f"{output}\n\nMkTask Log: \n{output_E}")
        self.out_text.configure(state="disabled")
    
    def runcmd(self, input):
        with open(self.scriptloc, "w") as f:
            f.write("@echo off\n" + str(input.get(1.0, tk.END)) + "\npause")

        proc = Popen(
            f"explorer.exe {self.scriptloc}",
            cwd=os.getcwd(),
            stdout=PIPE,
            stderr=PIPE,
            shell=True
        )

        

    def clear(self, input): input.delete(1.0, tk.END)

    def clearc(self):  # to fucking work on
        self.out_text.configure(state="normal")
        self.out_text.delete(1.0, tk.END)
        self.out_text.configure(state="disabled")

    def copy(self, input): pyperclip.copy(input.get(1.0, tk.END))

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Batch files", "*.bat"), ("All files", "*.*")]
        )

        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
            
            return content

    def copy_from_file(self, input):
        input.delete(1.0, tk.END)
        
        file_data = self.open_file()
        input.insert(1.0, file_data)
    
    def update_status_bar(self, input):
        content = input.get(1.0, tk.END)
        wospaces = content.replace(" ", "")

        num_chars = len(wospaces) - 1
        num_chars_real = len(content) - 1

        num_lines = int(input.index(tk.END).split('.')[0]) - 1 

        self._data_lines.config(text=f"Lines: {num_lines} | Characters: {num_chars} (w/spaces: {num_chars_real})")
        
    def auto_indent(self, event=None, input=None):
        text = input.get(1.0, tk.END)

        line = input.get("insert linestart", "insert")

        match = re.match(r'^(\s+)', line)
        whitespace = match.group(0) if match else ""


        input.insert("insert", f"\n{whitespace}")

        return "break"
    
    def Core(self):
        window = self.window

        mainframe = tk.Frame(window)
        mainframe.pack(fill="x")

        _input = CodeView(mainframe, bg="#1f1f1f", fg="#ffffff", height=30, lexer=pygments.lexers.shell.BatchLexer, color_scheme="dracula", font=("Lucida Console", 10))
        
        self.context_menu = tk.Menu(window, tearoff=0, borderwidth=0, relief='flat', activebackground="black")

        self.context_menu.add_command(label="RUN IN CMD", command=lambda: self.runcmd(_input))
        self.context_menu.add_command(label="RUN HERE", command=lambda: self.run(_input))
        self.context_menu.add_separator()

        self.context_menu.add_command(label="Copy all", command=lambda: self.copy(_input))
        self.context_menu.add_command(label="Clear all", command=lambda: self.clear(_input))
        self.context_menu.add_separator()

        self.context_menu.add_command(label="Open from file", command=lambda: self.copy_from_file(_input))
        self.context_menu.add_command(label="Open code location", command=lambda: os.system("explorer .\\Scripts\\"))
        
        _input.pack(fill="both")

        _data = tk.Frame(window, bg="#212126")
        _data.pack(fill="both")

        self._data_lines = tk.Label(_data, text="Thanks for using MkTask!", bg="#212126", fg="#bababa")
        self._data_lines.pack(anchor='w')

        self._output = tk.Frame(window, bg="#1f1f1f")
        self._output.pack(fill="both", expand=True)

        scrollb_out = tk.Scrollbar(self._output, orient='vertical')
        scrollb_out.pack(side=tk.RIGHT, fill="y")

        self.out_text = tk.Text(self._output, bg="#1f1f1f", fg="#ffffff", height=20, yscrollcommand=scrollb_out.set)
        self.out_text.pack(fill="both", expand=True)

        self.out_text.configure(state="disabled")

        scrollb_out.config(command=self.out_text.yview)

        _input.bind("<Return>", lambda x: self.auto_indent(input=_input))
        _input.bind('<KeyPress>', lambda x: self.update_status_bar(_input))
        _input.bind("<Button-3>", self.show_context_menu)

        window.bind('<Control-z>', lambda x: self.run(_input))
        window.bind('<Control-r>', lambda x: self.runcmd(_input))
        window.bind('<Control-x>', lambda x: self.copy(_input))

        window.mainloop()

root = MKTask()
main = root.Core()
