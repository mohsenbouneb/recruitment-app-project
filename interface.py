import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
import matplotlib.pyplot as plt

# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("Outils Administratifs")
root.geometry("1200x700")

# Cadre d'affichage pour différentes vues
display_frame = tk.Frame(root)
display_frame.pack(fill="both", expand=True)

# Fonction "À propos"
def show_about():
    messagebox.showinfo("À PROPOS", "Cette application de gestion de recrutement aide à simplifier le processus de recrutement en permettant d'ajouter, d'évaluer et de gérer les candidats. Elle offre des outils pour suivre les performances et visualiser les scores d’évaluation.")

# Fonction "Aide"
def show_help():
    messagebox.showinfo("AIDE", "Pour utiliser l'application, ajoutez des candidats, modifiez leurs informations ou visualisez les scores dans des graphiques. Pour plus d'options, explorez les menus.")

# Fonction pour afficher le graphique
def afficher_graphique():
    # Clear the content area (not the entire root)
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Connect to the database and retrieve data
    conn = sqlite3.connect("recrutement.db")
    try:
        df = pd.read_sql_query("SELECT nom, score FROM candidats", conn)
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        conn.close()
        return
    finally:
        conn.close()

    # Handle empty data
    if df.empty:
        label_empty = tk.Label(display_frame, text="No data available to display.", font=("Arial", 14))
        label_empty.pack(pady=10)
        return

    # Clear any previous plot
    plt.clf()

    # Get dimensions of the content area (excluding menus)
    display_frame.update()
    content_width = display_frame.winfo_width()
    content_height = display_frame.winfo_height()

    # Set figure size to match content area dimensions
 
    fig, ax = plt.subplots(figsize=(8, 5))

    # Create the bar chart
    ax.bar(df["nom"], df["score"], color="skyblue")
    ax.set_xlabel("Candidates", fontsize=10)
    ax.set_ylabel("Score", fontsize=10)
    ax.set_title("Candidate Evaluation Scores", fontsize=14)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    # Embed the figure in Tkinter inside display_frame
    canvas = FigureCanvasTkAgg(fig, master=display_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=False)

    
def show_admins():
    for widget in display_frame.winfo_children():
        widget.destroy()
    conn = sqlite3.connect("recrutement.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    admins = cursor.fetchall()
    conn.close()
    
    tree = ttk.Treeview(display_frame, columns=("ID", "Username"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Username", text="Username")
    
    for admin in admins:
        tree.insert("", tk.END, values=admin)
    
    tree.pack(fill="both", expand=True)

def add_admin():
    for widget in display_frame.winfo_children():
        widget.destroy()
    
    label_add = tk.Label(display_frame, text="Add a new admin", font=("Arial", 12))
    label_add.pack(pady=10)

    label_new_username = tk.Label(display_frame, text="New Username")
    label_new_username.pack(pady=5)
    entry_new_username = tk.Entry(display_frame)
    entry_new_username.pack(pady=5)

    label_new_password = tk.Label(display_frame, text="New Password")
    label_new_password.pack(pady=5)
    entry_new_password = tk.Entry(display_frame, show="*")
    entry_new_password.pack(pady=5)

    def save_user():
        new_username = entry_new_username.get()
        new_password = entry_new_password.get()
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_password))
            conn.commit()
            messagebox.showinfo("Registration", "User registered successfully!")
            show_admins()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        finally:
            conn.close()

    btn_save = tk.Button(display_frame, text="Save Admin", command=save_user)
    btn_save.pack(pady=20)
def modify_admin():
    for widget in display_frame.winfo_children():
        widget.destroy()

    label_modify = tk.Label(display_frame, text="Modify Admin Information", font=("Arial", 12))
    label_modify.pack(pady=10)

    label_id = tk.Label(display_frame, text="Enter Admin ID")
    label_id.pack(pady=5)
    entry_id = tk.Entry(display_frame)
    entry_id.pack(pady=5)

    # Input fields for new details
    label_new_username = tk.Label(display_frame, text="New Username (leave blank if unchanged)")
    label_new_username.pack(pady=5)
    entry_new_username = tk.Entry(display_frame)
    entry_new_username.pack(pady=5)

    label_new_password = tk.Label(display_frame, text="New Password (leave blank if unchanged)")
    label_new_password.pack(pady=5)
    entry_new_password = tk.Entry(display_frame, show="*")
    entry_new_password.pack(pady=5)

    def confirm_modify():
        admin_id = entry_id.get()
        new_username = entry_new_username.get()
        new_password = entry_new_password.get()
        
        if not admin_id:
            messagebox.showerror("Error", "Admin ID is required.")
            return

        # Prepare updates dynamically
        fields_to_update = []
        values = []
        
        if new_username:
            fields_to_update.append("username = ?")
            values.append(new_username)
        
        if new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            fields_to_update.append("password = ?")
            values.append(hashed_password)
        
        if not fields_to_update:
            messagebox.showwarning("No Update", "No fields to update.")
            return

        values.append(admin_id)

        # Execute the update
        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()

        try:
            update_query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE id = ?"
            cursor.execute(update_query, values)
            conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Modify Admin", f"Admin with ID {admin_id} updated successfully.")
                show_admins()  # Refresh the admin list
            else:
                messagebox.showwarning("Modify Admin", f"No admin found with ID {admin_id}.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    btn_modify = tk.Button(display_frame, text="Modify Admin", command=confirm_modify)
    btn_modify.pack(pady=20)

def delete_admin():
    for widget in display_frame.winfo_children():
        widget.destroy()
    
    label_delete = tk.Label(display_frame, text="Enter Admin ID to Delete", font=("Arial", 12))
    label_delete.pack(pady=10)

    entry_id = tk.Entry(display_frame)
    entry_id.pack(pady=5)

    def confirm_delete():
        admin_id = entry_id.get()
        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (admin_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Delete Admin", f"Admin with ID {admin_id} deleted successfully.")
        show_admins()

    btn_delete = tk.Button(display_frame, text="Delete Admin", command=confirm_delete)
    btn_delete.pack(pady=20)
def modify_candidatures():
    for widget in display_frame.winfo_children():
        widget.destroy()

    label_modify = tk.Label(display_frame, text="Modify Candidate Details", font=("Arial", 12))
    label_modify.pack(pady=10)

    # Input for candidate ID
    label_id = tk.Label(display_frame, text="Enter Candidate ID to Modify")
    label_id.pack(pady=5)
    entry_id = tk.Entry(display_frame)
    entry_id.pack(pady=5)

    # Fields to modify
    entries = {}
    fields = ["Nom", "Experience", "Diplome", "Competences Techniques", "Qualites Humaines", "Mobilite"]
    for field in fields:
        label_field = tk.Label(display_frame, text=f"New {field} (leave blank if unchanged)")
        label_field.pack(pady=5)
        entry_field = tk.Entry(display_frame)
        entry_field.pack(pady=5)
        entries[field] = entry_field

    def recalculate_score(candidat_id):
        """Recalculate the score based on candidate attributes."""
        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT experience, diplome, competences_techniques, qualites_humaines, mobilite 
            FROM candidats WHERE id = ?
        """, (candidat_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            experience, diplome, competences, qualites, mobilite = (int(x) if x is not None else 0 for x in row)
            new_score = experience + diplome + competences + qualites + mobilite  # Example formula
            conn = sqlite3.connect("recrutement.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE candidats SET score = ? WHERE id = ?", (new_score, candidat_id))
            conn.commit()
            conn.close()

    def confirm_modify():
        """Modify candidate details and optionally recalculate the score."""
        candidat_id = entry_id.get()
        if not candidat_id.isdigit():
            messagebox.showerror("Error", "Candidate ID must be a valid number.")
            return

        updated_fields = []
        values = []

        # Collect new values
        for field, entry in entries.items():
            new_value = entry.get()
            if new_value:
                db_field = field.lower().replace(" ", "_")
                updated_fields.append(f"{db_field} = ?")
                values.append(new_value)

        if not updated_fields:
            messagebox.showwarning("No Update", "No fields were updated.")
            return

        values.append(candidat_id)

        # Update database
        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()
        try:
            update_query = f"UPDATE candidats SET {', '.join(updated_fields)} WHERE id = ?"
            cursor.execute(update_query, values)
            conn.commit()

            if cursor.rowcount > 0:
                recalculate_score(candidat_id)  # Recalculate the score if relevant fields are updated
                messagebox.showinfo("Success", f"Candidate with ID {candidat_id} updated successfully.")
                afficher_candidats()  # Refresh the candidate list
            else:
                messagebox.showwarning("Not Found", f"No candidate found with ID {candidat_id}.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # Confirm button
    btn_modify = tk.Button(display_frame, text="Modify Candidate", command=confirm_modify)
    btn_modify.pack(pady=20)


def delete_candidats():
    for widget in display_frame.winfo_children():
        widget.destroy()

    label_delete = tk.Label(display_frame, text="Enter Candidate ID to Delete", font=("Arial", 12))
    label_delete.pack(pady=10)

    entry_id = tk.Entry(display_frame)
    entry_id.pack(pady=5)

    def confirm_delete():
        candidat_id = entry_id.get()  # Correct variable name for candidates
        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM candidats WHERE id = ?", (candidat_id,))
            conn.commit()
            messagebox.showinfo("Delete Candidate", f"Candidate with ID {candidat_id} deleted successfully.")
            afficher_candidats()  # Refresh the candidate list
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    btn_delete = tk.Button(display_frame, text="Delete Candidate", command=confirm_delete)
    btn_delete.pack(pady=20)

def ajouter_candidat():
    for widget in display_frame.winfo_children():
        widget.destroy()

    label = tk.Label(display_frame, text="Ajouter un Candidat", font=("Arial", 12))
    label.pack(pady=10)

    entries = {}
    fields = ["Nom", "Experience", "Diplome", "Competences Techniques", "Qualites Humaines", "Mobilite"]
    for i, field in enumerate(fields):
        label_field = tk.Label(display_frame, text=field)
        label_field.pack()
        entry_field = tk.Entry(display_frame)
        entry_field.pack(pady=5)
        entries[field] = entry_field

    def categorize_candidate(score):
        # Logic for categorizing based on score
        if score >= 20:
            return "candidat sérieux"
        elif score >= 10:
            return "pourquoi pas"
        else:
            return "poubelle"

    def save_candidat():
        # Retrieve data from the form fields
        data = {field: entries[field].get() for field in fields}
        data = {k: int(v) if v.isdigit() else v for k, v in data.items()}

        # Calculate the score based on the sum of all the fields
        score = data["Experience"] + data["Diplome"] + data["Competences Techniques"] + data["Qualites Humaines"] + data["Mobilite"]
        
        # Get the category based on the score
        category = categorize_candidate(score)

        # Insert the data into the database
        conn = sqlite3.connect("recrutement.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidats (nom, experience, diplome, competences_techniques, qualites_humaines, mobilite, score, categorie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data["Nom"], data["Experience"], data["Diplome"], data["Competences Techniques"], data["Qualites Humaines"], data["Mobilite"], score, category))
        conn.commit()
        conn.close()

        # Show a success message
        messagebox.showinfo("Succès", f"Candidat {data['Nom']} ajouté avec succès!")

    # Create and pack the save button
    btn_save = tk.Button(display_frame, text="Save Candidat", command=save_candidat)
    btn_save.pack(pady=20)

import tkinter as tk
from tkinter import ttk
import sqlite3

def afficher_candidats():
    for widget in display_frame.winfo_children():
        widget.destroy()

    conn = sqlite3.connect("recrutement.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidats")
    rows = cursor.fetchall()
    conn.close()

    tree = ttk.Treeview(display_frame, columns=("ID", "Nom", "Expérience", "Diplôme", "Compétences", "Qualités", "Mobilité", "Score", "Catégorie"), show="headings")
    
    # Define headers for the tree
    headers = ["ID", "Nom", "Expérience", "Diplôme", "Compétences", "Qualités", "Mobilité", "Score", "Catégorie"]
    
    # Set up headers and columns width
    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, anchor="center", width=120)  # Adjust width as needed
    
    # Insert rows into the treeview
    for row in rows:
        tree.insert("", tk.END, values=row)
    
    # Make sure the treeview fills the interface space properly
    tree.pack(fill="both", expand=True, padx=10, pady=10)

def logout():
    root.destroy()
    subprocess.Popen(["python", "login.py"])

# Barre de menu
menu_bar = tk.Menu(root)

# Menu "Utilisateurs"
tools_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="UTILISATEURS", menu=tools_menu)
tools_menu.add_command(label="Afficher Admins", command=show_admins)
tools_menu.add_command(label="Ajouter Admin", command=add_admin)
tools_menu.add_command(label="Modifier Admin", command=modify_admin)
tools_menu.add_command(label="Supprimer Admin", command=delete_admin)

# Menu "Candidatures"
candidature_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="CANDIDATURES", menu=candidature_menu)
candidature_menu.add_command(label="Ajouter Candidat", command=ajouter_candidat)
candidature_menu.add_command(label="Afficher Candidats", command=afficher_candidats)
candidature_menu.add_command(label="Modifier Candidats", command=modify_candidatures)
candidature_menu.add_command(label="Supprimer Candidat", command=delete_candidats)

# Menu "Graphique"
graph_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="GRAPHIQUES", menu=graph_menu)
graph_menu.add_command(label="Afficher Graphique", command=afficher_graphique)

# Menu "Aide"
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="AIDE", menu=help_menu)
help_menu.add_command(label="Aide", command=show_help)
help_menu.add_command(label="À Propos", command=show_about)

# Menu "Déconnexion"
logout_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="DÉCONNEXION", menu=logout_menu)
logout_menu.add_command(label="Se Déconnecter", command=logout)

root.config(menu=menu_bar)
root.mainloop()