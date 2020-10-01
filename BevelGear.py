#Author- Christopher Mühl
#Description- Creates parametric bevel gears

# PEP-0008 https://www.python.org/dev/peps/pep-0008/#introduction

import adsk.core
import adsk.fusion
import traceback
import math
from .bevel_gear.attributes import BevelGearAttributes
from .bevel_gear.command import GearCommandHandler

BEVEL_GEAR_BUTTON = 'pdrmConstructBevelGear'


def run(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Create a new command definition for an action button and add
        # it to the "Create" toolbar in the "Solid" tab
        cmdDef = ui.commandDefinitions.addButtonDefinition(BEVEL_GEAR_BUTTON, 'Bevel Gear', 'Constructs a bevel gear pair', 'Resources/icons')
        ui.allToolbarPanels.itemById('SolidCreatePanel').controls.addCommand(cmdDef)

        # Register our gear command handler to the command created
        # event of the command definition
        # handler = GearCommandHandler()
        # cmdDef.commandCreated.add(handler)

        # Notify the user about a new command only if the add-in
        # was started manually (i.e. not at startup)
        if context['IsApplicationStartup'] == False:
            ui.messageBox('The "Bevel Gear" command has been added\nto the CREATE panel of the MODEL workspace.')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Remove the command definition and button from Fusion again
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.itemById(BEVEL_GEAR_BUTTON)       
        if gearButton:
            gearButton.deleteMe()

        cmdDef = ui.commandDefinitions.itemById(BEVEL_GEAR_BUTTON)
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

