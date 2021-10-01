import adsk.core
import adsk.fusion
import traceback


class ValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
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
