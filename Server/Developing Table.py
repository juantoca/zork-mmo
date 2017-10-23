from Server.Objects.Sala import Sala
from Server.Objects.Subclases.Container import Container
from Server.World_Handler import create_sala_entry

sala = Sala("Spawn", (0, 0, 0), {})
sala.set_atribute("description", "ESTO ES EL SPAWN")

jorl = Container("coco", "jorl")
jorl.set_atribute("pickable", True)
jorl.set_atribute("description", "Mah little dommy")

contenedor = Container("jorl", "jorl")
contenedor.set_atribute("description", "ESTO ES UN CONTENEDOR")

sala.add_entity(contenedor)
sala.add_entity(jorl)

create_sala_entry(sala)
