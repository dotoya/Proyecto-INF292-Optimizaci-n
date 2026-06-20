import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

ruta_csv = 'resultados_entregables.csv' 

if not os.path.exists(ruta_csv):
    print(f"Error: No se encontró el archivo en la ruta {ruta_csv}")
    exit()

df = pd.read_csv(ruta_csv)
df.rename(columns={
    'Tipo': 'Tamaño', 
    'Tiempo_seg': 'Tiempo_Ejecucion',
    'Max_CD_Permitidos': 'Max_CDs_Permitidos'
}, inplace=True)
df_factibles = df[df['Estado'] == 'Optimal'].copy()
orden_tamanos = ['Pequeña', 'Mediana', 'Grande']
df['Tamaño'] = pd.Categorical(df['Tamaño'], categories=orden_tamanos, ordered=True)
df_factibles['Tamaño'] = pd.Categorical(df_factibles['Tamaño'], categories=orden_tamanos, ordered=True)

sns.set_theme(style="whitegrid")

#Gráfico 1:
plt.figure(figsize=(10, 6))
sns.boxplot(x='Tamaño', y='Costo_Total', data=df_factibles, palette='Set2')
sns.stripplot(x='Tamaño', y='Costo_Total', data=df_factibles, color=".25", alpha=0.6, jitter=True)
plt.title('Distribución del Costo Total de Operación por Tamaño de Instancia', fontsize=14)
plt.xlabel('Tamaño de Instancia', fontsize=12)
plt.ylabel('Costo Total ($)', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_costo_vs_tamano.png', dpi=300)
plt.show()

#Gráfico 2:
plt.figure(figsize=(10, 6))
# USAMOS DF COMPLETO: Porque incluso las infactibles consumen tiempo de cómputo del solver
sns.scatterplot(x='Variables', y='Tiempo_Ejecucion', hue='Tamaño', style='Tamaño', 
                s=100, palette='deep', data=df)
sns.lineplot(x='Variables', y='Tiempo_Ejecucion', data=df, color='gray', alpha=0.5)
plt.title('Impacto de la Dimensionalidad en el Tiempo de Ejecución', fontsize=14)
plt.xlabel('Número de Variables', fontsize=12)
plt.ylabel('Tiempo de Ejecución (segundos)', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_tiempo_vs_variables.png', dpi=300)
plt.show()

#Gráfico 3:
plt.figure(figsize=(12, 6))

df_melted = df_factibles.melt(id_vars=['Instancia', 'Tamaño'], 
                        value_vars=['Max_CDs_Permitidos', 'CDs_Abiertos'],
                        var_name='Tipo_Métrica', value_name='Cantidad')
df_melted['Nombre_Instancia'] = df_melted['Tamaño'].astype(str) + " - " + df_melted['Instancia'].str.replace('.txt', '')

sns.barplot(x='Nombre_Instancia', y='Cantidad', hue='Tipo_Métrica', data=df_melted, palette='muted')
plt.title('Relación entre CDs Habilitados y Límite Máximo Permitido (Solo Factibles)', fontsize=14)
plt.xlabel('Instancia', fontsize=12)
plt.ylabel('Número de Centros de Distribución', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Indicador', loc='upper left')
plt.tight_layout()
plt.savefig('grafico_cds_abiertos.png', dpi=300)
plt.show()

print("Gráficos generados y guardados con éxito en formato PNG.")