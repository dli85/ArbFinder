import tkinter as tk
from utils import apis, markets
from tkinter import ttk


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Arbitrage finder")
        self.window.geometry("800x600")
        self.window.resizable(width=False, height=False)

        top_bar = tk.Frame(self.window)

        top_bar.columnconfigure(4, weight=1)
        top_bar.pack()

        self.api_selection = tk.StringVar(self.window)
        self.api_selection.set(apis[0])

        self.market_selection = tk.StringVar(self.window)
        self.market_selection.set(markets.get(apis[0])[0])

        self.api_dropdown = tk.OptionMenu(top_bar, self.api_selection, *apis,
                                          command=self.update_dropdowns)

        self.market_dropdown = ttk.Combobox(top_bar, values=markets.get(apis[0]), state='readonly')
        self.market_dropdown.configure(width=35)
        self.market_dropdown.current(0)

        button1 = tk.Button(top_bar, text="Get data", command=lambda: self.update_scroll_info(["item 1", "item 2"]))
        button2 = tk.Button(top_bar, text="Button 2")
        button3 = tk.Button(top_bar, text="Button 3")
        button4 = tk.Button(top_bar, text="Button 4")

        self.api_dropdown.grid(row=0, column=0)
        self.market_dropdown.grid(row=0, column=1)
        button1.grid(row=0, column=2)
        button2.grid(row=0, column=3)
        button3.grid(row=0, column=4)
        button4.grid(row=0, column=5)

        self.scrollable_info_canvas = tk.Canvas(self.window)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.scrollable_info_canvas.yview)
        self.scrollable_info_canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_info_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scroll_frame = tk.Frame(self.scrollable_info_canvas)
        self.items = []

    def start_gui(self):
        self.window.mainloop()

    def update_scroll_info(self, new_info_list, replace=False):
        self.scroll_frame.destroy()
        self.scroll_frame = tk.Frame(self.scrollable_info_canvas)

        self.scroll_frame.pack()

        if replace:
            self.items = new_info_list
        else:
            self.items.extend(new_info_list)

        self.scroll_frame.columnconfigure(len(self.items), weight=1)
        self.scroll_frame.rowconfigure(len(self.items), weight=1)

        for i, item in enumerate(self.items):
            print(self.window.winfo_width())
            label = tk.Label(self.scroll_frame, text=item, relief="groove", width=109, height=2, wraplength=720)
            label.grid(row=i, column=0, stick="nsew")

        self.scrollable_info_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scrollable_info_canvas.bind_all("<MouseWheel>",
                                             lambda event: self.scrollable_info_canvas.yview_scroll
                                             (int(-1 * (event.delta / 120)), "units"))

        self.scroll_frame.update_idletasks()
        self.scrollable_info_canvas.configure(scrollregion=self.scrollable_info_canvas.bbox("all"))

    def update_dropdowns(self, event=None):
        selected_api = self.api_selection.get()

        self.market_dropdown.configure(values=markets.get(selected_api))
        self.market_dropdown.current(0)

    def get_market_selection(self):
        return self.market_dropdown.get()


if __name__ == '__main__':
    gui = GUI()
    gui.start_gui()
