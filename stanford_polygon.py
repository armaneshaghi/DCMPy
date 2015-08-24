def polygon_maker(mesh_path, label_files, output):
    '''
    Creates a Stanford polygon file http://brainder.org/2011/09/25/braindering-with-ascii-files/
    --------
    mesh_path:  path to freesurfer surface file ([r,l]h.pial or inflated, or sphere)
    label_files: list of labels (absolute paths)
    output = file path for the output ply file (include .ply)
    *assuming there are three files
    '''
    import nibabel as nb
    import matplotlib.pyplot as plt
    import random

    label_files = label_files

    #matplotlib colormaps
    #http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps

    mesh = nb.freesurfer.read_geometry(mesh_path)
    vertices = mesh[0]
    faces = mesh[1]

    number_of_vertices = vertices.shape[0]
    number_of_faces = faces.shape[0]
    ply_file = open(output, 'w')
    string = ''
    prefix = '''ply
format ascii 1.0
element vertex {number_of_vertices}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
element face {number_of_faces}
property list uchar int vertex_index
end_header\n'''.format(number_of_vertices = number_of_vertices,
              number_of_faces = number_of_faces)

    for i in range(number_of_vertices):
        current_row = '%f %f %f 255 255 255\n' %( vertices[i][0], vertices[i][1], 
                                           vertices[i][2])
        string = string + current_row

    string = string.split('\n')

    suffix = ''
    colors = ['9 0 255',
              '255 60 0',
              '0 255 9']

    for i in range(number_of_faces):
        current_row = '3 %d %d %d\n' %(faces[i][0], faces[i][1],
                                       faces[i][2])
        suffix = suffix + current_row

    for number, label in enumerate(label_files):
        label_array = convert_label_to_array(label)
        for item in np.nditer(label_array):
            current_row = string[item].split()
            new_row = current_row[0] + ' ' + current_row[1] + ' ' + current_row[2]
            color = colors[ number]
            new_row = new_row + ' ' + color
            string[item] = new_row
    string = "\n".join(item for item in string)
    string = prefix + string + suffix
    output_file = open(output, 'w')
    output_file.write(string)
    output_file.close()
    return None
