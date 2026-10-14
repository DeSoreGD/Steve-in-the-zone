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
from desktop_shortcut import create_shortcut
from update_installation import update_installation


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--request',type=Path);parser.add_argument('--report',type=Path)
    options=parser.parse_args()
    payload=(Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent.parent/'runtime/portable-dist')/'payload'
    if options.request:
        try:
            request=json.loads(options.request.read_text(encoding='utf-8'))
            result=update_installation(destination=request['destination'],payload=payload) if request.pop('update',False) else prepare(payload=payload,**request)
            report={'success':True,'config':str(result)}
        except Exception as error:report={'success':False,'error':str(error)}
        if options.report:options.report.write_text(json.dumps(report),encoding='utf-8')
        return 0 if report['success'] else 1
    window=tk.Tk();window.title('Steve in the Zone — Setup');window.geometry('780x650');window.resizable(False,False)
    window.configure(bg='#20211d');window.iconbitmap(str(payload/'app/_internal/assets/zone-mark.ico'))
    locale=tk.StringVar(value='ru');fields={};entries={};captions=[];messages=queue.Queue();worker=None
    update_enabled=tk.BooleanVar(value=False)
    body=tk.Frame(window,bg='#20211d');body.pack(fill='both',expand=True,padx=24,pady=20)
    title=tk.Label(body,text='',bg='#20211d',fg='#eee9d7',font=('Segoe UI',19,'bold'));title.grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,15))
    selector=ttk.Combobox(body,textvariable=locale,values=('ru','en'),state='readonly',width=4);selector.grid(row=0,column=3)
    update_check=tk.Checkbutton(body,variable=update_enabled,command=lambda:translate(),bg='#20211d',fg='#eee9d7',selectcolor='#2b2d26',activebackground='#20211d',activeforeground='#eee9d7')
    update_check.grid(row=1,column=0,columnspan=4,sticky='w',pady=(0,8))
    def browse(key,file=False):
        value=filedialog.askopenfilename(parent=window,filetypes=[('Java','javaw.exe java.exe')]) if file else filedialog.askdirectory(parent=window)
        if value:fields[key].set(value)
    for row,key,caption,is_file in [(1,'game_source','Папка S.T.A.L.K.E.R. SoC 1.0006',False),(2,'minecraft_source','Папка установленного Minecraft',False),(3,'java','Java — автоматически, если оставить пустым',True),(4,'destination','Новая папка игры',False)]:
        label=tk.Label(body,text='',bg='#20211d',fg='#b2b49f',font=('Segoe UI',10));label.grid(row=row*2+1,column=0,columnspan=4,sticky='w',pady=(5,2));captions.append((label,caption))
        fields[key]=tk.StringVar();entry=tk.Entry(body,textvariable=fields[key],bg='#2b2d26',fg='#eee9d7',insertbackground='#eee9d7',relief='flat',font=('Segoe UI',10),width=75);entry.grid(row=row*2+2,column=0,columnspan=3,sticky='ew',ipady=5)
        browse_button=ttk.Button(body,text='…',command=lambda key=key,file=is_file:browse(key,file));browse_button.grid(row=row*2+2,column=3,padx=(8,0));entries[key]=(entry,browse_button)
    fields['username']=tk.StringVar(value='Steve')
    name=tk.Label(body,text='',bg='#20211d',fg='#b2b49f');name.grid(row=11,column=0,sticky='w',pady=12)
    name_entry=tk.Entry(body,textvariable=fields['username'],width=18);name_entry.grid(row=11,column=1,sticky='w')
    note=tk.Label(body,text='',bg='#20211d',fg='#b2b49f',justify='left',wraplength=730);note.grid(row=12,column=0,columnspan=4,sticky='w',pady=8)
    desktop_enabled=tk.BooleanVar(value=True)
    desktop_check=tk.Checkbutton(body,variable=desktop_enabled,bg='#20211d',fg='#eee9d7',selectcolor='#2b2d26',activebackground='#20211d',activeforeground='#eee9d7')
    desktop_check.grid(row=13,column=0,columnspan=4,sticky='w',pady=(0,8))
    status=tk.StringVar();tk.Label(body,textvariable=status,bg='#20211d',fg='#d7c28d',wraplength=730,justify='left').grid(row=15,column=0,columnspan=4,sticky='w',pady=12)
    def start():
        nonlocal worker
        if worker and worker.is_alive():return
        values={key:value.get().strip() for key,value in fields.items()}
        updating=update_enabled.get()
        if not values['destination'] or (not updating and any(not value for key,value in values.items() if key!='java')):status.set(translator(locale.get())('Выберите папку игры и необходимые компоненты.'));return
        if not updating:values['destination']=str(Path(values['destination'])/'Steve in the Zone')
        language=locale.get()
        add_desktop=desktop_enabled.get()
        def run():
            try:
                callback=lambda text:messages.put(('status',text))
                result=update_installation(destination=values['destination'],payload=payload,notify=callback) if updating else prepare(payload=payload,language=language,notify=callback,**values)
                if add_desktop:
                    try:create_shortcut(result.parent)
                    except Exception:messages.put(('done_warning',str(result)));return
                messages.put(('updated' if updating else 'done',str(result)))
            except Exception as error:messages.put(('error',str(error)))
        launch.configure(state='disabled');selector.configure(state='disabled');desktop_check.configure(state='disabled');update_check.configure(state='disabled')
        worker=threading.Thread(target=run,daemon=False);worker.start()
    launch=tk.Button(body,text='',command=start,bg='#d7c28d',fg='#20211d',relief='flat',font=('Segoe UI',12,'bold'),pady=10)
    launch.grid(row=14,column=0,columnspan=4,sticky='ew',pady=(8,0))
    def translate(_=None):
        t=translator(locale.get());updating=update_enabled.get();title.configure(text=t('Установка'));launch.configure(text=t('Обновить' if updating else 'Установить'));name.configure(text=t('Имя игрока'))
        for label,text in captions:label.configure(text=t('Папка установленной игры' if updating and text=='Новая папка игры' else text))
        for key,widgets in entries.items():
            for widget in widgets:widget.configure(state='disabled' if updating and key!='destination' else 'normal')
        name_entry.configure(state='disabled' if updating else 'normal')
        update_check.configure(text=t('Обновить установленную игру, сохранив прогресс'))
        desktop_check.configure(text=t('Создать ярлык на рабочем столе'))
        note.configure(text=t('Выберите папку Steve in the Zone. Закройте игру и лаунчер. Сохранения, предметы и настройки сохранятся.' if updating else 'Локальная одиночная игра. Аккаунты и сохранения не импортируются. Недостающие компоненты Minecraft загружаются с официальных серверов.'))
    selector.bind('<<ComboboxSelected>>',translate);translate()
    def update():
        while not messages.empty():
            kind,text=messages.get_nowait()
            if kind=='done':status.set(translator(locale.get())('Установка завершена. Открой app/SteveInTheZone.exe в папке игры.'))
            elif kind=='updated':status.set(translator(locale.get())('Обновление завершено. Прогресс и настройки сохранены.'))
            elif kind=='done_warning':status.set(translator(locale.get())('Игра установлена, но ярлык создать не удалось. Откройте app/SteveInTheZone.exe в папке игры.'))
            else:status.set(translator(locale.get())(text))
            if kind in ('done','updated','done_warning','error'):launch.configure(state='normal');selector.configure(state='readonly');desktop_check.configure(state='normal');update_check.configure(state='normal')
        window.after(100,update)
    def close():
        if worker and worker.is_alive():status.set(translator(locale.get())('Дождись завершения подготовки.'));return
        window.destroy()
    window.protocol('WM_DELETE_WINDOW',close);update();window.mainloop();return 0


if __name__=='__main__':raise SystemExit(main())
