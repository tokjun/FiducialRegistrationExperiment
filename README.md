FiducialRegistrationExperiment
==============================

Require:
--------

### Registration & Error Calculation
* Slicer4
* MRRobotRegistration module (from SNRLab)
* Data (Mad Drive: Projects/Ca***/LiverMRIRobot/RegistrationValidation)

### Data analaysis
* R
* ggplot2 (It can be installed by typing 'install.packages("ggplot2")' from the R console.

Data could only be processed batch by batch (to avoid series number conflict).

Steps:
------

First, process the images using 3D Slicer to perform registration, and compute errors.

* Load all batch images from DICOM into Slicer
* Load fiducial pattern (RegistrationExperimentFiducialPattern.fcsv)
* Open Python interpreter and load batchProcessRegistrationExperiment.py
* Run registration

    batchRegistration('XXXX/RegistrationExperiment_XX_XX_XXXX.csv', 'XXXX/output-XXXX-XX-XX.csv')

* Execute function processExperimentData, with, the batch spreadsheet (containing series number) as first argument, and output file as second
* Wait until end of execution (could take a while)
* Compute errors

    batchComputeError('XXXX/output-XXXX-XX-XX.csv', 'XXX/Error-XXXX-XX-XX.csv')

Then, process the result using 'procErrorData.R' script.



Issues:
-------




