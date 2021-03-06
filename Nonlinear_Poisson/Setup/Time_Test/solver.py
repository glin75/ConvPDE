from mshr import *
from dolfin import *

import sys
import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt

import time
import csv
import png
from PIL import Image
#set_log_level(ERROR)
set_log_level(40)


import gc

##############################################  
#   Partial Differential Equation:           #
#                                            #
#   { div( a * grad(u) ) = f  on  Interior   #
#   { u = 0                   on  Boundary   #
#                                            #
##############################################

# Solves PDE defined above using the Finite Element Method; retrieves the
# mesh and coefficient data from the files generated by 'mesh.py' and 'data.py'
#def FEM_solver(resolution, mesh_resolution, mesh_directory, data_directory, solution_directory, mesh_ID, stiffness_ID, source_ID):
def FEM_solver(resolution, mesh_resolution, mesh_ID, data_ID, SAVE=False, COARSE=False):
    #set_log_level(ERROR)
    set_log_level(40)
    # Identifying label for saving files
    #ID_label = str(mesh_ID) + '_' + str(data_ID)
    ID_label = str(data_ID)
    
    # Specifiy file containing mesh
    if COARSE:
        mesh_filename = './Meshes/coarse_mesh_' + str(mesh_ID) + '.xml'
    else:
        mesh_filename = './Meshes/mesh_' + str(mesh_ID) + '.xml'

    # Recover mesh from file
    mesh = Mesh(mesh_filename)
    V = FunctionSpace(mesh, 'Lagrange', 1)

    # Create square mesh
    square_mesh = UnitSquareMesh(resolution-1,resolution-1)
    square_V = FunctionSpace(square_mesh, 'CG', 1)

    # Specify files containing stiffness/source function data
    #stiffness_function_filename = stiff_dir + 'stiff_function_' + str(stiff_ID) + '.xml'
    data_function_filename = './Data/data_' + str(data_ID) + '.xml'
    
    
    solution_function_filename = './Solutions/solution_' + ID_label  + '.xml'
    if COARSE:
        solution_filename = './Solutions/coarse_solution_' + ID_label + '.npy'
    else:
        solution_filename = './Solutions/solution_' + ID_label + '.npy'
    #hires_solution_filename = './Solutions/hires_solution_' + ID_label + '.npy'

    # Recover mesh from file
    #mesh = Mesh(mesh_filename)
    #V = FunctionSpace(mesh, 'Lagrange', 1)

    # Define mesh on unit square
    """
    square_domain = Rectangle(Point(-1.0,-1.0),Point(1.0,1.0))
    square_mesh = generate_mesh(square_domain,mesh_resolution)
    square_V = FunctionSpace(square_mesh, 'Lagrange', 1)
    """
    #square_mesh = UnitSquareMesh(resolution-1,resolution-1)
    #square_V = FunctionSpace(square_mesh, 'CG', 1)


    # Project stiffness term onto mesh
    #a_function = Function(square_V, stiffness_function_filename)
    #a = project(a_function, V)

    # Use constant stiffness term
    a = Constant('1.0')

    # Project source term onto mesh
    f_function = Function(square_V, data_function_filename)
    f = project(f_function, V)

    
    # Define boundary conditions
    u0 = Constant(0.0)
    def u0_boundary(x, on_boundary):
        return on_boundary
    bc = DirichletBC(V, u0, u0_boundary)

    # Define variational problem
    #u = TrialFunction(V)
    #v = TestFunction(V)
    
    #
    # Used to Interpolate New Data
    #
    
    #ti = np.linspace(-1.0, 1.0,resolution)
    #x = ti
    #y = ti
    #z = np.random.uniform(0.0,10.0,(resolution,resolution))
    #approximate = interpolate.RectBivariateSpline(x,y,z)
    #print('Interpolation Completed')
    #mesh_points = mesh.coordinates()
    #print(mesh_points)

    #a = Function(V)
    #a_vector = a.vector()
    #a_array = np.array(a_vector.array())
    #vals_shape = a_array.shape
    #vals_size = a_array.size

    #vals = np.zeros((vals_size,))
    #for k in range(0,vals_size):
    #    vals[k] = approximate.ev(mesh_points[k][0], mesh_points[k][1])

    #print(vals)

    #vals = np.random.uniform(0.0,1.0,vals_shape)
    #a.vector().set_local(np.array(vals))


    # Identity matrix for diagonal stiffness term
    #I_mat = Expression((('1.0','0.0'),
    #                    ('0.0','1.0')), degree=2)
    
    # Weak Formulation Integrand
    #A = inner(a*I_mat*nabla_grad(u), nabla_grad(v))*dx
    #L = f*v*dx

    # Compute Solution
    #u = Function(V)
    #solve(A == L, u, bc)

    # Define non-linearity term
    def q(u):
        return 1 + u**2


    # Define variational formulation
    u = Function(V)
    v = TestFunction(V)
    F = q(u)*inner(nabla_grad(u), nabla_grad(v))*dx + f*v*dx

    # Compute solution
    solve(F == 0, u, bc)



    # Compute min/max of solution
    #u_array = u.vector().array()
    #u_max = u_array.max()
    #u_min = u_array.min()

    # Save solution as Fenics Function
    #File(solution_function_filename) << u
    
    # Compute Norms
    #L2norm = norm(u, 'L2', mesh)
    #H1norm = norm(u, 'H1', mesh)



    step = 1.0/resolution
    start = 0.0 + step/2.0
        
    
    vals = np.zeros([resolution,resolution])
    for i in range(0,resolution):
        for j in range(0,resolution):
            x_coord = start + i*step
            y_coord = start + (resolution - 1 - j)*step
            pt = Point(x_coord, y_coord)
            cell_id = mesh.bounding_box_tree().compute_first_entity_collision(pt)
            #if mesh.bounding_box_tree().collides(pt):
            if cell_id < mesh.num_cells():
                try:
                    # Interior points can be evaluated directly
                    vals[j,i] = u(pt)
                except:
                    # Points near the boundary have issues due to rounding...
                    cell = Cell(mesh, cell_id)
                    coords = cell.get_vertex_coordinates()
                    new_x_coord = coords[0]
                    new_y_coord = coords[1]
                    new_pt = Point(new_x_coord, new_y_coord)
                    vals[j,i] = u(new_pt)
                    
                    


    # Save solutions to file [Note: must be False for time comparisons]
    if SAVE:

        np.save(solution_filename, vals)

        """
        ## Save hi-res solution array
        new_resolution = 2*resolution
        new_step = 1.0/new_resolution
        new_start = 0.0 + new_step/2.0
        
    
        new_vals = np.zeros([new_resolution,new_resolution])
        for i in range(0,new_resolution):
            for j in range(0,new_resolution):
                x_coord = new_start + i*new_step
                y_coord = new_start + (new_resolution - 1 - j)*new_step
                pt = Point(x_coord, y_coord)
                cell_id = mesh.bounding_box_tree().compute_first_entity_collision(pt)
                #if mesh.bounding_box_tree().collides(pt):
                if cell_id < mesh.num_cells():
                    try:
                        # Interior points can be evaluated directly
                        new_vals[j,i] = u(pt)
                    except:
                        # Points near the boundary have issues due to rounding...
                        cell = Cell(mesh, cell_id)
                        coords = cell.get_vertex_coordinates()
                        new_x_coord = coords[0]
                        new_y_coord = coords[1]
                        new_pt = Point(new_x_coord, new_y_coord)
                        new_vals[j,i] = u(new_pt)

        np.save(hires_solution_filename, new_vals)
        """


    
    # Cleanup to avoid continual memory increase
    #del_list = [mesh, V, square_mesh, square_V, f, f_function, u, vals, new_vals]
    #del del_list
    #gc.collect()
    


def gen_soln(current_data, total_count, resolution, mesh_resolution, SAVE, COARSE):
    #set_log_level(ERROR)
    set_log_level(40)
    time_step = 1
    step = 0
    #progress = '    [  Estimated Time  ~  N/A  ]'
    #start_time = time.clock()
    #count = 1
    #total_count = current_mesh*current_data
    #total_count = current_data

    
    for i in range(0,1):
        for j in range(current_data, current_data + total_count):
            step += 1
            #sys.stdout.flush()
            FEM_solver(resolution, mesh_resolution, j, j, SAVE, COARSE)
            #gc.collect()
            #count +=1
    #print('\n\n')

    
