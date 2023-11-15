import tkinter as tk

class Node:
    def __init__(self, canvas, x, y, label, app, num):
        self.canvas = canvas
        self.app = app
        self.x, self.y = x, y
        self.last_x, self.last_y = x, y
        self.label = label
        self.num = num
        self.root = app.root

        # 創建一個可以拖動的節點
        self.circle = canvas.create_oval(x-12, y-12, x+12, y+12, fill="white", outline="black")
        self.text = canvas.create_text(x, y, text=label+"("+num+")", font=("Arial", 10))

        # 綁定滑鼠事件
        self.canvas.tag_bind(self.circle, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.circle, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.text, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)
        self.context_menu = tk.Menu(canvas, tearoff=0)
        self.context_menu.add_command(label="Remove node", command=self.remove_node)
        self.canvas.tag_bind(self.circle, "<Button-3>" if self.root.tk.call('tk', 'windowingsystem') != 'aqua' else "<Button-2>", self.show_context_menu)
        self.canvas.tag_bind(self.text, "<Button-3>" if self.root.tk.call('tk', 'windowingsystem') != 'aqua' else "<Button-2>", self.show_context_menu)

    def move(self):
        self.canvas.tag_bind(self.circle, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)

    def dont_move(self):
        self.canvas.tag_unbind(self.circle, "<B1-Motion>")
        self.canvas.tag_unbind(self.text, "<B1-Motion>")

    def on_click(self, event):
        if self.app.selecting_edge:
            self.reset_color()
            self.app.select_node(self)
        else:
            self.last_x, self.last_y = event.x, event.y

    def on_drag(self, event):
        self.app.update_save_state(0,self.app.save_path,self.app.save_name)
        # 网格大小
        grid_spacing = 20
        # 计算最接近的网格交叉点坐标
        grid_x = round(event.x / grid_spacing) * grid_spacing
        grid_y = round(event.y / grid_spacing) * grid_spacing

        # 计算移动的距离
        dx = grid_x - self.x
        dy = grid_y - self.y

        # 移动节点到最近的网格交叉点
        self.canvas.move(self.circle, dx, dy)
        self.canvas.move(self.text, dx, dy)

        # 更新节点坐标
        self.x = grid_x
        self.y = grid_y
        self.last_x, self.last_y = self.x, self.y

        # 更新相关的边
        for edge in self.app.edges:
            if edge.start_node == self or edge.end_node == self:
                edge.update_position()

    # 使節點變為灰色
    def set_gray(self):
        self.canvas.itemconfig(self.circle, fill="gray")

    # 恢復節點的顏色為白色
    def reset_color(self):
        self.canvas.itemconfig(self.circle, fill="white")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def remove_node(self):
        # 從畫布上移除節點
        self.canvas.delete(self.circle)
        self.canvas.delete(self.text)
        # 從應用的節點列表中移除該節點
        self.app.nodes.remove(self)
        # 移除與該節點相關的邊緣
        edges_to_remove = [edge for edge in self.app.edges if edge.start_node == self or edge.end_node == self]
        for edge in edges_to_remove:
            edge.remove_edge()
        self.app.update_edge_button_state()