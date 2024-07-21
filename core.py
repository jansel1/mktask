import tkinter as tk
from tkinter import ttk
from subprocess import Popen, PIPE
import os, random

import pygments.lexer
import pygments.lexers
from chlorophyll import CodeView
import pygments.lexers.shell



class MKTask:
    def __init__(self):
        self.window = tk.Tk()
        self.style = ttk.Style()

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

        window.geometry("500x500")
        window.configure(bg="#1f1f1f")

        window.minsize(250, 250)

    def run(self, input):
        self.out_text.delete(1.0, tk.END)

        scriptloc = f"Code.bat"
        txt = "@echo off\n" # Turns this off if you want echo on

        txt += input.get(1.0, tk.END)

        with open(scriptloc, "w") as f:
            f.write(txt)

        proc = Popen(
            f"cmd.exe /c {scriptloc}",
            cwd=os.getcwd(),
            stdout=PIPE,
            stderr=PIPE,
            shell=True
        )

        stdout, stderr = proc.communicate()

        output = stdout.decode('utf-8')
        output_E = stderr.decode('utf-8')
        
        if output_E in [None, '']: output_E = 'No logs...'
        if output in [None, '']: output_E = "Could not fetch a response or program did not provide any.\n"

        output_E += stderr.decode('utf-8')

        self.out_text.configure(state="normal")
        self.out_text.insert(1.0, f"{output}\n\nMkTask Log: \n{output_E}")
        self.out_text.configure(state="disabled")
    
    def clear(self, input):
        input.delete(1.0, tk.END)

    def Core(self):
        window = self.window

        mainframe = tk.Frame(window)
        mainframe.pack(fill="x")

        _input = CodeView(mainframe, bg="#1f1f1f", fg="#ffffff", height=30, lexer=pygments.lexers.shell.BatchLexer, color_scheme="dracula", font=("Lucida Console", 10))
        
        _input.pack(fill="x")

        _commands = tk.Frame(window, bg="#212126")
        _commands.pack(fill="both")

        _commands_execute = tk.Button(_commands, text="RUN", bg="#0f2917", fg="#bababa", height=1, width=8, command=lambda: self.run(_input), cursor="hand2")
        _commands_execute.grid(row=0, column=0, padx=0)

        _commands_clear = tk.Button(_commands, text="CLEAR", bg="#290f0f", fg="#bababa", height=1, width=8, cursor="hand2", command=lambda: self.clear(_input))
        _commands_clear.grid(row=0, column=1, padx=0)

        _commands_copy = tk.Button(_commands, text="COPY", bg="#0f2929", fg="#bababa", height=1, width=8, cursor="hand2", command=lambda: self.clear(_input))
        _commands_copy.grid(row=0, column=2, padx=0)

        self._output = tk.Frame(window, bg="#1f1f1f")
        self._output.pack(fill="both", expand=True)

        scrollb_out = tk.Scrollbar(self._output, orient='vertical')
        scrollb_out.pack(side=tk.RIGHT, fill="y")

        self.out_text = tk.Text(self._output, bg="#1f1f1f", fg="#ffffff", height=20, yscrollcommand=scrollb_out.set)
        self.out_text.pack(fill="both", expand=True)

        self.out_text.configure(state="disabled")

        scrollb_out.config(command=self.out_text.yview)

        window.mainloop()

root = MKTask()
main = root.Core()
