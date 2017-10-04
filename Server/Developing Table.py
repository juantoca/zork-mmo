from Server.Objects.Sala import Sala
from Server.Objects.Entity import Entity

from Server.Objects.Subclases.Jorl import Jorl
from Server.World_Handler import create_sala_entry

sala = Sala("Spawn", (0, 0, 0), {"NORTH": (0, 1, 0)})
sala1 = Sala("Prueba", (0, 1, 0), {"SOUTH": (0, 0, 0)})
sala.description = "ESTO ES EL SPAWN"
sala1.description = "ESTO ES LA PRUEBA"
entidad = Jorl("jorl", sala)
entidad.set_atribute("pickable", True)
sala.add_entity(entidad)
create_sala_entry(sala)
create_sala_entry(sala1)
