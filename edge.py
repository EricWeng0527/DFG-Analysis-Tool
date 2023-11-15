import tkinter as tk
import math

class Edge:
    def __init__(self, canvas, start_node, end_node, app):
        self.canvas = canvas
        self.start_node = start_node
        self.end_node = end_node
        self.app = app
        self.root = app.root
        self.line = self.create_line()
        # 初始化 DFF 標籤
        self.dff_label = None
        self.dff_num = 0
        
        # 綁定右鍵菜單事件
        self.canvas.tag_bind(self.line, "<Button-3>" if self.root.tk.call('tk', 'windowingsystem') != 'aqua' else "<Button-2>", self.show_context_menu)
        
        # 創建右鍵菜單
        self.context_menu = tk.Menu(canvas, tearoff=0)
        self.context_menu.add_command(label="Remove edge", command=self.remove_edge)

    def add_dff(self, event=None, add=1):
        self.dff_num += add
        x = (self.start_node.x + self.end_node.x) / 2
        y = (self.start_node.y + self.end_node.y) / 2
        if self.dff_label:
            self.canvas.delete(self.dff_label)
        self.dff_label = self.canvas.create_text(x, y, text=str(self.dff_num)+"D", font=("Arial", 13), fill="#FF8000")
        # 綁定右鍵菜單事件
        self.canvas.tag_bind(self.dff_label, "<Button-3>" if self.root.tk.call('tk', 'windowingsystem') != 'aqua' else "<Button-2>", self.show_context_menu)
        self.context_menu.add_command(label="Remove D", command=self.remove_dff)
        self.canvas.tag_bind(self.dff_label, "<Button-1>", self.add_dff)
        
    
    def remove_dff(self):
        if self.dff_label:
            self.canvas.delete(self.dff_label)
            self.dff_label = None
            self.dff_num = 0
            self.context_menu.delete("Remove D")

    def create_line(self):
        x1, y1 = self.calculate_edge_point(self.start_node.x, self.start_node.y, self.end_node.x, self.end_node.y)
        x2, y2 = self.calculate_edge_point(self.end_node.x, self.end_node.y, self.start_node.x, self.start_node.y)
        return self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)

    def calculate_edge_point(self, x1, y1, x2, y2):
        angle = math.atan2(y2 - y1, x2 - x1)
        return x1 + 10 * math.cos(angle), y1 + 10 * math.sin(angle)

    def update_position(self):
        x1, y1 = self.calculate_edge_point(self.start_node.x, self.start_node.y, self.end_node.x, self.end_node.y)
        x2, y2 = self.calculate_edge_point(self.end_node.x, self.end_node.y, self.start_node.x, self.start_node.y)
        self.canvas.coords(self.line, x1, y1, x2, y2)
        # 更新 DFF 標籤的位置（如果存在）
        if self.dff_label:
            x = (self.start_node.x + self.end_node.x) / 2
            y = (self.start_node.y + self.end_node.y) / 2
            self.canvas.coords(self.dff_label, x, y)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def remove_edge(self):
        self.remove_dff()
        self.canvas.delete(self.line)
        self.app.edges.remove(self)
        self.app.update_dff_button_state()