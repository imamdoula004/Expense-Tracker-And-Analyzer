"""
Expense Tracker with Tabbed Analytics
Single-file Python app: main.py

Dependencies: Python 3.8+, tkinter (built-in), matplotlib, numpy
Optional: pillow (for nicer icons)

Run: python main.py
"""

import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CSV_FILE = 'expenses.csv'
DATE_FORMAT = '%Y-%m-%d'

# ---------------------------
# Utility Functions
# ---------------------------

def parse_date(s):
    try:
        return datetime.strptime(s, DATE_FORMAT).date()
    except:
        return None

def format_currency(v):
    return f"{v:,.2f}"

# ---------------------------
# CSV Database
# ---------------------------

class ExpenseDB:
    def __init__(self, path=CSV_FILE):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'category', 'amount', 'note'])
        self.load()

    def load(self):
        self.rows = []
        with open(self.path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row['date']
                category = row['category']
                amount = float(row['amount'])
                note = row.get('note', '')
                self.rows.append({'date': date, 'category': category, 'amount': amount, 'note': note})

    def save(self):
        with open(self.path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'category', 'amount', 'note'])
            for r in self.rows:
                writer.writerow([r['date'], r['category'], r['amount'], r['note']])

    def add(self, date, category, amount, note):
        self.rows.append({'date': date, 'category': category, 'amount': amount, 'note': note})
        self.save()

    def update(self, idx, date, category, amount, note):
        self.rows[idx] = {'date': date, 'category': category, 'amount': amount, 'note': note}
        self.save()

    def delete(self, idx):
        del self.rows[idx]
        self.save()

    def fetch_all(self):
        return self.rows

    def fetch_by_month(self, year=None, month=None):
        filtered = []
        for r in self.rows:
            dt = parse_date(r['date'])
            if not dt:
                continue
            if year is None and month is None:
                filtered.append(r)
            elif dt.year == year and dt.month == month:
                filtered.append(r)
        return filtered

# ---------------------------
# Analytics Window with Tabs
# ---------------------------

class AnalyticsWindow(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.title("Expense Analytics")
        self.geometry("1000x700")
        self.configure(bg="#f6f7fb")

        # Filter
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', pady=6)
        ttk.Label(filter_frame, text='Year:').pack(side='left')
        self.year_var = tk.StringVar()
        ttk.Entry(filter_frame, width=6, textvariable=self.year_var).pack(side='left', padx=4)
        ttk.Label(filter_frame, text='Month:').pack(side='left')
        self.month_var = tk.StringVar()
        ttk.Entry(filter_frame, width=4, textvariable=self.month_var).pack(side='left', padx=4)
        ttk.Button(filter_frame, text='Apply', command=self.draw_charts).pack(side='left', padx=6)
        ttk.Button(filter_frame, text='Clear', command=self.clear_filter).pack(side='left')

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {}
        for name in ['Trend', 'Monthly', 'Category']:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame

        # Figures for each tab
        self.fig_trend = Figure(figsize=(8,5), dpi=100)
        self.ax_trend = self.fig_trend.add_subplot(111)
        self.canvas_trend = FigureCanvasTkAgg(self.fig_trend, master=self.tabs['Trend'])
        self.canvas_trend.get_tk_widget().pack(fill='both', expand=True)

        self.fig_bar = Figure(figsize=(8,5), dpi=100)
        self.ax_bar = self.fig_bar.add_subplot(111)
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=self.tabs['Monthly'])
        self.canvas_bar.get_tk_widget().pack(fill='both', expand=True)

        self.fig_pie = Figure(figsize=(8,5), dpi=100)
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=self.tabs['Category'])
        self.canvas_pie.get_tk_widget().pack(fill='both', expand=True)

        self.draw_charts()

    def clear_filter(self):
        self.year_var.set('')
        self.month_var.set('')
        self.draw_charts()

    def draw_charts(self):
        self.ax_trend.clear()
        self.ax_bar.clear()
        self.ax_pie.clear()

        # Filter
        year = self.year_var.get().strip()
        month = self.month_var.get().strip()
        try: year = int(year)
        except: year = None
        try: month = int(month)
        except: month = None

        rows = self.db.fetch_by_month(year, month)
        if not rows:
            self.ax_trend.text(0.5,0.5,'No data',ha='center',va='center')
            self.ax_bar.text(0.5,0.5,'No data',ha='center',va='center')
            self.ax_pie.text(0.5,0.5,'No data',ha='center',va='center')
            self.canvas_trend.draw()
            self.canvas_bar.draw()
            self.canvas_pie.draw()
            return

        # Aggregate daily totals
        date_map = {}
        categories = {}
        for r in rows:
            d, c, amt = r['date'], r['category'], r['amount']
            date_map.setdefault(d, 0)
            date_map[d] += amt
            categories.setdefault(c, 0)
            categories[c] += amt

        # --- Trend Tab ---
        dates_sorted = sorted(date_map.keys())
        totals = [date_map[d] for d in dates_sorted]
        xs = np.arange(len(totals))
        ys = np.array(totals)
        if len(xs) > 1:
            slope, intercept = np.polyfit(xs, ys, 1)
            reg_vals = slope*xs + intercept
        else:
            reg_vals = ys

        self.ax_trend.plot(dates_sorted, totals, marker='o', label='Daily Total')
        self.ax_trend.plot(dates_sorted, reg_vals, linestyle='--', label='Trend')
        self.ax_trend.set_title('Daily Spending Trend')
        self.ax_trend.tick_params(axis='x', rotation=45)
        self.ax_trend.legend(loc='upper left', fontsize='small')
        self.fig_trend.tight_layout()
        self.canvas_trend.draw()

        # --- Monthly Tab ---
        month_map = {}
        for d_s, val in date_map.items():
            dt = parse_date(d_s)
            key = dt.strftime('%Y-%m')
            month_map.setdefault(key,0)
            month_map[key]+=val
        months = sorted(month_map.keys())
        mvals = [month_map[m] for m in months]
        self.ax_bar.bar(months, mvals)
        self.ax_bar.set_title('Monthly Spending')
        self.ax_bar.tick_params(axis='x', rotation=45)
        self.fig_bar.tight_layout()
        self.canvas_bar.draw()

        # --- Category Tab ---
        cats = list(categories.keys())
        cvals = [categories[c] for c in cats]
        if cvals:
            pairs = sorted(zip(cvals,cats), reverse=True)
            top = pairs[:6]
            rest = pairs[6:]
            top_vals, top_cats = zip(*top)
            if rest:
                rest_sum = sum(v for v,_ in rest)
                top_vals = list(top_vals)+[rest_sum]
                top_cats = list(top_cats)+['Other']
            self.ax_pie.pie(top_vals, labels=top_cats, autopct='%1.0f%%', startangle=140,textprops={'fontsize':10})
            self.ax_pie.axis('equal')
            self.ax_pie.set_title('Expenses by Category')
        else:
            self.ax_pie.text(0.5,0.5,'No categories',ha='center',va='center')
        self.fig_pie.tight_layout()
        self.canvas_pie.draw()

# ---------------------------
# Main App
# ---------------------------

class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker — Tabbed Analytics")
        self.geometry("1100x650")
        self.configure(bg="#f6f7fb")

        self.db = ExpenseDB()

        self._build_ui()
        self.refresh_transactions()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12,10))
        header.pack(side='top', fill='x')
        ttk.Label(header, text='Expense Tracker', font=('Helvetica',18,'bold')).pack(side='left')
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side='right')
        ttk.Button(btn_frame, text='Import CSV', command=self.import_csv).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Export CSV', command=self.export_csv).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Analytics', command=self.open_analytics).pack(side='left', padx=4)

        # Filters (month/year)
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', pady=6)
        ttk.Label(filter_frame, text='Year:').pack(side='left')
        self.year_var = tk.StringVar()
        ttk.Entry(filter_frame, width=6, textvariable=self.year_var).pack(side='left', padx=4)
        ttk.Label(filter_frame, text='Month:').pack(side='left')
        self.month_var = tk.StringVar()
        ttk.Entry(filter_frame, width=4, textvariable=self.month_var).pack(side='left', padx=4)
        ttk.Button(filter_frame, text='Apply Filter', command=self.refresh_transactions).pack(side='left', padx=6)
        ttk.Button(filter_frame, text='Clear', command=self.clear_filter).pack(side='left')

        # Left: Form
        left = ttk.Frame(self, width=300)
        left.pack(side='left', fill='y', padx=(12,6))
        form_card = ttk.LabelFrame(left, text='Add / Edit Expense', padding=12)
        form_card.pack(fill='both', expand=False)

        ttk.Label(form_card, text='Date (YYYY-MM-DD)').grid(row=0,column=0,sticky='w')
        self.date_var = tk.StringVar(value=datetime.now().strftime(DATE_FORMAT))
        ttk.Entry(form_card, textvariable=self.date_var).grid(row=1,column=0,sticky='we', pady=4)

        ttk.Label(form_card, text='Category').grid(row=2,column=0,sticky='w')
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(form_card, textvariable=self.cat_var, state='readonly', values=self.categories())
        self.cat_combo.grid(row=3,column=0,sticky='we', pady=4)

        ttk.Label(form_card, text='Amount').grid(row=4,column=0,sticky='w')
        self.amount_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.amount_var).grid(row=5,column=0,sticky='we', pady=4)

        ttk.Label(form_card, text='Note').grid(row=6,column=0,sticky='w')
        self.note_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.note_var).grid(row=7,column=0,sticky='we', pady=4)

        btns = ttk.Frame(form_card)
        btns.grid(row=8,column=0,pady=(8,0),sticky='we')
        self.add_btn = ttk.Button(btns, text='Add Expense', command=self.add_expense)
        self.add_btn.pack(side='left', fill='x', expand=True)
        self.update_btn = ttk.Button(btns, text='Update Selected', command=self.update_selected)
        self.update_btn.pack(side='left', fill='x', expand=True, padx=(4,0))

        # Right: Table
        right = ttk.Frame(self)
        right.pack(side='left', fill='both', expand=True, padx=(6,12))
        table_card = ttk.LabelFrame(right, text='Transactions', padding=8)
        table_card.pack(fill='both', expand=True)

        columns = ('date','category','amount','note')
        self.tree = ttk.Treeview(table_card, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.column('date', width=100)
        self.tree.column('category', width=120)
        self.tree.column('amount', width=100, anchor='e')
        self.tree.column('note', width=250)
        self.tree.pack(fill='both', expand=True, side='left')

        scrollbar = ttk.Scrollbar(table_card, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Bottom buttons
        bottom = ttk.Frame(self, padding=(12,6))
        bottom.pack(side='bottom', fill='x')
        ttk.Button(bottom, text='Delete Selected', command=self.delete_selected).pack(side='left')
        ttk.Button(bottom, text='Clear All', command=self.clear_all).pack(side='left', padx=4)

    def categories(self):
        return ['Rent','Tuition','Utilities','Groceries','Food','Transport','Shopping','Entertainment',
                'Health','Insurance','Internet','Subscriptions','Gifts','Travel','Other']

    # CRUD & CSV methods same as previous code
    def add_expense(self):
        date = self.date_var.get().strip()
        cat = self.cat_var.get().strip() or 'Other'
        try:
            amt = float(self.amount_var.get().strip())
        except:
            messagebox.showerror('Invalid', 'Enter a valid amount')
            return
        note = self.note_var.get().strip()
        if not parse_date(date):
            messagebox.showerror('Invalid', 'Date must be YYYY-MM-DD')
            return
        self.db.add(date, cat, amt, note)
        self.clear_form()
        self.refresh_transactions()

    def update_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('No selection', 'Select a transaction')
            return
        idx = int(sel[0])
        date = self.date_var.get().strip()
        cat = self.cat_var.get().strip() or 'Other'
        try:
            amt = float(self.amount_var.get().strip())
        except:
            messagebox.showerror('Invalid', 'Enter a valid amount')
            return
        note = self.note_var.get().strip()
        if not parse_date(date):
            messagebox.showerror('Invalid', 'Date must be YYYY-MM-DD')
            return
        self.db.update(idx, date, cat, amt, note)
        self.clear_form()
        self.refresh_transactions()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if messagebox.askyesno('Confirm', 'Delete selected transaction?'):
            self.db.delete(idx)
            self.refresh_transactions()

    def clear_all(self):
        if messagebox.askyesno('Confirm', 'Delete all transactions?'):
            self.db.rows.clear()
            self.db.save()
            self.refresh_transactions()

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        r = self.db.rows[idx]
        self.date_var.set(r['date'])
        self.cat_var.set(r['category'])
        self.amount_var.set(str(r['amount']))
        self.note_var.set(r['note'])

    def refresh_transactions(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        year = self.year_var.get().strip()
        month = self.month_var.get().strip()
        try: year = int(year)
        except: year = None
        try: month = int(month)
        except: month = None
        rows = self.db.fetch_by_month(year, month)
        for idx, r in enumerate(rows):
            self.tree.insert('', 'end', iid=str(self.db.rows.index(r)), values=(r['date'],r['category'],r['amount'],r['note']))

    def clear_filter(self):
        self.year_var.set('')
        self.month_var.set('')
        self.refresh_transactions()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV','*.csv')])
        if not path: return
        count = 0
        with open(path,newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                d = row.get('date')
                c = row.get('category') or 'Other'
                a = row.get('amount')
                n = row.get('note') or ''
                if d and a:
                    try:
                        amt = float(a)
                        if parse_date(d):
                            self.db.add(d,c,amt,n)
                            count += 1
                    except:
                        continue
        messagebox.showinfo('Import', f'Imported {count} records')
        self.refresh_transactions()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path: return
        with open(path,'w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date','category','amount','note'])
            for r in self.db.rows:
                writer.writerow([r['date'],r['category'],r['amount'],r['note']])
        messagebox.showinfo('Export', f'Exported {len(self.db.rows)} records')

    def clear_form(self):
        self.date_var.set(datetime.now().strftime(DATE_FORMAT))
        self.cat_var.set('')
        self.amount_var.set('')
        self.note_var.set('')

    def open_analytics(self):
        AnalyticsWindow(self, self.db)

# ---------------------------
# Run
# ---------------------------

if __name__ == '__main__':
    app = ExpenseTrackerApp()
    app.mainloop()
