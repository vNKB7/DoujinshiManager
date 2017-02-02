#!/usr/bin/env python3

import os
import shutil

'''
将解压后的文件整理到当前文件夹中
'''

def parseDir(path):
    lists = os.listdir(path)
    if len(lists) == 1:
        newPath = os.path.join(path, lists[0])
        if os.path.isdir(newPath):
            result = parseDir(newPath)
            if not result:
                return newPath
            else:
                return result
        else:
            return newPath
    else:
        return None

def safeRemove(path):
    isSafe = False
    for root, dirs, files in os.walk(path):
        if len(files) > 0:
            isSafe = False
        else:
            isSafe = True
    if isSafe:
        shutil.rmtree(path)
    return isSafe


rootDir = 'E:\\BaiduYunDownload\\gmm'
fileList = []
errorNameList = []

for lists in os.listdir(rootDir):
    path = os.path.join(rootDir, lists)
    if os.path.isdir(path):
        fileList.append([path, parseDir(path)])
    else:
        fileList.append([path, 0])

for tmp in fileList:
    print(tmp)
    lists = os.listdir(rootDir)
    if tmp[1] != 0 and tmp[1] is not None:
        oldPath = tmp[0]
        newPath = tmp[1]

        newName = newPath.split('\\')[-1]
        if newName == oldPath.split('\\')[-1]:
            dupNewName = newName+'(1)'
            realNewPath = os.path.join(rootDir, dupNewName)
            shutil.move(newPath, realNewPath)
            if safeRemove(oldPath):
                os.rename(realNewPath,os.path.join(rootDir, newName))
            else:
                errorNameList.append(tmp)
        elif newName in lists:
            errorNameList.append(tmp)
        else:
            realNewPath = os.path.join(rootDir, newPath.split('\\')[-1])
            shutil.move(newPath, realNewPath)
            if not safeRemove(oldPath):
                errorNameList.append(tmp)

print(errorNameList)
