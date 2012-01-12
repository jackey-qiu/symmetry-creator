import numpy as num
from numpy.linalg import inv
"""
Sym_creator is developped to generate symmetry operations for surface unit cell, it can also generate p1 atoms for bulk cell and surface cell
#########globals########
bulk_cell:a 3 item list, corresponding to a,b,c in bulk cell
surf_cell:a 3 item list, corresponding to a,b,c in bulk cell
bulk_to_surf:basis vector of surface unit cell in bulk unit cell
asym_atoms:a library containing asymmetry atom information
sym_file:a text file containing symmetry operations copied from cif file (no heads, no comments)
atm_p1_bulk:p1 atoms in original bulk unit cell,sorted by decreasing z value
atm_p1_surf:p1 atoms in surface unit cell, sorted by decreasing z value
sym_bulk:symmetry operations in bulk unit cell, expressed in matrix (3 by 4, rotation+shift)
sym_surf: symmetry operations in surface unit cell for each asymmetry atoms, in 3 by 4 matrix, the order is associated with (z,y,x) of atoms in surface unit cell
self.sym_surf_new_ref:symmetry operation of surface atoms for user defined reference atoms
#############################
print_file will create four text files, surface atom positions in fractional and angstrom, bulk atom positions in fractional and angstrom
"""
class sym_creator():
    def __init__(self,bulk_cell=[5.038,5.038,13.772],surf_cell=[5.038,5.434,7.3707],bulk_to_surf=[[1.,1.,0.],[-0.3333,0.333,0.333],[0.713,-0.713,0.287]],asym_atm={'Fe':(0.,0.,0.3553),'O':(0.3059,0.,0.25)},sym_file='c:\\python26\\symmetry of hematite.txt'):
        self.bulk_cell=bulk_cell
        self.surf_cell=surf_cell
        self.bulk_to_surf=bulk_to_surf
        self.sym_file=sym_file
        self.atm_p1_bulk={}
        self.atm_p1_surf={}
        self.sym_bulk=[]
        self.sym_surf={}
        self.asym_atm=asym_atm
        self.sym_surf_new_ref={}
        self.F=num.array(self.bulk_to_surf,dtype=float)
        self.F=inv(self.F).transpose()
        for k in self.asym_atm.keys():
            self.sym_surf_new_ref[k]={}

    def create_bulk_sym(self):
        f=open(self.sym_file,'r')
        fl=f.readlines()
        for i in fl:
            sym_tmp=num.array([[0,0,0,0]],dtype=float)
            i=eval(i).rsplit(',')
            for j in [0,1,2]:
                x,y,z=(0.,0.,0.)
                c=eval(i[j])
                x,y,z=(1.,0.,0.)
                x_=eval(i[j])-c
                x,y,z=(0.,1.,0.)
                y_=eval(i[j])-c
                x,y,z=(0.,0.,1.)
                z_=eval(i[j])-c
                sym_tmp=num.append(sym_tmp,[[x_,y_,z_,c]],axis=0)
            sym_tmp=sym_tmp[1::]
            self.sym_bulk.append(sym_tmp)
        
    def find_atm_bulk(self):
        for i in self.asym_atm.keys():
            self.atm_p1_bulk[i]=self._find_atm_bulk(self.asym_atm[i])
            
    def find_atm_surf(self):
        for i in self.asym_atm.keys():
            self.atm_p1_surf[i]=self._find_atm_surf(self.asym_atm[i])[0]
            self.sym_surf[i]=self._find_atm_surf(self.asym_atm[i])[1]
            
    def _find_atm_bulk(self,asym_atm):
        asym_atm=asym_atm
        atm_container=[]
        for i in [-1.,0.,1.]:
            for j in [-1.,0.,1.]:
                for k in [-1.,0.,1.]:
                    for s in self.sym_bulk:
                        temp= list(num.dot(s[0:3,0:3],asym_atm)+s[0:3,3]+[i,j,k])
                        #print list(temp)
                        temp[0]=num.round(temp[0],3)
                        temp[1]=num.round(temp[1],3)
                        temp[2]=num.round(temp[2],3)
                        if temp not in atm_container:
                            temp=num.array(temp)
                            tf=(temp>=0.)&(temp<=1.)
                            if (int(tf[0])+int(tf[1])+int(tf[2]))==3:
                                atm_container.append(list(temp))
        return atm_container
                
    def _find_atm_surf(self,asym_atm):
        asym_atm=asym_atm
        atm_container=[]
        sym_container=[]
        for r in range(1,10):
            ct=len(atm_container)
            for i in range(-r,r):
                for j in range(-r,r):
                    for k in range(-r,r):
                        for s in self.sym_bulk:
                            temp_sym=num.dot(self.F,s[0:3,0:3])
                            temp_sym=num.append(temp_sym,num.dot(self.F,s[0:3,3]+[i,j,k])[:,num.newaxis],axis=1)
                            temp=list(num.dot(temp_sym[0:3,0:3],asym_atm)+temp_sym[0:3,3])
                            temp[0]=num.round(temp[0],3)
                            temp[1]=num.round(temp[1],3)
                            temp[2]=num.round(temp[2],3)
                            if temp not in atm_container:
                                temp=num.array(temp)
                                tf=(temp>=0.)&(temp<=1.)
                                if (int(tf[0])+int(tf[1])+int(tf[2]))==3:
                                    atm_container.append(list(temp))
                                    sym_container.append(temp_sym)
            if ct==len(atm_container):
                break
        data=[]
        for i in range(len(atm_container)):
            data.append((sym_container[i],atm_container[i][0],atm_container[i][1],atm_container[i][2]))
        dtype=[('sym',num.ndarray),('x',float),('y',float),('z',float)]
        data=num.array(data,dtype=dtype)
        data=num.sort(data,order=['z','y','x'])
        data=data[::-1]
        for i in range(len(data)):
            sym_container[i]=data[i][0]
            atm_container[i]=[data[i][1],data[i][2],data[i][3]]
        return atm_container,sym_container
        
    def set_new_ref_atm_surf(self,el=['Fe','O'],rn=[0,1,2],print_file=False):
        for element in el:
            for ref_N in rn:
                sym=num.copy(self.sym_surf[element])
                ref_atm=sym[ref_N]
                T=inv(ref_atm[0:3,0:3])
                t=-num.dot(T,ref_atm[0:3,3])
                for i in range(len(sym)):
                    M=num.dot(sym[i][0:3,0:3],T)
                    c=num.dot(sym[i][0:3,0:3],t)+sym[i][0:3,3]
                    sym[i]=num.append(M,c[:,num.newaxis],axis=1)
                self.sym_surf_new_ref[element][ref_N]=sym
                if print_file==True:
                    sym_output=num.array([[0,0,0,0,0,0,0,0,0]],dtype=float)
                    for i in sym:
                    #here we only need the rotation part to set the dxdydz in Genx, the transpose is fit with function in Genx
                        sym_output=num.append(sym_output,i[0:3,0:3].transpose().reshape(1,9),axis=0)
                    sym_output=sym_output[1::]
                    num.savetxt(element+str(ref_N)+' output file for Genx reading.txt', sym_output, delimiter=',')
    
    def set_ref_all(self,print_file=False):    
        for i in self.atm_p1_surf.keys():
            for j in range(len(self.atm_p1_surf[i])):
                self.set_new_ref_atm_surf(el=[i],rn=[j],print_file=print_file)
                #print self.sym_surf_new_ref[i][j]
            
    def cal_coor(self,ref_N,element):
    #this function is for test purpose
        asym=self.atm_p1_surf[element][ref_N]
        atm_surf=num.array([[0.,0.,0.]])
        for i in self.sym_surf_new_ref[element][ref_N]:
            atm_surf=num.append(atm_surf,[num.dot(i[0:3,0:3],asym)+i[0:3,3]],axis=0)
        atm_surf=atm_surf[1:len(atm_surf)]
        return atm_surf
            
    def _test_sym_mat(self,atm_N,element):
        print 'surf_atm',self.atm_p1_surf[element][atm_N]
        for i in range(len(self.atm_p1_surf[element])):
            print ('calc_atm'+str(i),num.dot(self.sym_surf_new_ref[element][i][atm_N][0:3,0:3],self.atm_p1_surf[element][i])+self.sym_surf_new_ref[element][i][atm_N][0:3,3])
            
    def print_files(self,filename='hematite',b_f=True,b_a=True,s_f=True,s_a=True):
        if b_f==True:
            file=open(filename+'bulk_xyz_fract.txt','w')
            s = '%-5i\n' % sum([len(self.atm_p1_bulk[i]) for i in self.atm_p1_bulk.keys()])
            file.write(s)
            s= '%-5s\n' % '#bulk_xyz fractionals'
            file.write(s)
            for i in self.atm_p1_bulk.keys():
                for j in self.atm_p1_bulk[i]:
                    s = '%-5s   %7.5e   %7.5e   %7.5e\n' % (i,j[0],j[1],j[2])
                    file.write(s)
            file.close()
        
        if b_a==True:
            file=open(filename+'bulk_xyz_angstrom.txt','w')
            s = '%-5i\n' % sum([len(self.atm_p1_bulk[i]) for i in self.atm_p1_bulk.keys()])
            file.write(s)
            s= '%-5s\n' % '#bulk_xyz in angstrom'
            file.write(s)
            for i in self.atm_p1_bulk.keys():
                for j in self.atm_p1_bulk[i]:
                    s = '%-5s   %7.5e   %7.5e   %7.5e\n' % (i,j[0]*self.bulk_cell[0],j[1]*self.bulk_cell[1],j[2]*self.bulk_cell[2])
                    file.write(s)
            file.close()
        
        if s_f==True:
            file=open(filename+'surf_xyz_fract.txt','w')
            s = '%-5i\n' % sum([len(self.atm_p1_surf[i]) for i in self.atm_p1_surf.keys()])
            file.write(s)
            s= '%-5s\n' % '#surf_xyz fractionals'
            file.write(s)
            for i in self.atm_p1_surf.keys():
                for j in self.atm_p1_surf[i]:
                    s = '%-5s   %7.5e   %7.5e   %7.5e\n' % (i,j[0],j[1],j[2])
                    file.write(s)
            file.close()
        
        if s_a==True:
            file=open(filename+'surf_xyz_angstrom.txt','w')
            s = '%-5i\n' % sum([len(self.atm_p1_surf[i]) for i in self.atm_p1_surf.keys()])
            file.write(s)
            s= '%-5s\n' % '#surf_xyz in angstrom'
            file.write(s)
            for i in self.atm_p1_surf.keys():
                for j in self.atm_p1_surf[i]:
                    s = '%-5s   %7.5e   %7.5e   %7.5e\n' % (i,j[0]*self.surf_cell[0],j[1]*self.surf_cell[1],j[2]*self.surf_cell[2])
                    file.write(s)
            file.close()

def make_script(filename='Y:\\codes\\my code\\modeling files\\hematitesurf_xyz_fract.txt',domains=2,u={'Fe':0.32,'O':0.33},element={'Fe':0,'O':0},delta={'delta1':0.,'delta2':0.1391}):
    f=open(filename)
    fl=f.readlines()
    ff=open(filename+'_new.txt','w')
    
    for i in fl:
        line=i.rsplit()
        element[line[0]]=element[line[0]]+1
        s = '%-5s %-5s %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s\n' % \
        ('bulk.add_atom(','"'+line[0]+str(element[line[0]])+'",','"'+line[0]+'",',float(line[1]),\
        ',',float(line[2]),',',float(line[3]),',',u[line[0]],',',1.,',',1.,')')
        ff.write(s)
    for ii in element.keys():
        element[ii]=0
    for i in range(domains):
        for j in fl:
            line=j.rsplit()
            element[line[0]]=element[line[0]]+1
            s = '%-5s %-5s %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s\n' % \
            ('domain'+str(i)+'.add_atom(','"'+line[0]+str(element[line[0]])+'_'+str(i)+'",','"'+line[0]+'",',float(line[1]),\
            ',',float(line[2]),',',float(line[3]),',',u[line[0]],',',1.,',',1.,')')
            ff.write(s)
        for ii in element.keys():
            element[ii]=0
        for j in fl:
            line=j.rsplit()
            element[line[0]]=element[line[0]]+1
            s = '%-5s %-5s %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s %7.5e %-5s\n' % \
            ('domain'+str(i)+'.add_atom(','"'+line[0]+'1_'+str(element[line[0]])+'_'+str(i)+'",','"'+line[0]+'",',float(line[1])+delta['delta1'],\
            ',',float(line[2])+delta['delta2'],',',float(line[3])+1.,',',u[line[0]],',',1.,',',1.,')')
            ff.write(s)
        for ii in element.keys():
            element[ii]=0
    f.close()
    ff.close()
    
if __name__=='__main__':
    #a,b,c for bulk and surface unit cell
    bulk_cell=[5.038,5.038,13.772]
    surf_cell=[5.038,5.434,7.3707]
    #basis vector of surface unit cell expressed in bulk unit cell
    bulk_to_surf=[[1.,1.,0.],[-0.3333,0.333,0.333],[0.713,-0.713,0.287]]
    #asymmetry atoms
    asym_atm={'Fe':(0.,0.,0.3553),'O':(0.3059,0.,0.25)}
    #symmetry operations copy from cif file
    sym_file='c:\\python26\\symmetry of hematite.txt'
    test=sym_creator(bulk_cell=bulk_cell,surf_cell=surf_cell,bulk_to_surf=bulk_to_surf,asym_atm=asym_atm,sym_file=sym_file)
    #express the symmetry operations in form of matrix (3 by 4, rotation+shift)
    test.create_bulk_sym()
    #generate p1 atoms in the bulk unit cell
    test.find_atm_bulk()
    #generate p1 atoms in the surface unit cell, and at the same time generate the symmetry operations for each atom, expressed in array (3 by 4)
    test.find_atm_surf()
    #set the asymmetry atom in the surface unit cell, the surface atoms has been sorted by deceasing z value, so 0 here means first Fe atom
    test.set_new_ref_atm_surf(0,'Fe')
    #print the p1 atoms in surface unit cell
    num.array(test.atm_p1_surf['Fe'])
    #print the p1 atoms generated using new surface symmetry operations, the result should be the same as the original printing result
    test.cal_coor(0,'Fe')