"""Compact desktop launcher. Game languages and transport are independent of UI locale."""
from pathlib import Path
import ctypes
import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from ui_text import translator

BG="#20211d";FIELD="#2b2d26";LINE="#43463a";TEXT="#eee9d7";MUTED="#b2b49f";ACCENT="#d7c28d"
ICON=Path(__file__).parent/"assets/zone-mark.ico"

def desktop(config,supervise,validate):
    while True:
        result=window_once(config,supervise,validate)
        if result!="reload":return result

def window_once(config,supervise,validate):
    t=translator(config["settings"]["language"])
    # Separate identity/icon from the Python interpreter in Windows taskbar.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SteveInTheZone")
    window=tk.Tk();window.title(t("Стив в Зоне"));window.geometry("760x470")
    window.configure(bg=BG);window.resizable(False,False)
    if ICON.is_file():window.iconbitmap(str(ICON))
    window.update_idletasks()
    hwnd=ctypes.windll.user32.GetParent(window.winfo_id())
    dwm=ctypes.windll.dwmapi
    # Keep standard Windows drag/minimize/close behavior, with matching dark chrome.
    for attribute,value in [(20,1),(35,0x1d2120),(36,0xd7e9ee)]:
        setting=ctypes.c_int(value)
        dwm.DwmSetWindowAttribute(ctypes.c_void_p(hwnd),attribute,ctypes.byref(setting),4)
    style=ttk.Style(window);style.theme_use("clam")
    style.configure("Zone.TCombobox",fieldbackground=FIELD,background=LINE,foreground=TEXT,arrowcolor=ACCENT,bordercolor=LINE,padding=5)
    style.map("Zone.TCombobox",fieldbackground=[("readonly",FIELD)],foreground=[("readonly",TEXT)])
    style.configure("Zone.Horizontal.TScale",background=BG,troughcolor=LINE)
    window.option_add("*TCombobox*Listbox.background",FIELD);window.option_add("*TCombobox*Listbox.foreground",TEXT)
    messages=queue.Queue();cancel=threading.Event();worker=None;closing=False;reload_language=False
    def label(parent,text,size=11,color=TEXT,bold=False,**kw):
        return tk.Label(parent,text=t(text),bg=BG,fg=color,font=("Segoe UI",size,"bold" if bold else "normal"),**kw)
    def button(parent,text,command,primary=False):
        return tk.Button(parent,text=t(text),command=command,bg=ACCENT if primary else FIELD,fg=BG if primary else TEXT,
            activebackground="#e6d4a8" if primary else LINE,activeforeground=BG if primary else TEXT,
            disabledforeground=MUTED,relief="flat",bd=0,cursor="hand2",font=("Segoe UI",12,"bold" if primary else "normal"),padx=16,pady=11)
    def persist(values):
        values=validate(values);target=Path(config["settingsPath"]);temporary=target.with_suffix(".tmp")
        temporary.write_text(json.dumps(values,indent=2),encoding="utf-8");temporary.replace(target);config["settings"]=values
    root=tk.Frame(window,bg=BG);root.pack(fill="both",expand=True,padx=28,pady=24)
    head=tk.Frame(root,bg=BG);head.pack(fill="x")
    mark=tk.Canvas(head,width=42,height=44,bg=BG,highlightthickness=0);mark.pack(side="left",padx=(0,12))
    mark.create_polygon(3,14,20,5,37,14,20,23,fill=TEXT,outline=BG)
    mark.create_polygon(3,14,20,23,20,42,3,33,fill="#a08d5b",outline=BG)
    mark.create_polygon(20,23,37,14,37,33,20,42,fill="#6b7256",outline=BG)
    titles=tk.Frame(head,bg=BG);titles.pack(side="left")
    label(titles,"Стив в Зоне",size=22,bold=True).pack(anchor="w")
    label(titles,"Minecraft × S.T.A.L.K.E.R.  /  Кампания",size=9,color=MUTED).pack(anchor="w",pady=(1,0))
    language=tk.StringVar(value="EN" if config["settings"]["language"]=="en" else "RU")
    language_control=ttk.Combobox(head,textvariable=language,values=("RU","EN"),state="readonly",width=3,style="Zone.TCombobox")
    language_control.pack(side="right",anchor="n",pady=6)
    def selected_language(_):
        nonlocal reload_language
        if worker and worker.is_alive():return
        persist({**config["settings"],"language":language.get().lower()});reload_language=True;window.destroy()
    language_control.bind("<<ComboboxSelected>>",selected_language)
    tk.Frame(root,bg=LINE,height=1).pack(fill="x",pady=(22,22))
    main=tk.Frame(root,bg=BG);prefs=tk.Frame(root,bg=BG);main.pack(fill="x")
    left=tk.Frame(main,bg=BG,width=428);left.pack(side="left",fill="x",expand=True)
    label(left,"Режим игры",size=10,color=MUTED).pack(anchor="w")
    mode=tk.StringVar(value=config["settings"]["gameMode"]);modes=tk.Frame(left,bg=BG);modes.pack(fill="x",pady=(8,12))
    radios=[]
    for title,value in [("Творческий","creative"),("Выживание","survival")]:
        radio=tk.Radiobutton(modes,text=t(title),variable=mode,value=value,command=lambda:persist({**config["settings"],"gameMode":mode.get()}),
            indicatoron=False,bg=FIELD,fg=TEXT,selectcolor=LINE,activebackground=LINE,activeforeground=TEXT,
            relief="flat",bd=0,font=("Segoe UI",11),padx=14,pady=10,cursor="hand2")
        radio.pack(side="left",fill="x",expand=True,padx=(0,6));radios.append(radio)
    label(left,"F6 — сменить режим во время игры",size=9,color=MUTED).pack(anchor="w",pady=(0,20))
    def run():
        try:
            completed=False
            def report(value):
                nonlocal completed
                if value=="Кампания завершена.":completed=True
                messages.put(("status",value))
            supervise(config,cancel,report)
            messages.put(("done","Кампания завершена. Мир сохранён." if completed else "Игра закрыта. Мир сохранён."))
        except Exception as error:messages.put(("error",str(error)))
    def play():
        nonlocal worker
        if worker and worker.is_alive():cancel.set();play_button.configure(state="disabled");return
        cancel.clear();play_button.configure(text=t("Закрыть игру"))
        language_control.configure(state="disabled");settings_button.configure(state="disabled")
        for radio in radios:radio.configure(state="disabled")
        worker=threading.Thread(target=run,daemon=False);worker.start()
    play_button=button(left,"Запустить игру",play,True);play_button.pack(fill="x",padx=(0,6))
    def preferences():
        if worker and worker.is_alive():return
        main.pack_forget();prefs.pack(fill="x")
    settings_button=button(left,"Настройки",preferences);settings_button.pack(fill="x",padx=(0,6),pady=(8,0))
    help=tk.Frame(main,bg=BG,width=190);help.pack(side="right",fill="y",padx=(32,0))
    label(help,"Клавиши",size=15,bold=True).pack(anchor="w",pady=(0,12))
    for key,title in [("E","Инвентарь"),("F5","Вид от третьего лица"),("F7","Быстрое сохранение"),("F8","Быстрая загрузка"),("F9","Проход сквозь препятствия"),("G","Взаимодействие"),("Esc","Меню и графика")]:
        row=tk.Frame(help,bg=BG);row.pack(fill="x",pady=4)
        tk.Label(row,text=key,bg=FIELD,fg=ACCENT,font=("Consolas",10),width=4,pady=3).pack(side="left",padx=(0,10))
        label(row,title,size=9,color=MUTED).pack(side="left")
    label(help,"Отдельный мир.\nПрогресс сохраняется.",size=9,color=MUTED,justify="left").pack(anchor="w",pady=(18,0))
    label(prefs,"Настройки",size=17,bold=True).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,10))
    memory=tk.StringVar(value=str(config["settings"]["memoryMb"]//1024));fps=tk.StringVar(value=str(config["settings"]["maxFps"]))
    volume=tk.DoubleVar(value=config["settings"]["soundVolume"]*100)
    for row,title,variable,values in [(1,"Память Minecraft, ГБ",memory,("2","4","6")),(2,"Частота Minecraft",fps,("30","60","90"))]:
        label(prefs,title,size=10).grid(row=row,column=0,sticky="w",pady=6)
        ttk.Combobox(prefs,textvariable=variable,values=values,state="readonly",width=8,style="Zone.TCombobox").grid(row=row,column=1,sticky="e")
    label(prefs,"Звуки Minecraft",size=10).grid(row=3,column=0,sticky="w",pady=6)
    ttk.Scale(prefs,variable=volume,from_=0,to=100,style="Zone.Horizontal.TScale").grid(row=3,column=1,sticky="ew")
    prefs.columnconfigure(1,weight=1)
    label(prefs,"Графика «Сталкера»: Esc → Настройки.",size=9,color=MUTED).grid(row=4,column=0,columnspan=2,sticky="w",pady=10)
    def save():
        persist({**config["settings"],"memoryMb":int(memory.get())*1024,"maxFps":int(fps.get()),"soundVolume":round(volume.get()/100,2)})
        prefs.pack_forget();main.pack(fill="x");status.set(t("Настройки сохранены. Применятся при запуске."))
    button(prefs,"Готово",save,True).grid(row=5,column=0,columnspan=2,sticky="ew")
    def reset():
        if worker and worker.is_alive():return
        if not messagebox.askyesno(t('Новый мир'),t('Начать заново? Обе части мира будут сохранены в резервную копию.'),parent=window):return
        try:
            from reset_world import reset_demo
            reset_demo(config)
            status.set(t('Создан новый мир. Предыдущий сохранён в папке backups.'))
        except Exception as error:messagebox.showerror(t('Новый мир'),str(error),parent=window)
    if config.get('createNativeIfMissing'):
        button(prefs,'Новый мир',reset).grid(row=6,column=0,columnspan=2,sticky='ew',pady=(8,0))
    status=tk.StringVar(value=t("Готово к запуску."))
    footer=tk.Frame(root,bg=BG);footer.pack(side="bottom",fill="x",pady=(16,0))
    tk.Frame(footer,bg=LINE,height=1).pack(fill="x",pady=(0,14))
    tk.Label(footer,textvariable=status,bg=BG,fg=ACCENT,font=("Segoe UI",10),anchor="w",justify="left",wraplength=690).pack(fill="x")
    def close():
        nonlocal closing
        if worker and worker.is_alive():closing=True;cancel.set();play_button.configure(state="disabled")
        else:window.destroy()
    def update():
        while not messages.empty():
            kind,value=messages.get_nowait();status.set(t(value))
            if kind in ("done","error"):
                if closing:window.destroy();return
                play_button.configure(text=t("Запустить игру"),state="normal");language_control.configure(state="readonly");settings_button.configure(state="normal")
                for radio in radios:radio.configure(state="normal")
        window.after(100,update)
    window.protocol("WM_DELETE_WINDOW",close);update();window.mainloop();return "reload" if reload_language else 0
