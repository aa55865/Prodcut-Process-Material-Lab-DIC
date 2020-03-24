from data_parser import *
import csv
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.spatial import distance
import numpy as np

#INPUT SAMPLE INFORMATION
angle = 0
specimen = 8
Area = 1.8
upper_subset_ID = 27
lower_subset_ID = 14
initial_length = 143

#VIRTUAL EXTENSOMETER FUNCTION THAT EXTRACTS RAW DIC DISPLACEMENTS AND CONVERTS TO STRAIN
def extensometer(upper_subset, lower_subset, initial_length):
    upper_subset_x0 = DICer(subset=upper_subset, data='x_coordinate', samprate=1) #initial x-coordinate of upper subset
    upper_subset_y0 = DICer(subset=upper_subset, data='y_coordinate', samprate=1) #initial y-coordinate of upper subset
    upper_subset_x_disp = DICer(subset=upper_subset, data='x_displacement', samprate=1) #x-direction displacement of upper subset
    upper_subset_y_disp = DICer(subset=upper_subset, data='y_displacement', samprate=1) #y-direction displacement of upper subset
    lower_subset_x0 = DICer(subset=lower_subset, data='x_coordinate', samprate=1) #initial x-coordinate of lower subset
    lower_subset_y0 = DICer(subset=lower_subset, data='y_coordinate', samprate=1) #initial y-coordinate of lower subset
    lower_subset_x_disp = DICer(subset=lower_subset, data='x_displacement', samprate=1) #x-direction displacement of lower subset
    lower_subset_y_disp = DICer(subset=lower_subset, data='y_displacement', samprate=1) #y-direction displacement of lower subset

    upper_subset_x = [x-disp for x,disp in zip(upper_subset_x0[1],upper_subset_x_disp[1])]
    upper_subset_y = [y-disp for y,disp in zip(upper_subset_y0[1],upper_subset_y_disp[1])]
    lower_subset_x = [x-disp for x,disp in zip(lower_subset_x0[1],lower_subset_x_disp[1])]
    lower_subset_y = [y-disp for y,disp in zip(lower_subset_y0[1],lower_subset_y_disp[1])]

    strain_time = upper_subset_x0[0]
    upper_coordinates = [(x,y) for x,y in zip(upper_subset_x,upper_subset_y)]
    lower_coordinates = [(x,y) for x,y in zip(lower_subset_x,lower_subset_y)]
    strain = []
    dst_values = []
    for upper_coordinate,lower_coordinate in zip(upper_coordinates,lower_coordinates):
        dst = distance.euclidean(upper_coordinate,lower_coordinate)
        dst_values.append(dst)
        strain.append((dst-initial_length)/initial_length)
    plt.plot(strain_time,upper_subset_y_disp[1], 'o', strain_time, lower_subset_y_disp[1],'o')
    plt.title('Displacement vs Time: 3mm 90 Degree Specimen 1')
    plt.xlabel('time [s]')
    plt.ylabel('displacements [pixels]')
    plt.show()
    return strain_time, strain, upper_subset_y_disp[1]

dic_data = extensometer(upper_subset_ID,lower_subset_ID,initial_length)
strain_values = dic_data[1]
strain_time = dic_data[0]
upper_subset_displacement = dic_data[2]


plt.plot(strain_time,strain_values,'o')
plt.title('Virtual Extensometer: Strain vs. Time')
plt.xlabel('time [s]')
plt.ylabel('strain [pxl/pxl]')
plt.show()

#EXTRACT RAW LOAD DATA (LOAD & TIME)
path = 'C:\\Users\\aa55865\\Desktop\\lattice_strut_study\\final_strut_samples\\5mm_specimens\\{}deg\\specimen{}\\raw_load_v_time.csv'.format(angle,specimen)
load_samprate = 10 #samples per second
file = open(path, newline='')
reader = csv.reader(file)
header = next(reader)
load_values = []
load_time = []
for index, row in enumerate(reader):
    if index > 0:
        load_values.append(float(row[1].replace(',', '')))
        load_time.append(float(row[4]))
plt.figure()
plt.plot(load_time, load_values,'o')
plt.xlabel('time [s]')
plt.ylabel('Force [N]')
plt.title('Force vs. Time')
plt.show()

#DEFINE FUNCTION THAT ALLOWS COMPARISON OF ADJACENT DATA POINTS TO DETERMINE TIME OF FRACTURE
def adjacent_pairs(seq):
    it = iter(seq)
    prev = next(it)
    for item in it:
        yield(prev,item)
        prev = item

tbreak_strain = float(input('strain fracture time: '))
tbreak_load = float(input('load fracture time: '))

#ADJUST DIC TIME DOMAIN TO ALIGN STRAIN DATA FRACTURE TIME WITH LOAD DATA FRACTURE TIME AND NORMALIZE DATA SETS TO CONSTRUCT SYNCHRONIZATION CHECK PLOT
delay = tbreak_strain - tbreak_load
strain_norm_factor = max(strain_values)
load_norm_factor = max(load_values)
adj_strain_time = [value-delay for value in strain_time]
norm_strain = [value/strain_norm_factor for value in strain_values]
norm_load = [value/load_norm_factor for value in load_values]

fig = plt.figure()
plt.plot(adj_strain_time,norm_strain,'ro',load_time,norm_load,'bo')
plt.ylabel('Normalized Load and Strain')
plt.xlabel('Time (s)')
plt.title('Synchronization Check: Normalized Load & Normalized Strain')
plt.show()

sample_time = np.linspace(0,tbreak_load,1000)

sample_area = Area
load_curve = interpolate.splrep(load_time,load_values)
interpolated_load_values = interpolate.splev(sample_time,load_curve)
interpolated_stress_values = [value/sample_area for value in interpolated_load_values]

strain_curve = interpolate.splrep(adj_strain_time, strain_values,s=0.000005)
interpolated_strain_values = interpolate.splev(sample_time, strain_curve)

plt.figure()
plt.plot(sample_time,interpolated_load_values, load_time, load_values, 'o')
plt.title('interpolated load vs. time')
plt.ylabel('load [N]')
plt.xlabel('time [s]')
plt.show()

plt.figure()
plt.plot(sample_time,interpolated_strain_values,adj_strain_time,strain_values,'o')
plt.title('interpolated strain vs. time')
plt.ylabel('strain [pxl/pxl]')
plt.xlabel('time [s]')
plt.show()

plt.figure()
plt.plot(interpolated_strain_values,interpolated_stress_values,'o')
plt.title('Stress vs. Strain: 3mm {} Degree Specimen {}'.format(angle,specimen))
plt.ylabel('Stress [MPa]')
plt.xlabel('strain [pxl/pxl]')
plt.savefig('C:\\Users\\aa55865\\Desktop\\lattice_strut_study\\final_strut_samples\\5mm_specimens\\{}deg\\specimen{}\\stress-strain_curve.png'.format(angle,specimen))
plt.show()

with open('C:\\Users\\aa55865\\Desktop\\lattice_strut_study\\final_strut_samples\\5mm_specimens\\{}deg\\specimen{}\\stress-strain_data.csv'.format(angle,specimen),'w') as f:
    writer = csv.writer(f)
    writer.writerows(zip(interpolated_strain_values, interpolated_stress_values))