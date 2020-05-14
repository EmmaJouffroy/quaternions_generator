# -*- coding: utf-8 -*-

####
# JOUFFROY Emma intern 2020
####

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, colors
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import csv, glob, random, quaternion, collections, copy
import matplotlib.cm as cmx
import matplotlib.patches as mpatches


class Space():
    """
    This class allows us to create a space of quaternions distributed uniformly
    around an hypersphere, and to find a sequence of minimal transformations
    that allow us to span the sphere. 
    """

    def __init__(self, nb_quaternions, neighbour):
        """
        nb quaternions : number of quaternions in the space created
        neighbour : number from wich a quaternion can be chosen from the minimal distance
        """
        self.nb_quaternions = nb_quaternions
        self.neighbour = neighbour
        self.q0 = np.quaternion(1,0,0,0)

    def creating_couples(self):
        """
        Returns four points whose pairs satisfy conditions of Marsaglia 
        (1972) 
        """
        x1, x2, x3, x4 = 1, 1, 1, 1
        while (x1*x1+x2*x2 >= 1):
            x1, x2 = random.uniform(-1,1), random.uniform(-1,1)
        while (x3*x3+x4*x4>= 1):
            x3, x4 = random.uniform(-1,1), random.uniform(-1,1)
        return x1, x2, x3, x4

    def creating_quaternion(self):
        """
        Returns a quaternion formed by the poits returned by
        the function creatings_couples()
        """
        x1, x2, x3, x4 = self.creating_couples()
        sqrt_quat = np.math.sqrt((1-(x1*x1)-(x2*x2))/((x3*x3)+(x4*x4)))
        x, y, z, w = x1, x2, x3 * sqrt_quat, x4 * sqrt_quat
        quaternion = np.quaternion(x,y,z,w)
        return quaternion

    def create_space_distribution(self):
        """
        Returns an array formed by n quaternions evenly distribued
        on a surface of an hypersphere. 
        """
        quaternions_space = []
        for i in range(self.nb_quaternions):
            quaternion = self.creating_quaternion()
            while(quaternion in quaternions_space):
                quaternion = self.creating_quaternion()
            quaternions_space.append(quaternion)
        return quaternions_space

    def calcul_quaternion_transformation(self, q1, q2):
        """
        Returns the quaternion equivalent to the transformation 
        applied to q1 to obtain q2

        q1: quaternion at the beginning 
        q2: quaternion at the end
        """
        transformation = q1.inverse() * q2
        return transformation

    def find_next_quaternion(self, q_now, espace, transf_prec, first):
        """
        Returs the best next position in the hypersphere from the previous
        position, and the transformation associated. The best position is calculating
        by browsing the space of quaternions and finding the quaternion which minimzes
        the distance with the quaternion associated to the null angle plus the distance
        with the previous position.
        For this project, we decided to chose a random quaternion between the one 
        which minimizes the distance and self.neighbour. 

        q_now : the quaternion we are now
        space: space of quaternions evenly distributed in hypersphere
        transf_prec : the transformation applied to the previous quaternion to arrive
        at the actual quaternion q_now
        """
        # In order to chose the best next quaternion, we must create an ordered dictionary
        # (meaning an indexed dictionary)
        distances = collections.OrderedDict()
        space = copy.copy(espace)
        if(first == False):
            space.remove(q_now)
        for i, _ in enumerate(space):
            # qt1 is the quaternion which multiplied by rd_q1 gives space_array[i]
            qt1 = self.calcul_quaternion_transformation(q_now, space[i])
            # we compute the distance between the transformation applied before
            # and qt1 that we want to be minimal
            first_term = (transf_prec - qt1).absolute()
            # we compute the distance between the quaternion with null angle and qt1
            # that we want to be minimal 
            second_term = (self.q0 - qt1).absolute()
            # the final distance is the sum between the previous distances
            distance = first_term + second_term
            # we append the distance in the dictionnary associated to the quaternion
            distances[distance] = space[i]
        # we need to sort the distances, beginning by the lowest
        sorted_distance =  collections.OrderedDict(sorted(distances.items(), key=lambda t: t[0]))
        q2 = list(sorted_distance.items())
        #We get a random index between zero and self.neighbour to get out best_q2
        if self.neighbour != 0:
            rd_index = np.random.randint(0,self.neighbour)
        else : 
            rd_index = self.neighbour
        best_q2 = q2[rd_index][1]
        # transformation is the quaternion which multiplied by rd_q1 gives best_q2
        transformation = self.calcul_quaternion_transformation(q_now, best_q2)
        return best_q2, transformation

    def plot_hypersphere(self, space, colorsMap='jet'):
        """
        Plots a sphere in a 3D space, and all the axis of rotation for every
        quaternion created in the space.

        space: space of quaternions evenly distributed in hypersphere
        """
        #We need to get every component of the quaternions separately
        X, Y, Z ,W = np.array([]),np.array([]),np.array([]),np.array([])

        for i, space in enumerate(space):
            X = np.append(X, space.x)
            Y = np.append(Y, space.y)
            Z = np.append(Z, space.z)
            W = np.append(W, space.w)
        # parameters of the colormap
        cm = plt.get_cmap(colorsMap)
        cNorm = colors.Normalize(vmin=min(W), vmax=max(W))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        # parameters of the figure
        fig = plt.figure()
        ax = Axes3D(fig)
        # plot of the hypersphere
        u = np.linspace( 0, 2 * np.pi, 50 )
        v = np.linspace( 0, np.pi, 25 )
        x = 1 * np.outer( np.cos( u ), np.sin( v ) )
        y = 1 * np.outer( np.sin( u ), np.sin( v ) )
        z = 1 * np.outer( np.ones( np.size( u ) ), np.cos( v ) )
        ax.plot_wireframe( x, y, z, color='g', alpha=.3 ) 
        # plot of the components (x,y,z) of everyquaternion as a vector
        # with a color associated to the value w.
        ax.quiver(0, 0, 0, X, Y, Z, color=scalarMap.to_rgba(W))
        scalarMap.set_array(W)
        fig.colorbar(scalarMap,label='Value of rotation')
        plt.axis('off')
        plt.title('Quaternions distribution in hypersphere')  
        plt.show()
        plt.savefig('quaternions_distribution.png')

    def explore_space(self, space):
        """
        From the quaternion associated with the null angle, creates the sequence of
        every best new position and transformation associated. Returns an array with every 
        position and every transformation. Creates a csv file that can be used with blender
        to make the rotations.

        space: space of quaternions evenly distributed in hypersphere
        """
        # we create three numpy arrays to get the positions and the transformations
        # "position_list_quat" and "position_list" are the same arrays, with the 
        # difference that one contains the quaternions as quaternions Object and the 
        # other as numpy arrays.
        position_list_quat = []
        position_list = []
        transf_list = []
        # first, we find the best quaternion and the transformation associated 
        # beginning by q0, with a transformation of q0. 
        q, transf = self.find_next_quaternion(self.q0, space, self.q0, first=True)
        # We get the vector part (x,y,z) from q0 as a numpy array and
        # appends it to the position array
        position_list_quat.append(quaternion.as_float_array(q))
        position_list.append(q)
        # we append the transformation in the transf_list as a numpy array
        # [w,x,y,z]
        transf_list.append(transf)
        # for every quaternion in space :
        for i in range(10000):
            # we find the best next quaternion and transformation associated,
            # beginning with what we found for q0
            q, transf = self.find_next_quaternion(q, space, transf, first=False)
            # we append the position and the transformation respectively in 
            # the two numpy arrays.
            position_list_quat.append(quaternion.as_float_array(q))
            position_list.append(q)
            transf_list.append(transf)
        # Finally, we create a csv file containing every position
        # that can be used in Blender to create the rotations of our stl files. 
        np.savetxt("rotations_csv.csv", position_list_quat, delimiter=",")
        return position_list, transf_list, position_list_quat

    def create_gif(self, filepath, filename):
        """
        Saves a GIF image for every STL rotated with blender, using the transformation
        csv file.

        filepath: path to the folder containing images for the gif
        """
        frames=[]
        # for every file in a given path
        for file in glob.glob(filepath + "**/*.png", recursive = True):
            # we copy an image and append it in the array
            keep = copy.deepcopy(Image.open(file))
            frames.append(keep)
        # then we create the gif fil.
        frames[0].save(filename+'.gif', format='GIF', append_images=frames[1:], save_all=True, duration=200, loop=0)

if __name__ == '__main__':
    space = Space(1000, 2)
    space_dist = space.create_space_distribution()
    space.explore_space(space_dist)