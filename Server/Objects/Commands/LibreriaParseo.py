
def parsear_targets(comando):
    if len(comando) == 0:
        return comando
    returneo = [comando[0]]
    for x in comando[1:]:
        try:
            returneo.append(int(x))
        except:
            if type(returneo[-1]) != int:
                returneo.append(0)
            returneo.append(x)
    if type(returneo[-1]) != int:
        returneo.append(0)
    return returneo


def count_target_object(comando):
    returneo = len(comando)
    for x in comando:
        if type(x) == int:
            returneo -= 1
    return returneo
