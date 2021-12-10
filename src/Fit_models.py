"""
    The relACs is a analysis tool for magnetic data for SMM systems using
    various models for ac magnetic characteristics and the further reliable
    determination of diverse relaxation processes.

    Copyright (C) 2021  Wiktor Zychowicz & Mikolaj Zychowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" 

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


