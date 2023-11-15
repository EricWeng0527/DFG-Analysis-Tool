import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not file_path:  # 如果没有选择文件就返回
        return
    with open(file_path, 'w') as file:
        file.write("这里是你要保存的内容")

def on_closing():
    if messagebox.askyesno("Quit", "Do you want to save your work before quitting?"):
        # 提供保存文件的功能
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            # 这里应该是保存文件的代码
            print(f"文件已保存到 {file_path}")
        root.destroy()
    else:
        root.destroy()

root = tk.Tk()
save_button = tk.Button(root, text="保存文件", command=save_file)
save_button.pack()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
