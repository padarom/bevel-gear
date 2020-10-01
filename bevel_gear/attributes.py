import adsk.core
import adsk.fusion
import traceback
import math

# Verfies that a value command input has a valid expression and returns
# the value if it does.  Otherwise it returns False.  This works around
# a problem where when you get the value from a ValueCommandInput it 
# causes the current expression to be evaluated and updates the
# display. Some new functionality is being added in the future to the
# ValueCommandInput object that will make this easier and should make
# this function obsolete.
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

class BevelGearAttributes:
    def __init__(self, teeth, module, shaftAngle, faceWidth):
        self.teeth = teeth
        self.module = module
        self.shaftAngle = shaftAngle
        self.faceWidth = faceWidth

    @classmethod
    def createGearPair(cls, gearTeeth, pinionTeeth, module, shaftAngle, faceWidth):
        gear = cls(gearTeeth, module, shaftAngle, faceWidth)
        pinion = cls(gearTeeth, module, shaftAngle, faceWidth)

        referenceDiameterPinion = pinionTeeth * module
        referenceDiameterGear = gearTeeth * module
        
        referenceConeAnglePinion = math.atan(math.sin(math.radians(shaftAngle)) / (gearTeeth/pinionTeeth + math.cos(math.radians(shaftAngle))))
        referenceConeAngleGear = shaftAngle - math.degrees(referenceConeAnglePinion)

        coneDistance = referenceConeAngleGear / (2 * math.sin(math.radians(referenceConeAngleGear)))
        
        if (faceWidth > coneDistance / 3):
            print("Oh noes.")
        
        _temp = (gearTeeth * math.cos(math.radians(referenceConeAnglePinion)) / pinionTeeth * math.cos(math.radians(referenceConeAngleGear)))
        addendumGear = 0.54*module + 0.46*module / _temp
        addendumPinion = 2*module - addendumGear
        
        dedendumGear = 2.188 * module - addendumGear
        dedendumPinion = 2.188 * module - addendumPinion

        return (gear, pinion)
