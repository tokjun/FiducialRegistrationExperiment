import os
import csv
import time
import numpy
from __main__ import vtk, qt, ctk, slicer

def runRegistration(scan, volId):
   
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
   
   if reg.applyButton.enabled == True:
      reg.onApplyButton()

   procTime = reg.logic.procTimeDetection + reg.logic.procTimeCircleFit
   wallTime = reg.logic.wallTimeDetection + reg.logic.wallTimeCircleFit

   return reg.fiducialDetectedBox.text, reg.outliersDetectedBox.text, reg.registrationError.text, procTime, wallTime, registrationMatrix.GetName(), registrationMatrix.GetID()

def calculateGoldStandard(scan,x,y,z,block,block_rot,fid_rot, transform):

   transform.RotateY(-float(fid_rot)*vtk.vtkMath.Pi()/180.0)
   transform.RotateX(float(block)*vtk.vtkMath.Pi()/180.0)
   transform.RotateY(float(block_rot)*vtk.vtkMath.Pi()/180.0)
   
   transform.Translate(-int(x)*50,int(z)*10,-int(y)*50)
   
   #### Debug ###
   #n = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
   #n.SetName("Transform_GoldStandard_Serie"+str(scan))
   #slicer.mrmlScene.AddNode(n)
   #n.SetAndObserveMatrixTransformToParent(transform.GetMatrix())
   ##############

   return 0


def batchRegistration(imageInfoCSV, outputFile):
   
   # Open spreadsheets
   with open(imageInfoCSV,'rb') as ss:
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
         csvwriter.writerow( ('Scan#','X','Y','Z','Block','Bloc Rotation', 'Fiducial Rotation', 'Fiducials Detected', 'Outliers Detected', 'TRE', 'Wall Time', 'Proc Time', 'R00, R01, R02, R03, R10, R11, R12, R13, R20, R21, R22, R23, R30, R31, R32, R33') )

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
               scanstr = str(int(scan))
               if scanstr in node_dict:
                                                  
                  volId = node_dict[str(int(scan))]
                  [fiducialDetected, outliersDetected, registrationError, wallTime, procTime, registrationMatrixName, registrationMatrixId] = runRegistration(str(int(scan)), volId)

                  regT = slicer.mrmlScene.GetNodeByID(registrationMatrixId)
                  regMat = vtk.vtkMatrix4x4()
                  regT.GetMatrixTransformToParent(regMat)

                  csvwriter.writerow( (str(int(scan)), x, y, z, block, block_rot, fid_rot, fiducialDetected, outliersDetected, registrationError, wallTime, procTime, regMat.GetElement(0,0), regMat.GetElement(0,1), regMat.GetElement(0,2), regMat.GetElement(0,3), regMat.GetElement(1,0), regMat.GetElement(1,1), regMat.GetElement(1,2), regMat.GetElement(1,3), regMat.GetElement(2,0), regMat.GetElement(2,1), regMat.GetElement(2,2), regMat.GetElement(2,3), regMat.GetElement(3,0), regMat.GetElement(3,1), regMat.GetElement(3,2), regMat.GetElement(3,3)) )

                  slicer.mrmlScene.RemoveNode(regT)

   

def batchComputeError(registrationResultCSV, errorCSV):
   
   with open(registrationResultCSV,'rb') as inputFile:
      
      # Parse csv file
      csvreader = csv.reader(inputFile.readlines()[6:], delimiter=',')

      regMat = vtk.vtkMatrix4x4()
      transform = vtk.vtkTransform()
      baseMat = vtk.vtkMatrix4x4()
      
      for row in csvreader:
         #[scan, x, y, z, block, block_rot, fid_rot, fiducialDetected, outliersDetected, registrationError, wallTime, procTime] = row[0:12]

         scan = int(row[0])
         x = int(row[1])
         y = int(row[2])
         z = int(row[3])
         block = int(row[4])
         block_rot = int(row[5])
         fid_rot = int(row[6])
         fiducialDetected = int(row[7])
         outliersDetected = int(row[8])
         registrationError = float(row[9])
         wallTime = float(row[10])
         procTime = float(row[11])

         for i in range(0,16):
            regMat.SetElement(i/4, i%4, float(row[i+12]))
         
         # Calculate gold standard (could be done only for each line)
         calculateGoldStandard(str(int(scan)),x,y,z,block,block_rot,fid_rot, transform)
         transform.GetMatrix(baseMat)

         print '======================'
         print regMat
         print baseMat
         

                  
def processExperimentData(imageInfoCSV, outputFile):

   # Open spreadsheets
   with open(imageInfoCSV,'rb') as ss:
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

         baseMat = vtk.vtkMatrix4x4()
         transform = vtk.vtkTransform()
         
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
                  calculateGoldStandard(scan,x,y,z,block,block_rot,fid_rot, transform)
                  transform.GetMatrix(baseMat)

                  volId = node_dict[str(int(scan))]
                  [fiducialDetected, outliersDetected, registrationError, wallTime, procTime, registrationMatrixName, registrationMatrixId] = runRegistration(scan, volId)

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

                  csvwriter.writerow( (scan, x, y, z, block, block_rot, fid_rot, fiducialDetected, outliersDetected, registrationError, wallTime, ProcTime, registrationMatrixName) )



