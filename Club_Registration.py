import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv
import os

class ClubMembershipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Club Membership Registration")
        self.root.geometry("800x600")
        
        self.members = []
        self.next_id = 1
        self.data_file = "members.json"
        
        self.load_data()
        
        self.create_widgets()
        self.refresh_table()
        
    def create_widgets(self):
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N))
        
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Club Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.club_type_var = tk.StringVar()
        self.club_type_combo = ttk.Combobox(input_frame, textvariable=self.club_type_var, 
                                            values=["Sport Club", "Book Club"], 
                                            state="readonly", width=28)
        self.club_type_combo.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(input_frame, text="Favorite Activity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.activity_entry = ttk.Entry(input_frame, width=30)
        self.activity_entry.grid(row=2, column=1, pady=5, padx=5)
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Register", command=self.register_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="List Members", command=self.list_all_members).pack(side=tk.LEFT, padx=5)
        
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(search_frame, text="Search by Name:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_members).pack(side=tk.LEFT, padx=5)
        
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        columns = ("ID", "Name", "Club Type", "Favorite Activity")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("ID", text="Membership ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Club Type", text="Club Type")
        self.tree.heading("Favorite Activity", text="Favorite Activity")
        
        self.tree.column("ID", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("Club Type", width=150)
        self.tree.column("Favorite Activity", width=250)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="Delete", command=self.delete_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
    def register_member(self):
        name = self.name_entry.get().strip()
        club_type = self.club_type_var.get().strip()
        activity = self.activity_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name cannot be empty")
            return
        
        if not club_type:
            messagebox.showerror("Error", "Please select a club type")
            return
            
        if not activity:
            messagebox.showerror("Error", "Favorite Activity cannot be empty")
            return
        
        member = {
            "id": self.next_id,
            "name": name,
            "club_type": club_type,
            "activity": activity
        }
        
        self.members.append(member)
        self.next_id += 1
        
        self.save_data()
        self.refresh_table()
        
        self.name_entry.delete(0, tk.END)
        self.club_type_var.set("")
        self.activity_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Member registered with ID: {member['id']}")
        
    def list_all_members(self):
        self.refresh_table()
        
    def search_members(self):
        query = self.search_entry.get().strip().lower()
        
        if not query:
            self.refresh_table()
            return
        
        filtered = [m for m in self.members if query in m["name"].lower()]
        self.refresh_table(filtered)
        
    def delete_member(self):
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showerror("Error", "Please select a member to delete")
            return
        
        item = self.tree.item(selection[0])
        member_id = int(item["values"][0])
        
        confirm = messagebox.askyesno("Confirm", f"Delete member with ID {member_id}?")
        
        if confirm:
            self.members = [m for m in self.members if m["id"] != member_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Success", "Member deleted successfully")
    
    def export_csv(self):
        try:
            with open("members_export.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Membership ID", "Name", "Club Type", "Favorite Activity"])
                
                for child in self.tree.get_children():
                    values = self.tree.item(child)["values"]
                    writer.writerow(values)
            
            messagebox.showinfo("Success", "Data exported to members_export.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def refresh_table(self, members=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        display_members = members if members is not None else self.members
        
        for member in display_members:
            self.tree.insert("", tk.END, values=(
                member["id"],
                member["name"],
                member["club_type"],
                member["activity"]
            ))
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.members = data.get("members", [])
                    self.next_id = data.get("next_id", 1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.members = []
            self.next_id = 1
    
    def save_data(self):
        try:
            data = {
                "members": self.members,
                "next_id": self.next_id
            }
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClubMembershipApp(root)
    root.mainloop()