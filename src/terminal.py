import tkinter as tk

class Terminal:
    def __init__(self, master):
        self.master = master
        self.master.title("Terminal Output")
        self.master.configure(bg='yellow')
        self.master.geometry("600x600+800+100")
        self.text_widget = tk.Text(self.master, wrap=tk.WORD, bg="black", fg="yellow", insertbackground="white",
                                   font=("Source Sans Pro Black", 14, 'bold'), foreground="white")
        self.text_widget.pack(expand=True, fill='both',padx=5, pady=5)
        # self.hide_button = tk.Button(self.master, text="Hide Window", command=self.hide_window)
        # self.hide_button.pack()
        self.master.bind('<q>', self.quit_app)

    def clear_text(self):
        self.text_widget.delete('1.0', tk.END)
    
    def print_text(self, text):
        self.text_widget.insert(tk.END, text + '\n')
        self.text_widget.see(tk.END) 

    def hide_window(self):
        self.master.withdraw()

    def show_window(self, event=None):
        self.master.deiconify()

    def quit_app(self, event=None):
        self.master.quit()

# Example usage

# root = tk.Tk()
# terminal_output = Terminal(root)
# # terminal_output.hide_window()
# root.mainloop()