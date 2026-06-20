import os
import csv
import time
import pulp
import subprocess

def leerInstancia(rutaArchivo):
    with open(rutaArchivo, 'r', encoding='utf-8') as f:
        lineas = [linea.strip() for linea in f.readlines() if linea.strip() != ""]

    datos = {}
    
    idxTamanos = lineas.index("TAMANOS")
    idxDemandas = lineas.index("DEMANDAS")
    idxCapPlantas = lineas.index("CAP_PLANTAS")
    idxCapCd = lineas.index("CAP_CD")
    idxCostosFij = lineas.index("costosFij")
    idxMaxCd = lineas.index("maxCD")
    idxCostosPc = lineas.index("costosPC")
    idxCostosCz = lineas.index("costosCZ")

    p, cd, zd = map(int, lineas[idxTamanos + 1].split())
    datos['pNum'] = p
    datos['cdNum'] = cd
    datos['zdNum'] = zd
    
    datos['demandas'] = list(map(int, lineas[idxDemandas + 1].split()))
    datos['capP'] = list(map(int, lineas[idxCapPlantas + 1].split()))
    datos['capCD'] = list(map(int, lineas[idxCapCd + 1].split()))
    datos['costFijos'] = list(map(int, lineas[idxCostosFij + 1].split()))
    datos['maxCD'] = int(lineas[idxMaxCd + 1])
    
    datos['costP_CD'] = []
    for i in range(p):
        fila = list(map(int, lineas[idxCostosPc + 1 + i].split()))
        datos['costP_CD'].append(fila)
        
    datos['costCD_ZD'] = []
    for j in range(cd):
        fila = list(map(int, lineas[idxCostosCz + 1 + j].split()))
        datos['costCD_ZD'].append(fila)

    return datos

def resolverModelo(datos, nombreInstancia, tipoInstancia):
    inicioTiempo = time.time()

    I = range(datos['pNum'])
    J = range(datos['cdNum'])
    K = range(datos['zdNum'])

    modelo = pulp.LpProblem("Red_Logistica", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", (I, J), lowBound=0, cat='Continuous')
    y = pulp.LpVariable.dicts("y", (J, K), lowBound=0, cat='Continuous')
    z = pulp.LpVariable.dicts("z", J, cat='Binary')

    costoFijo = pulp.lpSum(datos['costFijos'][j] * z[j] for j in J)
    costoTransPc = pulp.lpSum(datos['costP_CD'][i][j] * x[i][j] for i in I for j in J)
    costoTransCz = pulp.lpSum(datos['costCD_ZD'][j][k] * y[j][k] for j in J for k in K)
    
    modelo += costoFijo + costoTransPc + costoTransCz, "Costo_Total"

    for i in I:
        modelo += pulp.lpSum(x[i][j] for j in J) <= datos['capP'][i], f"CapPlanta_{i}"

    for j in J:
        modelo += pulp.lpSum(x[i][j] for i in I) == pulp.lpSum(y[j][k] for k in K), f"Flujo_{j}"

    for j in J:
        modelo += pulp.lpSum(y[j][k] for k in K) <= datos['capCD'][j] * z[j], f"CapCD_{j}"

    for k in K:
        modelo += pulp.lpSum(y[j][k] for j in J) == datos['demandas'][k], f"Demanda_{k}"

    modelo += pulp.lpSum(z[j] for j in J) <= datos['maxCD'], "Max_CDs"

    # --- LA SOLUCIÓN AQUÍ ---
    # Generamos un archivo MPS universal en lugar de un archivo LP conflictivo
    nombreMps = f"{tipoInstancia}_{nombreInstancia.replace('.txt', '')}.mps"
    modelo.writeMPS(nombreMps)

    # Ejecutamos lp_solve pasándole el flag -fmps (Free MPS)
    proceso = subprocess.run(["lp_solve", "-fmps", nombreMps], capture_output=True, text=True)
    
    tiempoEjecucion = time.time() - inicioTiempo

    estado = "Desconocido"
    costoTotal = None
    cdsAbiertos = 0

    if "Value of objective function:" in proceso.stdout:
        estado = "Optimal"
        for linea in proceso.stdout.split('\n'):
            linea = linea.strip()
            if "Value of objective function:" in linea:
                costoTotal = float(linea.split(':')[1].strip())
            elif linea.startswith('z_'):
                partes = linea.split()
                if len(partes) == 2 and float(partes[1]) > 0.5:
                    cdsAbiertos += 1
    elif "infeasible" in proceso.stdout.lower() or "infeasible" in proceso.stderr.lower():
        estado = "Infeasible"
    else:
        print(f"\n[!] Error procesando {nombreInstancia}:")
        print(proceso.stderr or proceso.stdout)

    # (Opcional) Borrar los archivos .mps basura para no llenar tu disco
    if os.path.exists(nombreMps):
        os.remove(nombreMps)

    return {
        "Instancia": nombreInstancia,
        "Tipo": tipoInstancia,
        "Estado": estado,
        "Costo_Total": costoTotal,
        "Max_CD_Permitidos": datos['maxCD'],
        "CDs_Abiertos": cdsAbiertos,
        "Variables": len(modelo.variables()),
        "Restricciones": len(modelo.constraints),
        "Tiempo_seg": round(tiempoEjecucion, 4)
    }

def ejecutarLote():
    tipos = ["Pequeña", "Mediana", "Grande"]
    resultadosTotales = []

    print("Iniciando resolución de instancias...\n")

    for tipo in tipos:
        carpeta = f"instancias/{tipo}"
        if not os.path.exists(carpeta):
            print(f"Carpeta no encontrada: {carpeta}. ¿Generaste las instancias?")
            continue
            
        for i in range(1, 6):
            nombreArchivo = f"instancia{i}.txt"
            ruta = os.path.join(carpeta, nombreArchivo)
            
            if os.path.exists(ruta):
                print(f"Resolviendo {tipo} - {nombreArchivo}...")
                datos = leerInstancia(ruta)
                resultado = resolverModelo(datos, nombreArchivo, tipo)
                resultadosTotales.append(resultado)

    if resultadosTotales:
        archivoCsv = "resultados_entregables.csv"
        columnas = ["Instancia", "Tipo", "Estado", "Costo_Total", "Max_CD_Permitidos", 
                    "CDs_Abiertos", "Variables", "Restricciones", "Tiempo_seg"]
        
        with open(archivoCsv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(resultadosTotales)
            
        print(f"\n¡Proceso finalizado! Los resultados se han guardado en '{archivoCsv}'.")

if __name__ == "__main__":
    ejecutarLote()