class Shop:
    def __init__(self):
        # Objetos disponibles en la tienda
        self.items = {
            "mejora_ataque": {"precio": 200, "bonus": 5},
            "mejora_defensa": {"precio": 150, "bonus": 3},
            "vida_extra": {"precio": 300, "bonus": 50}
        }

    def comprar(self, jugador, item):
        """El jugador compra mejoras si tiene dinero suficiente"""
        if item in self.items:
            if jugador.money >= self.items[item]["precio"]:
                jugador.money -= self.items[item]["precio"]

                if item == "mejora_ataque":
                    jugador.attack += self.items[item]["bonus"]
                elif item == "mejora_defensa":
                    jugador.defense += self.items[item]["bonus"]
                elif item == "vida_extra":
                    jugador.hp += self.items[item]["bonus"]

                print(f"✅ {item} comprado con éxito.")
            else:
                print("❌ No tienes suficiente dinero.")
