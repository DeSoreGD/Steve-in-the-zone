"""Windowed setup entry. Component sources are selected explicitly by the owner."""
from pathlib import Path
import argparse
import json
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog,ttk
from prepare_demo import prepare
from ui_text import translator


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--request',type=Path);parser.add_argument('--report',type=Path)
    options=parser.parse_args()
    payload=(Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent.parent/'runtime/portable-dist')/'payload'
    if options.request:
        try:
            result=prepare(payload=payload,**json.loads(options.request.read_text(encoding='utf-8')))
            report={'success':True,'config':str(result)}
        except Exception as error:report={'success':False,'error':str(error)}
        if options.report:options.report.write_text(json.dumps(report),encoding='utf-8')
        return 0 if report['success'] else 1
    window=tk.Tk();window.title('Steve in the Zone — Setup');window.geometry('780x530');window.resizable(False,False)
    window.configure(bg='#20211d');window.iconbitmap(str(payload/'app/_internal/assets/zone-mark.ico'))
    locale=tk.StringVar(value='ru');fields={};captions=[];messages=queue.Queue();worker=None
    body=tk.Frame(window,bg='#20211d');body.pack(fill='both',expand=True,padx=24,pady=20)
    title=tk.Label(body,text='',bg='#20211d',fg='#eee9d7',font=('Segoe UI',19,'bold'));title.grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,15))
    selector=ttk.Combobox(body,textvariable=locale,values=('ru','en'),state='readonly',width=4);selector.grid(row=0,column=3)
    def browse(key,file=False):
        value=filedialog.askopenfilename(parent=window,filetypes=[('Java','javaw.exe java.exe')]) if file else filedialog.askdirectory(parent=window)
        if value:fields[key].set(value)
    for row,key,caption,is_file in [(1,'game_source','Папка S.T.A.L.K.E.R. SoC 1.0006',False),(2,'minecraft_source','Папка установленного Minecraft',False),(3,'java','Java — автоматически, если оставить пустым',True),(4,'destination','Новая папка игры',False)]:
        label=tk.Label(body,text='',bg='#20211d',fg='#b2b49f',font=('Segoe UI',10));label.grid(row=row*2-1,column=0,columnspan=4,sticky='w',pady=(5,2));captions.append((label,caption))
        fields[key]=tk.StringVar();tk.Entry(body,textvariable=fields[key],bg='#2b2d26',fg='#eee9d7',insertbackground='#eee9d7',relief='flat',font=('Segoe UI',10),width=75).grid(row=row*2,column=0,columnspan=3,sticky='ew',ipady=5)
        ttk.Button(body,text='…',command=lambda key=key,file=is_file:browse(key,file)).grid(row=row*2,column=3,padx=(8,0))
    fields['username']=tk.StringVar(value='Steve')
    name=tk.Label(body,text='',bg='#20211d',fg='#b2b49f');name.grid(row=9,column=0,sticky='w',pady=12)
    tk.Entry(body,textvariable=fields['username'],width=18).grid(row=9,column=1,sticky='w')
    note=tk.Label(body,text='',bg='#20211d',fg='#b2b49f',justify='left',wraplength=730);note.grid(row=10,column=0,columnspan=4,sticky='w',pady=8)
    status=tk.StringVar();tk.Label(body,textvariable=status,bg='#20211d',fg='#d7c28d',wraplength=730,justify='left').grid(row=12,column=0,columnspan=4,sticky='w',pady=12)
    def start():
        nonlocal worker
        if worker and worker.is_alive():return
        values={key:value.get().strip() for key,value in fields.items()}
        if any(not value for key,value in values.items() if key!='java'):status.set('Choose the component folders first.');return
        values['destination']=str(Path(values['destination'])/'Steve in the Zone')
        language=locale.get()
        def run():
            try:
                result=prepare(payload=payload,language=language,notify=lambda text:messages.put(('status',text)),**values)
                messages.put(('done',str(result)))
            except Exception as error:messages.put(('error',str(error)))
        launch.configure(state='disabled');selector.configure(state='disabled')
        worker=threading.Thread(target=run,daemon=False);worker.start()
    launch=tk.Button(body,text='',command=start,bg='#d7c28d',fg='#20211d',relief='flat',font=('Segoe UI',12,'bold'),pady=10)
    launch.grid(row=11,column=0,columnspan=4,sticky='ew',pady=(8,0))
    def translate(_=None):
        t=translator(locale.get());title.configure(text=t('Установка'));launch.configure(text=t('Установить'));name.configure(text=t('Имя игрока'))
        for label,text in captions:label.configure(text=t(text))
        note.configure(text=t('Локальная одиночная игра. Аккаунты и сохранения не импортируются. Недостающие компоненты Minecraft загружаются с официальных серверов.'))
    selector.bind('<<ComboboxSelected>>',translate);translate()
    def update():
        while not messages.empty():
            kind,text=messages.get_nowait()
            if kind=='done':status.set(translator(locale.get())('Установка завершена. Открой app/SteveInTheZone.exe в папке игры.'))
            else:status.set(translator(locale.get())(text))
            if kind in ('done','error'):launch.configure(state='normal');selector.configure(state='readonly')
        window.after(100,update)
    def close():
        if worker and worker.is_alive():status.set(translator(locale.get())('Дождись завершения подготовки.'));return
        window.destroy()
    window.protocol('WM_DELETE_WINDOW',close);update();window.mainloop();return 0


if __name__=='__main__':raise SystemExit(main())
