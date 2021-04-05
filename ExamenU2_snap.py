# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 00:33:01 2021

@author: yessi
"""
######## -----------EXAMEN UNIDAD 2--------------

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os
import snappy
from snappy import Product
from snappy import ProductIO
from snappy import ProductUtils
from snappy import WKTReader
from snappy import HashMap
from snappy import GPF
# Para leer shapefiles
import shapefile
import pygeoif

####LEER LOS DATOS DE LA IMAGEN
#Cargar imagenes
path_to_sentinel_data = "D:/AP09/data/S1B_IW_GRDH_1SDV_20201119T235742_20201119T235807_024341_02E47D_DCF6.zip"
product = ProductIO.readProduct(path_to_sentinel_data)

#Leer y mostrar la informaciónd de la imagen
width = product.getSceneRasterWidth()
print("Width: {} px".format(width))
height = product.getSceneRasterHeight()
print("Height: {} px".format(height))
name = product.getName()
print("Name: {}".format(name))
band_names = product.getBandNames()
print("Band names: {}".format(", ".join(band_names)))

##Crear una funcion para mostrar el producto en una
def plotBand(product, band, vmin, vmax):
    band = product.getBand(band)
    w = band.getRasterWidth()
    h = band.getRasterHeight()
    print(w, h)
    band_data = np.zeros(w * h, np.float32)
    band.readPixels(0, 0, w, h, band_data)
    band_data.shape = h, w
    width = 12
    height = 12
    plt.figure(figsize=(width, height))
    imgplot = plt.imshow(band_data, cmap=plt.cm.binary, vmin=vmin, vmax=vmax)
    return imgplot

##--------------------------------------------------------------------------------------------------------------
##PRE-PROCESAMIENTO
def preprosesamiento(product, HashMap):
##Aplicar correccion orbital
    parameters = HashMap()
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', 'false')
    apply_orbit_file = GPF.createProduct('Apply-Orbit-File', parameters, product)
    
    ##Recortar la imagen
    r = shapefile.Reader("D:/AP09/shp/Villanueva.shp")
    g=[]
    for s in r.shapes():
        g.append(pygeoif.geometry.as_shape(s))
    m = pygeoif.MultiPoint(g)
    wkt = str(m.wkt).replace("MULTIPOINT", "POLYGON(") + ")"
    
    #Usar el shapefile para cortar la imagen
    SubsetOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')
    bounding_wkt = wkt
    geometry = WKTReader().read(bounding_wkt)
    HashMap = snappy.jpy.get_type('java.util.HashMap')
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', geometry)
    product_subset = snappy.GPF.createProduct('Subset', parameters, apply_orbit_file)
    
    #Mostrar las dimensiones de la imagen
    #width = product_subset.getSceneRasterWidth()
    #print("Width: {} px".format(width))
    #height = product_subset.getSceneRasterHeight()
    #print("Height: {} px".format(height))
    #band_names = product_subset.getBandNames()
    #print("Band names: {}".format(", ".join(band_names)))
    #band = product_subset.getBand(band_names[0])
    #print(band.getRasterSize())
    #plotBand(product_subset, "Intensity_VV", 0, 100000)
    
    ##Aplicar la calibracion de la imagen
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    parameters.put('sourceBands', 'Intensity_VV')
    parameters.put('selectedPolarisations', "VV")
    parameters.put('outputImageScaleInDb', False)
    product_calibrated = GPF.createProduct("Calibration", parameters, product_subset)
    plotBand(product_calibrated, "Sigma0_VV", 0, 1)
    
    ##Aplicar el filtro Speckle
    filterSizeY = '5'
    filterSizeX = '5'
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_VV')
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', filterSizeX)
    parameters.put('filterSizeY', filterSizeY)
    parameters.put('dampingFactor', '2')
    parameters.put('estimateENL', 'true')
    parameters.put('enl', '1.0')
    parameters.put('numLooksStr', '1')
    parameters.put('targetWindowSizeStr', '3x3')
    parameters.put('sigmaStr', '0.9')
    parameters.put('anSize', '50')
    speckle_filter = snappy.GPF.createProduct('Speckle-Filter', parameters, product_calibrated)
    plotBand(speckle_filter, 'Sigma0_VV', 0, 1)
    
    ##Aplicar la correccion del terremo
    parameters = HashMap()
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('sourceBands', 'Sigma0_VV')
    speckle_filter_tc = GPF.createProduct("Terrain-Correction", parameters, speckle_filter)
    plotBand(speckle_filter_tc, 'Sigma0_VV', 0, 0.1)

def BiMask(product, speckle_filter_tc): 
    #Crear una mascara binaria para la inundacion
    parameters = HashMap()
    BandDescriptor = snappy.jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    targetBand = BandDescriptor()
    targetBand.name = 'Sigma0_VV_Flooded'
    targetBand.type = 'uint8'
    targetBand.expression = '(Sigma0_VV < 1.57E-2) ? 1 : 0'
    targetBands = snappy.jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand
    parameters.put('targetBands', targetBands)
    flood_mask = GPF.createProduct('BandMaths', parameters, speckle_filter_tc)
    plotBand(flood_mask, 'Sigma0_VV_Flooded', 0, 1)
    
    
    #Crear la imagen a partir de la mascara
    ProductIO.writeProduct(flood_mask, "data2/final_mask", 'GeoTIFF')
    os.path.exists("data2/final_mask.tif")







