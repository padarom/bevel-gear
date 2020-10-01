# Bevel Gear Generator
Fusion 360 Bevel Gear Generator add-in. **This is still a work in progress and not yet a finished add-in.**

## Installation
There's two ways to install this add-in:
- **GitHub**: Download the Zip file of this repository and import it in Fusion 360
- **Autodesk App Store**: Click [here]() (tbd) and follow the instructions

## Options
As opposed to spur gears which can be created individually and will mesh with any other spur gear of the same module, bevel gears are usually created in pairs. The shape of a bevel gear depends on the ratio of its number of teeth to the one it's being meshed with and its pitch angle. The add-in will create both bevel gears in a pair for you.

- **Module**: The ratio between the number of teeth of the gear and its diameter. At the same tooth count a gear with a larger module will be larger than one with a smaller module.
- **Pitch Angle**: The angle at which two bevel gears come into contact. Currently this add-in only supports pitch angles of less than 90°, but crown gears (90°) and internal bevel gears (>90°) will potentially be added at a later point.
- **Geometry**: This add-in only supports straight gear geometry currently, but I plan to eventually add spiral and hypoid geometries as well.

