import adsk.core
import adsk.fusion
import traceback

"""

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_imgInputEnglish = adsk.core.ImageCommandInput.cast(None)
_imgInputMetric = adsk.core.ImageCommandInput.cast(None)
_standard = adsk.core.DropDownCommandInput.cast(None)
_pressureAngle = adsk.core.DropDownCommandInput.cast(None)
_pressureAngleCustom = adsk.core.ValueCommandInput.cast(None)
_bevelGearType = adsk.core.DropDownCommandInput.cast(None)
_backlash = adsk.core.ValueCommandInput.cast(None)
_diaPitch = adsk.core.ValueCommandInput.cast(None)
_module = adsk.core.ValueCommandInput.cast(None)
_numTeeth = adsk.core.StringValueCommandInput.cast(None)
_rootFilletRad = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_pitchDiam = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

"""

# Event handler for the commandCreated event.



def drawBevelGear(design, component, constructionPlane, gearValues):
    try:
        # Start calculating all the dependent parameters within the Gleason system for straight bevel gears
        # Note that for spiral bevel gears the calculations will look different
        numberOfTeethPinion = 20
        numberOfTeethGear = 40
        module = 3
        pressureAngle = 20
        shaftAngle = 90
        faceWidth = 20
        
        referenceDiameterPinion = numberOfTeethPinion * module
        referenceDiameterGear = numberOfTeethGear * module
        
        backConeRadiusGear = (referenceDiameterGear / 2) / math.cos(math.atan2(numberOfTeethGear, numberOfTeethPinion))
        
        referenceConeAnglePinion = math.atan(math.sin(math.radians(shaftAngle)) / (numberOfTeethGear/numberOfTeethPinion + math.cos(math.radians(shaftAngle))))
        referenceConeAngleGear = shaftAngle - math.degrees(referenceConeAnglePinion)

        coneDistance = referenceConeAngleGear / (2 * math.sin(math.radians(referenceConeAngleGear)))
        
        if (faceWidth > coneDistance / 3):
            print("Oh noes.")
        
        _temp = (numberOfTeethGear * math.cos(math.radians(referenceConeAnglePinion)) / numberOfTeethPinion * math.cos(math.radians(referenceConeAngleGear)))
        addendumGear = 0.54*module + 0.46*module / _temp
        addendumPinion = 2*module - addendumGear
        
        dedendumGear = 2.188 * module - addendumGear
        dedendumPinion = 2.188 * module - addendumPinion
        
        point = lambda x, y : adsk.core.Point3D.create(x, y, 0)
        
        # Start with the construction
        sketches = component.sketches
        sketch = sketches.add(constructionPlane)

        lines = sketch.sketchCurves.sketchLines
        constraints = sketch.geometricConstraints
        dimensions = sketch.sketchDimensions
        
        # Add a vertical helper line
        vertical = lines.addByTwoPoints(point(0, 5), point(0, -5))
        vertical.isConstruction = True
        constraints.addVertical(vertical)
        constraints.addMidPoint(sketch.originPoint, vertical)
        
        horizontal = lines.addByTwoPoints(point(5, 0), point(-5, 0))
        horizontal.isConstruction = True
        constraints.addHorizontal(horizontal)
        constraints.addMidPoint(sketch.originPoint, horizontal)
        dimensions.addDistanceDimension(horizontal.startSketchPoint, horizontal.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, point(-1, -1)).parameter._set_expression(str(referenceDiameterGear))
        
        rootCone = lines.addByTwoPoints(vertical.endSketchPoint, horizontal.startSketchPoint)
        rootCone.isConstruction = True
        dimensions.addAngularDimension(vertical, rootCone, point(1, 0)).parameter._set_expression(str(referenceConeAngleGear) + " deg")
        
        backCone = lines.addByTwoPoints(rootCone.endSketchPoint, point(0, -4))
        constraints.addPerpendicular(rootCone, backCone)
        constraints.addCoincident(backCone.endSketchPoint, vertical)
        
        backConeAddendum = lines.addByTwoPoints(backCone.startSketchPoint, point(500, 0))
        constraints.addCollinear(backConeAddendum, backCone)
        dimensions.addDistanceDimension(backConeAddendum.endSketchPoint, backCone.startSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, point(1, 1)).parameter._set_expression(str(addendumGear))
        
        backConeDedendumPoint = sketch.sketchPoints.add(point(0, 0))
        constraints.addCoincident(backConeDedendumPoint, backCone)
        dimensions.addDistanceDimension(backConeDedendumPoint, backCone.startSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, point(1, 1)).parameter._set_expression(str(dedendumGear))
        
        faceCone = lines.addByTwoPoints(rootCone.startSketchPoint, backConeAddendum.endSketchPoint)
        innerCone = lines.addByTwoPoints(rootCone.startSketchPoint, backConeDedendumPoint)
        
        innerFace = lines.addByTwoPoints(point(0, 0), point(1, 0))
        constraints.addCoincident(innerFace.startSketchPoint, faceCone)
        constraints.addCoincident(innerFace.endSketchPoint, innerCone)
        constraints.addPerpendicular(innerFace, rootCone)
        dimensions.addDistanceDimension(faceCone.endSketchPoint, innerFace.startSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, point(1, 1)).parameter._set_expression(str(faceWidth))

        innerFaceExtension = lines.addByTwoPoints(innerFace.endSketchPoint, point(0, 0))
        constraints.addCollinear(innerFaceExtension, innerFace)
        dimensions.addDistanceDimension(innerFace.endSketchPoint, innerFaceExtension.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, point(1, 1)).parameter._set_expression("5")
        
        gearBottom = lines.addByTwoPoints(point(0, 0), point(1, 0))
        constraints.addHorizontal(gearBottom)
        constraints.addCoincident(gearBottom.endSketchPoint, backCone)
        dimensions.addDistanceDimension(backConeDedendumPoint, gearBottom.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, point(1, 1)).parameter._set_expression("10")
        dimensions.addDistanceDimension(vertical.startSketchPoint, gearBottom.startSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, point(1, 1)).parameter._set_expression("5")
        
        gearTop = lines.addByTwoPoints(point(0, 0), innerFaceExtension.endSketchPoint)
        constraints.addHorizontal(gearTop)
        constraints.addVerticalPoints(gearTop.startSketchPoint, gearBottom.startSketchPoint)

        lines.addByTwoPoints(gearTop.startSketchPoint, gearBottom.startSketchPoint)
        
        profiles = adsk.core.ObjectCollection.create()
        profiles.add(sketch.profiles.item(0))
        profiles.add(sketch.profiles.item(1))
        
        revolves = component.features.revolveFeatures
        revInput = revolves.createInput(profiles, vertical, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        revInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(math.pi * 2))
        revolveBody = revolves.add(revInput)
        
        planeInput = component.constructionPlanes.createInput()
        planeInput.setByTangentAtPoint(revolveBody.faces[4], backCone.startSketchPoint)
        spurGearEquivalentPlane = component.constructionPlanes.add(planeInput)
        
        sketch = sketches.add(spurGearEquivalentPlane)
        projectedBackConeCenter = sketch.project(backCone.endSketchPoint)[0]
        
        pitchCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(projectedBackConeCenter, 5)
        addendumCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(projectedBackConeCenter, 6)
        dedendumCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(projectedBackConeCenter, 4)
        pitchCircle.isConstruction = True
        addendumCircle.isConstruction = True
        dedendumCircle.isConstruction = True
        
        sketch.sketchDimensions.addDiameterDimension(pitchCircle, point(0, 0)).parameter._set_expression(str(backConeRadiusGear) + " * 2")
        sketch.sketchDimensions.addDiameterDimension(addendumCircle, point(0, 0)).parameter._set_expression(str(backConeRadiusGear) + " * 2 + 2 * " + str(addendumGear))
        sketch.sketchDimensions.addDiameterDimension(dedendumCircle, point(0, 0)).parameter._set_expression(str(backConeRadiusGear) + " * 2 - 2 * " + str(dedendumGear))
        
        outsideAddendumCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(projectedBackConeCenter, 6)
        outsideAddendumCircle.isConstruction = True
        sketch.sketchDimensions.addDiameterDimension(outsideAddendumCircle, point(0, 0)).parameter._set_expression(str(backConeRadiusGear) + " * 2 + 1 + 2 * " + str(addendumGear))
        
        temp = sketch.sketchCurves.sketchLines.addByTwoPoints(projectedBackConeCenter, point(0, 0))
        sketch.geometricConstraints.addCoincident(temp.endSketchPoint, addendumCircle)
        sketch.geometricConstraints.addVertical(temp)
        temp.isConstruction = True
        
        verticalHelper = sketch.sketchCurves.sketchLines.addByTwoPoints(point(0, -10), point(0, 10))
        verticalHelper.isConstruction = True
        sketch.geometricConstraints.addVertical(verticalHelper)
        sketch.geometricConstraints.addCoincident(verticalHelper.startSketchPoint, projectedBackConeCenter)
        
        involuteArc = sketch.sketchCurves.sketchArcs.addByThreePoints(point(-100, 100), point(0, 0), point(-1, -10))
        sketch.geometricConstraints.addCoincident(involuteArc.startSketchPoint, dedendumCircle)
        
        involuteExtension = sketch.sketchCurves.sketchLines.addByTwoPoints(involuteArc.startSketchPoint, projectedBackConeCenter)
        involuteExtension.isConstruction = True
        sketch.geometricConstraints.addTangent(involuteExtension, involuteArc)

        pitchCircleCollection = adsk.core.ObjectCollection.create()
        pitchCircleCollection.add(pitchCircle)
        _, _, points = involuteArc.intersections(pitchCircleCollection)
        pitchCirclePoint = sketch.sketchPoints.add(points.item(0))
        sketch.geometricConstraints.addCoincident(pitchCirclePoint, pitchCircle)
        sketch.geometricConstraints.addCoincident(pitchCirclePoint, involuteArc)
        
        sketch.geometricConstraints.addCoincident(involuteArc.endSketchPoint, outsideAddendumCircle)
        
        pressureAngleLine = sketch.sketchCurves.sketchLines.addByTwoPoints(pitchCirclePoint, point(10, 10))
        pressureAngleLine.isConstruction = True
        sketch.geometricConstraints.addCoincident(pressureAngleLine.endSketchPoint, outsideAddendumCircle)
        sketch.geometricConstraints.addTangent(pressureAngleLine, involuteArc)
        
        sketch.sketchDimensions.addAngularDimension(pressureAngleLine, verticalHelper, point(-1, 1000)).parameter._set_expression("20")
        
        toothShapeDefiner = sketch.sketchCurves.sketchLines.addByTwoPoints(projectedBackConeCenter, pitchCirclePoint)
        toothShapeDefiner.isConstruction = True
        equivalentSpurTeeth = numberOfTeethGear / math.cos(math.atan2(numberOfTeethGear, numberOfTeethPinion))
        sketch.sketchDimensions.addAngularDimension(toothShapeDefiner, verticalHelper, point(-1, 1000)).parameter._set_expression("90 / " + str(equivalentSpurTeeth))
                
        mirroredInvoluteArc = sketch.sketchCurves.sketchArcs.addByThreePoints(point(100, 100), point(0, 0), point(1, -10))
        sketch.geometricConstraints.addSymmetry(involuteArc, mirroredInvoluteArc, verticalHelper)
        sketch.geometricConstraints.addCoincident(mirroredInvoluteArc.startSketchPoint, outsideAddendumCircle)
        sketch.geometricConstraints.addCoincident(mirroredInvoluteArc.endSketchPoint, dedendumCircle)
        
        outsideClosingLoop = sketch.sketchCurves.sketchArcs.addByThreePoints(involuteArc.endSketchPoint, point(0, 1000), mirroredInvoluteArc.startSketchPoint)
        sketch.geometricConstraints.addCoincident(outsideClosingLoop.centerSketchPoint, projectedBackConeCenter)
        insideClosingLoop = sketch.sketchCurves.sketchArcs.addByThreePoints(involuteArc.startSketchPoint, point(0, 1000), mirroredInvoluteArc.endSketchPoint)
        sketch.geometricConstraints.addCoincident(insideClosingLoop.centerSketchPoint, projectedBackConeCenter)
        
        loftFeatures = component.loftFeatures
        loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
        sections = loftInput.loftSections
        sections.add(sketch.profiles.item(0))
        sections.add(rootCone.startSketchPoint.worldGeometry)
        loftInput.isSolid = False
        
        loftFeatures.add(loftInput)
        
        return sketch        
    except Exception as error:
        _ui.messageBox("drawGear Failed : " + str(error)) 
        return None

# Builds a spur gear.
def drawGear(design, diametralPitch, numTeeth, thickness, rootFilletRad, pressureAngle, backlash, holeDiam):
    try:
        gearValues = {}
        gearValues['numberOfTeethPinion'] = str(20)
        gearValues['numberOfTeethGear'] = str(40)
        gearValues['module'] = str(20)
        gearValues['pressureAngle'] = str(20)
        gearValues['shaftAngle'] = str(90)
        gearValues['faceWidth'] = str(22)
        
        pinionValues = {}
        
        occurrences = design.rootComponent.occurrences
        matrix = adsk.core.Matrix3D.create()
        
        # Start with the construction
        gearOccurrence = occurrences.addNewComponent(matrix)
        gear = adsk.fusion.Component.cast(gearOccurrence.component)
        gear.attributes.add('BevelGear', 'Values',str(gearValues))
        
        pinionOccurrence = occurrences.addNewComponent(matrix)
        pinion = adsk.fusion.Component.cast(pinionOccurrence.component)
        
        finalSketch = drawBevelGear(design, gear, gear.xZConstructionPlane, gearValues)
        # drawBevelGear(design, pinion, pinion.xZConstructionPlane, pinionValues)
        
        gear.name = "Gear"
        pinion.name = "Pinion"
        
        timelineGroups = design.timeline.timelineGroups
        timelineGroup = timelineGroups.add(gearOccurrence.timelineObject.index, finalSketch.timelineObject.index)
        timelineGroup.name = 'Bevel Gear'
        
        return gear

        # Group everything used to create the gear in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        pitchSketchIndex = diametralPitchSketch.timelineObject.index
        # ui.messageBox("Indices: " + str(newOccIndex) + ", " + str(pitchSketchIndex))
        timelineGroup = timelineGroups.add(newOccIndex, finalSketch.timelineObject.index)
        timelineGroup.name = 'Spur Gear'
        
        # Add an attribute to the component with all of the input values.  This might 
        # be used in the future to be able to edit the gear.     
        gearValues = {}
        gearValues['diametralPitch'] = str(diametralPitch * 2.54)
        gearValues['numTeeth'] = str(numTeeth)
        gearValues['thickness'] = str(thickness)
        gearValues['rootFilletRad'] = str(rootFilletRad)
        gearValues['pressureAngle'] = str(pressureAngle)
        gearValues['holeDiam'] = str(holeDiam)
        gearValues['backlash'] = str(backlash)
        attrib = newComp.attributes.add('BevelGear', 'Values',str(gearValues))
        
        newComp.name = 'Spur Gear (' + str(numTeeth) + ' teeth)'
        return newComp
    except Exception as error:
        _ui.messageBox("drawGear Failed : " + str(error)) 
        return None
