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
import pyuac, sys

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
    "auto_pause": true,
}
""")

def is_running_as_admin():
    return pyuac.isUserAdmin()

def run_as_admin():
    # Re-run the script with admin privileges if not already
    if not is_running_as_admin():
        pyuac.runAsAdmin()
        sys.exit()  # Ensure the current process exits

with open("./User/cfg.json", 'r') as cfg:
    data = cfg.read()
    data_j = json.loads(data)

    json_data = data_j

    if (data_j["auto_echo_off"] == True): _ECHO_OFF = True
    if (data_j["auto_pause"] == True): _AUTO_PAUSE = True



class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.default_fg_color = self.cget("foreground")
        self.placeholder_fg_color = "grey"
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.insert(0, self.placeholder)
        self.config(foreground=self.placeholder_fg_color)

    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.config(foreground=self.default_fg_color)
            self.delete(0, tk.END)

    def _on_focus_out(self, event):
        if not self.get():
            self.config(foreground=self.placeholder_fg_color)
            self.insert(0, self.placeholder)



class MKTask:
    def __init__(self):
        run_as_admin()

        self.window = tk.Tk()
        self.style = ttk.Style()
        self.scriptloc = f".\\Scripts\\Code.bat"

        self.timeline = []
        self.timeline_current_index = 0

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
        window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def parse(self, input):
        noauto = False
        leave_code = False

        txt = ""

        if "$noauto" in str(input.get(1.0, tk.END)): 
            noauto = True

        if _ECHO_OFF == True and not noauto: txt += "\n@echo off\n"

        txt += str(input.get(1.0, tk.END))

        if _AUTO_PAUSE == True and not noauto: txt += "\npause\n"

        txt = txt.replace("$noauto", "")
        txt = txt.replace("$error", "echo An error has occured.\npause\nexit")

        return txt

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()
            quit()
            
    def error(self, errorText, title="Error"):
        root = self.window

        root.withdraw()  # Hide the root window initially

        messagebox.showerror(title, errorText)
        
        root.deiconify()

    def run(self, input): # dont use
        self.out_text.delete(1.0, tk.END)

        txt = ""

        if _ECHO_OFF: txt += "\n@echo off\n"

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
            txt = self.parse(input)

            f.write(txt)

        proc = Popen(
            f"explorer.exe {self.scriptloc}",
            cwd=os.getcwd(),
            stdout=PIPE,
            stderr=PIPE,
            shell=True
        )
        print(self.scriptloc, os.getcwd())

        

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

        self.currently_open = file_path

        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
            
            return content
        else: return 69420 # nice

    def copy_from_file(self, input, floc=None):
        file_data = self.open_file()

        with open(os.path.abspath(floc), "r+") as f:
            file_data = f.read()

        if not file_data == 69420:
            input.delete(1.0, tk.END)
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

    def view_startups(self): os.system(f"explorer.exe {startup}")

    def save_file(self, input):
        txt = self.parse(input)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Batch file", "*.bat"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w') as file:
                file.write(txt)

    def save_proj(self, input):
        with open(self.scriptloc, 'w') as f:
            f.write(self.parse(input))

    def get_name(self, input):
        self.project_name = self._proj_name.get()
        self._proj_name.configure(fg="#5b9c49")

        if self.project_name == "":
            self.scriptloc = ".\\Scripts\\Code.bat"
            self.save_proj(input)

            self.window.title("MKTask")
        else:
            project_dir = f".\\Scripts\\{self.project_name}"
            
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
                print(f"Created directory: {project_dir}")

                        
                self.scriptloc = f"{project_dir}\\Code.bat"
                
                with open(self.scriptloc, "w") as f:
                    f.write("@echo off\n")
                    f.write("REM Your script commands here\n")
                    f.write("echo Hello, World!\n")
                    f.close()
                
                self.save_proj(input)
                self.window.title(f"MKTask - {self.project_name} - {os.path.abspath(self.scriptloc)}")

            else:
                self.scriptloc = f"{project_dir}\\Code.bat"

                self.save_proj(input)
                self.window.title(f"MKTask - {self.project_name} - {os.path.abspath(self.scriptloc)}")

    def get_name_color(self):
        try:
            if not self.project_name == self._proj_name.get():
                self._proj_name.configure(fg="#bababa")
        except: pass

    def go_back(self, input):
        if self.timeline_current_index > 0:
            self.timeline_current_index -= 1

            input.delete(1.0, tk.END)
            input.insert(1.0, self.timeline[self.timeline_current_index])
            input.highlight_all()

    def update_timeline(self, input):
        current_text = input.get(1.0, tk.END).strip()

        if current_text:
            self.timeline.append(current_text)
            self.timeline_current_index += 1

            print(self.timeline)

    def timeline_main(self, event):
        if not (event.state == 0x4 ):
            self.update_timeline(self._input)

    def Core(self):
        if not os.path.exists(startup): 
            self.can_make_task = False
            self.error(f"MkTask - Missing startup folder\n\nCannot find windows startup folder. You won't be able to make tasks.\n\nFolder should be located in: \n\n`{startup}` ")

        window = self.window

        mainframe = tk.Frame(window, bg="#282a36")
        mainframe.pack(fill="x")

        self._input = _input = CodeView(mainframe,  bg="#1f1f1f", fg="#ffffff", height=40, lexer=syntax.BatchLexer, color_scheme="dracula", font=("Lucida Console", 10))
        _input = self._input

        _input.insert(1.0, "rem\t\tWrite, view, and run Batch scripts.\nrem\t\tTo run, press Ctrl+R!\n\necho Hello, world!")
        _input.highlight_all()

        _input.pack(pady=5)

        self.context_menu = tk.Menu(window, tearoff=0, borderwidth=0, relief='flat', activebackground="black")

        self.context_runs = tk.Menu(self.context_menu, tearoff=0)
        self.context_actions = tk.Menu(self.context_menu, tearoff=0)
        self.context_files = tk.Menu(self.context_menu, tearoff=0)
        self.context_tasks = tk.Menu(self.context_menu, tearoff=0)

        self.context_runs.add_command(label="Run (CTRL+R)", command=lambda: self.runcmd(_input))
        self.context_runs.add_command(label="Run in MkTask (CTRL+H)", command=lambda: self.run(_input))
        self.context_menu.add_cascade(label="Run", menu=self.context_runs)

        self.context_actions.add_command(label="Copy all (CTRL+X)", command=lambda: self.copy(_input))
        self.context_actions.add_command(label="Clear all (CTRL+B)", command=lambda: self.clear(_input))
        self.context_menu.add_cascade(label="Actions", menu=self.context_actions)

        self.context_files.add_command(label="Open from file (CTRL+O)", command=lambda: self.copy_from_file(_input))
        self.context_files.add_command(label="Open script location (CTRL+F)", command=lambda: os.system("explorer .\\Scripts\\"))
        self.context_files.add_command(label="Save file (CTRL+S)", command=lambda: self.save_file(_input))

        self.context_tasks.add_command(label="Add to startup (CTRL+M)", command=lambda: self.add_to_startup(_input))
        self.context_tasks.add_command(label="View startups (ALT+T)", command=self.view_startups)

        self.context_menu.add_cascade(label="File", menu=self.context_files)
        self.context_menu.add_cascade(label="Tasks", menu=self.context_tasks)

        _input.pack(fill="both")

        _data = tk.Frame(window, bg="#212126")
        _data.pack(fill="both")

        self._data_lines = tk.Label(_data, text="Thanks for using MkTask!", bg="#212126", fg="#bababa")
        self._data_lines.pack(anchor='w')

        self._proj_name = PlaceholderEntry(_data, bg="#212126", fg="#bababa", placeholder="Project name", bd=1)
        self._proj_name.pack(anchor='w', padx=3)

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

        self._proj_name.bind("<KeyRelease>", lambda x: self.get_name_color())
        self._proj_name.bind("<Return>", lambda x: self.get_name(_input))

        _input.focus()

    
        _input.bind("<Return>", lambda x: self.auto_indent(input=_input))
        _input.bind('<KeyPress>', lambda x: self.update_status_bar(_input))
        _input.bind('<KeyRelease>', lambda x: self.save_proj(_input))
        _input.bind("<Button-3>", self.show_context_menu)

        self.out_text.bind("<Button-3>", self.show_context_menu_out)

        self.update_timeline(_input)

        window.bind('<Control-z>', lambda x: self.go_back(_input))
        window.bind('<KeyRelease>', self.timeline_main)
        window.bind('<Alt-t>', lambda x: self.view_startups())
        window.bind('<Control-s>', lambda x: self.save_file(_input))
        window.bind('<Control-m>', lambda x: self.add_to_startup(_input))
        window.bind('<Control-f>', lambda x: os.system("explorer .\\Scripts\\"))
        window.bind('<Control-o>', lambda x: self.copy_from_file(_input))
        window.bind('<Control-b>', lambda x: self.clear(_input))
        window.bind('<Control-h>', lambda x: self.run(_input))
        window.bind('<Control-r>', lambda x: self.runcmd(_input))
        window.bind('<Control-x>', lambda x: self.copy(_input))

        window.mainloop()

root = MKTask()
main = root.Core()
