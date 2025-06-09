## ISOEndPointAnalysis.py

ISOEndPointAnalysis.py is a Python script, aiming to analyze the endpoint data in different input modalities and radius.

## Usage

```Bash

python ISOEndPointAnalysis.py --folder <Technique to be analyzed> --radius <Radius to be analyzed>

```

### --folder:

    'ControllerTracking' : DC
    'ControllerIntenSelect' : BC
    'BareHandIntenSelect' : BH
    'BareHandTracking' : DH

### --radius:

0: no specific radius
0.05: 5 cm
0.15: 15 cm
0.25: 25 cm

## Example

Analyze the endpoint in “ControllerTracking” and 15cm:

```Bash

python ISOEndPointAnalysis.py --folder ControllerTracking --radius 0.15
```
