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


def calculateTheoreticalTransform(x,y,z,block,block_rot,fid_rot, matrix):

   transform = vtk.vtkTransform()
   transform.Identity()
   transform.PostMultiply()

   transform.RotateY(float(fid_rot))
   transform.RotateZ(-float(block))
   transform.RotateY(float(block_rot))
   transform.Translate(-int(x)*50,int(z)*10,-int(y)*50)

   transform.GetMatrix(matrix)

   print matrix

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


def closeEnough(a, b):
   return (numpy.finfo(float).eps > numpy.abs(a - b));

def computeEulerAngles(R):
   # Based on http://stackoverflow.com/questions/18433801/converting-a-3x3-matrix-to-euler-tait-bryan-angles-pitch-yaw-roll

   #check for gimbal lock
   if closeEnough(R.GetElement(0, 2), -1.0):

      x = 0.0 #gimbal lock, value of x doesn't matter
      y = numpy.pi / 2.0
      z = x + numpy.arctan2(R.GetElement(1, 0), R.GetElement(2, 0))

      return (x, y, z)

   elif closeEnough(R.GetElement(0, 2), 1.0):

      x = 0.0
      y = -numpy.pi / 2.0;
      z = -x + numpy.arctan2(-R.GetElement(1, 0), -R.GetElement(2, 0))

      return (x, y, z)

   else: # two solutions exist

      x1 = -numpy.arcsin(R.GetElement(0, 2))
      x2 = numpy.pi - x1
      y1 = numpy.arctan2(R.GetElement(1, 2) / numpy.cos(x1), R.GetElement(2, 2) / numpy.cos(x1))
      y2 = numpy.arctan2(R.GetElement(1, 2) / numpy.cos(x2), R.GetElement(2, 2) / numpy.cos(x2))
      z1 = numpy.arctan2(R.GetElement(0, 1) / numpy.cos(x1), R.GetElement(0, 0) / numpy.cos(x1))
      z2 = numpy.arctan2(R.GetElement(0, 1) / numpy.cos(x2), R.GetElement(0, 0) / numpy.cos(x2))

      # choose one solution to return
      # for example the "shortest" rotation
      if (numpy.abs(x1) + numpy.abs(y1) + numpy.abs(z1)) <= (numpy.abs(x2) + numpy.abs(y2) + numpy.abs(z2)):
         return (x1, y1, z1)
      else:
         return (x2, y2, z2)


def batchComputeError(registrationResultCSV, errorCSV):
   
   with open(registrationResultCSV,'rb') as inputFile:
      with open(errorCSV,'wb') as outputFile:

         csvwriter = csv.writer(outputFile)

         # Parse csv file
         csvreader = csv.reader(inputFile.readlines()[1:], delimiter=',')
   
         paramArray = []
         regMatrixArray = []
         theoMatrixArray = []
   
         originArray = [] # Array of scan # where the marker is placed at the origin
         nScans = 0

         for row in csvreader:
   
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
   
            regMatrix = vtk.vtkMatrix4x4()
            for i in range(0,16):
               regMatrix.SetElement(i/4, i%4, float(row[i+12]))
            
            if x == 0 and y == 0 and z == 1 and block == 0 and block_rot == 0 and fid_rot == 0:
               originArray.append(nScans)
   
            paramArray.append([scan, x, y, z, block, block_rot, fid_rot])
            regMatrixArray.append(regMatrix)
   
            # Calculate theoretical transform
            theoMatrix = vtk.vtkMatrix4x4()
            calculateTheoreticalTransform(x,y,z,block,block_rot,fid_rot, theoMatrix)
            theoMatrixArray.append(theoMatrix)
   
            nScans = nScans + 1

         if len(originArray) == 0:  ## for 11-19-2015 (no scan at the origin) 
            for n in range(0, nScans):
               [scan, x, y, z, block, block_rot, fid_rot] = paramArray[n]
               if x == 0 and y == 0 and z == 1 and block == 30 and block_rot == 0 and fid_rot == 0:
                  originArray.append(n)
   
   
         # Was the marker scanned consecutively at the origin?
         fConsecutiveOrigin = 0
         scan0 = paramArray[originArray[0]][0]
         scan1 = paramArray[originArray[1]][0]
         if (scan0 - scan1) == 1:
            fConsecutiveOrigin = 1
            
         print 'fConsecutiveOrigin = %d' % fConsecutiveOrigin

         # Always assume that the marker was scanned at the origin consectively
         # (Don't try to find the most recent origin scan.)
         # Comment out if the ost recent origin scan needs to be selected.
         fConsecutiveOrigin=1
   
         csvwriter.writerow(('Scan', 'R', 'A', 'S', 'BlockTilt', 'BlockRot', 'FiducialRot', 'FiducialDetected', 'OutliersDetected', 'RegistrationError', 'WallTime', 'ProcTime', 'dR', 'dA', 'dS', 'ThetaR', 'ThetaA', 'ThetaS'))

         # Main loop
         recentOriginArrayIndex = 0
         for n in range(0, nScans):
            
            [scan, x, y, z, block, block_rot, fid_rot] = paramArray[n]
   
            ## Find the most recent scan at the origin
            # If the marker was scannend at the origin consecutively,
            # the origin scan was assigned alternatively
            recentOriginIndex = -1
            recentOriginScan = -1
   
            if fConsecutiveOrigin:
               recentOriginIndex = originArray[recentOriginArrayIndex]
               recentOriginArrayIndex = (recentOriginArrayIndex + 1)%len(originArray)
            else:
               for m in originArray:
                  [scan_o, x_o, y_o, z_o, block_o, block_rot_o, fid_rot_o] = paramArray[m]
                  if scan_o <= scan and scan_o > recentOriginScan:
                     recentOriginScan = scan_o
                     recentOriginIndex = m
   
            if recentOriginIndex < 0:
               print "ERROR: No recent scan at origin."
               return

            [scan_o, x_o, y_o, z_o, block_o, block_rot_o, fid_rot_o] = paramArray[recentOriginIndex]
            recentOriginScan = scan_o
            #print 'currentScan/recentOriginScan  = %d/%d' % (scan, recentOriginScan)
            
            ## Obtain theoretical transform from the origin to the current
            theoOriginMatrix = theoMatrixArray[recentOriginIndex]
            theoRefMatrix = theoMatrixArray[n]

            ## Obtain actual transform from the origin to the current
            originMatrix = regMatrixArray[recentOriginIndex]
            refMatrix = regMatrixArray[n]

            ## Calibrate the transform at origin
            ## T = T_orig * T_orig^-1
            invTheoOriginMatrix = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Invert(theoOriginMatrix, invTheoOriginMatrix)
            calibrationMatrix = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Multiply4x4(originMatrix, invTheoOriginMatrix, calibrationMatrix)
            
            ## Calibrate theoretical reference matrix
            ## <T> = <T_ref> * <T_orig>^-1
            correctedTheoRefMatrix = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Multiply4x4(calibrationMatrix, theoRefMatrix, correctedTheoRefMatrix)

            ## Compute the error between the actual and the theoretical transforms
            ## T_err = <T> * T^-1
            invCorrectedTheoRefMatrix = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Invert(correctedTheoRefMatrix, invCorrectedTheoRefMatrix)
   
            errorMatrix = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Multiply4x4(refMatrix, invCorrectedTheoRefMatrix, errorMatrix)

            ## Compute Euler Angles (rad)
            (thetaX, thetaY, thetaZ) = computeEulerAngles(errorMatrix)

            ## Convert to angles
            thetaR = thetaX * 180.0/numpy.pi
            thetaA = thetaY * 180.0/numpy.pi
            thetaS = thetaZ * 180.0/numpy.pi

            ## Extract offsets
            dR = errorMatrix.GetElement(0, 3)
            dA = errorMatrix.GetElement(1, 3)
            dS = errorMatrix.GetElement(2, 3)

            R = -50.0*x
            A = 10.0*z
            S = -50.0*y
            csvwriter.writerow((scan, R, A, S, block, block_rot, fid_rot, fiducialDetected, outliersDetected, registrationError, wallTime, procTime, dR, dA, dS, thetaR, thetaA, thetaS ))

            #print "errorMatrix"
            #print '(x, y, z) = (%f, %f, %f)' % (x, y, z)
            #print '(block, block_rot, fid_rot) = (%f, %f, %f)' % (block, block_rot, fid_rot)
            #print errorMatrix
            #csvwriter.writerow( (str(int(scan)), x, y, z, block, block_rot, fid_rot, fiducialDetected, outliersDetected, registrationError, wallTime, procTime, errorMatrix.GetElement(0,0), errorMatrix.GetElement(0,1), errorMatrix.GetElement(0,2), errorMatrix.GetElement(0,3), errorMatrix.GetElement(1,0), errorMatrix.GetElement(1,1), errorMatrix.GetElement(1,2), errorMatrix.GetElement(1,3), errorMatrix.GetElement(2,0), errorMatrix.GetElement(2,1), errorMatrix.GetElement(2,2), errorMatrix.GetElement(2,3), errorMatrix.GetElement(3,0), errorMatrix.GetElement(3,1), errorMatrix.GetElement(3,2), errorMatrix.GetElement(3,3)) )



