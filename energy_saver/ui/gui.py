"""Simple graphical user interface (Tkinter) for the Electricity Bill Estimator.

Tkinter is part of the Python standard library, so no extra installation is
needed. The GUI reuses exactly the same classes as the console version
(Household, Appliance, TariffCalculator, EnergyAnalyzer); only the way the
user enters data and sees results is different.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from energy_saver.app import SAMPLE_APPLIANCES
from energy_saver.models import Appliance, Household
from energy_saver.services import EnergyAnalyzer, TariffCalculator

GREEN = "#0b5e3c"
LIGHT_GREEN = "#eef6f1"


class EnergyGUI:
    """Main window: appliance form, appliance table, summary and results."""

    def __init__(self, root):
        self.root = root
        self.household = Household()
        self.calculator = TariffCalculator(service_tax_rate=0.08, tax_free_kwh=600)
        self.analyzer = EnergyAnalyzer()

        root.title("SDG 7 Household Electricity Bill Estimator")
        root.geometry("1000x780")
        root.minsize(900, 720)

        self._build_header()
        body = ttk.Frame(root, padding=10)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)
        self._build_summary(body)
        self._build_output(body)
        self.refresh()

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_header(self):
        """Green title bar at the top of the window."""
        header = tk.Frame(self.root, bg=GREEN)
        header.pack(fill="x")
        tk.Label(header, text="Household Electricity Bill Estimator", bg=GREEN, fg="white",
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=14, pady=10)
        tk.Label(header, text="SDG 7 · Affordable and Clean Energy", bg="#fcc30b",
                 font=("Helvetica", 11, "bold"), padx=8, pady=3).pack(side="right", padx=14)

    def _build_form(self, parent):
        """Left panel: fields to add an appliance plus action buttons."""
        form = ttk.LabelFrame(parent, text="Add an appliance", padding=10)
        form.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0, 10))

        # (label, default value) for each input field
        fields = [("Appliance name", ""), ("Power (watts)", ""), ("Quantity", "1"),
                  ("Hours per day", ""), ("Days per month", "30")]
        self.entries = []
        for row, (label, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row * 2, column=0, sticky="w")
            entry = ttk.Entry(form, width=24)
            entry.insert(0, default)
            entry.grid(row=row * 2 + 1, column=0, sticky="we", pady=(0, 6))
            self.entries.append(entry)
        self.entries[0].focus()

        ttk.Button(form, text="Add appliance", command=self.add_appliance).grid(
            row=10, column=0, sticky="we", pady=(4, 12))

        # Other actions, one button per row
        actions = [
            ("Remove selected", self.remove_selected),
            ("Load sample household", self.load_sample),
            ("Clear all", self.clear_all),
            ("Save to CSV...", self.save_csv),
            ("Load from CSV...", self.load_csv),
        ]
        for offset, (text, command) in enumerate(actions):
            ttk.Button(form, text=text, command=command).grid(
                row=11 + offset, column=0, sticky="we", pady=2)

        self.root.bind("<Return>", lambda event: self.add_appliance())

    def _build_table(self, parent):
        """Centre: table listing every appliance."""
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = ("name", "watts", "qty", "hours", "days", "kwh")
        headings = ("Appliance", "Watts", "Qty", "Hrs/day", "Days", "kWh/month")
        widths = (190, 70, 50, 70, 60, 90)
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for column, heading, width in zip(columns, headings, widths):
            self.table.heading(column, text=heading)
            anchor = "w" if column == "name" else "e"
            self.table.column(column, width=width, anchor=anchor)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_summary(self, parent):
        """Summary cards that update after every change."""
        summary = tk.Frame(parent, bg=LIGHT_GREEN, padx=10, pady=8)
        summary.grid(row=1, column=1, sticky="we", pady=(10, 0))
        self.summary_values = {}
        for column, title in enumerate(("Monthly usage", "Estimated bill", "CO2 / month", "Rating")):
            summary.columnconfigure(column, weight=1)
            tk.Label(summary, text=title, bg=LIGHT_GREEN, fg="#555",
                     font=("Helvetica", 10)).grid(row=0, column=column, sticky="w")
            value = tk.Label(summary, text="-", bg=LIGHT_GREEN, fg=GREEN,
                             font=("Helvetica", 16, "bold"))
            value.grid(row=1, column=column, sticky="w")
            self.summary_values[title] = value

    def _build_output(self, parent):
        """Bottom: buttons for detailed results and a text area to show them."""
        bar = ttk.Frame(parent)
        bar.grid(row=2, column=0, columnspan=2, sticky="we", pady=(10, 4))
        ttk.Button(bar, text="Bill breakdown", command=self.show_bill).pack(side="left")
        ttk.Button(bar, text="Energy-saving analysis", command=self.show_analysis).pack(side="left", padx=6)
        ttk.Button(bar, text="What-if simulator", command=self.what_if).pack(side="left")

        self.output = tk.Text(parent, height=8, font=("Courier", 12), wrap="word",
                              relief="solid", borderwidth=1)
        self.output.grid(row=3, column=0, columnspan=2, sticky="nsew")
        parent.rowconfigure(3, weight=1)
        self.write_output("Add your appliances on the left, or click 'Load sample household' to try it.")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def write_output(self, text):
        """Replace the contents of the results text area."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def refresh(self):
        """Redraw the table and summary from the household data."""
        self.table.delete(*self.table.get_children())
        for appliance in self.household.appliances:
            self.table.insert("", "end", values=(
                appliance.name, f"{appliance.power_watts:.0f}", appliance.quantity,
                f"{appliance.hours_per_day:g}", appliance.days_per_month,
                f"{appliance.monthly_kwh():.1f}"))

        total = self.household.total_monthly_kwh()
        if self.household.is_empty():
            texts = ("-", "-", "-", "-")
        else:
            rating = self.analyzer.usage_rating(total).split(" - ")[0]
            texts = (f"{total:.1f} kWh", f"RM {self.calculator.total_bill(total):.2f}",
                     f"{self.analyzer.carbon_kg(total):.1f} kg", rating)
        for label, text in zip(self.summary_values.values(), texts):
            label.configure(text=text)

    def _need_appliances(self):
        """Show a message and return False when the list is empty."""
        if self.household.is_empty():
            messagebox.showinfo("No appliances", "Please add an appliance or load the sample household first.")
            return False
        return True

    @staticmethod
    def _read_number(text, label, minimum, maximum, whole=False):
        """Convert text to a number in range, or raise ValueError with a clear message."""
        try:
            value = int(text) if whole else float(text)
        except ValueError:
            kind = "a whole number" if whole else "a number"
            raise ValueError(f"{label} must be {kind}.")
        if not minimum <= value <= maximum:  # also rejects nan
            raise ValueError(f"{label} must be between {minimum:g} and {maximum:g}.")
        return value

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def add_appliance(self):
        """Validate the form and add the appliance."""
        name, watts, qty, hours, days = (entry.get().strip() for entry in self.entries)
        try:
            if not name:
                raise ValueError("Please enter an appliance name.")
            if len(name) > 40:
                raise ValueError("Appliance name must be under 40 characters.")
            appliance = Appliance(
                name,
                self._read_number(watts, "Power", 1, 10000),
                self._read_number(qty, "Quantity", 1, 100, whole=True),
                self._read_number(hours, "Hours per day", 0, 24),
                self._read_number(days, "Days per month", 1, 31, whole=True),
            )
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return
        self.household.add_appliance(appliance)
        for entry in (self.entries[0], self.entries[1], self.entries[3]):
            entry.delete(0, "end")  # clear name, watts, hours for the next entry
        self.entries[0].focus()
        self.refresh()
        self.write_output(f"Added {appliance}\nIt uses about {appliance.monthly_kwh():.1f} kWh per month.")

    def remove_selected(self):
        """Remove the appliance(s) selected in the table."""
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Remove", "Select an appliance in the table first.")
            return
        # Remove from the highest index down so earlier indexes stay valid.
        for index in sorted((self.table.index(item) for item in selected), reverse=True):
            self.household.remove_appliance(index)
        self.refresh()

    def load_sample(self):
        """Replace the list with the demo household."""
        if not self.household.is_empty() and not messagebox.askyesno(
                "Load sample", "This replaces your current list. Continue?"):
            return
        self.household.appliances = [Appliance(*row) for row in SAMPLE_APPLIANCES]
        self.refresh()
        self.write_output(f"Loaded {len(SAMPLE_APPLIANCES)} sample appliances.")

    def clear_all(self):
        """Remove every appliance after confirmation."""
        if self.household.is_empty() or messagebox.askyesno("Clear all", "Remove all appliances?"):
            self.household.appliances = []
            self.refresh()

    def save_csv(self):
        """Save the appliance list to a CSV file chosen by the user."""
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                self.household.save_to_csv(filename)
                self.write_output(f"Saved {len(self.household.appliances)} appliances to {filename}")
            except OSError as error:
                messagebox.showerror("Save failed", str(error))

    def load_csv(self):
        """Load an appliance list from a CSV file chosen by the user."""
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                count = self.household.load_from_csv(filename)
            except (OSError, ValueError) as error:
                messagebox.showerror("Load failed", f"Could not read the file:\n{error}")
                return
            self.refresh()
            self.write_output(f"Loaded {count} appliances from {filename}")

    def show_bill(self):
        """Show the tariff block breakdown in the results area."""
        if not self._need_appliances():
            return
        total = self.household.total_monthly_kwh()
        lines = [f"Total usage: {total:.1f} kWh/month ({total / 30:.2f} kWh/day)", "",
                 f"{'Tariff block':<16}{'kWh':>9}{'Rate':>9}{'Cost RM':>10}"]
        for label, kwh, rate, cost in self.calculator.breakdown(total):
            lines.append(f"{label:<16}{kwh:>9.1f}{rate:>9.3f}{cost:>10.2f}")
        lines += ["",
                  f"{'Energy charge':<34}{self.calculator.energy_charge(total):>10.2f}",
                  f"{'Service tax':<34}{self.calculator.service_tax(total):>10.2f}",
                  f"{'ESTIMATED MONTHLY BILL (RM)':<34}{self.calculator.total_bill(total):>10.2f}",
                  f"Projected yearly cost: RM {self.calculator.total_bill(total) * 12:,.2f}"]
        self.write_output("\n".join(lines))

    def show_analysis(self):
        """Show rating, CO2, usage shares and tips."""
        if not self._need_appliances():
            return
        total = self.household.total_monthly_kwh()
        lines = [f"Usage rating : {self.analyzer.usage_rating(total)}",
                 f"CO2          : {self.analyzer.carbon_kg(total):.1f} kg/month",
                 f"Trees needed : {self.analyzer.trees_to_offset(total):.0f} (to absorb one year of CO2)",
                 "", "Share of usage:"]
        ranked = self.household.sorted_by_usage()
        for appliance in ranked:
            share = appliance.monthly_kwh() / total * 100 if total > 0 else 0
            lines.append(f"  {appliance.name[:18]:<18} {share:5.1f}% {'#' * int(share // 2)}")
        lines += ["", "Top saving tips:"]
        for rank, appliance in enumerate(ranked[:3], start=1):
            lines.append(f"  {rank}. {appliance.name}: {self.analyzer.tip_for(appliance.name)}")
        self.write_output("\n".join(lines))

    def what_if(self):
        """Open a small dialog to simulate using one appliance fewer hours."""
        if not self._need_appliances():
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("What-if simulator")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        frame = ttk.Frame(dialog, padding=14)
        frame.pack()

        names = [a.name for a in self.household.appliances]
        ttk.Label(frame, text="Appliance").grid(row=0, column=0, sticky="w")
        choice = ttk.Combobox(frame, values=names, state="readonly", width=26)
        choice.current(0)
        choice.grid(row=1, column=0, pady=(0, 8))
        ttk.Label(frame, text="Use fewer hours per day").grid(row=2, column=0, sticky="w")
        hours_entry = ttk.Entry(frame, width=28)
        hours_entry.insert(0, "1")
        hours_entry.grid(row=3, column=0, pady=(0, 10))

        def run_simulation():
            appliance = self.household.appliances[choice.current()]
            try:
                hours = self._read_number(hours_entry.get(), "Hours", 0, appliance.hours_per_day)
            except ValueError as error:
                messagebox.showerror("Invalid input", str(error), parent=dialog)
                return
            before = self.household.total_monthly_kwh()
            saved = self.analyzer.what_if_reduce(appliance, hours)
            bill_before = self.calculator.total_bill(before)
            bill_after = self.calculator.total_bill(before - saved)
            self.write_output(
                f"What if {appliance.name} is used {hours:g} hour(s) less per day?\n\n"
                f"{'':<14}{'Now':>10}{'After':>10}\n"
                f"{'Usage (kWh)':<14}{before:>10.1f}{before - saved:>10.1f}\n"
                f"{'Bill (RM)':<14}{bill_before:>10.2f}{bill_after:>10.2f}\n\n"
                f"You save {saved:.1f} kWh and RM {bill_before - bill_after:.2f} per month "
                f"(RM {(bill_before - bill_after) * 12:.2f} per year)\n"
                f"and avoid {self.analyzer.carbon_kg(saved):.1f} kg of CO2 each month.")
            dialog.destroy()

        ttk.Button(frame, text="Calculate savings", command=run_simulation).grid(row=4, column=0, sticky="we")
        hours_entry.focus()


def main():
    """Open the GUI window."""
    root = tk.Tk()
    EnergyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
