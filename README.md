# Expense-Analyzer
A Python desktop app for tracking personal expenses with CSV storage, category-wise logs, and interactive analytics. Features include monthly/daily trends using NumPy regression, tabbed Matplotlib charts, and a modern Tkinter/ttk GUI for easy expense management and insightful visualizations.


# Features

- Add/Edit/Delete Expenses
- Date, category, amount, and optional notes
- Select from a wide range of predefined categories (Rent, Tuition, Utilities, Groceries, Food, Transport, Entertainment, Health, Insurance, Internet, Subscriptions, Gifts, Travel, Other)
- Filter Transactions by Month and Year
- View only relevant logs in the main dashboard
- CSV-based Storage
- Easy import/export of expense data
- Backup and restore functionality
- Analytics with Tabbed Charts
- Trend Tab: Daily expense trend with linear regression line
- Monthly Tab: Monthly spending bar chart
- Category Tab: Pie chart showing distribution across categories
- Interactive filtering by year and month
- Beautiful UI
- Uses ttk themed widgets for modern look and feel
- Responsive layout for forms, tables, and charts
- NumPy Linear Regression
- Provides trend prediction for daily expenses

# Installation

Clone the repository:

` git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker`

Install dependencies:

`pip install matplotlib numpy`


Tkinter is included with Python by default.
Pillow is optional if you want to add icons.

# Run the application:

`python main.py`

# Usage

- Add Expense: Fill in the date, category, amount, and note, then click Add Expense.
- Edit Expense: Select a transaction from the table, modify fields, and click Update Selected.
- Delete Expense: Select a transaction and click Delete Selected.
- Clear All: Remove all transactions from the database.
- Filter: Enter a year and/or month to filter displayed transactions.
- Analytics: Click Analytics to open a separate window with tabbed charts. Filter charts by year and month.
- Import/Export CSV: Import or export your expense data for backup or sharing.

# Technology Stack

- Python 3.8+
- Tkinter & ttk — for GUI
- Matplotlib — for charts
- NumPy — for linear regression in trend analysis
- CSV — for lightweight database

# Future Improvements

- Add interactive charts with hover tooltips
- Category-wise monthly trend analysis
- Export charts as images
- Multi-user support with authentication

# License
This project is open-source under the MIT License.

