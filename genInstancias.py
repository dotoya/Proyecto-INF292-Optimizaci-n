import os
import random

def genInstancias(tipo, numero):
    if tipo == "Pequeña":
        p = random.randint(3, 10)
        cd = random.randint(6, 12)
        zd = random.randint(8, 15)
    elif tipo == "Mediana":
        p = random.randint(11, 20)
        cd = random.randint(12, 24)
        zd = random.randint(16, 30)
    else:
        p = random.randint(21, 35)
        cd = random.randint(25, 40)
        zd = random.randint(31, 45)

    demandas = [random.randint(10, 100) for _ in range(zd)]
    demTotal = sum(demandas)
    cBaseP = int((demTotal * 1.5) / p)
    capP = [random.randint(cBaseP, cBaseP + 100) for _ in range(p)]
    cBaseCD = int((demTotal * 1.5) / cd)
    capCD = [random.randint(cBaseCD, cBaseCD + 100) for _ in range(cd)]
    maxCD = random.randint(1, cd - 1)
    costP_CD = [[random.randint(10, 50) for _ in range(cd)] for _ in range(p)]
    costCD_ZD = [[random.randint(10, 50) for _ in range(zd)] for _ in range(cd)]
    costFijos = [random.randint(5000, 15000) for _ in range(cd)]

    os.makedirs(f"instancias/{tipo}", exist_ok=True)
    archivo = f"instancias/{tipo}/instancia{numero}.txt"
    with open(archivo, "w", encoding="utf-8") as f:
        f.write("TAMANOS\n")
        f.write(f"{p} {cd} {zd}\n\n")

        f.write("DEMANDAS\n")
        f.write(" ".join(map(str, demandas)) + "\n\n")

        f.write("CAP_PLANTAS\n")
        f.write(" ".join(map(str, capP)) + "\n\n")

        f.write("CAP_CD\n")
        f.write(" ".join(map(str, capCD)) + "\n\n")

        f.write("costosFij\n")
        f.write(" ".join(map(str, costFijos)) + "\n\n")

        f.write("maxCD\n")
        f.write(str(maxCD) + "\n\n")

        f.write("costosPC\n")
        for fila in costP_CD:
            f.write(" ".join(map(str, fila)) + "\n")
        f.write("\n")

        f.write("costosCZ\n")
        for fila in costCD_ZD:
            f.write(" ".join(map(str, fila)) + "\n")

for tipo in ["Pequeña", "Mediana", "Grande"]:
    for i in range(1, 6):
        genInstancias(tipo, i)