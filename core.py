import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox, simpledialog

from subprocess import Popen, PIPE
import os, random

import pygments.lexer
import pygments.lexers

import pygments.lexers.shell

import pyperclip, time, re
import keyboard, threading, json

import chlorophyll
from chlorophyll import CodeView

import syntax
import pyuac

_ECHO_OFF = None
_AUTO_PAUSE = None

json_data = None
current_dir = None

current_dir = os.chdir(os.getcwd())
startup = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"

if not os.path.exists(".\\Scripts"): os.mkdir("Scripts")
if not os.path.exists(".\\Scripts\\Code.bat"): 
    with open("./Scripts/Code.bat", "w") as f: f.write("")

if not os.path.exists(".\\User"): os.mkdir("User")
if not os.path.exists(".\\User\\cfg.json"): 
    with open("./User/cfg.json", "w") as f: f.write("""
{
    "auto_echo_off": true,
    "auto_pause": true
}
""")

with open("./User/cfg.json", 'r') as cfg:
    data = cfg.read()
    data_j = json.loads(data)

    json_data = data_j

    if (data_j["auto_echo_off"] == True): _ECHO_OFF = True
    if (data_j["auto_pause"] == True): _AUTO_PAUSE = True

class MKTask:
    def __init__(self):
        self.window = tk.Tk()
        self.style = ttk.Style()
        self.scriptloc = f".\\Scripts\\Code.bat"

        if not pyuac.isUserAdmin() and self.window.winfo_exists: 
            pyuac.runAsAdmin()
        
        self.style.theme_use('classic')

        style = self.style
        window = self.window

        self.can_make_task = True

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

    def error(self, errorText, title="Error"):
        root = self.window

        root.withdraw()  # Hide the root window initially

        messagebox.showerror(title, errorText)
        
        root.deiconify()

    def run(self, input): # dont use
        self.out_text.delete(1.0, tk.END)

        if _ECHO_OFF: txt = "\n@echo off\n"

        txt += input.get(1.0, tk.END)

        with open(self.scriptloc, "w") as f:
            f.write(txt)

        if _AUTO_PAUSE: txt += "\npause\n"

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
            txt = ""
            noauto = False

            if "noauto" in str(input.get(1.0, tk.END)): 
                noauto = True


            if _ECHO_OFF == True and not noauto: txt += "\n@echo off\n"

            txt += str(input.get(1.0, tk.END))

            if _AUTO_PAUSE == True and not noauto: txt += "\npause\n"
            txt = txt.replace("noauto", "")

            f.write(txt)


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

    def show_context_menu_out(self, event):
        self.context_menu_out.tk_popup(event.x_root, event.y_root)

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

    def msg_prompt(self, text, title_="Question"):
        user_input = simpledialog.askstring(title_, text)

        return user_input
    
    def add_to_startup(self, input):
        n=self.msg_prompt("What would you like to name this task?", title_="Task Name")

        if n is None:
            return
        
        with open(f"{startup}\\{n}", 'w') as f:
            txt = ""
            noauto = False

            if "noauto" in str(input.get(1.0, tk.END)): 
                noauto = True


            if _ECHO_OFF == True and not noauto: txt += "\n@echo off\n"

            txt += str(input.get(1.0, tk.END))

            if _AUTO_PAUSE == True and not noauto: txt += "\npause\n"
            txt = txt.replace("noauto", "")

            f.write(txt)

    def Core(self):
        if not os.path.exists(startup): 
            self.can_make_task = False
            self.error(f"MkTask - Missing startup folder\n\nCannot find windows startup folder. You won't be able to make tasks.\n\nFolder should be located in: \n\n`{startup}` ")

        window = self.window

        mainframe = tk.Frame(window)
        mainframe.pack(fill="x")

        _input = CodeView(mainframe,  bg="#1f1f1f", fg="#ffffff", height=40, lexer=syntax.BatchLexer, color_scheme="dracula", font=("Lucida Console", 10))
        _input.insert(1.0, "rem Write, view, and run Batch scripts.\nrem To run, press Ctrl+R!\n\necho Hello, world!")
        _input.highlight_all()

        self.context_menu = tk.Menu(window, tearoff=0, borderwidth=0, relief='flat', activebackground="black")

        self.context_runs = tk.Menu(self.context_menu, tearoff=0)
        self.context_actions = tk.Menu(self.context_menu, tearoff=0)
        self.context_files = tk.Menu(self.context_menu, tearoff=0)

        self.context_runs.add_command(label="Run (CTRL+R)", command=lambda: self.runcmd(_input))
        self.context_runs.add_command(label="Run in MkTask (CTRL+Z)", command=lambda: self.run(_input))
        self.context_menu.add_cascade(label="Run", menu=self.context_runs)

        self.context_actions.add_command(label="Copy all (CTRL+X)", command=lambda: self.copy(_input))
        self.context_actions.add_command(label="Clear all (CTRL+B)", command=lambda: self.clear(_input))
        self.context_menu.add_cascade(label="Actions", menu=self.context_actions)

        self.context_files.add_command(label="Open from file (CTRL+O)", command=lambda: self.copy_from_file(_input))
        self.context_files.add_command(label="Open code location (CTRL+F)", command=lambda: os.system("explorer .\\Scripts\\"))
        
        self.context_tasks = tk.Menu(self.context_files, tearoff=0)
        self.context_tasks.add_command(label="Add to startup", command=lambda: self.add_to_startup(input))
        

        self.context_menu.add_cascade(label="File", menu=self.context_files)
        self.context_files.add_cascade(label="Tasks", menu=self.context_tasks)

        _input.pack(fill="both")

        _data = tk.Frame(window, bg="#212126")
        _data.pack(fill="both")

        self._data_lines = tk.Label(_data, text="Thanks for using MkTask!", bg="#212126", fg="#bababa")
        self._data_lines.pack(anchor='w')

        self._output = tk.Frame(window, bg="#1f1f1f")
        self._output.pack(fill="both", expand=True)

        self.context_menu_out = tk.Menu(window, tearoff=0, borderwidth=0, relief='flat', activebackground="black")
        self.context_menu_out.add_command(label="Clear", command= self.clearc)
        self.context_menu_out.add_command(label="Copy all", command=lambda: self.copy(self.out_text))

        scrollb_out = tk.Scrollbar(self._output, orient='vertical')
        scrollb_out.pack(side=tk.RIGHT, fill="y")

        self.out_text = tk.Text(self._output, bg="#1f1f1f", fg="#ffffff", height=20, yscrollcommand=scrollb_out.set)
        self.out_text.pack(fill="both", expand=True)

        self.out_text.configure(state="disabled")

        scrollb_out.config(command=self.out_text.yview)

        _input.bind("<Return>", lambda x: self.auto_indent(input=_input))
        _input.bind('<KeyPress>', lambda x: self.update_status_bar(_input))
        _input.bind("<Button-3>", self.show_context_menu)

        self.out_text.bind("<Button-3>", self.show_context_menu_out)

        window.bind('<Control-f>', lambda x: os.system("explorer .\\Scripts\\"))
        window.bind('<Control-o>', lambda x: self.copy_from_file(_input))
        window.bind('<Control-b>', lambda x: self.clear(_input))
        window.bind('<Control-z>', lambda x: self.run(_input))
        window.bind('<Control-r>', lambda x: self.runcmd(_input))
        window.bind('<Control-x>', lambda x: self.copy(_input))

        window.mainloop()

root = MKTask()
main = root.Core()
