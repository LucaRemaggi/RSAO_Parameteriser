# RSAO_Parameteriser
This Python library generates those parameters that define reverberant spatial audio objects (RSAOs). To run it, just run the main.py file. The .json file in output contains the RSAO parameters, in a structure that can be interpreted by VISR, i.e. the S3A project object-based renderer. Following the RSAO definition, these parameters describe the three components of a RIR: direct sound, early reflections, and late reverberation. 

INPUT: when running the main.py, you need to provide in input a .wav file, containing the four channels of a B-Format room impulse response (RIR) recording (i.e. ordered as W, X, Y, Z). As additional input, it is also required to provide the 3 dimensions of the room (in meters). 

OUTPUT: main.py generates a .json file, where the RSAO parameters are written following the metadata structure that can be interpreted by the S3A object-based renderer (i.e. VISR).  

Coded by: 
Luca Remaggi, CVSSP, University of Surrey

Public Release:
2019

You can use any code included in this package for research purposes. If you do, please cite the following papers: 
- P. Coleman, A. Franck, P. J. B. Jackson, R. J. Hughes, L. Remaggi, F. Melchior, "Object-based reverberation for   spatial audio", Journal of the Audio Engineering Society, Vol. 65, No. 1/2, pp. 66-77, 2017. 
- L. Remaggi, P. J. B. Jackson, P. Coleman, "Estimation of room reflection parameters for a reverberant spatial audio   object", 138th AES Convention, Warsaw, Poland, 2015. 
- P. Coleman, A. Franck, D. Menzies, P. J. B. Jackson, "Object-Based Reverberation Encoding from First-Order Ambisonic RIRs", 142nd AES Convention, Berlin, Germany, 2017.
