"""
=======================
Simulation Manager
=======================
The simulation manager allows the user to locate, interact with, and take notes about simulations.
"""
import json
import logging
import os
import pathlib as pt
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from PyHPC.PyHPC_System.simulation_management import SimulationLog
from PyHPC.PyHPC_Utils.standard_utils import getFromDict

# -------------------------------------------------------------------------------------------------------------------- #
# Setup ============================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
modlog = logging.getLogger(__name__)

LARGEFONT = ("Verdana", 35)


def find_headers(dictionary, loc=None):
    """
    Finds the headers of the ``dictionary`` object recursively.
    Parameters
    ----------
    dictionary : dict
        The dictionary to search.

    Returns
    -------
    list of tuple
        The headers ``[header,location]``.
    """
    out = []
    if not loc:
        loc = []
    for k, v in dictionary.items():
        if isinstance(v, dict) and len(v):
            out += find_headers(v, loc=loc + [k])
        else:
            pass

        if isinstance(v, str):
            out.append((loc + [k], k))

    return out


#  Pulling header information
# ----------------------------------------------------------------------------------------------------------------- #
with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "struct", "simlog_struct.json"),
          "r") as file:
    _structure_data = json.load(file)

# generating the headers #
headers = {}
for level, obj in zip([1, 2, 3], ["SimulationLog", "InitCon", "SimRec"]):
    headers[level] = find_headers(_structure_data[obj]["format"])

print(headers)


# -------------------------------------------------------------------------------------------------------------------- #
# Building the tkinter root ========================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class Root(tk.Tk):
    """
    Defines the root class / controller of the gui system.
    """

    def __init__(self, *args, **kwargs):
        #  Assigning attributes
        # ----------------------------------------------------------------------------------------------------------------- #

        #  Initializing the basis
        # ----------------------------------------------------------------------------------------------------------------- #
        super().__init__(*args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #  Additional attributes
        # ----------------------------------------------------------------------------------------------------------------- #
        self.simpath = tk.StringVar(container)
        self.simpath.set("None")
        self.simulation_log = SimulationLog()
        self._page_raised = None
        self.headers = headers.copy()
        #  Adding pages
        # ----------------------------------------------------------------------------------------------------------------- #
        self.pages = {
            "front" : FrontPage(container, self),
            "middle": InitConPage(container, self),
            "back"  : SimPage(container, self)
        }

        for value in self.pages.values():
            value.grid(row=0, column=0, sticky="nsew")

        #  Managing the menu
        # ----------------------------------------------------------------------------------------------------------------- #
        # - Creating the menu bar -#
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # - Creating the file menu -#
        self.filemenu = tk.Menu(self.menubar)

        self.filemenu.add_command(
            label='Exit',
            command=self.destroy,
        )
        self.filemenu.add_command(
            label="Open",
            command=self.load_simlog
        )

        self.menubar.add_cascade(
            label="File",
            menu=self.filemenu,
            underline=0
        )

        # - Creating the view menu - #
        self.viewmenu = tk.Menu(self.menubar)

        self.viewmenu.add_command(
            label="Configure Columns",
            command=self.config_columns
        )

        self.menubar.add_cascade(
            label="View",
            menu=self.viewmenu,
            underline=0
        )
        #
        # ----------------------------------------------------------------------------------------------------------------- #
        self.raise_page("front")

    def raise_page(self, cont):
        frame = self.pages[cont]
        frame.tkraise()
        self._page_raised = frame

    def load_simlog(self):
        """
        Loads a simulation log selected by the user into the core structure of the gui.
        Returns
        -------
        None
        """
        #  Fetching file
        # ----------------------------------------------------------------------------------------------------------------- #
        path = askopenfilename()

        if os.path.exists(path) and pt.Path(path).suffix == ".json":
            try:
                self.simpath.set(path)
                self.simulation_log = SimulationLog(path=self.simpath.get())
            except json.JSONDecodeError:
                modlog.exception("Failed to open the simulation log at %s." % self.simpath.get())
                self.simpath.set("None")
        else:
            pass

    def config_columns(self):
        config_window = SubRoot(self, enabled_headers=self.headers)
        config_window.grab_set()


class SubRoot(tk.Toplevel):
    def __init__(self,controller,enabled_headers=None, **kwargs):
        #  Assigning attributes
        # ----------------------------------------------------------------------------------------------------------------- #

        #  Initializing the basis
        # ----------------------------------------------------------------------------------------------------------------- #
        super().__init__(controller, **kwargs)
        self.controller = controller
        self.headers = enabled_headers
        self.enabled_headers = {i: [tk.IntVar(value=1) if v in self.headers[i] else tk.IntVar(value=0) for v in headers[i] ] for i in headers}
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #  Adding pages
        # ----------------------------------------------------------------------------------------------------------------- #
        self.pages = {
            "headers": HeaderConfigPage(container, self),
        }

        for value in self.pages.values():
            value.grid(row=0, column=0, sticky="nsew")
        #
        # ----------------------------------------------------------------------------------------------------------------- #
        self.raise_page("headers")
        self.geometry("300x400")

    def raise_page(self, cont):
        frame = self.pages[cont]
        frame.tkraise()

    def destroy(self):
        self.controller.headers = {i: [header for k,header in enumerate(headers[i]) if self.enabled_headers[i][k].get() == 1] for i in headers}
        self.controller._page_raised.rebuild_database()
        super().destroy()

class HeaderConfigPage(tk.Frame):
    def __init__(self, parent, controller):
        #  Attributes
        # ----------------------------------------------------------------------------------------------------------------- #
        self.parent = parent
        self.controller = controller
        #  Loading in the frame
        # ----------------------------------------------------------------------------------------------------------------- #
        tk.Frame.__init__(self, parent)

        #  Managing the grid
        # ----------------------------------------------------------------------------------------------------------------- #

        # - Managing the base grid -#
        for col_id, weight in zip([0, 1, 2, 3, 4, ], [1, 5, 5, 5, 1]):
            self.columnconfigure(col_id, weight=weight)

        for row_id, weight in zip([0, 1], [1, 10]):
            self.rowconfigure(row_id, weight=weight)

        # - adding frames -#
        title_frame = tk.Frame(self, bg="#546fd1")
        title_frame.grid(row=0, column=0, columnspan=5, rowspan=1, sticky="nesw")
        title_label = ttk.Label(title_frame, text="Configure Level Headers", font=("Cascadia Code", 18),
                                background=title_frame["bg"])
        title_label.place(relx=0.05, rely=0.1)
        # - options frame -#
        left_frame = tk.Frame(self)
        left_frame.grid(row=1, column=1, rowspan=1, sticky="nesw")

        # - bottom frame -#
        center_frame = tk.Frame(self)
        center_frame.grid(row=1, column=2, columnspan=1, sticky="nesw")

        # - RHS frame -#
        right_frame = tk.Frame(self)
        right_frame.grid(row=1, column=3, rowspan=1, sticky="nesw")

        self.chx_box = {}
        for level,frame in zip([1,2,3],[left_frame,center_frame,right_frame]):
            self.chx_box[level] = []
            for j,header in enumerate(headers[level]):
                self.chx_box[level].append(tk.Checkbutton(frame, text=header[1], variable=controller.enabled_headers[level][j]))
                self.chx_box[level][j].grid(row=j,column=0)

class FrontPage(tk.Frame):
    def __init__(self, parent, controller):
        #  Attributes
        # ----------------------------------------------------------------------------------------------------------------- #
        self.parent = parent
        self.controller = controller
        #  Loading in the frame
        # ----------------------------------------------------------------------------------------------------------------- #
        tk.Frame.__init__(self, parent)

        #  Managing the grid
        # ----------------------------------------------------------------------------------------------------------------- #

        # - Managing the base grid -#
        for col_id, weight in zip([0, 1, 2], [1, 3, 2]):
            self.columnconfigure(col_id, weight=weight)

        for row_id, weight in zip([0, 1, 2, 3], [2, 4, 4, 1]):
            self.rowconfigure(row_id, weight=weight)

        # - adding frames -#
        title_frame = tk.Frame(self, bg="#546fd1")
        title_frame.grid(row=0, column=0, columnspan=3, rowspan=1, sticky="nesw")

        # - options frame -#
        options_frame = tk.Frame(self, bg="#34937e")
        options_frame.grid(row=1, column=0, rowspan=2, sticky="nesw")

        # - bottom frame -#
        bottom_frame = tk.Frame(self, bg="#666f77")
        bottom_frame.grid(row=3, column=0, columnspan=3, sticky="nesw")

        # - RHS frame -#
        right_frame = tk.Frame(self, bg="#4b8b4a")
        right_frame.grid(row=1, column=2, rowspan=2, sticky="nesw")


        #  Managing text elements
        # ----------------------------------------------------------------------------------------------------------------- #
        # - Title - #
        title_label = ttk.Label(title_frame, text="PyHPC Simulation Manager", font=("Cascadia Code", 30),
                                background=title_frame["bg"])
        title_label.place(relx=0.05, rely=0.1)

        # - options - #
        options_label = tk.Label(options_frame, text="Options", font=("Helvetica", 15), background=options_frame["bg"])
        options_label.place(relx=0.5, rely=0.1, anchor="center")
        #: label of the simulation log directory
        simlog_label = ttk.Label(bottom_frame, textvariable=self.controller.simpath, background=bottom_frame["bg"])
        simlog_label.grid(row=0, column=0, sticky="ew", columnspan=3)

        #  Database
        # ----------------------------------------------------------------------------------------------------------------- #
        # - Center Frame -#
        self.center_frame = tk.Frame(self, bg="#FFFFFF")
        self.center_frame.grid(row=1, column=1, rowspan=2, sticky="nsew")
        self.center_frame.rowconfigure(0, weight=99)
        self.center_frame.rowconfigure(0, weight=1)
        self.center_frame.columnconfigure(0, weight=99)
        self.center_frame.columnconfigure(0, weight=1)
        self.db = MultiColumnListbox(self.center_frame, self.controller.simulation_log, 1, enabled_headers=controller.headers[1])

        # Configuring the action_log viewer #
        #-----------------------------------#

        """
        #: label of the options area.
        options_label = ttk.Label(self, text="Options", background="#62d9c9")

        options_label.grid(row=2, column=0, padx=50, pady=0, sticky="nwes")

        #: buttons for the options
        button1 = tk.Button(self, text="Page 1",
                             command=lambda: controller.raise_page("middle"),bg="#62d9c9")
        button1.grid(row=3, column=0, padx=10, pady=10,sticky="nwes")

        button2 = tk.Button(self, text="Page 2",
                             command=lambda: controller.raise_page("back"),bg="#62d9c9")
        button2.grid(row=4, column=0, padx=10, pady=10,sticky="nwes")
        """
    def rebuild_database(self):
        self.db = MultiColumnListbox(self.center_frame, self.controller.simulation_log, 1,
                                     enabled_headers=self.controller.headers[1])

# second window frame FrontPage
class InitConPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Page 1", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(self, text="StartPage",
                             command=lambda: controller.raise_page(FrontPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button2 = ttk.Button(self, text="Page 2",
                             command=lambda: controller.raise_page("middle"))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)


# third window frame "middle"
class SimPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Page 2", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(self, text="Page 1",
                             command=lambda: controller.raise_page(FrontPage))

        # putting the button in its place by
        # using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        # button to show frame 3 with text
        # layout3
        button2 = ttk.Button(self, text="Startpage",
                             command=lambda: controller.raise_page(FrontPage))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)


class MultiColumnListbox(object):
    """
    MultiColumnListbox
    """

    def __init__(self, container, log, level, enabled_headers=None):
        """
        Initializes a ``MultiColumnListbox`` object with the given simulation log ``log``, a specified level and headers.
        Parameters
        ----------
        container
            The container corresponding to this object.
        log : SimulationLog
            The simulation log object to retrieve data from.
        level : int
            Level indicating the location of the user in the database.
        enabled_headers : list of str
            A list of the enabled headers for that object.
        """
        #  Managing input data
        # ----------------------------------------------------------------------------------------------------------------- #
        self.container = container  # Building the self.container reference.

        print(headers)
        if not enabled_headers:  # Managing the header construction
            self.headers, self._headers_location = [header[1] for header in headers[level]], [header[0] for header in
                                                                                              headers[level]]
        else:
            self.headers, self._headers_location = [header[1] for header in enabled_headers], [header[0] for header in
                                                                                               enabled_headers]

        self.headers = ["Name"] + self.headers
        print(self.headers)
        #  Managing the data
        # ----------------------------------------------------------------------------------------------------------------- #
        self.data = log.raw

        self.tree = None
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        """
        Sets up the widget
        Returns
        -------

        """
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=self.headers, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.container)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.container)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.container)

    def _build_tree(self):
        for col in self.headers:
            self.tree.heading(col, text=col,
                              command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col))

        for item, value in self.data.items():
            self.tree.insert('', 'end',
                             values=[pt.Path(item).name, *[getFromDict(value, h) for h in self._headers_location]])
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate([getFromDict(value, h) for h in self._headers_location], 1):
                col_w = tkFont.Font().measure(val)
                print(self.headers[ix])
                if self.tree.column(self.headers[ix], width=None) < col_w:
                    self.tree.column(self.headers[ix], width=col_w)


# -------------------------------------------------------------------------------------------------------------------- #
#  Functions ========================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    # data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
                                                     int(not descending)))


if __name__ == '__main__':
    app = Root()
    app.mainloop()
