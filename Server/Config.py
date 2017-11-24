import glob
from logging import warning, info


class Languages:

    def __init__(self, root="./Langs/*"):
        """
        Carga todos los idiomas en un directorio dado
        :param root: Directorio donde buscar
        """
        self.languages = {}
        files = glob.glob(root)
        for x in files:
            idioma = x.split("/")[-1]
            info("Cargando idioma: " + idioma)
            self.languages[idioma] = Archivo(x)

    def get_option(self, option, language, advise_non_availability=True):
        """
        Obtiene el valor de un token de idioma
        :param option: Opción a obtener
        :param language: Lenguaje a consultar
        :param advise_non_availability: Si no existe el criteio de búsqueda, ¿debo notificarlo por pantalla?
        :return: Traducción del token o "UNTRANSLATED_TOKEN "+token si no se ha encontrado
        """
        try:
            return self.languages[language].get_option(option)
        except KeyError:
            if advise_non_availability:
                warning("El token de idioma \""+option+"\" no esta traducido para el idioma \""+language+"\"")
            return "UNTRANSLATED_TOKEN "+option

    def get_languages(self):
        """
        Obtiene la lista de lenguajes
        :return: Lista de strings de lenguaje
        """
        lista = list(self.languages.keys())
        returneo = []
        for x in lista:
            if "HIDDEN" not in x:
                returneo.append(x)
        return returneo


class Archivo:

    def __init__(self, entrada):
        """
        Carga un archivo de configuración
        :param entrada: Archivo a cargar
        """
        self.data = {}
        with open(entrada, "r") as f:
            arch = f.readlines()
            working = ""
            for linea in arch:
                if linea == "\n" or linea[0] == "#":
                    continue
                if "=" in linea:
                    tmp = linea.split("=")
                    working = tmp[0].strip(" ")
                    if working in self.data:
                        raise ValueError("Corrupted file. Key " + working + " repeated")
                    self.data[working] = tmp[1].split("\n")[0].strip(" ")
                else:
                    self.data[working] += "\n" + linea.split("\n")[0]

    def get_option(self, option):
        """
        Obtiene una opción del archivo
        :param option: Opción a obtener
        :return: Valor de la petición
        """
        return self.data[option]

    def set_option(self, option, value):
        """
        Escribe en una opción del archivo(no lo guarda en disco)
        :param option: Opción a modificar
        :param value: Valor a escribir
        """
        self.data[option] = value


if __name__ == "__main__":
    idiomas = Languages()
    print(idiomas.get_option("descripcion", "es_ES"))
