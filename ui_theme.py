"""Project-owned Tk surfaces. This module also works before pip packages are installed."""
from tkinter import ttk
from tkinter import font as tkfont

PAPER = '#ffffff'
CANVAS = '#f5f6f7'
INK = '#202328'
MUTED = '#555d67'
LINE = '#dadde1'
EDGE = '#a2a8b1'
BLUE = '#2454cf'
PRESS = '#173e9b'
TINT = '#eaf0ff'
LIME = '#bfde3c'


def apply(root):
    """Set application-owned controls to light, independent of the OS theme."""
    style = ttk.Style(root)
    style.theme_use('clam')
    root.configure(background=CANVAS)
    # Tk-created dialogs inherit these defaults; OS-native panels keep their native chrome.
    for key, value in [('*background', PAPER), ('*foreground', INK), ('*selectBackground', BLUE),
                       ('*selectForeground', PAPER), ('*activeBackground', TINT), ('*activeForeground', INK)]:
        root.option_add(key, value)
    family = tkfont.nametofont('TkDefaultFont', root=root).actual('family')
    style.configure('.', background=PAPER, foreground=INK, font=(family, 10),
                    bordercolor=LINE, lightcolor=PAPER, darkcolor=PAPER, focuscolor=BLUE)
    style.configure('TFrame', background=PAPER)
    style.configure('TLabel', background=PAPER, foreground=INK)
    style.configure('TButton', background=PAPER, foreground=INK, padding=(10, 6),
                    anchor='w', relief='flat', borderwidth=1, focusthickness=1)
    style.map('TButton', background=[('disabled', CANVAS), ('pressed', TINT), ('active', CANVAS)],
              foreground=[('disabled', MUTED)], bordercolor=[('focus', BLUE), ('active', EDGE)])
    style.configure('Primary.TButton', background=BLUE, foreground=PAPER, bordercolor=BLUE,
                    lightcolor=BLUE, darkcolor=BLUE, focuscolor=PAPER, font=(family, 10, 'bold'))
    style.map('Primary.TButton', background=[('disabled', CANVAS), ('pressed', PRESS), ('active', PRESS)],
              foreground=[('disabled', MUTED), ('!disabled', PAPER)],
              bordercolor=[('focus', INK), ('!disabled', BLUE)],
              lightcolor=[('disabled', CANVAS), ('!disabled', BLUE)], darkcolor=[('disabled', CANVAS), ('!disabled', BLUE)])
    style.configure('TCombobox', padding=(5, 4), background=PAPER, fieldbackground=PAPER,
                    foreground=INK, bordercolor=EDGE, arrowcolor=MUTED, arrowsize=13)
    style.map('TCombobox', fieldbackground=[('readonly', PAPER)], foreground=[('readonly', INK)],
              background=[('readonly', PAPER)], selectbackground=[('readonly', PAPER)],
              selectforeground=[('readonly', INK)], bordercolor=[('focus', BLUE), ('active', BLUE)])
    style.configure('Horizontal.TProgressbar', background=BLUE, troughcolor=CANVAS,
                    bordercolor=LINE, lightcolor=BLUE, darkcolor=BLUE, thickness=5)
    for key, value in [('background', PAPER), ('foreground', INK), ('selectBackground', BLUE),
                       ('selectForeground', PAPER)]:
        root.option_add('*TCombobox*Listbox.' + key, value)
    return family
