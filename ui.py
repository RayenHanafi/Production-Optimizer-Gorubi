from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from solver import SolverThread


class ProductionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimisation de Production (Gurobi + PyQt) - Version Avancée")
        self.setGeometry(100, 100, 1000, 700)
        
        # Apply dark blue theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a1929;
            }
            QWidget {
                background-color: #0a1929;
                color: #b8d4f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13pt;
            }
            QLabel {
                color: #7ba8d1;
                font-weight: 500;
            }
            QTableWidget {
                background-color: #132f4c;
                alternate-background-color: #1a3a52;
                border: 2px solid #2196f3;
                border-radius: 8px;
                gridline-color: #1e4976;
                color: #b8d4f0;
                selection-background-color: #1976d2;
                padding: 5px;
                font-size: 12pt;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #1976d2;
                color: white;
            }
            QHeaderView::section {
                background-color: #1565c0;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2196f3;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
            QPushButton#solveButton {
                background-color: #0d47a1;
                font-size: 12pt;
                padding: 15px;
                min-height: 45px;
            }
            QPushButton#solveButton:hover {
                background-color: #1565c0;
            }
            QPushButton#addButton {
                background-color: #1976d2;
            }
            QPushButton#delButton {
                background-color: #424242;
            }
            QPushButton#delButton:hover {
                background-color: #616161;
            }
            QMessageBox {
                background-color: #132f4c;
                color: #e3f2fd;
            }
            QMessageBox QLabel {
                color: #e3f2fd;
            }
            QMessageBox QPushButton {
                background-color: #1976d2;
                min-width: 80px;
            }
        """)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(25, 25, 25, 25)

        # --- Section ressources ---
        title_ressources = QLabel("<h2>Ressources disponibles</h2>")
        title_ressources.setStyleSheet("color: #64b5f6; font-size: 16pt; font-weight: bold;")
        self.layout.addWidget(title_ressources)
        
        self.table_ressources = QTableWidget(2, 2)
        self.table_ressources.setHorizontalHeaderLabels(["Ressource", "Disponibilité"])
        self.table_ressources.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ressources.setAlternatingRowColors(True)
        self.layout.addWidget(self.table_ressources)

        # Valeurs initiales
        self.table_ressources.setItem(0, 0, QTableWidgetItem("Essence"))
        self.table_ressources.setItem(0, 1, QTableWidgetItem("100"))
        self.table_ressources.setItem(1, 0, QTableWidgetItem("Additif"))
        self.table_ressources.setItem(1, 1, QTableWidgetItem("90"))

        # Boutons ressources
        btn_r_layout = QHBoxLayout()
        btn_r_layout.setSpacing(10)
        btn_add_r = QPushButton("➕ Ajouter Ressource")
        btn_add_r.setObjectName("addButton")
        btn_del_r = QPushButton("➖ Supprimer Ressource")
        btn_del_r.setObjectName("delButton")
        btn_add_r.clicked.connect(self.add_resource)
        btn_del_r.clicked.connect(self.del_resource)
        btn_r_layout.addWidget(btn_add_r)
        btn_r_layout.addWidget(btn_del_r)
        self.layout.addLayout(btn_r_layout)

        # --- Section produits ---
        title_produits = QLabel("<h2>Produits</h2>")
        title_produits.setStyleSheet("color: #64b5f6; font-size: 16pt; font-weight: bold; margin-top: 10px;")
        self.layout.addWidget(title_produits)
        
        self.table_produits = QTableWidget(2, 3)
        self.table_produits.setHorizontalHeaderLabels(["Produit", "Profit", "Besoins par ressource"])
        self.table_produits.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_produits.setAlternatingRowColors(True)
        self.layout.addWidget(self.table_produits)

        # Valeurs initiales
        self.table_produits.setItem(0, 0, QTableWidgetItem("A"))
        self.table_produits.setItem(0, 1, QTableWidgetItem("50"))
        self.table_produits.setItem(0, 2, QTableWidgetItem("2,4"))
        self.table_produits.setItem(1, 0, QTableWidgetItem("B"))
        self.table_produits.setItem(1, 1, QTableWidgetItem("40"))
        self.table_produits.setItem(1, 2, QTableWidgetItem("3,3"))

        # Boutons produits
        btn_p_layout = QHBoxLayout()
        btn_p_layout.setSpacing(10)
        btn_add_p = QPushButton("➕ Ajouter Produit")
        btn_add_p.setObjectName("addButton")
        btn_del_p = QPushButton("➖ Supprimer Produit")
        btn_del_p.setObjectName("delButton")
        btn_add_p.clicked.connect(self.add_product)
        btn_del_p.clicked.connect(self.del_product)
        btn_p_layout.addWidget(btn_add_p)
        btn_p_layout.addWidget(btn_del_p)
        self.layout.addLayout(btn_p_layout)

        # --- Bouton de calcul ---
        self.btn_solve = QPushButton("Résoudre avec Gurobi")
        self.btn_solve.setObjectName("solveButton")
        self.btn_solve.clicked.connect(self.solve_problem)
        self.layout.addWidget(self.btn_solve)

        # --- Résultats ---
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            color: #90caf9;
            font-size: 12pt;
            background-color: #132f4c;
            border: 2px solid #1976d2;
            border-radius: 10px;
            padding: 20px;
            margin-top: 10px;
        """)
        self.layout.addWidget(self.result_label)

    # ----------------- Fonctions pour gérer les tables -----------------
    def add_product(self):
        if self.table_produits.rowCount() >= 10:
            QMessageBox.warning(self, "Limite atteinte", "Maximum 10 produits autorisés.")
            return
        row = self.table_produits.rowCount()
        self.table_produits.insertRow(row)
        self.table_produits.setItem(row, 0, QTableWidgetItem(f"P{row+1}"))
        self.table_produits.setItem(row, 1, QTableWidgetItem("0"))
        self.table_produits.setItem(row, 2, QTableWidgetItem(""))

    def del_product(self):
        if self.table_produits.rowCount() > 1:
            self.table_produits.removeRow(self.table_produits.rowCount() - 1)

    def add_resource(self):
        if self.table_ressources.rowCount() >= 10:
            QMessageBox.warning(self, "Limite atteinte", "Maximum 10 ressources autorisées.")
            return
        row = self.table_ressources.rowCount()
        self.table_ressources.insertRow(row)
        self.table_ressources.setItem(row, 0, QTableWidgetItem(f"R{row+1}"))
        self.table_ressources.setItem(row, 1, QTableWidgetItem("0"))

    def del_resource(self):
        if self.table_ressources.rowCount() > 1:
            self.table_ressources.removeRow(self.table_ressources.rowCount() - 1)

    # ----------------- Lecture des données et lancement solveur -----------------
    def solve_problem(self):
        try:
            produits, profit, ressources, besoins, disponibilite = self.read_tables()

            self.thread = SolverThread(produits, profit, ressources, besoins, disponibilite)
            self.thread.result_ready.connect(self.display_results)
            self.thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def read_tables(self):
        produits = []
        profit = {}
        ressources = []
        besoins = {}
        disponibilite = {}

        # Lecture ressources
        for i in range(self.table_ressources.rowCount()):
            r = self.table_ressources.item(i, 0).text()
            ressources.append(r)
            disponibilite[r] = float(self.table_ressources.item(i, 1).text())

        # Lecture produits
        for i in range(self.table_produits.rowCount()):
            p = self.table_produits.item(i, 0).text()
            produits.append(p)
            profit[p] = float(self.table_produits.item(i, 1).text())

            besoin_vals = [float(v) for v in self.table_produits.item(i, 2).text().split(",")]
            if len(besoin_vals) != len(ressources):
                raise Exception("Le nombre de besoins doit correspondre au nombre de ressources.")
            for j, r in enumerate(ressources):
                besoins[(p, r)] = besoin_vals[j]

        return produits, profit, ressources, besoins, disponibilite

    # ----------------- Affichage des résultats -----------------
    def display_results(self, solution, obj_val):
        if not solution:
            self.result_label.setText("<b>❌ Aucune solution trouvée.</b>")
            return

        text = "<h3>✅ Solution optimale :</h3><br>"
        for p, val in solution.items():
            text += f"<b>{p}</b> = {val:.2f}<br>"
        text += f"<br><b style='color: #4fc3f7; font-size: 14pt;'>💰 Profit total : {obj_val:.2f}</b>"
        self.result_label.setText(text)

        # Set matplotlib dark theme
        plt.style.use('dark_background')
        plt.figure(figsize=(8, 5))
        bars = plt.bar(solution.keys(), solution.values(), color='#42a5f5', edgecolor='#1976d2', linewidth=2)
        plt.title("Quantités optimales produites", fontsize=14, fontweight='bold', color='#90caf9')
        plt.xlabel("Produits", fontsize=12, color='#90caf9')
        plt.ylabel("Quantité", fontsize=12, color='#90caf9')
        plt.grid(True, axis='y', linestyle='--', alpha=0.3, color='#1976d2')
        plt.tight_layout()
        
        # Style the plot
        ax = plt.gca()
        ax.set_facecolor('#0a1929')
        ax.spines['bottom'].set_color('#1976d2')
        ax.spines['left'].set_color('#1976d2')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#90caf9')
        
        plt.show()