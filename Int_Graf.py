# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 23:21:33 2021

@author: yessi
"""

import tkinter as tk 
from tkinter.messagebox import showinfo
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ExamenU2_snap import * 

##VENTANA TKINTER
ventana = tk.Tk()
ventana.geometry("800x600")

##fondo
ventana.config(bg='pink')
ventana.title("Examen U2")

# SELECCION DE RASTER - LABEL 1
label1 = tk.Label(ventana, text='1. Seleccione la imagen raster', bg='pink')
label1.pack()

folder_path = tk.StringVar()


def selectRaster():
    global raster
    raster = filedialog.askopenfilename() 
    folder_path.set(raster)
    textRaster.insert(tk.END, raster)
    
    path_to_sentinel_data = "{}".format(raster)
    product = ProductIO.readProduct(path_to_sentinel_data)
    

##BOTON 1 
Rasterbutton = tk.Button(ventana, text = 'Carga una Imagen', command = selectRaster)   
Rasterbutton.pack()                      
#text font
textRaster = tk.Entry(ventana, font = ('arial'), justify = 'center' )
textRaster.pack()


# SELECCION DE SHAPEFILE - LABEL 2
label2 = tk.Label(ventana, text='2. Seleccione el shapefile', bg='pink')
label2.pack()

folder_path = tk.StringVar()

def selectShp():
    global shp
    shp = filedialog.askopenfilename() 
    folder_path.set(shp)
    textshp.insert(tk.END, shp) 
    r = shapefile.Reader(shp)
    
##BOTON 2 
shpbutton = tk.Button(ventana, text = 'Carga un shapefile', command = selectShp)   
shpbutton.pack()                      
#text font
textshp = tk.Entry(ventana, font = ('arial'), justify = 'center' )
textshp.pack()


# PREPROCESAMIENTO - LABEL 3
label2 = tk.Label(ventana, text='2. Seleccione el shapefile', bg='pink')
label2.pack()

def preprocesamiento(product, ExamenU2_snap):
    textprep.insert(tk.END, preprocesamiento)
    
##BOTON 3 
Prepbutton = tk.Button(ventana, text = 'Preprocesar', command = preprocesamiento)   
Prepbutton.pack()                      
#text font
textprep = tk.Entry(ventana, font = ('arial'), justify = 'center' )
textprep.pack()


#GUI
ventana.mainloop()