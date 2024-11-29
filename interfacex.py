import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

# Function to show admins
def show_admins():
    messagebox.showinfo("afficher admins", "Displaying all admins.")
# Function to add an admin
def add_admin():
    messagebox.showinfo("Aajouter Admins", "Adding a new admin.")

# Function to delete an admin
def delete_admin():
    messagebox.showinfo("supprimer Admins", "Deleting an admin.")
def show_about():
    messagebox.showinfo("HELP", "Cette application de gestion de recrutement aide à simplifier le processus de recrutement en permettant aux utilisateurs d'ajouter, d'évaluer et de gérer efficacement les candidats. Les utilisateurs peuvent saisir les informations des candidats, calculer des scores basés sur des critères clés, et suivre les performances globales. Conçue pour soutenir les équipes de recrutement, cette application offre une interface simple pour maintenir une base de données de candidats et visualiser les scores d’évaluation")
def show_help():
    messagebox.showinfo("ABOUT", "Pour utiliser l'application, commencez par entrer les informations d'un candidat, puis cliquez sur 'Ajouter Candidat'. Vous pouvez modifier les détails en sélectionnant un candidat et en utilisant le bouton 'Modifier Candidat'. Pour visualiser les scores des candidats dans un graphique, allez dans le menu 'Outils' et sélectionnez 'Afficher Graphique'. Pour vous déconnecter ou accéder à d'autres options administratives, explorez le menu 'Outils'. En cas de problème, assurez-vous que tous les champs sont correctement remplis ou contactez le support")
# Function to evaluate candidates
def evaluate_candidate(data):
    score = (
        data["experience"] * 4 +
        data["diplome"] * 3 +
        data["competences_techniques"] * 5 +
        data["qualites_humaines"] * 4 +
        data["mobilite"] * 2
    )
    if score >= 20:
        return score, "Candidat sérieux"
    elif score >= 15:
        return score, "Pourquoi pas"
    else:
        return score, "poubelle"

# Function to add a candidate to the database
def ajouter_candidat():
    nom = entry_nom.get()
    experience = int(entry_experience.get())
    diplome = int(entry_diplome.get())
    competences_techniques = int(entry_competences_techniques.get())
    qualites_humaines = int(entry_qualites_humaines.get())
    mobilite = int(entry_mobilite.get())

    data = {
        "experience": experience,
        "diplome": diplome,
        "competences_techniques": competences_techniques,
        "qualites_humaines": qualites_humaines,
        "mobilite": mobilite
    }
    score, categorie = evaluate_candidate(data)

    conn = sqlite3.connect("recrutement.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO candidats (nom, experience, diplome, competences_techniques, qualites_humaines, mobilite, score, categorie)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nom, experience, diplome, competences_techniques, qualites_humaines, mobilite, score, categorie))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Succès", f"Candidat {nom} ajouté avec succès!")
    afficher_candidats()

# Function to display candidates in a scrollable table
def afficher_candidats():
    for widget in frame_tableau.winfo_children():
        widget.destroy()

    conn = sqlite3.connect("recrutement.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidats")
    rows = cursor.fetchall()
    conn.close()

    canvas = tk.Canvas(frame_tableau)
    scrollbar = ttk.Scrollbar(frame_tableau, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    headers = ["ID", "Nom", "Expérience", "Diplôme", "Compétences", "Qualités", "Mobilité", "Score", "Catégorie"]
    for j, header_text in enumerate(headers):
        header = tk.Label(scrollable_frame, text=header_text, borderwidth=1, relief="solid", padx=5, pady=5, bg="#cce7ff")
        header.grid(row=0, column=j, sticky="nsew")

    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            cell = tk.Label(scrollable_frame, text=value, borderwidth=1, relief="solid", padx=5, pady=5, bg="#f0f0f0")
            cell.grid(row=i, column=j, sticky="nsew")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Function to show a separate graph window
def afficher_graphique():
    conn = sqlite3.connect("recrutement.db")
    df = pd.read_sql_query("SELECT nom, score FROM candidats", conn)
    conn.close()

    plt.figure(figsize=(10, 5))
    plt.bar(df["nom"], df["score"], color="skyblue")
    plt.xlabel("Candidats")
    plt.ylabel("Score")
    plt.title("Évaluation des Candidats")
    plt.show()

# Function to update a candidate's information
def modifier_candidat():
    candidate_id = entry_id.get()
    nom = entry_nom.get()
    experience = int(entry_experience.get())
    diplome = int(entry_diplome.get())
    competences_techniques = int(entry_competences_techniques.get())
    qualites_humaines = int(entry_qualites_humaines.get())
    mobilite = int(entry_mobilite.get())

    data = {
        "experience": experience,
        "diplome": diplome,
        "competences_techniques": competences_techniques,
        "qualites_humaines": qualites_humaines,
        "mobilite": mobilite
    }
    score, categorie = evaluate_candidate(data)

    conn = sqlite3.connect("recrutement.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE candidats
        SET nom = ?, experience = ?, diplome = ?, competences_techniques = ?, qualites_humaines = ?, mobilite = ?, score = ?, categorie = ?
        WHERE id = ?
    ''', (nom, experience, diplome, competences_techniques, qualites_humaines, mobilite, score, categorie, candidate_id))
    conn.commit()
    conn.close()

    messagebox.showinfo("Succès", f"Candidat {nom} modifié avec succès!")
    afficher_candidats()

# Logout function to return to login page
def logout():
    root.destroy()
    subprocess.Popen(["python", "login.py"])

# GUI setup with Tkinter
root = tk.Tk()
root.title("Système de Recrutement")
root.geometry("800x800")
root.configure(bg="#e1f0ff")

main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(fill="both", expand=True)

frame_entrer = ttk.LabelFrame(main_frame, text="Informations du Candidat", padding="10 10 10 10")
frame_entrer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

ttk.Label(frame_entrer, text="ID").grid(row=0, column=0, sticky="w")
entry_id = ttk.Entry(frame_entrer)
entry_id.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_entrer, text="Nom").grid(row=1, column=0, sticky="w")
entry_nom = ttk.Entry(frame_entrer)
entry_nom.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_entrer, text="Expérience").grid(row=2, column=0, sticky="w")
entry_experience = ttk.Entry(frame_entrer)
entry_experience.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_entrer, text="Diplôme").grid(row=3, column=0, sticky="w")
entry_diplome = ttk.Entry(frame_entrer)
entry_diplome.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame_entrer, text="Compétences Techniques").grid(row=4, column=0, sticky="w")
entry_competences_techniques = ttk.Entry(frame_entrer)
entry_competences_techniques.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(frame_entrer, text="Qualités Humaines").grid(row=5, column=0, sticky="w")
entry_qualites_humaines = ttk.Entry(frame_entrer)
entry_qualites_humaines.grid(row=5, column=1, padx=5, pady=5)

ttk.Label(frame_entrer, text="Mobilité").grid(row=6, column=0, sticky="w")
entry_mobilite = ttk.Entry(frame_entrer)
entry_mobilite.grid(row=6, column=1, padx=5, pady=5)

frame_buttons = ttk.Frame(main_frame)
frame_buttons.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

btn_ajouter = ttk.Button(frame_buttons, text="Ajouter Candidat", command=ajouter_candidat)
btn_ajouter.grid(row=0, column=0, padx=5, pady=5)

btn_modifier = ttk.Button(frame_buttons, text="Modifier Candidat", command=modifier_candidat)
btn_modifier.grid(row=0, column=1, padx=5, pady=5)

# Frame for the candidate table with scrollable view
frame_tableau = ttk.LabelFrame(main_frame, text="Liste des Candidats", padding="10 10 10 10")
frame_tableau.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

# Ensure the frame expands correctly with window resizing
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Create the menu bar
menu_bar = tk.Menu(root)

# Add the 'Tools' menu
tools_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="USERS", menu=tools_menu)

# Add the 'Admin' submenu under 'Tools'
admin_menu = tk.Menu(tools_menu, tearoff=0)
tools_menu.add_cascade(label="ADMIN", menu=admin_menu)

# Add options under the 'Admin' submenu
admin_menu.add_command(label="Afficher Admins", command=show_admins)
admin_menu.add_command(label="Ajouter Admins", command=add_admin)
admin_menu.add_command(label="supprimer Admins", command=delete_admin)
# Add the 'Tools' menu

tools_menu2 = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="AFFICHER", menu=tools_menu2)
# Add 'Afficher Graphique' under 'Tools' menu
tools_menu2.add_command(label="Affichage Graphique", command=afficher_graphique)

tools_menu3 = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="HELP", menu=tools_menu3)
# Add 'about and help' under 'HELP' menu
tools_menu3.add_command(label="HELP", command=show_help)
tools_menu3.add_command(label="ABOUT", command=show_about)
# deconnexion
tools_menu4 = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="LOGOUT", menu=tools_menu4)
tools_menu4.add_command(label="DECONNEXION", command=logout)
# Configure the menu bar
root.config(menu=menu_bar)

# Display initial candidate list in the scrollable table
afficher_candidats()

# Run the application
root.mainloop()

