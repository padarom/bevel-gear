
des = adsk.fusion.Design.cast(app.activeProduct)
root = des.rootComponent

if root.customGraphicsGroups.count > 0:
    root.customGraphicsGroups.item(0).deleteMe()
    ui.messageBox('Deleted existing graphics.')
    app.activeViewport.refresh()
    return

pyramidSize = 10
pyramidWidth = math.sqrt(pyramidSize**2 - (pyramidSize/2)**2)
pyramidHeight = 6

graphics = root.customGraphicsGroups.add()

coordArray = [0, 0, 0,
                pyramidSize, 0, 0,
                pyramidSize/2, pyramidWidth, 0,
                pyramidSize/2, pyramidWidth*(1/3), pyramidHeight]
coords = adsk.fusion.CustomGraphicsCoordinates.create(coordArray)

vertexIndices = [0,1,2, 0,1,3, 1,2,3, 2,0,3]

vec1 = coords.getCoordinate(0).vectorTo(coords.getCoordinate(1))
vec2 = coords.getCoordinate(0).vectorTo(coords.getCoordinate(3))
normal1 = vec1.crossProduct(vec2)

vec1 = coords.getCoordinate(1).vectorTo(coords.getCoordinate(2))
vec2 = coords.getCoordinate(1).vectorTo(coords.getCoordinate(3))
normal2 = vec1.crossProduct(vec2)

vec1 = coords.getCoordinate(2).vectorTo(coords.getCoordinate(0))
vec2 = coords.getCoordinate(2).vectorTo(coords.getCoordinate(3))
normal3 = vec1.crossProduct(vec2)

normals = [0,0,-1,
            normal1.x, normal1.y, normal1.z,
            normal1.x, normal2.y, normal2.z,
            normal1.x, normal3.y, normal3.z]

normalIndices = [0,0,0, 1,1,1, 2,2,2, 3,3,3]
mesh = graphics.addMesh(coords, vertexIndices, normals, normalIndices)
app.activeViewport.refresh()
