import tkinter as tk
import tkinter.messagebox
from utils import apis, markets, responses_path
from tkinter import ttk, filedialog


def ask_confirmation():
    result = tkinter.messagebox.askyesno("Confirmation", "Are you sure you would like to get this data?"
                                                         " This is an API call")

    return result


def load_file():
    path = filedialog.askopenfilename(initialdir=responses_path, filetypes=[('JSON files', "*.json")])

    return path


class GUI:
    def __init__(self):
        self.controller = None

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

        self.button1 = tk.Button(top_bar, text="Get data")
        self.button2 = tk.Button(top_bar, text="Clear list")
        self.button3 = tk.Button(top_bar, text="Set stake")
        self.button4 = tk.Button(top_bar, text="Load from JSON")

        self.api_dropdown.grid(row=0, column=0)
        self.market_dropdown.grid(row=0, column=1)
        self.button1.grid(row=0, column=2)
        self.button2.grid(row=0, column=3)
        self.button3.grid(row=0, column=4)
        self.button4.grid(row=0, column=5)

        self.scrollable_info_canvas = tk.Canvas(self.window)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.scrollable_info_canvas.yview)
        self.scrollable_info_canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_info_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scroll_frame = tk.Frame(self.scrollable_info_canvas)
        self.items = []

    def set_controller(self, controller):
        self.controller = controller

        self.button1.configure(command=controller.get_data_and_update_info)
        self.button2.configure(command=controller.clear_list)
        self.button4.configure(command=controller.load_json)

    def start_gui(self):
        self.window.mainloop()

    def update_scrollable_info(self, new_info_list):
        self.scroll_frame.destroy()
        self.scroll_frame = tk.Frame(self.scrollable_info_canvas)

        self.scroll_frame.pack()

        self.items = new_info_list

        self.scroll_frame.columnconfigure(len(self.items), weight=1)
        self.scroll_frame.rowconfigure(len(self.items), weight=1)

        for i, item in enumerate(self.items):
            split_by_dollar_sign = item.split("$")
            profit = float(split_by_dollar_sign[len(split_by_dollar_sign) - 1])
            color = "black"
            if profit > 0.0:
                color = "green"
            elif profit < 0.0:
                color = "red"
            label = tk.Label(self.scroll_frame, text=item, foreground=color,
                             relief="groove", width=109, height=2, wraplength=720)
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

    def get_api_market(self):
        return self.api_selection.get(), self.market_dropdown.get()


if __name__ == '__main__':
    gui = GUI()
    gui.start_gui()
