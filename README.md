# FiducialRegistrationExperiment

##Require:
* Slicer4
* MRRobotRegistration module (from SNRLab)
* Data (Mad Drive: Projects/Ca***/LiverMRIRobot/RegistrationValidation)

Data could only be processed batch by batch (to avoid series number conflict).

##Steps:
* Load all batch images from DICOM into Slicer
* Load fiducial pattern (RegistrationExperimentFiducialPattern.fcsv)
* Open Python interpreter and load batchProcessRegistrationExperiment.py
* Run registration

    batchRegistration('XXXX/RegistrationExperiment_XX_XX_XXXX.csv', 'XXXX/output-2015-11-19.csv')

* Execute function processExperimentData, with, the batch spreadsheet (containing series number) as first argument, and output file as second
* Wait until end of execution (could take a while)

##Results:
For each image, Slicer will create 3 transforms:
* Transform_GoldStandard_Serie###, which correspond to the gold standard transform based on the spreadsheet information (bloc andgle, fiducial rotation, x,y,z, etc...)
* Original_Registration_Matrix_Serie###, which is the absolute registration matrix
* Relative_Registration_Matrix_Serie###, which is the registration matrix relatively to the reference image (which is the first serie number that appear in the spreadsheet)
The output file will contains all information about the experimental configuration (bloc used, fiducial rotation angle, position, ...), as well as the registration results (fiducial detected, outliers, FRE, ...)

##Issues:
* Some registration seems to have a big FRE, need some investigation.
* The GoldStandard calculation has to be checked (I'm not sure I had time to properly finish to calculate it), as well as Relative_Registration_Matrix_Serie###


