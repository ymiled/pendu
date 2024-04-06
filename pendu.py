from tkinter import *
from tkinter import Menu, Menubutton, simpledialog, messagebox
from tkinter import colorchooser
from random import randint
from formes import *

class FenPrincipale(Tk):
	def __init__(self):
		Tk.__init__(self)

		# configuration de la fenêtre
		self.title('Jeu du pendu')
		self.geometry('700x650+400+50')

		# Affichage du pseudo et de l'historique une fois sélectionné:

		self.__pseudo = ""


		self.__historique = {"Pseudo": self.__pseudo, "scores":[]}
		self.__historique_text = StringVar()
		self.__historique_text.set('Sélectionner un joueur')

		self.__bPlayer_historique = Label(self, textvariable=self.__historique_text, fg='black')
		self.__bPlayer_historique.pack(side=TOP, padx=10, pady=10)
		self.__bPlayer_historique.config(font=("Consolas",12))



		# Touches du haut
		self.__bBox = Frame(self,bg='#eeeeee')
		self.__bBox.pack(side=TOP, padx=10, pady=10)

		self.__bNewGame = Button(self.__bBox, text=' Nouvelle partie ', bg='#884400', fg='white')
		self.__bNewGame.pack(side=LEFT, padx=5, pady=0)
		self.__bNewGame.config(state=DISABLED)
		
		self.__bQuit = Button(self.__bBox, text=' Quitter ', bg='#884400', fg='white')
		self.__bQuit.pack(side=LEFT, padx=5, pady=0)

		self.__bUndo = Button(self.__bBox, text='Undo', bg='#884400', fg='white')
		self.__bUndo.pack(side=LEFT, padx=5, pady=0)
		self.__bUndo.config(command=self.revenir_arriere, state=DISABLED)

		self.__menu_couleurs = Menubutton(self.__bBox, text="Choisir une couleur", bg='#884400', fg='white')
		self.__menu_couleurs.pack(side=LEFT, padx=10, pady=0)

		parametre_couleurs = Menu(self.__menu_couleurs)
		parametre_couleurs.add_command(label = 'Couleur de la zone affichage', activebackground='darkorange', command = self.changer_couleur_zone_affichage)
		parametre_couleurs.add_command(label = "Couleur du fond",activebackground='darkorange', command = self.changer_couleur_fond)
		parametre_couleurs.add_command(label = "Couleur des touches",activebackground='darkorange', command = self.changer_couleur_touches)

		self.__menu_couleurs.config(menu=parametre_couleurs)


		self.__bPseudo = Menubutton(self.__bBox, text='Sélectionner un pseudo', bg='#884400', fg='white')
		self.__bPseudo.pack(side=LEFT, padx=5, pady=0)
		self.charger_pseudos()
		self.__menu_pseudos = Menu(self.__bPseudo)

		for name in self.__pseudo_enregistres:
			name.strip('\n')
			def make_function(pseudo=name):
				def fonction():
					self.set_pseudo(pseudo)
					self.get_historique_joueur(pseudo)
					self.sauvegarder_historique(pseudo)
					self.sauvegarder_pseudo()
					self.affiche_details_joueur()
					self.__bNewGame.config(state=NORMAL)
					self.griserClavier()
					self.__bUndo.config(state=DISABLED)
				return fonction()

			
			self.__menu_pseudos.add_command(label=name, command=make_function)

		self.__bPseudo.config(menu=self.__menu_pseudos)

		self.__bBeginner = Button(self.__bBox, text='Creer un pseudo', bg='#884400', fg='white')
		self.__bBeginner.pack(side=LEFT, padx=5, pady=5)
		self.__bBeginner.config(command=self.demander_pseudo)

		# mise en place du comportement des touches ded contrôle
		self.__bQuit.config(command=self.destroy)
		self.__bNewGame.config(command=self.nouvellePartie)
		
		# Zone de dessin
		self.__pendu = ZoneAffichage(self, width=480, height=380, bg='#aaaaaa')
		self.__pendu.pack(side=TOP, padx=10, pady=0)
		
		# Mot à trouver
		self.__displayText = StringVar()
		self.__displayText.set('Sélectionner "Nouvelle Partie"')
		self.__display = Label(self,  textvariable=self.__displayText)
		self.__display.config(font=("Consolas",12))
		self.__display.pack(side=TOP, padx=5, pady=5)

		# Clavier
		self.__kbd = Frame(self,bg='#eeeeee')
		self.__kbd.pack(side=TOP, padx=10, pady=(0,10))
		
		self.__touches = []
		for i in range(26):
			t = MonBoutonLettre(self.__kbd, text=chr(ord('A')+i) , width=7, bg='#cccccc')
			t.grid(column=i%7 + (1 if i>20 else 0), row=i//7, padx=2, pady=2)
			t.config(state=DISABLED, command=self.traitement)
			self.__touches.append(t)

		# Touches du clavier sélectionnées :
		self.__selected_letters = []

		# Nombre d'erreurs:
		self.__erreurs = 0
		
		# Lecture du fichier de mots
		f = open('mots.txt', 'r')
		s = f.read()
		self.__mots = s.split('\n')
		f.close()

	
	def nouvellePartie(self):
		# nouveau mot à trouver
		self.__motMystere = self.__mots[randint(0,len(self.__mots))]
		self.__motCache = '*'*len(self.__motMystere)
		self.afficheMot()
		
		# On calcule le nombre de caractères trouvés pour pouvoir calculer le score
		self.__caracteres_trouves = 0


		# réactivation des touches du clavier
		for t in self.__touches:
			t.config(state=NORMAL)
			
		# effacement du pendu
		self.__erreurs = 0
		self.__pendu.tracer(0)

		# Score :
		self.__historique["scores"].append(0.0)
			
	def afficheMot(self):
		self.__displayText.set('Mot à trouver : ' + self.__motCache)

		
	def traitement(self,lettre):
		
		if self.__erreurs >= 0:
			self.__bUndo.config(state=NORMAL)
		# mise à jour du mot caché (contenant les *)
		nouveauMotCache = ''
		for i,c in enumerate(self.__motMystere):
			if c == lettre:
				nouveauMotCache += lettre
				self.__caracteres_trouves += 1
			else:
				nouveauMotCache += self.__motCache[i]		
	
		# nombre d'erreurs et mise à jour du pendu
		if self.__motCache == nouveauMotCache:
			self.__erreurs += 1
			self.affiche_details_joueur()
			self.__pendu.tracer(self.__erreurs)

		# affichage du mot caché mis à jour
		self.__motCache = nouveauMotCache
		self.afficheMot()
			
		# a-t-on gagné ?
		if not '*' in self.__motCache:
			self.partieGagnee()
		
		# a-t-on perdu ?
		if self.__erreurs > 9:
			self.partiePerdue()


		# Mise à jour de l'affichage des données sur le joueur
		self.__historique['scores'][-1] = "{:.2f}".format(self.__caracteres_trouves/len(self.__motCache))  # on se limite à deux chiffres après la virgule

		self.sauvegarder_historique(self.__pseudo)
		self.get_historique_joueur(self.__pseudo)
		self.affiche_details_joueur()
			
	def partieGagnee(self):
		self.__displayText.set('Gagné ! Le mot était: '+self.__motCache)
		self.griserClavier()
	
	def partiePerdue(self):
		self.__displayText.set('Perdu ! Le mot était: '+self.__motMystere)
		self.griserClavier()
		self.__bUndo.config(state=DISABLED)
	
	def griserClavier(self):
		for t in self.__touches:
			t.config(state=DISABLED)

	def ouvrir_menu_couleurs(self):
		menu = Toplevel(self)
		menu.geometry('300x500+50+50')
		menu.title('Paramètres de couleur')

		def changer_couleur():
			couleur = colorchooser.askcolor()
			if couleur[1]:
				self.configure(background=couleur[1])
			
			bg_button = Button(menu, text='Couleur de fond', command=changer_couleur)
			bg_button.pack(padx=10, pady=5)


	def changer_couleur_zone_affichage(self):
		color = colorchooser.askcolor(title='Choisissez votre couleur')[1] #le deuxieme([1]) paramètre donne la couleur (red, ...)
		self.__pendu.config(bg=color)

	def changer_couleur_fond(self):
		couleur = colorchooser.askcolor(title='Choisir la couleur du dessin')[1]
		self.config(bg=couleur)
		self.__bBox.config(bg=couleur)
		self.__kbd.config(bg=couleur)

	def changer_couleur_touches(self):
		couleur = colorchooser.askcolor(title='Choisir la couleur du dessin')[1]
		buttons = [self.__bQuit, self.__bNewGame, self.__bUndo, self.__menu_couleurs, self.__bPseudo]
		for b in buttons:
			b.config(bg=couleur)

	
	def revenir_arriere(self):
		if self.__erreurs != 0 and self.__erreurs < 10:
			self.__pendu.get_items()[self.__erreurs - 1].set_state('hidden')
			self.__erreurs -= 1
			self.__historique['scores'][-1] = "{:.2f}".format(self.__caracteres_trouves/len(self.__motCache))
			if self.__selected_letters != []:  # Ici on déselectionne la dernière lettre utilisée, on la remettant active
				touche = self.__selected_letters[-1] 
				touche.config(state=NORMAL)
				self.__selected_letters.pop()

		self.affiche_details_joueur()

	def add_to_selected_letters(self, touche):
		self.__selected_letters.append(touche)
	
	def get_selected_letters(self):
		return self.__selected_letters
	
	# Charger le fichier des joueurs :
	def charger_pseudos(self):
		try:
			with open('pseudo.txt', 'r') as file:
				self.__pseudo_enregistres = (file.read().split('\n'))
				#self.__pseudo_enregistres.remove(' ') 

		except FileNotFoundError:
			return self.demander_pseudo()
		
	def demander_pseudo(self):
		pseudo = simpledialog.askstring("Pseudo", "Saisissez un pseudo")
			
		# Mise à jour dans le menu des pseudo pour rajouter le nouveau surnom :
		def mise_a_jour():
			self.set_pseudo(pseudo)
			self.get_historique_joueur(pseudo)
			self.sauvegarder_historique(pseudo)
			self.affiche_details_joueur()
			self.__bNewGame.config(state=NORMAL)

		# on vérifie qu'il n'existe pas déjà
		if pseudo not in self.__pseudo_enregistres:
			self.set_pseudo(pseudo)
			self.creer_historique_nouveau(pseudo)
			self.affiche_details_joueur()
			self.sauvegarder_pseudo()
			self.__bNewGame.config(state=NORMAL)
			self.__menu_pseudos.add_command(label=pseudo, command=mise_a_jour)
		
		if pseudo in self.__pseudo_enregistres:
			messagebox.showerror("Erreur", "Le pseudo existe déjà")

		self.__historique['Pseudo'] = pseudo
	
		return pseudo
	
	def creer_historique_nouveau(self, pseudo):
		self.__historique = {'Pseudo': pseudo, 'scores': []}
		with open('historique.txt', 'a') as file:
			file.write(self.historique_to_string()+'\n')

	
	def get_historique_joueur(self, pseudo):
		try:
			with open('historique.txt', 'r') as file:
				for line in file:
					infos = line.split(", ")
					if infos[0].split(":")[1].strip() == pseudo in line:
						self.__historique["Pseudo"] = pseudo
						scores_info = infos[1].split(":")[1].strip().split(" ")
						self.__historique["scores"] = [float(score) for score in scores_info]			
		except FileNotFoundError:
			pass
	
	
	def sauvegarder_pseudo(self):
		with open('pseudo.txt', 'a') as file:  # 'a' signifie qu'on écrit en ajoutant au fichier .txt
			if not self.__pseudo in self.__pseudo_enregistres:
				file.write(self.__pseudo+'\n')
			
	def sauvegarder_historique(self, joueur):
		lignes_modifiees = []
		with open('historique.txt', 'r') as file:
			for ligne in file:
				infos = ligne.split(", ")
				if infos[0].split(":")[1].strip() == joueur:
					scores = ''
					for score in self.__historique['scores']:
						scores += str(score) + ' '
					lignes_modifiees.append(
						f"Pseudo: {self.__historique['Pseudo']}, scores: {scores}"+ "\n"
					)
				else:
					lignes_modifiees.append(ligne)
		
		with open('historique.txt', 'w') as file:
			file.writelines(lignes_modifiees)

	def affiche_details_joueur(self):
		self.__historique_text.set(self.historique_to_string())

	def historique_to_string(self):
		# on n'affiche pas sous forme de liste, mais plutôt sous forme des nombres qui se suivent 
		scores = ''
		for score in self.__historique['scores']:
			scores += str(score) + ' '

		return f"Pseudo: {self.__historique['Pseudo']}, scores: {scores}"
	
	def set_pseudo(self, pseudo):
		self.__pseudo = pseudo
		self.affiche_details_joueur()

			
class ZoneAffichage(Canvas):

	def __init__(self,*args,**kwargs):
		# on appelle le constructeur de la classe mère avec la même liste
		# d'arguments (args) et les mêmes arguments nommés (kwargs) que
		# ceux qu'on a nous-même reçus...
		# args est une liste, kwargs est un dico
		Canvas.__init__(self, *args, **kwargs)
	
		self.__items = []
		
		# Base, Poteau, Traverse, Corde
		self.__items.append(Rectangle(self, 50,  270, 200,  26, "saddlebrown"))
		self.__items.append(Rectangle(self, 87,   83,  26, 200, "saddlebrown"))
		self.__items.append(Rectangle(self, 87,   70, 150,  26, "saddlebrown"))
		self.__items.append(Rectangle(self, 188,  67,  5,  60, "orange"))

		# Tete, Tronc
		self.__items.append(Ellipse(self, 198, 125,  15,  15, "red"))
		self.__items.append(Rectangle(self, 175, 143,  26,  60, "black"))

		# Bras gauche et droit
		self.__items.append(Rectangle(self, 133, 150,  40, 10, "pink"))
		self.__items.append(Rectangle(self, 203, 150,  40,  10, "pink"))

		# Jambes gauche et droite
		self.__items.append(Rectangle(self, 175, 205,  10,  40, "navy"))
		self.__items.append(Rectangle(self, 191, 205,  10,  40, "navy"))

		self.changer_couleur_items("yellow")

		# on recentre le pendu
		for i in self.__items:
			i.deplacement(80,0)

	def tracer(self,n):
		for i in range(10):
			s = 'normal' if i < n else 'hidden'
			self.__items[i].set_state(s)
			self.__items[i].set_color("blue")

	def changer_couleur_items(self, couleur):
		poub = []
		for f in self.__items:
			f.set_color(couleur)

	def get_items(self):
		return self.__items

class MonBoutonLettre(Button):
	def __init__(self,*args,**kwargs):
		Button.__init__(self, *args, **kwargs)
		self.config(**kwargs)
		
	def config(self,**kwargs):
		Button.config(self, **kwargs)
		if 'text' in kwargs:
			self.__lettre = kwargs['text']
		if 'command' in kwargs:
			self.__command = kwargs['command'] # la commande ici sera traitement()
			Button.config(self, command=self.cliquer)
		
			
	def cliquer(self):
		self.config(state=DISABLED)
		self.__command(self.__lettre)
		fenetre = self.winfo_toplevel()   # on accède à la fenêtre d'où vient le frame d'où vient le boutton
		fenetre.add_to_selected_letters(self)

if __name__ == '__main__':
	fen = FenPrincipale()
	fen.mainloop()
