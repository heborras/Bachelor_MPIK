# Source code repository for the bachelor thesis of Hendrik Borras

The thesis was published in the publication repository of the Max Planck Society. It is freely accessible via this [link](http://hdl.handle.net/21.11116/0000-0001-193B-2).

## Folder structure and links to important source code
This repository contains multiple folders, which structure is inspired by the structure of the thesis.
* CosMO-detector: Everything within the CosMO-chapter
  * Numerical detector response calculation: [here](CosMO-detector/Detector%20numerical%20simulation.ipynb)
  * Monte Carlo detector response calculation: [here](CosMO-detector/Detector%20monte%20carlo.ipynb)
  * Script for performing a threshold scan with the DAQ-Card of the CosMO-detector: [here](CosMO-detector/Threshold_scan.ipynb)
  * Script for analysing the results of a threshold scan: [here](CosMO-detector/Threshold_scan_anaysis.ipynb)
  * Other things in here: Raw results from the inegral and efficency measurement, script to do an efficency measurement with the DAQ-Card, integration of the model by Biallas and Hebbeker
* PIN-diode-detector: Everything within the PIN-diode-chapter, mainly oscilloscope readout and analysis of the saved waveforms
  * Script to read out the HDO6004 scope: [here](PIN-diode-detector/Scope_readout_on_trigger.ipynb)
  * Script to analyse the saved data: [here](PIN-diode-detector/PIN-waveform_analysis_for_detailed_file_format.ipynb)
* uTelescope: Findings with the uTelescope
  * Component check on the uTelescope: [here](uTelescope/problems_on_seeed_board.xlsx)
* presentations: .pdf's of the presentations, that I gave at the weekly group meeting of the LHCb-group of the MPIK


## Software that is needed to run some of the code
* Python 2.7 or 3.6
* Jupyter
* Python packages:
  * numpy
  * scipy
  * matplotlib
  * pandas
  * [iminuit](https://github.com/iminuit/iminuit)
  * [pyik](https://github.com/HDembinski/pyik)
  * [pyserial](https://github.com/pyserial/pyserial)
* Mathematica >= 10.2
* Excel

