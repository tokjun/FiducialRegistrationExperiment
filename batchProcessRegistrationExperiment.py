import os
import csv
import time
import numpy
from __main__ import vtk, qt, ctk, slicer

def registerScan(scan, volId):

   # Prepare data for registration
   fiducials = slicer.mrmlScene.GetNodesByName("RegistrationExperimentFiducialPattern").GetItemAsObject(0)
   volume = slicer.mrmlScene.GetNodeByID(volId)
   registrationMatrix = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
   registrationMatrix.SetName("Original_RegistrationMatrix_Serie"+str(scan))
   slicer.mrmlScene.AddNode(registrationMatrix)
   
   # Register
   slicer.modules.mrrobotregistration.widgetRepresentation()
   reg = slicer.modules.MRRobotRegistrationWidget
   reg.volumeSelector.setCurrentNode(volume)
   reg.fiducialSelector.setCurrentNode(fiducials)
   reg.transformSelector.setCurrentNode(registrationMatrix)
   reg.circleFitBox.setChecked(True)
   reg.icpBox.setChecked(False)
   
   start = time.time()
   if reg.applyButton.enabled == True:
      reg.onApplyButton()

   end = time.time()

   return reg.fiducialDetectedBox.text, reg.outliersDetectedBox.text, reg.registrationError.text, (end-start), registrationMatrix.GetName(), registrationMatrix.GetID()

def calculateGoldStandard(scan,x,y,z,block,block_rot,fid_rot):
   transform = vtk.vtkTransform()

   transform.RotateY(int(fid_rot))
   transform.RotateZ(-int(block))
   transform.RotateY(int(block_rot))
   transform.Translate(-int(x)*50,int(z)*10,-int(y)*50)
   
   ### Debug ###
   n = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
   n.SetName("Transform_GoldStandard_Serie"+str(scan))
   slicer.mrmlScene.AddNode(n)
   n.SetAndObserveMatrixTransformToParent(transform.GetMatrix())
   #############

   return 0

def processExperimentData(spreadsheet, outputFile):

   # Open spreadsheets
   with open(spreadsheet,'rb') as ss:
      with open(outputFile,'wb') as output:

         # Create dictionary of nodes in the scene
         node_dict = {}
         volumes_in_scene = slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode")
         for i in range(volumes_in_scene.GetNumberOfItems()):
            volume = volumes_in_scene.GetItemAsObject(i)
            volumeSeries = volume.GetName().split(":")[0]
            node_dict[volumeSeries] = volume.GetID()

         # Prepare output file
         csvwriter = csv.writer(output)
         csvwriter.writerow( ('Scan#','X','Y','Z','Block','Bloc Rotation', 'Fiducial Rotation', 'Fiducials Detected', 'Outliers Detected', 'Registration Error', 'Time', 'Registration Matrix ID') )

         # Init
         referenceRegDone = False
         referenceMatrix = numpy.matrix('1.0 0.0 0.0 0.0; 0.0 1.0 0.0 0.0; 0.0 0.0 1.0 0.0; 0.0 0.0 0.0 1.0')
         invertReferenceMatrix = numpy.matrix('1.0 0.0 0.0 0.0; 0.0 1.0 0.0 0.0; 0.0 0.0 1.0 0.0; 0.0 0.0 0.0 1.0')
         newRegistrationMatrix = numpy.matrix('1.0 0.0 0.0 0.0; 0.0 1.0 0.0 0.0; 0.0 0.0 1.0 0.0; 0.0 0.0 0.0 1.0')   
         
         # Parse csv file
         csvreader = csv.reader(ss.readlines()[6:], delimiter=',')
         for row in csvreader:

            # Skip line if empty
            if all(el is '' for el in row):
               continue

            [x,y,z,block,block_rot,fid_rot,scans] = row
         
            # Remove 'block' and 'deg' from text
            block = block.split(" ")[0]
            block_rot = block_rot.split(" ")[0]
            fid_rot = fid_rot.split(" ")[0]
         
            # Split scans in list
            scans = scans.split(",")
         
            # Skip line if scans are empty
            if all(el is '' for el in scans):
               continue

            for scan in scans:               

               # Check if scan is in the scene ( = dictionary)
               if str(int(scan)) in node_dict:
                                                  
                  # Calculate gold standard (could be done only for each line)
                  calculateGoldStandard(scan,x,y,z,block,block_rot,fid_rot)

                  volId = node_dict[str(int(scan))]
                  [fiducialDetected, outliersDetected, registrationError, registrationTime, registrationMatrixName, registrationMatrixId] = registerScan(scan, volId)

                  regT = slicer.mrmlScene.GetNodeByID(registrationMatrixId)
                  regMat = vtk.vtkMatrix4x4()
                  regT.GetMatrixTransformToParent(regMat)

                  if not referenceRegDone:
                     for i in range (0,4):
                        for j in range(0,4):
                           referenceMatrix[i,j] = regMat.GetElement(i,j)
                     invertReferenceMatrix = referenceMatrix.I
                     referenceRegDone = True
                     continue

                  for i in range(0,4):
                     for j in range(0,4):
                        newRegistrationMatrix[i,j] = regMat.GetElement(i,j)
                  relativeMatrix = newRegistrationMatrix*invertReferenceMatrix

                  relativeTransform = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
                  relativeTransform.SetName("Relative_RegistrationMatrix_Serie"+str(scan))
                  slicer.mrmlScene.AddNode(relativeTransform)
                  transformRelativeMatrix = vtk.vtkMatrix4x4()
                  for i in range(0,4):
                     for j in range(0,4):
                        transformRelativeMatrix.SetElement(i,j,relativeMatrix[i,j])
                  relativeTransform.SetAndObserveMatrixTransformToParent(transformRelativeMatrix)

                  csvwriter.writerow( (scan, x, y, z, block, block_rot, fid_rot, fiducialDetected, outliersDetected, registrationError, registrationTime, registrationMatrixName) )

         
