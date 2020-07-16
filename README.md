# mdocspoofer
Create dummy [SerialEM](https://bio3d.colorado.edu/SerialEM/) mdoc files for a set of tomograms collected as dose fractionated movies in Tomo5.

This serves to allow processing of cryo-ET data collected in Tomo5 using [Warp](http://www.warpem.com/warp/#).

## Installation
Python version 3.6+
```
pip install mdocspoofer
```

## Usage
From the command line run 
```
mdocspoofer
```

This will start an interactive command-line interface, provide the path to the folder containing 
the dose-fractionated micrographs and the applied electron dose per tilt image in electrons per square angstrom.

To run in non-interactive mode, supply options at the command line. Details can be found using
```
mdocspoofer --help
```
