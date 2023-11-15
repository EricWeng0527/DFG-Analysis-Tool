import networkx as nx
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import json
from func import *
from edge import *
from node import *

class App:
    def __init__(self, root):
        self.root = root
        self.G = nx.DiGraph()
        # Create a container for left and right frames
        self.top_container = tk.Frame(root, bg="#F0F0F0")
        self.top_container.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.top_container, width=600, height=500, bg="#F0F0F0")
        self.right_frame = tk.Frame(self.top_container, width=400, height=500, bg="#F0F0F0")
        self.left_frame.pack(side="left", fill="y")
        self.right_frame.pack(side="right", fill="y")

        self.bottom_frame = tk.Frame(root, width=600, height=100, bg="white")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # menu
        # 创建顶级菜单
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # 创建“File”菜单并添加到顶级菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # 在“File”菜单中添加命令
        self.file_menu.add_command(label="New DFG", command=self.new_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Load DFG", command=self.load_from_file)
        self.file_menu.add_command(label="Save DFG", command=self.save_to_file)
        self.file_menu.add_command(label="Save DFG as new file", command=self.save_to_new_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)
        
        self.file_menu.entryconfig("Save DFG", state="disabled")
        


        # left frame
        self.canvas = tk.Canvas(self.left_frame, bg="white", width=560, height=400)
        self.canvas.pack(side="top")
        
        # right frame
        self.node_num_label = tk.Label(self.right_frame, text="Node Weight", bg="#F0F0F0", font=("Arial", 12))
        self.node_num_label.pack(side="top", pady=5)

        self.node_num = tk.Spinbox(self.right_frame, from_=0, to=99, width=6)
        self.node_num.pack(side="top")

        self.add_node_button = tk.Button(self.right_frame, text="Add Node", command=self.add_node, bg="#F0F0F0", width=6)
        self.add_node_button.pack(side="top", pady=5)

        self.add_edge_button = tk.Button(self.right_frame, text="Add Edge", command=self.start_adding_edge, bg="#F0F0F0", width=6)
        self.add_edge_button.pack(side="top", pady=5)

        self.add_dff_button = tk.Button(self.right_frame, text="Add DFF", command=self.toggle_adding_dff, bg="#F0F0F0", width=6)
        self.add_dff_button.pack(side="top", pady=5)

        self.clear_button = tk.Button(self.right_frame, text="Clear", command=self.clear_canvas, bg="#F0F0F0", width=6)
        self.clear_button.pack(side="top", pady=5)

        
        self.add_graph_button = tk.Button(self.right_frame, text="Generate \nGraph", command=self.add_Graph, bg="#F0F0F0", width=6)

        self.iteration_button = tk.Button(self.right_frame, text="Iteration", command=self.iteration, bg="#F0F0F0", width=6)
        
        self.critical_button = tk.Button(self.right_frame, text="Critical", command=self.critical, bg="#F0F0F0", width=6)

        self.clk_mini_button = tk.Button(self.right_frame, text="Retiming", command=self.clk_mini, bg="#F0F0F0", width=6)
        
        self.clk_mini_button.pack(side="bottom", pady=5)
        self.critical_button.pack(side="bottom", pady=5)
        self.iteration_button.pack(side="bottom", pady=5)
        self.add_graph_button.pack(side="bottom", pady=10)

        #bottom frame
        self.output_area = tk.Text(self.bottom_frame, width=60, height=5, wrap=tk.WORD)
        self.output_area.pack(side="bottom", fill="both", expand=True)

        self.edges = []  # 確保先初始化這個屬性
        # 初始化編輯 DFF 的狀態
        self.adding_dff = False

        self.nodes = []
        self.label_order = ord('A') - 1
        
        self.selecting_edge = False
        self.selected_nodes = []

        # 初始化最後一次新增節點的位置
        self.last_node_position = (80, 80)

        self.update_edge_button_state()
        self.update_dff_button_state()
        self.update_graph_state()
        self.update_iteration_button_state()
        self.update_save_state(1,"","new file")
        self.start_grid()

    # grid function
    def start_grid(self):
        # Canvas 完全加载后调用 draw_grid
        self.canvas.after(100, self.draw_grid, 20)
    
    def draw_grid(self, grid_spacing, major_line_color="#ddd", minor_line_color="#ddd", dash=(2, 4)):
         # 删除之前的网格线
        self.canvas.delete("grid_line")
        # 获取当前 Canvas 的宽度和高度
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        # 画水平线
        for i in range(0, height, grid_spacing):
            line_color = major_line_color if i % (grid_spacing * 4) == 0 else minor_line_color
            dash_option = None if i % (grid_spacing * 4) == 0 else dash
            self.canvas.create_line(0, i, width, i, fill=line_color, dash=dash_option, tags="grid_line")
        # 画垂直线
        for i in range(0, width, grid_spacing):
            line_color = major_line_color if i % (grid_spacing * 4) == 0 else minor_line_color
            dash_option = None if i % (grid_spacing * 4) == 0 else dash
            self.canvas.create_line(i, 0, i, height, fill=line_color, dash=dash_option, tags="grid_line")

    def hide_grid(self):
        # 隐藏所有标记为 'grid_line' 的网格线
        self.canvas.itemconfigure('grid_line', state='hidden')

    def show_grid(self):
        # 显示所有标记为 'grid_line' 的网格线
        self.canvas.itemconfigure('grid_line', state='normal')
    
    # node function
    def add_node(self):
        self.label_order += 1
        label = chr(self.label_order)
        if self.label_order >= ord('Z'):
            self.label_order = ord('A')-1
        # 從上次的位置開始，偏移一定的距離
        x, y = self.last_node_position
        num = self.node_num.get()
        node = Node(self.canvas, x, y, label, self, num)
        self.nodes.append(node)
        
        if x<450:
            x += 80
        else:
            x = 80
            y += 80

        # 更新最後一次新增節點的位置
        self.last_node_position = (x, y)

        self.update_edge_button_state()
        self.update_graph_state()
        self.update_save_state(0,self.save_path,self.save_name)
        
        
    def select_node(self, node):
        self.selected_nodes.append(node)
        if len(self.selected_nodes) == 2:
            edge = Edge(self.canvas, self.selected_nodes[0], self.selected_nodes[1], self)
            self.edges.append(edge)
            self.selected_nodes[0].set_gray()
            self.selected_nodes[1].set_gray()
            self.selected_nodes = []
    
    def get_node_by_label(self, label):
        return next(node for node in self.nodes if node.label == label)
    
    def change_color(self, node, color):
        self.canvas.itemconfig(node.circle, outline=color)
        self.canvas.itemconfig(node.text, fill=color)


    #edge function
    def start_adding_edge(self):
        if self.selecting_edge:
            self.show_grid()
            # 如果已經在編輯模式，則結束編輯模式
            self.selecting_edge = False
            self.add_edge_button.config(text="Add Edge")
            # 恢復畫布和所有節點的顏色為白色
            self.canvas.config(bg="white")
            for node in self.nodes:
                node.move()
                node.reset_color()
            self.recover_button_state()
            # 移除提示文字
            self.canvas.delete(self.instruction_text)
            self.update_save_state(0,self.save_path,self.save_name)
        else:
            # 進入編輯模式
            self.hide_grid()
            self.add_edge_button.config(text="Done")
            self.selecting_edge = True
            self.selected_nodes = []
            self.set_buttons_state_except(tk.DISABLED, self.add_edge_button)
            # 將畫布和所有節點變為灰色
            self.canvas.config(bg="gray")
            for node in self.nodes:
                node.dont_move()
                node.set_gray()

            # 添加提示文字"Select two nodes"，位置在畫布的頂部，字體較小
            self.instruction_text = self.canvas.create_text(280, 20, text="Select any two nodes to connect", font=("Arial", 15), fill="white")
            
    
    def toggle_adding_dff(self):
        if self.adding_dff:
            # 如果已經在編輯模式，則結束編輯模式
            self.show_grid()
            self.add_dff_button.config(text="Add DFF")
            self.adding_dff = False
            self.canvas.config(bg="white")
            for node in self.nodes:
                node.move()
                node.reset_color()
            for edge in self.edges:
                self.canvas.tag_unbind(edge.line, "<Button-1>")
                if edge.dff_label:
                    self.canvas.itemconfig(edge.dff_label, fill="black")
                    self.canvas.tag_unbind(edge.dff_label, "<Button-1>")

                
            # 恢復其他按鈕的狀態
            self.recover_button_state()
            # 移除提示文字
            self.canvas.delete(self.instruction_text)
            self.update_save_state(0,self.save_path,self.save_name)
        else:
            # 進入編輯模式
            self.hide_grid()
            self.instruction_text = self.canvas.create_text(280, 20, text="Select edges to add DFF, press again to add more", font=("Arial", 15), fill="white")
            self.add_dff_button.config(text="Done")
            self.adding_dff = True
            # 禁用其他按鈕
            self.set_buttons_state_except(tk.DISABLED, self.add_dff_button)
            self.canvas.config(bg="gray")
            for node in self.nodes:
                node.dont_move()
                node.set_gray()
            for edge in self.edges:
                self.canvas.tag_bind(edge.line, "<Button-1>", lambda event, edge=edge: edge.add_dff())
                if edge.dff_label:
                    self.canvas.tag_bind(edge.dff_label, "<Button-1>", lambda event, edge=edge: edge.add_dff())

    def get_edge_by_nodes(self, start_node, end_node):
        return next(edge for edge in self.edges if edge.start_node == start_node and edge.end_node == end_node)
    
    def change_edge_color(self, edge, color):
        self.canvas.itemconfig(edge.line, fill=color)
        if edge.dff_label:
            self.canvas.itemconfig(edge.dff_label, fill=color)
                
    # update button state function
    def update_edge_button_state(self):
        if len(self.nodes) < 2:
            self.add_edge_button.config(state=tk.DISABLED)
        else:
            self.add_edge_button.config(state=tk.NORMAL)

    def update_dff_button_state(self):
        if len(self.edges) < 1:
            self.add_dff_button.config(state=tk.DISABLED)
        else:
            self.add_dff_button.config(state=tk.NORMAL)

    def update_iteration_button_state(self):
        if len(self.G.nodes()) < 1:
            self.iteration_button.config(state=tk.DISABLED)
            self.critical_button.config(state=tk.DISABLED)
            self.clk_mini_button.config(state=tk.DISABLED)
        else:
            self.iteration_button.config(state=tk.NORMAL)
            self.critical_button.config(state=tk.NORMAL)
            self.clk_mini_button.config(state=tk.NORMAL)

    def update_graph_state(self):
        if len(self.nodes) < 1:
            self.add_graph_button.config(state=tk.DISABLED)
            self.clear_button.config(state=tk.DISABLED)
        else:
            self.add_graph_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)

    def set_buttons_state_except(self, state, except_button):
        buttons = [self.add_node_button, self.add_edge_button, self.add_dff_button, self.add_graph_button, self.iteration_button, self.critical_button, self.clk_mini_button, self.clear_button]
        for btn in buttons:
            if btn != except_button:
                btn.config(state=state)
    
    def recover_button_state(self):
        self.add_node_button.config(state=tk.NORMAL)
        self.update_edge_button_state()
        self.update_dff_button_state()
        self.update_graph_state()
        self.update_iteration_button_state()

    def update_save_state(self, save, save_path, save_name):
        self.save = save
        self.save_path = save_path
        self.save_name = save_name
        if self.save == 1:
            self.root.title("DFG Analysis <"+self.save_name+">")
        else:
            self.root.title("DFG Analysis <"+self.save_name+">*")



    def clear_canvas(self):
        # clear canvas
        self.canvas.delete("all")
        self.nodes = []
        self.edges = []
        self.label_order = ord('A') - 1
        self.last_node_position = (80, 80)
        self.selecting_edge = False
        self.selected_nodes = []
        self.adding_dff = False
        self.G.clear()
        self.recover_button_state()
        self.update_graph_state()
        self.update_iteration_button_state()
        self.output_area.delete(1.0, tk.END)
        self.draw_grid(20)
        self.update_save_state(0,self.save_path,self.save_name)
        


    def display_output(self, content):
        # 清空輸出區域並添加新的內容
        self.output_area.insert(tk.END, content)

    #save and load function
    def new_file(self):
        if self.save == 0:
            response = messagebox.askyesnocancel("New", "Do you want to save your DFG before creating new file?")
            if response==True:
                if self.save_path == "":
                    self.save_to_new_file()
                else:
                    self.save_to_file()
            elif response==False:
                pass
            else:
                return
        self.clear_canvas()
        self.update_save_state(0,"","new file")
        self.file_menu.entryconfig("Save DFG", state="disabled")
        self.output_area.delete(1.0, tk.END)

    def save_to_file(self):
        data = {
            "nodes": [
                {"label": node.label, "num": node.num, "x": node.x, "y": node.y}
                for node in self.nodes
            ],
            "edges": [
                {"start": edge.start_node.label, "end": edge.end_node.label, "dff_num": edge.dff_num}
                for edge in self.edges
            ]
        }
        file_path = self.save_path
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(data, file)
            self.update_save_state(1,file_path,self.save_name)
            messagebox.showinfo("Save", "Save successfully!")
        else:
            messagebox.showinfo("Save", "Save Error!")

    def save_to_new_file(self):
        data = {
            "nodes": [
                {"label": node.label, "num": node.num, "x": node.x, "y": node.y}
                for node in self.nodes
            ],
            "edges": [
                {"start": edge.start_node.label, "end": edge.end_node.label, "dff_num": edge.dff_num}
                for edge in self.edges
            ]
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Text files", "*.json"), ("All files", "*.*")]) 
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(data, file)
            self.update_save_state(1,file_path,file_path.split("/")[-1][:-5])
            self.file_menu.entryconfig("Save DFG", state="normal")
            messagebox.showinfo("Save", "Save successfully!")
        else:
            messagebox.showinfo("Save", "Save Error!")
            
    
    def load_from_file(self):
        if self.save == 0:
            response = messagebox.askyesnocancel("Load", "Do you want to save your DFG before loading file?")
            if response==True:
                if self.save_path == "":
                    self.save_to_new_file()
                else:
                    self.save_to_file()
            elif response==False:
                pass
            else:
                return
            
        
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
            # 清空当前画布和图表
            self.clear_canvas()
            # 重建节点和边
            if data["nodes"] != []:
                for node_data in data["nodes"]:
                    node = Node(self.canvas, node_data["x"], node_data["y"], node_data["label"], self, node_data["num"])
                    self.nodes.append(node)
                
                self.label_order = ord(self.nodes[-1].label)
                x, y = self.nodes[-1].x, self.nodes[-1].y
                if x<450:
                    x += 80
                else:
                    x = 80
                    y += 80
                self.last_node_position = (x, y)

            if data["edges"] != []:
                for edge_data in data["edges"]:
                    start_node = next(node for node in self.nodes if node.label == edge_data["start"])
                    end_node = next(node for node in self.nodes if node.label == edge_data["end"])
                    edge = Edge(self.canvas, start_node, end_node, self)
                    edge.dff_num = edge_data["dff_num"]
                    self.edges.append(edge)
                    # add D label
                    if edge.dff_num > 0:
                        edge.add_dff(add=0)
                        self.canvas.itemconfig(edge.dff_label, fill="black")
            
            
            self.file_menu.entryconfig("Save DFG", state="normal")
                
            self.update_edge_button_state()
            self.update_dff_button_state()
            self.update_graph_state()
            self.update_iteration_button_state()
            self.update_save_state(1,file_path,file_path.split("/")[-1][:-5])
            self.output_area.delete(1.0, tk.END)
            messagebox.showinfo("Load", "Load successfully!")
        else:
            messagebox.showinfo("Load", "Load Error!")
            
    def on_closing(self):
        if self.save == 0:
            response = messagebox.askyesnocancel("Quit", "Do you want to save your DFG before quitting?")
            if response == True:
                if self.save_path == "":
                    self.save_to_new_file()
                else:
                    self.save_to_file()
                
                self.root.destroy()
            elif response == False:
                self.root.destroy()
            else:
                pass
        else:
            self.root.destroy()
        


    # graph function
    
    def add_Graph(self):
        self.G.clear()
        self.reset_color()
        for node in self.nodes:
            self.G.add_node(node.label, value=int(node.num), rt=0)
        
        for edge in self.edges:
            self.G.add_edge(edge.start_node.label, edge.end_node.label, weight = edge.dff_num)

        self.update_iteration_button_state()
        self.output_area.delete(1.0, tk.END)
        self.display_output("Graph generated\n")
        self.display_output("Nodes in graph : " + str(self.G.nodes()) + "\nEdges in graph : " + str(self.G.edges()))

    def change_path_color(self, path, color):
        for i in path:
            node = self.get_node_by_label(i)
            self.change_color(node, color)
        
        for i in range(len(path)-1):
            edge = self.get_edge_by_nodes(self.get_node_by_label(path[i]), self.get_node_by_label(path[i+1]))
            self.change_edge_color(edge, color)

    def reset_color(self):
        for node in self.nodes:
            self.change_color(node, "black")
        
        for edge in self.edges:
            self.change_edge_color(edge, "black")

    
    def iteration(self):
        iter = iter_b(self.G)
        self.reset_color()
        if iter[1]!=[]:
            self.change_path_color(iter[1], "#0080FF")
            self.change_path_color([iter[1][-1],iter[1][0]], "#0080FF")
        self.output_area.delete(1.0, tk.END)
        self.display_output("Iteration bound : " + str(iter[0]) + "\nIteration path : " + p(iter[1]))

    def critical(self):
        cri = critical(self.G)
        self.reset_color()
        if cri[0]!=[]:
            self.change_path_color(cri[0], "#CE0000")
        self.output_area.delete(1.0, tk.END)
        self.display_output("Critical path value : " + str(cri[1]) + "\nCritical path : " + p(cri[0]))

    def clk_mini(self):
        self.output_area.delete(1.0, tk.END)
        ans = clk_minimize(self.G)
        if ans[0]!=0:
            self.display_output("minimun clk = "+str(ans[1])+"\n")
            #print(ans[1])
            for i in ans[2]:
                self.display_output(i+" ")
                #print(i)
        else:
            self.display_output("Graph can't be retiming or Graph has negitive loop")
