#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib2
import shutil
import md5

import zipfile
import xml.etree.ElementTree as ET

xml_root = ET.Element("addons")
addonsIDs = []

def checkDir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)

def tmpFile(tFile):
  return os.path.join('tmp', tFile)

def addPluginFile(pFile):  
  
  print '-----------------------'
  print 'Atidaromas ZIP failas: ' + pFile
  
  zf = open(pFile, 'r')
  z = zipfile.ZipFile(zf)
  
  print('Testuojamas ZIP failas:'), 
  if z.testzip() != None:
    print "Blogas ZIP failas"
  else:
    print 'OK'
    
  names = z.namelist()
  addon_xml = None
  icon_png = None
  
  for name in names:
    path = name.split('/')
    
    if len(path) > 2:
      continue
    
    filename = path[-1]
    
    if filename == 'addon.xml':
      addon_xml = name
      
    if filename == 'icon.png':
      icon_png = name
  
  print ('Išpakuojami failai:'),
  
  if not addon_xml:
    print 'addon.xml failas nerastas'
    zf.close()
    return

  if not icon_png:
    print 'icon_png failas nerastas'
    zf.close()
    return    
  
  print 'OK'
  
  xml_addon = ET.fromstring(z.read(addon_xml))
  
  addon_id = xml_addon.get('id')
  addon_version = xml_addon.get('version')
  
  if not addon_id:
    print 'Nenurodytas įskiepio ID'
    zf.close()
    return
  
  if not addon_version:
    print "Nenurodyta įskiepio versija"
    zf.close()
    return
  
  print 'ID: %s, version: %s' % (addon_id, addon_version)
  
  if addon_id in addonsIDs:
    print "Klaida: Besidubliuojantis įskiepis!"
    zf.close()
    return
  
  addonsIDs.append(addon_id)  
  
  xml_root.append(xml_addon)  
  
  checkDir(os.path.join('repo', addon_id))
  
  ico_file = open(os.path.join('repo', addon_id, 'icon.png'), 'wb')
  ico_file.write(z.read(icon_png))
  ico_file.close()
  
  zf.close()
  
  shutil.move(pFile, os.path.join('repo', addon_id, '%s-%s.zip' % (addon_id, addon_version)))

def addRemotePlugins():
  
  f = open('remotePlugins.txt', 'r')

  for line in f.readlines():
    mfile = line.strip()
    
    if not mfile:
      continue
    
    print "Parsiunčiamas failas: " + mfile
    
    tFile = tmpFile(os.path.basename(mfile))
    
    urllib.urlretrieve (mfile, tFile)
    
    addPluginFile(tFile)    
    
  f.close()  

def addLocalPlugins():
  
  for f in os.listdir('localPlugins'):
    f = os.path.join('localPlugins', f)
    if not os.path.isfile(f):
      return
    
    tFile = tmpFile('plugin.zip')
    shutil.copy(f, tFile)
    addPluginFile(tFile)

def md5sum(mFile):
  
  tFile = open(mFile, 'r')  
  m = md5.new(tFile.read())
  tFile.close()
  
  pFile = open(mFile+'.md5', 'w')
  pFile.write(m.hexdigest())
  pFile.close()  

def buildRepositoryPlugin():
  
  zipFile = tmpFile('repository.zip')
  
  with zipfile.ZipFile(zipFile, 'w') as repoZip:
    repoZip.write('repository.lt/addon.xml')
    repoZip.write('repository.lt/icon.png')
    repoZip.close()
    
    addPluginFile(zipFile)
 
if __name__ == '__main__':

  shutil.rmtree('repo')
  checkDir('repo')

  shutil.rmtree('tmp')
  checkDir('tmp')
    
  addRemotePlugins()
  addLocalPlugins()
  buildRepositoryPlugin()
  
  addons_xml_file = os.path.join('repo', 'addons.xml')

  addons_xml = ET.ElementTree(xml_root)
  addons_xml.write(addons_xml_file, 'UTF-8')
  
  md5sum(addons_xml_file)