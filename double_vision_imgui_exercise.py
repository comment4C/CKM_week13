import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd
import imgui
from imgui.integrations.glut import GlutRenderer
from gl_helpers import *
from PIL import Image

impl, vao = None, None
win_w, win_h = 600, 600
clear_color = [0, 0.3, 0.3]
separation = 0
tex_unit = 0

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

def draw_gui():
    global separation, clear_color
    impl.process_inputs()
    imgui.new_frame()                 # Start the Dear ImGui frame 
    imgui.set_next_window_position(win_w-250, win_h-100, imgui.FIRST_USE_EVER)
    imgui.begin("Control")            # Create a window
    imgui.push_item_width(200)
    _, separation = imgui.slider_float("Separation Value", separation, 0, 3)
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)    
    imgui.pop_item_width()

    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    impl.set_current_gui_params(imgui.get_window_position(), imgui.get_window_size())        
    imgui.end()

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    
def display():
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glUseProgram(prog_id)

    loc = glGetUniformLocation( prog_id, "separation" )
    glUniform1f(loc, separation)

    loc = glGetUniformLocation( prog_id, "image" )
    glUniform1i( loc, tex_unit )
    
    glBegin(GL_TRIANGLES)
    glTexCoord2f(0, 0)
    glVertex2f(-0.8, 0.8)
    glTexCoord2f(1, 0)
    glVertex2f(0.8, 0.8)
    glTexCoord2f(0.5, 1)
    glVertex2f(0.0, -0.8)
    glEnd()


    draw_gui()
    imgui.render()
    impl.render(imgui.get_draw_data())

    glutSwapBuffers()

wireframe = False
def keyboard(key, x, y):
    global wireframe

    key = key.decode("utf-8")
    if key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)        
    elif key == 'q':
        impl.shutdown()
        sys.exit(0)

def idle():
    glutPostRedisplay()

def initialize():
    global impl, tex_unit

    tex_unit = load_texture("../texture_map/demon.png", 1)
    show_versions()
    glEnable(GL_DEPTH_TEST)
    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlutRenderer()
    impl.user_keyboard_func(keyboard)
    impl.user_reshape_func(reshape)
       
def create_shaders():
    global prog_id

    vert_code = b'''
#version 130
uniform float separation;
out vec2 texCo;
void main()
{
   gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
   texCo = vec2(gl_MultiTexCoord0);
   // gl_Color, gl_Normal, gl_MultiTexCoord0
}'''
    frag_code = b'''
#version 130
uniform float separation;
uniform sampler2D image;
in vec2 texCo;
out vec4 fColor;
void main()
{
    fColor = (texture(image, texCo - vec2(separation, 0)) + texture(image, texCo + vec2(separation, 0)))/2;
    //gl_FragColor = vec4(0, 0, 1, 1);
}'''

    prog_id = compileProgram(vert_code, frag_code)


def main():
    global impl
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowPosition(80, 0)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow("Double Vision Exercise")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    initialize()
    create_shaders()

    glutMainLoop()

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

if __name__ == "__main__":
    main()