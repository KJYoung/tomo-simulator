## Repository for the Tomogram simulation based on PyTom
This scripts are under development. Not optimized code.

### Done.
1. volume object(and .em file) generator from given PDB ID(.pdb, .cif both supported).   
2. compact volume generator(Cuboidal form).   
3. mrc file formatter
4. naive multiparticle generator.   
   1. Crowd scenario generator
   2. Particle incorporator
5. test rotation scheme   
   1. Compact Cuboid
   2. Relaxation to Minimum Cube
   3. Rotate
   4. Re-compact Cuboid
6. Random rotation with rotationStep.
7. PYTOM's em2mrc generates mrc file much faster. [ for certain file(1_withoutrotation.em) : 99s vs 6.6s ]
   1. But, mrcfile.validate -> false.
   2. int mode mrc generated. -> File size is efficient : 134.2M vs 536.9M
8. Dimension adjustment   
9. Subtomogram generator   
10. EMAN2-based mrc converter merged   
11. MRC fragment(split) module + merge module [fragment.py]   
12. Gaussian Noise Applier    

### TODO1.
1. EMDB not PDB
   1. Start with wgetPDB2ExactCompactMRC
2. Direct Subtomo not from Grandmodel
3. Subtomo percentage
4. Grandmodel particle distribution(ratio)
5. Normalization function!

### TODO2.
1. Standalone...
2. Image formation options...
3. Minus Noise
4. Subtomo include?
5. Other processing options?
6. Multithreading?

### Timeline
20220227 00:50 - compact volume generator completed.      
20220306 23:47 - Update Readme for rotation TODO.   
20220313 24:00 - Rotation.   
20220321 16:00 - Subtomogram generator, Metadata writer.   
20220402 04:00 - mrc output. dimension adjustment.   
20220411 23:00 - EMAN2 merged. volumeResizer(with average mode). Server Test.   
20220608 16:50 - Fragment MRC + Merge MRC.   
20220623 17:20 - Gaussian noise applier   
