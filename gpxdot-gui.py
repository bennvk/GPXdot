#!/usr/bin/env python3

import os
import sys
import math
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import gpxpy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

#######################################
##### FONCTIONS DE BASE DU SCRIPT #####
#######################################

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def gpx_to_coordinates(gpx_file, min_distance=0):
    points = []
    last_kept_point = None
    prev_point = None
    distance_since_last_kept_point = 0.0

    with open(gpx_file, 'r', encoding='utf-8') as f:
        gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if last_kept_point is None:
                        points.append((point.latitude, point.longitude, point.elevation))
                        last_kept_point = point
                        prev_point = point
                        distance_since_last_kept_point = 0.0
                    else:
                        dist = haversine(prev_point.latitude, prev_point.longitude,
                                         point.latitude, point.longitude)
                        distance_since_last_kept_point += dist
                        prev_point = point

                        if distance_since_last_kept_point >= min_distance:
                            points.append((point.latitude, point.longitude, point.elevation))
                            last_kept_point = point
                            distance_since_last_kept_point = 0.0
    return points


def reverse_geocode(points, language='fr', user_agent="gpxdot_gui (contact: you@example.com)", min_delay_seconds=1.0, cancel_event=None, progress_cb=None):
    geolocator = Nominatim(user_agent=user_agent)
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=min_delay_seconds)

    villes = []
    n = len(points)
    for i, (lat, lon, ele) in enumerate(points, start=1):
        if cancel_event and cancel_event.is_set():
            break
        try:
            location = reverse((lat, lon), language=language)
        except Exception:
            location = None
        if location is None:
            ville = "Localité inconnue"
        else:
            ville = None
            for key in ['village', 'town', 'city', 'municipality']:
                ville = location.raw.get('address', {}).get(key)
                if ville:
                    break
            if not ville:
                ville = "Localité non trouvée"
        villes.append(ville)
        if progress_cb:
            progress_cb(i, n)
    return villes

#######################################
#####   GUI DU SCRIPT - TKINTER   #####
#######################################

class GPXDotGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPX → Villes (gpxdot)")
        self.geometry("900x600")

        home = os.path.expanduser('~')
        self.GPX_DIR = os.path.join(home, 'gpxdot', 'gpxFiles')
        self.TXT_DIR = os.path.join(home, 'gpxdot', 'txtFiles')

        self._apply_dark_theme()

        frm_file = ttk.Frame(self)
        frm_file.pack(fill='x', padx=12, pady=(12, 6))

        self.var_path = tk.StringVar()
        if os.path.isdir(self.GPX_DIR):
            self.var_path.set(self.GPX_DIR)

        ttk.Label(frm_file, text="Fichier GPX :").pack(side='left')
        self.ent_file = ttk.Entry(frm_file, textvariable=self.var_path, width=70)
        self.ent_file.pack(side='left', padx=6, expand=True, fill='x')
        ttk.Button(frm_file, text="Parcourir…", command=self.browse_file).pack(side='left')

        frm_opts = ttk.Frame(self)
        frm_opts.pack(fill='x', padx=12, pady=6)

        self.var_distance = tk.StringVar(value='0')
        ttk.Label(frm_opts, text="Distance entre les points (en mètres) :").pack(side='left')
        ttk.Entry(frm_opts, textvariable=self.var_distance, width=8).pack(side='left', padx=(6, 18))

        frm_save = ttk.Frame(self)
        frm_save.pack(fill='x', padx=12, pady=6)

        self.var_save = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_save, text="Enregistrer la sortie dans un fichier", variable=self.var_save, command=self.toggle_save).pack(side='left')

        ttk.Label(frm_save, text="Fichier de sortie :").pack(side='left', padx=(18, 0))
        self.var_out = tk.StringVar(value="")
        self.ent_out = ttk.Entry(frm_save, textvariable=self.var_out, width=50, state='disabled')
        self.ent_out.pack(side='left', padx=6, fill='x', expand=True)
        self.btn_out = ttk.Button(frm_save, text="Parcourir…", command=self.browse_save, state='disabled')
        self.btn_out.pack(side='left')

        frm_actions = ttk.Frame(self)
        frm_actions.pack(fill='x', padx=12, pady=6)

        self.btn_run = ttk.Button(frm_actions, text="Lancer", command=self.run)
        self.btn_run.pack(side='left')
        self.btn_cancel = ttk.Button(frm_actions, text="Annuler", command=self.cancel, state='disabled')
        self.btn_cancel.pack(side='left', padx=(6, 0))
        self.btn_export = ttk.Button(frm_actions, text="Exporter la sortie…", command=self.export_output)
        self.btn_export.pack(side='right')

        frm_prog = ttk.Frame(self)
        frm_prog.pack(fill='x', padx=12, pady=(0, 6))
        self.prog = ttk.Progressbar(frm_prog, mode='determinate', style='Modern.Horizontal.TProgressbar')
        self.prog.pack(side='left', fill='x', expand=True)
        self.var_prog = tk.StringVar(value="Prêt")
        ttk.Label(frm_prog, textvariable=self.var_prog, width=24, anchor='e', style='Muted.TLabel').pack(side='left', padx=(6,0))

        self.txt = tk.Text(
            self, wrap='none', height=20,
            bg='#161B22',
            fg='#C9D1D9',
            insertbackground='#C9D1D9',
            highlightthickness=0, bd=0
        )
        self.txt.pack(fill='both', expand=True, padx=12, pady=(0,12))
        self.txt.configure(font=("Consolas", 10))

        self.cancel_event = threading.Event()
        self.worker = None
        self.msg_queue = queue.Queue()
        self.after(100, self._poll_queue)

    def _apply_dark_theme(self):
        bg = '#0D1117'
        surface = '#161B22'
        border = '#30363D'
        text = '#C9D1D9'
        muted = '#8B949E'
        accent = '#58A6FF'

        self.configure(bg=bg)
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=text)
        style.configure('Muted.TLabel', background=bg, foreground=muted)
        style.configure('TCheckbutton', background=bg, foreground=text)
        style.map('TCheckbutton',
                  background=[('active', bg), ('selected', bg)],
                  foreground=[('active', text), ('selected', text)])

        style.configure(
            'TEntry',
            fieldbackground=surface,
            background=surface,
            foreground=text,
            bordercolor=border
        )
        style.map('TEntry', fieldbackground=[('focus', surface)], bordercolor=[('focus', accent)])

        style.configure('TButton', background=surface, foreground=text, relief='flat', padding=8)
        style.map('TButton', background=[('active', '#1C2128')])

        style.configure('Modern.Horizontal.TProgressbar', troughcolor=surface, background=accent, thickness=10)
        
        style.configure('.', background=bg, foreground=text)

    def browse_file(self):
        initdir = self.GPX_DIR if os.path.isdir(self.GPX_DIR) else os.path.expanduser('~')
        path = filedialog.askopenfilename(
            title="Choisir un fichier GPX",
            initialdir=initdir,
            filetypes=[("Fichiers GPX", "*.gpx"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.var_path.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            txt_dir = self.TXT_DIR if os.path.isdir(self.TXT_DIR) else os.path.dirname(path)
            out_default = os.path.join(txt_dir, f"{base}.txt")
            self.var_out.set(out_default)

    def toggle_save(self):
        state = 'normal' if self.var_save.get() else 'disabled'
        self.ent_out.configure(state=state)
        self.btn_out.configure(state=state)

    def browse_save(self):
        initdir = self.TXT_DIR if os.path.isdir(self.TXT_DIR) else os.path.expanduser('~')
        path = filedialog.asksaveasfilename(
            title="Enregistrer la sortie sous…",
            defaultextension=".txt",
            initialdir=initdir,
            filetypes=[("Texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.var_out.set(path)

    def cancel(self):
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self.var_prog.set("Annulation en cours…")
            self.btn_cancel.configure(state='disabled')

    def export_output(self):
        content = self.txt.get('1.0', 'end-1c')
        if not content.strip():
            messagebox.showinfo("Exporter", "Aucun contenu à exporter.")
            return
        initdir = self.TXT_DIR if os.path.isdir(self.TXT_DIR) else os.path.expanduser('~')
        path = filedialog.asksaveasfilename(
            title="Exporter la sortie",
            defaultextension=".txt",
            initialdir=initdir,
            filetypes=[("Texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Exporter", f"Fichier sauvegardé :\n{path}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def run(self):
        path = self.var_path.get().strip()
        if not path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier GPX.")
            return
        if not os.path.isfile(path):
            alt = os.path.join(self.GPX_DIR, path)
            if os.path.isfile(alt):
                path = alt
                self.var_path.set(path)
            else:
                messagebox.showerror("Erreur", f"Fichier introuvable :\n{path}")
                return
        try:
            dist = float(self.var_distance.get().strip() or '0')
            if dist < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Distance minimale invalide.")
            return

        if self.var_save.get():
            out = self.var_out.get().strip()
            if not out:
                messagebox.showerror("Erreur", "Veuillez choisir un fichier de sortie.")
                return
            out_dir = os.path.dirname(out) or '.'
            if not os.path.isdir(out_dir):
                try:
                    os.makedirs(out_dir, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de créer le dossier :\n{out_dir}\n{e}")
                    return

        self.txt.delete('1.0', 'end')
        self.prog.configure(value=0, maximum=100)
        self.var_prog.set("Lecture du GPX…")
        self.btn_run.configure(state='disabled')
        self.btn_cancel.configure(state='normal')
        self.cancel_event.clear()

        args = {
            'path': path,
            'dist': dist,
            'save': self.var_save.get(),
            'out': self.var_out.get().strip(),
        }
        self.worker = threading.Thread(target=self._worker_run, args=(args,))
        self.worker.daemon = True
        self.worker.start()

    def _worker_run(self, args):
        try:
            path = args['path']
            dist = args['dist']
            save = args['save']
            out = args['out']

            coords = gpx_to_coordinates(path, dist)
            n = len(coords)
            if n == 0:
                self.msg_queue.put(('status', "Aucun point après filtrage."))
                self.msg_queue.put(('done', None))
                return
            self.msg_queue.put(('progress', (0, f"{n} points extraits")))

            def pcb(i, total):
                pct = int(i * 100 / max(total, 1))
                self.msg_queue.put(('progress', (pct, f"Reverse geocoding… {i}/{total}")))
            villes = reverse_geocode(coords, language='fr', cancel_event=self.cancel_event, progress_cb=pcb)

            if self.cancel_event.is_set():
                self.msg_queue.put(('status', "Annulé par l'utilisateur."))
                self.msg_queue.put(('done', None))
                return

            lines = ["\nListe des points avec localités (reverse geocode) :"]
            for idx, ((lat, lon, ele), ville) in enumerate(zip(coords, villes), start=1):
                ele_str = f"{ele:.2f}" if ele is not None else "N/A"
                lines.append(f"{idx}: {lat:.6f} {lon:.6f} {ele_str} => {ville}")
            output_text = "\n".join(lines)

            if save and out:
                try:
                    with open(out, 'w', encoding='utf-8') as f:
                        f.write(output_text + "\n")
                    self.msg_queue.put(('status', f"Fichier sauvegardé : {out}"))
                except Exception as e:
                    self.msg_queue.put(('status', f"Erreur d'écriture : {e}"))

            self.msg_queue.put(('output', output_text))
            self.msg_queue.put(('progress', (100, "Terminé")))
            self.msg_queue.put(('done', None))

        except Exception as e:
            self.msg_queue.put(('error', str(e)))
            self.msg_queue.put(('done', None))

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.msg_queue.get_nowait()
                if kind == 'progress':
                    pct, label = payload
                    self.prog.configure(value=pct)
                    self.var_prog.set(label)
                elif kind == 'status':
                    self.var_prog.set(payload)
                elif kind == 'output':
                    self.txt.delete('1.0', 'end')
                    self.txt.insert('1.0', payload)
                    self.txt.see('end')
                elif kind == 'error':
                    messagebox.showerror("Erreur", payload)
                elif kind == 'done':
                    self.btn_run.configure(state='normal')
                    self.btn_cancel.configure(state='disabled')
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)


if __name__ == '__main__':
    app = GPXDotGUI()
    app.mainloop()
