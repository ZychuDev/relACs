import numpy as np  

def Direct(temp, field, Adir, Ndir):
    return Adir*temp*np.power(field ,Ndir)

def QTM(temp, field, B1, B2, B3):
    return B1*(1+B3*field*field)/(1+B2*field*field)

def Raman(temp, field, CRaman, NRaman):
    return CRaman* np.power(temp, NRaman)

def Orbach(temp, field, Tau0, DeltaE):
    return Tau0 *np.exp(-DeltaE/temp)

def model(temp, field, Adir, Ndir, B1, B2, B3, CRaman, NRaman, Tau0, DeltaE):

    return Adir*temp*(field**Ndir) \
    + B1*(1+B3*field*field)/(1+B2*field*field) \
    + CRaman * np.power(temp, NRaman) \
    + Tau0 *np.exp(-DeltaE/(temp))


