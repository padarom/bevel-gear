#Author-Brian Ekins
#Description-Creates a spur gear component.

# AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY  
# DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.  
# AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE  
# UNINTERRUPTED OR ERROR FREE. 


import adsk.core, adsk.fusion, adsk.cam, traceback
import math

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

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = _ui.commandDefinitions.addButtonDefinition('adskBevelGearPythonAddIn', 'Bevel Gear', 'Creates a bevel gear component', 'Resources/BevelGear')        
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.addCommand(cmdDef)
        
        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "Bevel Gear" command has been added\nto the CREATE panel of the MODEL workspace.')
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.itemById('adskBevelGearPythonAddIn')       
        if gearButton:
            gearButton.deleteMe()
        
        cmdDef = _ui.commandDefinitions.itemById('adskBevelGearPythonAddIn')
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Verfies that a value command input has a valid expression and returns the 
# value if it does.  Otherwise it returns False.  This works around a 
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make 
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()
                
            defaultUnits = des.unitsManager.defaultLengthUnits
                
            # Determine whether to use inches or millimeters as the intial default.
            global _units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                _units = 'in'
            else:
                _units = 'mm'
                        
            # Define the default values and get the previous values from the attributes.
            if _units == 'in':
                standard = 'English'
            else:
                standard = 'Metric'
            standardAttrib = des.attributes.itemByName('BevelGear', 'standard')
            if standardAttrib:
                standard = standardAttrib.value
                
            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'

            bevelGearType = 'Straight'
            bevelGearTypeAttrib = des.attributes.itemByName('BevelGear', 'bevelGearType')
            if bevelGearTypeAttrib:
                bevelGearType = bevelGearTypeAttrib.value
            
            pressureAngle = '20 deg'
            pressureAngleAttrib = des.attributes.itemByName('BevelGear', 'pressureAngle')
            if pressureAngleAttrib:
                pressureAngle = pressureAngleAttrib.value
            
            pressureAngleCustom = 20 * (math.pi/180.0)
            pressureAngleCustomAttrib = des.attributes.itemByName('BevelGear', 'pressureAngleCustom')
            if pressureAngleCustomAttrib:
                pressureAngleCustom = float(pressureAngleCustomAttrib.value)            

            diaPitch = '2'
            diaPitchAttrib = des.attributes.itemByName('BevelGear', 'diaPitch')
            if diaPitchAttrib:
                diaPitch = diaPitchAttrib.value
            metricModule = 25.4 / float(diaPitch)

            backlash = '0'
            backlashAttrib = des.attributes.itemByName('BevelGear', 'backlash')
            if backlashAttrib:
                backlash = backlashAttrib.value

            numTeeth = '24'            
            numTeethAttrib = des.attributes.itemByName('BevelGear', 'numTeeth')
            if numTeethAttrib:
                numTeeth = numTeethAttrib.value

            rootFilletRad = str(.0625 * 2.54)
            rootFilletRadAttrib = des.attributes.itemByName('BevelGear', 'rootFilletRad')
            if rootFilletRadAttrib:
                rootFilletRad = rootFilletRadAttrib.value

            thickness = str(0.5 * 2.54)
            thicknessAttrib = des.attributes.itemByName('BevelGear', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value
            
            holeDiam = str(0.5 * 2.54)
            holeDiamAttrib = des.attributes.itemByName('BevelGear', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            global _standard, _pressureAngle, _pressureAngleCustom, _bevelGearType, _diaPitch, _pitch, _module, _numTeeth, _rootFilletRad, _thickness, _holeDiam, _pitchDiam, _backlash, _imgInputEnglish, _imgInputMetric, _errMessage

            # Define the command dialog.
            _imgInputEnglish = inputs.addImageCommandInput('gearImageEnglish', '', 'Resources/GearEnglish.png')
            _imgInputEnglish.isFullWidth = True

            _imgInputMetric = inputs.addImageCommandInput('gearImageMetric', '', 'Resources/GearMetric.png')
            _imgInputMetric.isFullWidth = True

            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)
                _imgInputMetric.isVisible = False
            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)
                _imgInputEnglish.isVisible = False
                
            _bevelGearType = inputs.addDropDownCommandInput('bevelGearType', 'Gear Type', adsk.core.DropDownStyles.TextListDropDownStyle)
            _bevelGearType.listItems.add('Straight', bevelGearType == 'Straight')
            _bevelGearType.listItems.add('Spiral', bevelGearType == 'Spiral')
            _bevelGearType.listItems.add('Helical', bevelGearType == 'Helical')
            
            _pressureAngle = inputs.addDropDownCommandInput('pressureAngle', 'Pressure Angle', adsk.core.DropDownStyles.TextListDropDownStyle)
            if pressureAngle == '14.5 deg':
                _pressureAngle.listItems.add('14.5 deg', True)
            else:
                _pressureAngle.listItems.add('14.5 deg', False)

            if pressureAngle == '20 deg':
                _pressureAngle.listItems.add('20 deg', True)
            else:
                _pressureAngle.listItems.add('20 deg', False)

            if pressureAngle == '25 deg':
                _pressureAngle.listItems.add('25 deg', True)
            else:
                _pressureAngle.listItems.add('25 deg', False)

            if pressureAngle == 'Custom':
                _pressureAngle.listItems.add('Custom', True)
            else:
                _pressureAngle.listItems.add('Custom', False)

            _pressureAngleCustom = inputs.addValueInput('pressureAngleCustom', 'Custom Angle', 'deg', adsk.core.ValueInput.createByReal(pressureAngleCustom))
            if pressureAngle != 'Custom':
                _pressureAngleCustom.isVisible = False
                        
            _diaPitch = inputs.addValueInput('diaPitch', 'Diametral Pitch', '', adsk.core.ValueInput.createByString(diaPitch))   

            _module = inputs.addValueInput('module', 'Module', '', adsk.core.ValueInput.createByReal(metricModule))   
            
            if standard == 'English':
                _module.isVisible = False
            elif standard == 'Metric':
                _diaPitch.isVisible = False
                
            _numTeeth = inputs.addStringValueInput('numTeeth', 'Number of Teeth', numTeeth)        

            _backlash = inputs.addValueInput('backlash', 'Backlash', _units, adsk.core.ValueInput.createByReal(float(backlash)))

            _rootFilletRad = inputs.addValueInput('rootFilletRad', 'Root Fillet Radius', _units, adsk.core.ValueInput.createByReal(float(rootFilletRad)))

            _thickness = inputs.addValueInput('thickness', 'Gear Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _pitchDiam = inputs.addTextBoxCommandInput('pitchDiam', 'Pitch Diameter', '', 1, True)
            
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True
            
            # Connect to the command related events.
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)        
            
            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)     
            
            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)        
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            if _standard.selectedItem.name == 'English':
                diaPitch = _diaPitch.value            
            elif _standard.selectedItem.name == 'Metric':
                diaPitch = 25.4 / _module.value
            
            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('BevelGear', 'standard', _standard.selectedItem.name)
            attribs.add('BevelGear', 'pressureAngle', _pressureAngle.selectedItem.name)
            attribs.add('BevelGear', 'pressureAngleCustom', str(_pressureAngleCustom.value))
            attribs.add('BevelGear', 'diaPitch', str(diaPitch))
            attribs.add('BevelGear', 'numTeeth', str(_numTeeth.value))
            attribs.add('BevelGear', 'rootFilletRad', str(_rootFilletRad.value))
            attribs.add('BevelGear', 'thickness', str(_thickness.value))
            attribs.add('BevelGear', 'holeDiam', str(_holeDiam.value))
            attribs.add('BevelGear', 'backlash', str(_backlash.value))

            # Get the current values.
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)

            numTeeth = int(_numTeeth.value)
            rootFilletRad = _rootFilletRad.value
            thickness = _thickness.value
            holeDiam = _holeDiam.value
            backlash = _backlash.value

            # Create the gear.
            gearComp = drawGear(des, diaPitch, numTeeth, thickness, rootFilletRad, pressureAngle, backlash, holeDiam)
            
            if gearComp:
                if _standard.selectedItem.name == 'English':
                    desc = 'Spur Gear; Diametrial Pitch: ' + str(diaPitch) + '; '            
                elif _standard.selectedItem.name == 'Metric':
                    desc = 'Spur Gear; Module: ' +  str(25.4 / diaPitch) + '; '
                
                desc += 'Num Teeth: ' + str(numTeeth) + '; '
                desc += 'Pressure Angle: ' + str(pressureAngle * (180/math.pi)) + '; '
                
                desc += 'Backlash: ' + des.unitsManager.formatInternalValue(backlash, _units, True)
                gearComp.description = desc
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


        
# Event handler for the inputChanged event.
class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            global _units
            if changedInput.id == 'standard':
                if _standard.selectedItem.name == 'English':
                    _imgInputMetric.isVisible = False
                    _imgInputEnglish.isVisible = True
                    
                    _diaPitch.isVisible = True
                    _module.isVisible = False
    
                    _diaPitch.value = 25.4 / _module.value
                    
                    _units = 'in'
                elif _standard.selectedItem.name == 'Metric':
                    _imgInputMetric.isVisible = True
                    _imgInputEnglish.isVisible = False
                    
                    _diaPitch.isVisible = False
                    _module.isVisible = True
                
                    _module.value = 25.4 / _diaPitch.value
                    
                    _units = 'mm'

                # Set each one to it's current value because otherwised if the user 
                # has edited it, the value won't update in the dialog because 
                # apparently it remembers the units when the value was edited.
                # Setting the value using the API resets this.
                _backlash.value = _backlash.value
                _backlash.unitType = _units
                _rootFilletRad.value = _rootFilletRad.value
                _rootFilletRad.unitType = _units
                _thickness.value = _thickness.value
                _thickness.unitType = _units
                _holeDiam.value = _holeDiam.value
                _holeDiam.unitType = _units
                
            # Update the pitch diameter value.
            diaPitch = None
            if _standard.selectedItem.name == 'English':
                result = getCommandInputValue(_diaPitch, '')
                if result[0]:
                    diaPitch = result[1]
            elif _standard.selectedItem.name == 'Metric':
                result = getCommandInputValue(_module, '')
                if result[0]:
                    diaPitch = 25.4 / result[1]
            if not diaPitch == None:
                if _numTeeth.value.isdigit(): 
                    numTeeth = int(_numTeeth.value)
                    pitchDia = numTeeth/diaPitch

                    # The pitch dia has been calculated in inches, but this expects cm as the input units.
                    des = adsk.fusion.Design.cast(_app.activeProduct)
                    pitchDiaText = des.unitsManager.formatInternalValue(pitchDia * 2.54, _units, True)
                    _pitchDiam.text = pitchDiaText
                else:
                    _pitchDiam.text = ''                    
            else:
                _pitchDiam.text = ''

            if changedInput.id == 'pressureAngle':
                if _pressureAngle.selectedItem.name == 'Custom':
                    _pressureAngleCustom.isVisible = True
                else:
                    _pressureAngleCustom.isVisible = False                    
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''

            # Verify that at lesat 4 teath are specified.
            if not _numTeeth.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:    
                numTeeth = int(_numTeeth.value)
            
            if numTeeth < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
                eventArgs.areInputsValid = False
                return
                
            # Calculate some of the gear sizes to use in validation.
            if _standard.selectedItem.name == 'English':
                result = getCommandInputValue(_diaPitch, '')
                if result[0] == False:
                    eventArgs.areInputsValid = False
                    return
                else:
                    diaPitch = result[1]
            elif _standard.selectedItem.name == 'Metric':
                result = getCommandInputValue(_module, '')
                if result[0] == False:
                    eventArgs.areInputsValid = False
                    return
                else:
                    diaPitch = 25.4 / result[1]

            diametralPitch = diaPitch / 2.54
            pitchDia = numTeeth / diametralPitch
            
            if (diametralPitch < (20 *(math.pi/180))-0.000001):
                dedendum = 1.157 / diametralPitch
            else:
                circularPitch = math.pi / diametralPitch
                if circularPitch >= 20:
                    dedendum = 1.25 / diametralPitch
                else:
                    dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

            rootDia = pitchDia - (2 * dedendum)        
                    
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)
            baseCircleDia = pitchDia * math.cos(pressureAngle)
            baseCircleCircumference = 2 * math.pi * (baseCircleDia / 2) 

            des = adsk.fusion.Design.cast(_app.activeProduct)

            result = getCommandInputValue(_holeDiam, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                holeDiam = result[1]
                           
            if holeDiam >= (rootDia - 0.01):
                _errMessage.text = 'The center hole diameter is too large.  It must be less than ' + des.unitsManager.formatInternalValue(rootDia - 0.01, _units, True)
                eventArgs.areInputsValid = False
                return

            toothThickness = baseCircleCircumference / (numTeeth * 2)
            if _rootFilletRad.value > toothThickness * .4:
                _errMessage.text = 'The root fillet radius is too large.  It must be less than ' + des.unitsManager.formatInternalValue(toothThickness * .4, _units, True)
                eventArgs.areInputsValid = False
                return
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Calculate points along an involute curve.
def involutePoint(baseCircleRadius, distFromCenterToInvolutePoint):
    try:
        # Calculate the other side of the right-angle triangle defined by the base circle and the current distance radius.
        # This is also the length of the involute chord as it comes off of the base circle.
        triangleSide = math.sqrt(math.pow(distFromCenterToInvolutePoint,2) - math.pow(baseCircleRadius,2)) 
        
        # Calculate the angle of the involute.
        alpha = triangleSide / baseCircleRadius

        # Calculate the angle where the current involute point is.
        theta = alpha - math.acos(baseCircleRadius / distFromCenterToInvolutePoint)

        # Calculate the coordinates of the involute point.    
        x = distFromCenterToInvolutePoint * math.cos(theta)
        y = distFromCenterToInvolutePoint * math.sin(theta)

        # Create a point to return.        
        return adsk.core.Point3D.create(x, y, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Builds a spur gear.
def drawGear(design, diametralPitch, numTeeth, thickness, rootFilletRad, pressureAngle, backlash, holeDiam):
    try:
        # The diametral pitch is specified in inches but everthing
        # here expects all distances to be in centimeters, so convert
        # for the gear creation.
        diametralPitch = diametralPitch / 2.54
    
        # Compute the various values for a gear.
        pitchDia = numTeeth / diametralPitch
        
        #addendum = 1.0 / diametralPitch
        if (diametralPitch < (20 *(math.pi/180))-0.000001):
            dedendum = 1.157 / diametralPitch
        else:
            circularPitch = math.pi / diametralPitch
            if circularPitch >= 20:
                dedendum = 1.25 / diametralPitch
            else:
                dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

        rootDia = pitchDia - (2 * dedendum)
        
        baseCircleDia = pitchDia * math.cos(pressureAngle)
        outsideDia = (numTeeth + 2) / diametralPitch
        
        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)        
        newComp = adsk.fusion.Component.cast(newOcc.component)
        
        # Create a new sketch.
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        baseSketch = sketches.add(xyPlane)

        # Draw a circle for the base.
        baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), rootDia/2.0)
        
        # Draw a circle for the center hole, if the value is greater than 0.
        prof = adsk.fusion.Profile.cast(None)
        if holeDiam - (_app.pointTolerance * 2) > 0:
            baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), holeDiam/2.0)

            # Find the profile that uses both circles.
            for prof in baseSketch.profiles:
                if prof.profileLoops.count == 2:
                    break
        else:
            # Use the single profile.
            prof = baseSketch.profiles.item(0)
        
        #### Extrude the circle to create the base of the gear.

        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(thickness)
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion.
        baseExtrude = extrudes.add(extInput)
        
        # Create a second sketch for the tooth.
        toothSketch = sketches.add(xyPlane)

        # Calculate points along the involute curve.
        involutePointCount = 15; 
        involuteIntersectionRadius = baseCircleDia / 2.0
        involutePoints = []
        involuteSize = (outsideDia - baseCircleDia) / 2.0
        for i in range(0, involutePointCount):
            involuteIntersectionRadius = (baseCircleDia / 2.0) + ((involuteSize / (involutePointCount - 1)) * i)
            newPoint = involutePoint(baseCircleDia / 2.0, involuteIntersectionRadius)
            involutePoints.append(newPoint)
            
        # Get the point along the tooth that's at the pictch diameter and then
        # calculate the angle to that point.
        pitchInvolutePoint = involutePoint(baseCircleDia / 2.0, pitchDia / 2.0)
        pitchPointAngle = math.atan(pitchInvolutePoint.y / pitchInvolutePoint.x)

        # Determine the angle defined by the tooth thickness as measured at
        # the pitch diameter circle.
        toothThicknessAngle = (2 * math.pi) / (2 * numTeeth)
        
        # Determine the angle needed for the specified backlash.
        backlashAngle = (backlash / (pitchDia / 2.0)) * .25
        
        # Determine the angle to rotate the curve.
        rotateAngle = -((toothThicknessAngle/2) + pitchPointAngle - backlashAngle)
        
        # Rotate the involute so the middle of the tooth lies on the x axis.
        cosAngle = math.cos(rotateAngle)
        sinAngle = math.sin(rotateAngle)
        for i in range(0, involutePointCount):
            newX = involutePoints[i].x * cosAngle - involutePoints[i].y * sinAngle
            newY = involutePoints[i].x * sinAngle + involutePoints[i].y * cosAngle
            involutePoints[i] = adsk.core.Point3D.create(newX, newY, 0)

        # Create a new set of points with a negated y.  This effectively mirrors the original
        # points about the X axis.
        involute2Points = []
        for i in range(0, involutePointCount):
            involute2Points.append(adsk.core.Point3D.create(involutePoints[i].x, -involutePoints[i].y, 0))

        curve1Dist = []
        curve1Angle = []
        for i in range(0, involutePointCount):
            curve1Dist.append(math.sqrt(involutePoints[i].x * involutePoints[i].x + involutePoints[i].y * involutePoints[i].y))
            curve1Angle.append(math.atan(involutePoints[i].y / involutePoints[i].x))
        
        curve2Dist = []
        curve2Angle = []
        for i in range(0, involutePointCount):
            curve2Dist.append(math.sqrt(involute2Points[i].x * involute2Points[i].x + involute2Points[i].y * involute2Points[i].y))
            curve2Angle.append(math.atan(involute2Points[i].y / involute2Points[i].x))

        toothSketch.isComputeDeferred = True
		
        # Create and load an object collection with the points.
        pointSet = adsk.core.ObjectCollection.create()
        for i in range(0, involutePointCount):
            pointSet.add(involutePoints[i])

        # Create the first spline.
        spline1 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

        # Add the involute points for the second spline to an ObjectCollection.
        pointSet = adsk.core.ObjectCollection.create()
        for i in range(0, involutePointCount):
            pointSet.add(involute2Points[i])

        # Create the second spline.
        spline2 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

        # Draw the arc for the top of the tooth.
        midPoint = adsk.core.Point3D.create((outsideDia / 2), 0, 0)
        toothSketch.sketchCurves.sketchArcs.addByThreePoints(spline1.endSketchPoint, midPoint, spline2.endSketchPoint)     

        # Check to see if involute goes down to the root or not.  If not, then
        # create lines to connect the involute to the root.
        if( baseCircleDia < rootDia ):
            toothSketch.sketchCurves.sketchLines.addByTwoPoints(spline2.startSketchPoint, spline1.startSketchPoint)
        else:
            rootPoint1 = adsk.core.Point3D.create((rootDia / 2 - 0.001) * math.cos(curve1Angle[0] ), (rootDia / 2) * math.sin(curve1Angle[0]), 0)
            line1 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(rootPoint1, spline1.startSketchPoint)

            rootPoint2 = adsk.core.Point3D.create((rootDia / 2 - 0.001) * math.cos(curve2Angle[0]), (rootDia / 2) * math.sin(curve2Angle[0]), 0)
            line2 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(rootPoint2, spline2.startSketchPoint)

            baseLine = toothSketch.sketchCurves.sketchLines.addByTwoPoints(line1.startSketchPoint, line2.startSketchPoint)

            # Make the lines tangent to the spline so the root fillet will behave correctly.            
            line1.isFixed = True
            line2.isFixed = True
            toothSketch.geometricConstraints.addTangent(spline1, line1)
            toothSketch.geometricConstraints.addTangent(spline2, line2)
        
        toothSketch.isComputeDeferred = False

        ### Extrude the tooth.
        
        # Get the profile defined by the tooth.
        prof = toothSketch.profiles.item(0)

        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.JoinFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(thickness)
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion.
        toothExtrude = extrudes.add(extInput)

        baseFillet = None
        if rootFilletRad > 0:
            ### Find the edges between the base cylinder and the tooth.
            
            # Get the outer cylindrical face from the base extrusion by checking the number
            # of edges and if it's 2 get the other one.
            cylFace = baseExtrude.sideFaces.item(0)
            if cylFace.edges.count == 2:
                cylFace = baseExtrude.sideFaces.item(1)
    
            # Get the two linear edges, which are the connection between the cylinder and tooth.
            edges = adsk.core.ObjectCollection.create()
            for edge in cylFace.edges:
                if isinstance(edge.geometry, adsk.core.Line3D):
                    edges.add(edge)
    
            # Create a fillet input to be able to define the input needed for a fillet.
            fillets = newComp.features.filletFeatures;
            filletInput = fillets.createInput()
    
            # Define that the extent is a distance extent of 5 cm.
            radius = adsk.core.ValueInput.createByReal(rootFilletRad)
            filletInput.addConstantRadiusEdgeSet(edges, radius, False)
    
            # Create the extrusion.
            baseFillet = fillets.add(filletInput)

        # Create a pattern of the tooth extrude and the base fillet.
        circularPatterns = newComp.features.circularPatternFeatures
        entities = adsk.core.ObjectCollection.create()
        entities.add(toothExtrude)
        if baseFillet:
            entities.add(baseFillet)
        cylFace = baseExtrude.sideFaces.item(0)        
        patternInput = circularPatterns.createInput(entities, cylFace)
        numTeethInput = adsk.core.ValueInput.createByString(str(numTeeth))
        patternInput.quantity = numTeethInput
        pattern = circularPatterns.add(patternInput)        
        
        # Create an extra sketch that contains a circle of the diametral pitch.
        diametralPitchSketch = sketches.add(xyPlane)
        diametralPitchCircle = diametralPitchSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), pitchDia/2.0)
        diametralPitchCircle.isConstruction = True
        diametralPitchCircle.isFixed = True
        
        # Group everything used to create the gear in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        pitchSketchIndex = diametralPitchSketch.timelineObject.index
        # ui.messageBox("Indices: " + str(newOccIndex) + ", " + str(pitchSketchIndex))
        timelineGroup = timelineGroups.add(newOccIndex, pitchSketchIndex)
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

