import adsk.core
import adsk.fusion
import traceback
from ..cfg import handlers
from .commandExecuted import CommandExecutedHandler
from .inputChanged import InputChangedHandler
from .validateInputs import ValidateInputsHandler


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface

            # Verify that a Fusion design is active.
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            command = adsk.core.CommandCreatedEventArgs.cast(args).command
            command.isExecutedWhenPreEmpted = False

            inputs = command.commandInputs
            inputs.addBoolValueInput('123', 'Name', True)
            
            onExecute = CommandExecutedHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)        
            
            onInputChanged = InputChangedHandler()
            command.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)     
            
            onValidateInputs = ValidateInputsHandler()
            command.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)
            
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
