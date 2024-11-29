import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import subprocess

# Fonction pour connecter l'utilisateur
def connexion():
    utilisateur = entree_utilisateur.get()
    mot_de_passe = entree_mot_de_passe.get()

    # Hachage du mot de passe entré pour correspondre au hash stocké
    mot_de_passe_hache = hashlib.sha256(mot_de_passe.encode()).hexdigest()

    # Connexion à la base de données
    conn = sqlite3.connect("recrutement.db")
    cursor = conn.cursor()

    # Vérification si l'utilisateur existe et si le mot de passe correspond
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (utilisateur, mot_de_passe_hache))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Connexion", "Connexion réussie !")
        root.destroy()  # Fermer la fenêtre de connexion
        subprocess.Popen(["python", "interface.py"])  # Ouvrir interface.py après une connexion réussie
    else:
        messagebox.showerror("Échec de la connexion", "Nom d'utilisateur ou mot de passe incorrect.")

    # Fermeture de la connexion à la base de données
    conn.close()

# Création de la fenêtre de connexion
root = tk.Tk()
root.title("Connexion")
root.geometry("300x300")

# Étiquette et champ pour le nom d'utilisateur
etiquette_utilisateur = tk.Label(root, text="Nom d'utilisateur")
etiquette_utilisateur.pack(pady=5)
entree_utilisateur = tk.Entry(root)
entree_utilisateur.pack(pady=5)

# Étiquette et champ pour le mot de passe
etiquette_mot_de_passe = tk.Label(root, text="Mot de passe")
etiquette_mot_de_passe.pack(pady=5)
entree_mot_de_passe = tk.Entry(root, show="*")
entree_mot_de_passe.pack(pady=5)

# Bouton de connexion
btn_connexion = tk.Button(root, text="Se connecter", command=connexion)
btn_connexion.pack(pady=10)

# Lancement de l'interface de connexion
root.mainloop()
