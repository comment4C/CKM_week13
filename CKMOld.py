# ชื่อ รหัสนิสิต และอีเมลล์
# ณัฐวรรธน์   สุนทรเสถียรกุล     6110400106      Nuttawatt.S@ku.th
# พันธุ์ธิชชัย   ขรรค์บริวาร       6110406121      phantichchai.kh@ku.th
# วัชริศ      สายพิมพ์          6110406201      wacharis.s@ku.th

import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np
import pandas as pd
import math as m

t_value = 0
light_position = [1.0, 1.0, 1.0, 1.0]
xtmp = 0
rad = 0

def compileProgram(vertex_code, fragment_code):
    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(vert_id, vertex_code)
    glShaderSource(frag_id, fragment_code)

    glCompileShader(vert_id)
    glCompileShader(frag_id)

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)

    glLinkProgram(prog_id)
    return prog_id

def load_texture(filename, texture_unit):
   try:
       im = Image.open(filename)
   except:
       print("Error:", sys.exc_info()[0])
   w = im.size[0]
   h = im.size[1]
   image = im.tobytes("raw", "RGB", 0)
   glActiveTexture(GL_TEXTURE0 + texture_unit)
   texture_id = glGenTextures(1)
   glBindTexture(GL_TEXTURE_2D, texture_id)
   glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
   glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
   glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
   glTexImage2D(GL_TEXTURE_2D, 0, 3, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
   return texture_unit

def mouseCB(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        print("Left mouse button", end="")

    global xtmp 
    xtmp = x
    # print("%d %s" % (xtmp, "First"))

def motionCB(x, y): 
    # print("Mouse is at position (%d, %d)" % (x, y))
    global rad, xtmp
    rad += x-xtmp
    # print(rad, x)
    xtmp = x
    glutPostRedisplay()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.1, 50)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_TEXTURE)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    
    eye_pos = [0, 1, 2]
    eye_at = centroid

    gluLookAt(*eye_pos, *eye_at, 0, 1, 0)

    glUseProgram(prog_id)

    loc = glGetUniformLocation( prog_id, "image" )
    glUniform1i( loc, tex_unit )

    loc = glGetUniformLocation( prog_id, "image2" )
    glUniform1i( loc, tex_unit2 )

    


    glVertexPointer(3, GL_FLOAT, 0, positions)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glNormalPointer(GL_FLOAT, 0, normals)
    glTexCoordPointer(2, GL_FLOAT, 0, uvs)
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)


    glutSwapBuffers()



wireframe, pause = False, True


def keyboard(key, x, y):
    global wireframe, pause

    key = key.decode("utf-8")
    if key == ' ':
        pause = not pause
        glutIdleFunc(None if pause else idle)
    elif key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
    elif key == 'q':
        exit(0)
    glutPostRedisplay()


def idle():
    global t_value
    t_value += 1
    glutPostRedisplay()


def gl_init():
    global n_vertices, positions, colors, normals, uvs, centroid, bbox, tex_unit, tex_unit2, prog_id
    
    filename = "../texture_map/bunny_hair.jpg"
    tex_unit = load_texture(filename, 1)
    filename = "../texture_map/brick_wall_small.jpg"
    tex_unit2 = load_texture(filename, 2)

    glEnable(GL_TEXTURE_2D)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    al = [0.1, 0.1, 0.1, 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, al)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    df = pd.read_csv("../models/bunny_uv.tri", delim_whitespace=True,
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    n_vertices = len(df.values)
    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    # print("no. of vertices: %d, no. of triangles: %d" %
    #       (n_vertices, n_vertices//3))
    # print("Centroid:", centroid)
    # print("BBox:", bbox)

    vert_code = '''
#version 130
void main()
{
    gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
}'''

    frag_code = '''
#version 130
uniform sampler2D image, image2;
out vec4 fColor;
void main()
{
    //fColor = texture(image, uv)
}'''

    prog_id = compileProgram(vert_code, frag_code)
    

def print_shader_info_log(shader, prompt=""):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetShaderInfoLog(shader).decode("utf-8")))
        exit()



def print_program_info_log(program, prompt=""):
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetProgramInfoLog(program).decode("utf-8")))
        exit()

    

def main():

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutCreateWindow("OpenGL Lighting Exercise")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouseCB)
    glutMotionFunc(motionCB)
    glutIdleFunc(idle)
    gl_init()
    glutMainLoop()
    

if __name__ == "__main__":
    main()
