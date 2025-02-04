import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# Paleta de colores
COLOR_FONDO = "#F0F0F0"
COLOR_BOTONES = "#4CAF50"
COLOR_TEXTO = "#FFFFFF"
COLOR_GRAFICO = "#5B913B"
COLOR_TABLA = "#E0E0E0"
COLOR_RECUADRO = "#E0E0E0"

# Función para cargar archivo CSV
def cargar_csv():
    archivo = filedialog.askopenfilename(
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        if not archivo.endswith(".csv"):
            messagebox.showerror("Error", "El archivo seleccionado no es un archivo CSV.")
            return
        try:
            global df
            df = pd.read_csv(archivo)
            preguntas_combo["values"] = df.columns.tolist()
            preguntas_combo.current(0)
            limpiar_grafica()
            limpiar_tabla()
            limpiar_estadisticas()
            messagebox.showinfo("Éxito", f"Archivo cargado: {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo.\n{e}")

# Función para analizar la columna seleccionada
def analizar_columna():
    if "df" not in globals():
        messagebox.showerror("Error", "Primero debes cargar un archivo CSV.")
        return

    columna = preguntas_combo.get()
    datos = df[columna]

    # Limpiar gráfica existente, tabla y estadísticas
    limpiar_grafica()
    limpiar_tabla()
    limpiar_estadisticas()

    # Contador de datos analizados
    total_datos = len(datos)
    contador_label.config(text=f"Datos analizados: {total_datos}")

    # Clasificación de la columna
    if pd.api.types.is_numeric_dtype(datos):
        tipo_dato = "Cuantitativa"
        media = datos.mean()
        mediana = datos.median()
        desviacion = datos.std()
        varianza = datos.var()
        minimo = datos.min()
        maximo = datos.max()
        percentiles = datos.quantile([0.25, 0.5, 0.75])  # Percentiles 25%, 50% (mediana), 75%

        estadisticas_label.config(
            text=f"Distribución de {columna}\n"
                 f"Tipo de dato: {tipo_dato}\n"
                 f"Media: {media:.2f} | Mediana: {mediana:.2f}\n"
                 f"Desviación estándar: {desviacion:.2f}\n"
                 f"Varianza: {varianza:.2f}\n"
                 f"Mínimo: {minimo:.2f} | Máximo: {maximo:.2f}\n"
                 f"Percentiles:\n"
                 f"  - 25%: {percentiles[0.25]:.2f}\n"
                 f"  - 50%: {percentiles[0.50]:.2f}\n"
                 f"  - 75%: {percentiles[0.75]:.2f}"
        )

        # Ocultar la tabla de frecuencias
        frame_tabla.pack_forget()

        # Dibujar histograma y gráfico de caja
        dibujar_grafica(datos, tipo_dato, columna)
    else:
        tipo_dato = "Cualitativa"
        estadisticas_label.config(
            text=f"Tipo de dato: {tipo_dato}\n"
                 f"Frecuencia de {columna}\n")
        frecuencias = datos.value_counts()
        total = len(datos)
        tabla_frecuencias = [
            (cat, freq, round((freq / total) * 100, 2))
            for cat, freq in frecuencias.items()
        ]

        # Mostrar la tabla de frecuencias
        frame_tabla.pack(pady=10)
        mostrar_tabla(tabla_frecuencias)
        dibujar_grafica(datos, tipo_dato, columna)

# Función para mostrar la tabla en el Treeview
def mostrar_tabla(tabla_frecuencias):
    for fila in tabla_frecuencias:
        tabla.insert("", "end", values=fila)

# Función para dibujar la gráfica
def dibujar_grafica(datos, tipo_dato, columna):
    if tipo_dato == "Cuantitativa":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))  # Dos gráficos: histograma y boxplot
        fig.patch.set_facecolor(COLOR_FONDO)  # Color de fondo de la gráfica

        # Histograma
        sns.histplot(datos, bins=10, color=COLOR_GRAFICO, kde=True, ax=ax1)
        ax1.set_xlabel(columna)
        ax1.set_ylabel("Frecuencia")

        # Gráfico de caja (boxplot)
        sns.boxplot(x=datos, color=COLOR_GRAFICO, ax=ax2)
        ax2.set_xlabel(columna)
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))  # Dos gráficos: uno principal y uno de pastel
        fig.patch.set_facecolor(COLOR_FONDO)  # Color de fondo de la gráfica

        datos.value_counts().head(5).plot(kind="bar", color=COLOR_GRAFICO, edgecolor="black", ax=ax1)
        ax1.set_xlabel("Categorías")
        ax1.set_ylabel("Frecuencia")
        ax1.tick_params(axis="x", rotation=45)  # Rotar etiquetas del eje X

        # Gráfico de pastel
        datos.value_counts().head(5).plot(kind="pie", autopct="%1.1f%%", colors=sns.color_palette("pastel"), ax=ax2)
        ax2.set_ylabel("")  # Ocultar el label del eje Y

    plt.tight_layout()  # Ajustar márgenes automáticamente

    global canvas
    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.get_tk_widget().pack(pady=10)
    canvas.draw()

# Función para limpiar la gráfica actual
def limpiar_grafica():
    global canvas
    if "canvas" in globals():
        canvas.get_tk_widget().destroy()

# Función para limpiar las estadísticas actuales
def limpiar_estadisticas():
    estadisticas_label.config(text="")
    contador_label.config(text="Datos analizados: 0")

# Función para limpiar la tabla
def limpiar_tabla():
    for fila in tabla.get_children():
        tabla.delete(fila)

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Análisis de Encuestas CSV de Probabilidad")
ventana.geometry("1200x800")  # Ampliar el tamaño de la ventana
ventana.config(bg=COLOR_FONDO)  # Color de fondo de la ventana

# Botón para cargar archivo CSV
btn_cargar = tk.Button(
    ventana, text="Cargar archivo CSV", command=cargar_csv, bg=COLOR_BOTONES, fg=COLOR_TEXTO, font=("Arial", 14)
)
btn_cargar.place(x=20, y=20)  # Posicionar en la esquina superior izquierda

# Selector de preguntas
preguntas_combo = ttk.Combobox(ventana, state="readonly", width=50)
preguntas_combo.pack(pady=10)

btn_analizar = tk.Button(
    ventana, text="Analizar columna", command=analizar_columna, bg=COLOR_BOTONES, fg=COLOR_TEXTO, font=("Arial", 12)
)
btn_analizar.pack(pady=10)

# Recuadro para el número de datos analizados (esquina superior derecha)
contador_frame = tk.Frame(ventana, bg=COLOR_RECUADRO, padx=10, pady=10)
contador_frame.place(relx=1.0, rely=0.0, anchor="ne")  # Posicionar en la esquina superior derecha

contador_label = tk.Label(contador_frame, text="Datos analizados: 0", font=("Arial", 12), bg=COLOR_RECUADRO)
contador_label.pack()

# Resultados y ajustar parámetros como el tipo de letra
estadisticas_label = tk.Label(ventana, text="", font=("Arial", 12), bg=COLOR_FONDO)
estadisticas_label.pack(pady=10)

# Marco para contener la tabla y la barra de desplazamiento
frame_tabla = tk.Frame(ventana)
frame_tabla.pack(pady=10)

# Barra de desplazamiento vertical
scrollbar = tk.Scrollbar(frame_tabla, orient="vertical")
scrollbar.pack(side="right", fill="y")

# Tabla para frecuencias
tabla = ttk.Treeview(
    frame_tabla, 
    columns=("Categoría", "Frecuencia", "Frecuencia relativa (%)"), 
    show="headings", 
    height=5,  # Reducir la altura de la tabla
    yscrollcommand=scrollbar.set
)
tabla.heading("Categoría", text="Categoría")
tabla.heading("Frecuencia", text="Frecuencia")
tabla.heading("Frecuencia relativa (%)", text="Frecuencia relativa (%)")
tabla.column("Categoría", anchor="center", width=200)
tabla.column("Frecuencia", anchor="center", width=100)
tabla.column("Frecuencia relativa (%)", anchor="center", width=150)
tabla.pack(side="left")

# Vincular barra de desplazamiento con la tabla
scrollbar.config(command=tabla.yview)

ventana.mainloop()