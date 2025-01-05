import json
import os
import time
import pytmx
import shutil

def move(fromPath,toPath):
    if not os.path.exists(toPath):
        os.makedirs(toPath)
    
    shutil.copytree(fromPath, toPath,dirs_exist_ok=True)

def createTmx(filePath,outputDir):
    basePath=os.path.dirname(filePath)
    fileName=os.path.basename(filePath)
    baseFileName=os.path.splitext(fileName)[0]

    mapData={}
    tmxData=pytmx.TiledMap(filePath)
    
    mapData["width"] = tmxData.width
    mapData["height"] =tmxData.height
    mapData["tileWidth"] =tmxData.tilewidth
    mapData["tileHeight"] =tmxData.tileheight

    tiles={}
    imageIndex=1
    images={}
    layers=[]

    for layer in tmxData.layers:
        layerData={}
        if isinstance(layer, pytmx.TiledTileLayer):
            layerData["name"]=layer.name
            layerData["opacity"]=layer.opacity
            layerData["visible"]=layer.visible

            layerMapData=[]
            for x, y, gid in layer:
                if gid > 0 and not gid in tiles:
                    tileTuple=tmxData.get_tile_image_by_gid(gid)
                    tileProps=tmxData.get_tile_properties_by_gid(gid)

                    tile={}
                    if tileProps and "colliders" in tileProps:
                        tileColliders=tileProps["colliders"]

                        colliders=[]
                        for collider in tileColliders:
                            colliderData=[]
                            points=collider.apply_transformations()
                            for it in points:
                                data={
                                    "x":it[0],
                                    "y":it[1]
                                }
                                colliderData.append(data)
                            colliders.append(colliderData)
                        tile["colliders"]=colliders

                    if tileTuple:
                        imageName=tileTuple[0]
                        imageName=imageName.replace("\\","/")
                        imageName=imageName.replace(basePath+"/","")

                        imageId=0
                        if not imageName in images:
                            images[imageName]=imageIndex
                            imageId=imageIndex
                            imageIndex=imageIndex+1
                        else:
                            imageId=images[imageName]

                        tileRect=tileTuple[1]
                        tile["id"]=imageId
                        if imageId > 0:
                            tile["width"]=tileRect[2]
                            tile["height"]=tileRect[3]
                            tile["x"]=tileRect[0]
                            tile["y"]=tileRect[1]
                        
                        tiles[gid]=tile
                layerMapData.append(gid)
            layerData["data"]=layerMapData

        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                print(f"Object: {obj.name} at ({obj.x}, {obj.y})")

        layers.append(layerData)

    mapData["layers"]=layers
    mapData["tiles"]=tiles

    imageReverts={}
    for k,v in images.items():
        imageReverts[v]=k

    mapData["images"]=imageReverts

    outputFilePath=os.path.join(outputDir,baseFileName+".json")
    with open(outputFilePath, 'w', encoding='utf-8') as f:
        json.dump(mapData, f, ensure_ascii=False, indent=4)
    
    print(filePath+"=>"+outputFilePath)

def main():
    json_data={}
    with open("../config.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    if not os.path.exists(json_data["output"]):
        os.makedirs(json_data["output"])

    for root, dirs, files in os.walk(json_data["input"]):
        for file in files:
            if not file.endswith(".tmx"):
                continue

            filepath = os.path.join(root, file)
            createTmx(filepath,json_data["output"])
    
    print("will move map...")
    if "client" in json_data["move"]:
        print("move client map...")
        move(json_data["output"],json_data["move"]["client"])

    if "server" in json_data["move"]:
        print("move server map...")
        move(json_data["output"],json_data["move"]["server"])
    
    print("move map finish!")
    print()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print("total time:"+str(execution_time))
    print("Done!")