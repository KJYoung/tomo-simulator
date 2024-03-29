# Rotate each axis : value explode..
def resolutionResizeUpper(identifier, pdbDir, volumeDir, outputDir, toResolution):
    inputPDBPath = f"{pdbDir}/{identifier}.pdb"
    from pytom.tools.files import checkFileExists

    if not checkFileExists(inputPDBPath):
        inputPDBPath = f"{pdbDir}/{identifier}.cif"
        if not checkFileExists(inputPDBPath):
            raise RuntimeError('resolutionResize : input File not found! ', filePath)

    inputVolumePath = f"{volumeDir}/{identifier}.em"
    outputVolumePath = f"{outputDir}/{identifier}.em"
    # Assume input is cube form!!
    resolution = getResolution( inputPDBPath )
    inputVolume = read( inputVolumePath )
    X, Y, Z = inputVolume.sizeX(), inputVolume.sizeY(), inputVolume.sizeZ()
    resizedSize = math.ceil( (inputVolume.sizeX() - 1)*resolution / toResolution ) 
    outputVolume = vol(resizedSize, Y, Z)
    outputVolume.setAll(0.0)
    print(f" BEFORE SIZE : {inputVolume.sizeX()} x {inputVolume.sizeY()} x {inputVolume.sizeZ()}")
    print(f" AFTER SIZE : {outputVolume.sizeX()} x {outputVolume.sizeX()} x {outputVolume.sizeX()}")
    # interpolate.
    for i in range(resizedSize):
        realcoord_im1 = (i-1) * toResolution
        realcoord_i   =   i   * toResolution
        realcoord_ip1 = (i+1) * toResolution

        lowerIdx = math.ceil(realcoord_im1 / resolution) if i-1 > 0 else 0
        upperIdx = math.floor(realcoord_ip1 / resolution)
        for j in range(Y):
            for k in range(Z):
                curVal = 0.0
                idx = lowerIdx
                #print(lowerIdx, "~", upperIdx, "-----------------------------------------------------------------------")
                while idx <= upperIdx:
                    realcoord_org = round( idx * resolution, 4 )
                    try:
                        modfactor = round( ( toResolution - abs( realcoord_i - realcoord_org ) ) / toResolution, 4 )
                        #print(toResolution, realcoord_i, realcoord_org, "at ", idx)
                        #print(modfactor, "at ", idx)
                        curVal += inputVolume.getV(idx, j, k) * modfactor
                    except:
                        pass
                    idx += 1
                outputVolume.setV(curVal, i, j, k)

    inputVolume = outputVolume
    #print("inputVolume", inputVolume.sizeX(), inputVolume.sizeY(), inputVolume.sizeZ())
    outputVolume = vol(resizedSize, resizedSize, Z)
    outputVolume.setAll(0.0)
    for j in range(resizedSize):
        realcoord_jm1 = (j-1) * toResolution
        realcoord_j   =   j   * toResolution
        realcoord_jp1 = (j+1) * toResolution

        lowerIdx = math.ceil(realcoord_jm1 / resolution) if j-1 > 0 else 0
        upperIdx = math.floor(realcoord_jp1 / resolution)
        for i in range(resizedSize):
            for k in range(Z):
                curVal = 0.0
                idx = lowerIdx
                while idx <= upperIdx:
                    realcoord_org = idx * resolution
                    try:
                        curVal += inputVolume.getV(i, idx, k) * ( toResolution - abs( realcoord_i - realcoord_org ) ) / toResolution
                    except:
                        pass
                        #print(idx, j, k, "//", X, Y, Z, "//", lowerIdx, "~", upperIdx)
                    idx += 1
                outputVolume.setV(curVal, i, j, k)

    inputVolume = outputVolume
    outputVolume = vol(resizedSize, resizedSize, resizedSize)
    outputVolume.setAll(0.0)
    for k in range(resizedSize):
        realcoord_km1 = (k-1) * toResolution
        realcoord_k   =   k   * toResolution
        realcoord_kp1 = (k+1) * toResolution
        lowerIdx = math.ceil(realcoord_km1 / resolution) if k-1 > 0 else 0
        upperIdx = math.floor(realcoord_kp1 / resolution)
        for i in range(resizedSize):
            for j in range(resizedSize):
                curVal = 0.0
                idx = lowerIdx
                while idx <= upperIdx:
                    realcoord_org = idx * resolution
                    try:
                        curVal += inputVolume.getV(i, j, idx) * ( toResolution - abs( realcoord_i - realcoord_org ) ) / toResolution
                    except:
                        pass
                    idx += 1
                outputVolume.setV(curVal, i, j, k)
    outputVolume.write(outputVolumePath)

def compactCuboid2rotateCube(cuboidPath, cubePath):
    cuboid = read(cuboidPath)
    x, y, z = cuboid.sizeX(), cuboid.sizeY(), cuboid.sizeZ()
    size = int(math.sqrt( x**2 + y**2 + z**2 )) + 1 # 0.5 * 2 = 1.
    cube = vol(size, size, size)
    
    sx, sy, sz = int((size-x)/2), int((size-y)/2), int((size-z)/2) 
    for i in range(x):
        for j in range(y):
            for k in range(z):
                cube.setV( cuboid.getV(i, j, k), i+sx, j+sy, k+sz )
    cube.write(cubePath)

def customSimulation(volumePath, simulatedPath=None, snrValue=0.1, rotation=None, wedgeAngle=None, shift=None):
    # Rotation : [ x axis , z axis , y axis ]
    wedge = 0.0
    shiftList = [0, 0, 0]

    v = read(volumePath)
    if rotation == None:
        rotation = [0, 0, 0]
    
    if wedgeAngle == None:
        wi = None
    else:
        wi = WedgeInfo(wedgeAngle=wedgeAngle, cutoffRadius=0.0)
    if not shift == None:
        shiftList = shift
    
    s = simpleSimulation( volume=v, rotation=rotation, shiftV=shiftList, wedgeInfo=wi, SNR=snrValue)
    if simulatedPath:
        s.write(simulatedPath)
    
    appendMetaDataln(f"customSimulation is done : inputfile is {volumePath} / outputfile is {simulatedPath}")
    appendMetaDataln(f"-snr : {snrValue}, rotation : {rotation}, wedgeAngle : {wedgeAngle}, shift : {shift}")
    return s

def simpleSimulation(volume,rotation,shiftV,wedgeInfo=None,SNR=0.1,mask=None):
    """
    simpleSimulation: Simulates an ET by applying rotation,shift,wedge and noise to an volume
    
    @param volume: the volume used for simulations
    @param rotation: the rotation applied to volume
    @param shiftV: shift vector applied to volume
    @param wedgeInfo: wedge applied to volume
    @param SNR: noise level applied to volume
    @param mask: Apodisation mask 
    @return: a simple cryo em simulation of volume 
    """
    from pytom_volume import vol,rotate,shift,initSphere
    from pytom.simulation import whiteNoise
    
    if not rotation == [0,0,0]:
        print('---ROTATE---')
        #print 'EMSimulation simpleSimulation: in rotation 1 ' + str(rotation)
        rotatedCopy = vol(volume.sizeX(),volume.sizeY(),volume.sizeZ())
        rotate(volume,rotatedCopy,rotation[0],rotation[1],rotation[2])
    else:
        rotatedCopy = vol(volume.sizeX(),volume.sizeY(),volume.sizeZ())
        rotatedCopy.copyVolume(volume)
    
    # #print 'EMSimulation simpleSimulation: after rotation ' 
    
    if not mask:
        #print 'EMSimulation simpleSimulation: in mask 1' 
        # mask = vol(volume.sizeX(),volume.sizeY(),volume.sizeZ())
        # initSphere(mask,volume.sizeX()//2-1,0,0, volume.sizeX()//2,
	    # volume.sizeX()//2, volume.sizeX()//2)
        # maskedCopy = rotatedCopy * mask # element wise multiplication.
        maskedCopy = rotatedCopy
    # if not mask.__class__ == vol:
    #     #print 'EMSimulation simpleSimulation: in mask 2'
        
    #     mask = mask.getVolume(rotation)
    #     maskedCopy = rotatedCopy * mask        
    # else:
    #     #print 'EMSimulation simpleSimulation: in mask 3'
    #     maskedCopy = rotatedCopy * mask
    
    print("EMSimulation simpleSimulation:  after mask")
    
    if not shiftV == [0,0,0]:
        print('--SHIFT---')
        shiftedCopy = vol(volume.sizeX(),volume.sizeY(),volume.sizeZ())
        shift(maskedCopy,shiftedCopy,shiftV[0],shiftV[1],shiftV[2])
    else:
        shiftedCopy = vol(volume.sizeX(),volume.sizeY(),volume.sizeZ())
        shiftedCopy.copyVolume(maskedCopy)
        
    if (shiftV == [0,0,0]) and (rotation==[0,0,0]):
        #no shift and no rotation -> simply take the original volume
        c = vol(maskedCopy.sizeX(),volume.sizeY(),volume.sizeZ())
        c.copyVolume(maskedCopy)
        noisyCopy = whiteNoise.add(c,SNR)
    else:
        noisyCopy = whiteNoise.add(shiftedCopy,SNR)
    
    if wedgeInfo:
        print('---WEDGE---')
        result = wedgeInfo.apply(noisyCopy)
    else:
        result = noisyCopy
    
    print('EMSimulation Simulation: end function')
        
    if result.__class__ == list :
        return result[0]
    else:
        return result