import adsk.core
import adsk.fusion
import traceback


class InputChangedHandler(adsk.core.InputChangedEventHandler):
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
        