import adsk.core
import adsk.fusion
import traceback


class CommandExecutedHandler(adsk.core.CommandEventHandler):
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

            
            # Start calculating all the dependent parameters within the Gleason system for straight bevel gears
            # Note that for spiral bevel gears the calculations will look different
            numberOfTeethPinion = int(_numTeeth.value)
            numberOfTeethGear = int(_numTeeth.value)
            module = 3
            shaftAngle = 90
            faceWidth = 22
            
            gearAttributes, pinionAttributes = BevelGearAttributes.createGearPair(numberOfTeethGear, numberOfTeethPinion, module, shaftAngle, faceWidth)
            
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
