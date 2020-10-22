# ชื่อ รหัสนิสิต และอีเมลล์
# ณัฐวรรธน์   สุนทรเสถียรกุล     6110400106      Nuttawatt.S@ku.th
# พันธุ์ธิชชัย   ขรรค์บริวาร       6110406121      phantichchai.kh@ku.th
# วัชริศ      สายพิมพ์          6110406201      wacharis.s@ku.th

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
shininess = 50
Ka, Kd, Ks, clear_color = [0.05, 0.05, 0.05], [0.5, 1.0, 0.2], [0.9, 0.9, 0.9], [0.1, 0.6, 0.6]
light_intensity, light_pos, eye_pos = [1, 1, 1], [0, 0, 0], [0, 0, 0]
specular_on = True
selection = [True, False, False, False]
selectiontmp = 0.0
phong_on = True

angle = 0
angle_x = 0

xtmp = 0
ytmp = 0
rad_x = 0
rad_y = 0

tex_unit, tex_unit2 = 0, 0

def compileProgram(vertex_code, fragment_code):                     # change 1.0
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

def load_texture(filename, texture_unit):                          # change 1.1
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
    global selection, light_intensity, Ka, Kd, Ks, shininess, specular_on, clear_color, angle, angle_x, phong_on
    impl.process_inputs()
    imgui.new_frame()                    # Start the Dear ImGui frame   
    imgui.begin("Control")               # Create a window
    imgui.push_item_width(300)
    _, light_intensity = imgui.color_edit3("Light Intensity", *light_intensity)
    _, Ka = imgui.color_edit3("Ka", *Ka)
    _, Kd = imgui.color_edit3("Kd", *Kd)
    _, Ks = imgui.color_edit3("Ks", *Ks)

    _, shininess = imgui.slider_float("shininess", shininess, 0, 100)

    imgui.text("Eye At")
    imgui.push_item_width(100)
    _, centroid[0] = imgui.slider_float("X###eye_at_x", centroid[0], -10, 10)
    imgui.same_line()
    _, centroid[1] = imgui.slider_float("Y###eye_at_y", centroid[1], -10, 10)
    imgui.same_line()
    _, centroid[2] = imgui.slider_float("Z###eye_at_z", centroid[2], -10, 10)


    _, angle = imgui.slider_float("Rotate Y", angle, -pi, pi)
    _, angle_x = imgui.slider_float("Rotate X", angle_x, -pi, pi)

    if imgui.radio_button("OpenGL Lighting", selection[0] and not selection[1] and not selection[2] and not selection[3]): 
        selection[0] = True
        selection[1] = False
        selection[2] = False
        selection[3] = False
    imgui.same_line()
    if imgui.radio_button("Flat Shading", not selection[0] and selection[1] and not selection[2] and not selection[3]): 
        selection[0] = False
        selection[1] = True
        selection[2] = False
        selection[3] = False

    if imgui.radio_button("Gouraud Shading", not selection[0] and not selection[1] and selection[2] and not selection[3]): 
        selection[0] = False
        selection[1] = False
        selection[2] = True
        selection[3] = False
    imgui.same_line()
    if imgui.radio_button("Phong Shading", not selection[0] and not selection[1] and not selection[2] and selection[3]): 
        selection[0] = False
        selection[1] = False
        selection[2] = False
        selection[3] = True

    if imgui.radio_button("Phong Specular", phong_on): 
        phong_on = True
    imgui.same_line()
    if imgui.radio_button("Blinn Specular", not phong_on): 
        phong_on = False

    _, specular_on = imgui.checkbox("Specular Enabled", specular_on)
    
    imgui.text("Light Position")
    imgui.push_item_width(100)
    _, light_pos[0] = imgui.slider_float("X###light_pos_x", light_pos[0], -10, 10)
    imgui.same_line()
    _, light_pos[1] = imgui.slider_float("Y###light_pos_y", light_pos[1], -10, 10)
    imgui.same_line()
    _, light_pos[2] = imgui.slider_float("Z###light_pos_z", light_pos[2], -10, 10)
    imgui.text("Eye Position")
    _, eye_pos[0] = imgui.slider_float("X###eye_pos_x", eye_pos[0], -10, 10)
    imgui.same_line()
    _, eye_pos[1] = imgui.slider_float("Y###eye_pos_y", eye_pos[1], -10, 10)
    imgui.same_line()
    _, eye_pos[2] = imgui.slider_float("Z###eye_pos_z", eye_pos[2], -10, 10)
    imgui.pop_item_width()
    _, clear_color = imgui.color_edit3("Clear Color", *clear_color)

    imgui.text("Application average %.3f ms/frame (%.1f FPS)" % \
        (1000 / imgui.get_io().framerate, imgui.get_io().framerate))
    imgui.pop_item_width()
    imgui.end()

def mouseWheel(button, dir, x, y):
    if dir < 0:
        eye_pos[2] += 1
    else:
        eye_pos[2] -= 1

def mouseCB(button, state, x, y):
    print("Inside mouseCB")
    # if button == GLUT_LEFT_BUTTON:
    #     print("Left mouse button", end="")

    global xtmp, ytmp
    xtmp = x
    ytmp = y
    print(GLUT_MIDDLE_BUTTON)
    # print("%d %s" % (xtmp, "First"))

def motionCB(x, y): 
    print("Mouse is at position (%d, %d)" % (x, y))
    global rad_x, rad_y, xtmp, ytmp

    mod = glutGetModifiers()
    print(glutGetModifiers())
    if mod == 0:
        rad_x += x-xtmp
        rad_y += y-ytmp
        print(rad_x, x)
        xtmp = x
        ytmp = y 

    elif mod == 1:
        eye_pos[0] += -(x-xtmp)/100
        eye_pos[1] += (y-ytmp)/100
        centroid[0] += -(x-xtmp)/100
        centroid[1] += (y-ytmp)/100
        xtmp = x
        ytmp = y

    glutPostRedisplay()

def reshape(w, h):
    global win_w, win_h, proj_mat

    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    proj_mat = Perspective(60, w/h, 0.1, 10)
    
def display():
    global angle, angle_x, rad_x, selection, selectiontmp
    glClearColor(*clear_color, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # model_mat = Identity()
    model_mat = Rotate(rad_y/100, 1, 0, 0) @ Rotate(rad_x/100, 0, 1, 0) @ Identity()

    view_mat = LookAt(*eye_pos, *centroid, 0, 1, 0)


    if(selection[0]):
        glUseProgram(0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(proj_mat.T)
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf((view_mat @ model_mat).T)

        mat_ambient = [0.05, 0.05, 0.05, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, Ka)

        mat_diffuse = [0.86, 0.65, 0.13, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, Kd)

        mat_specular = [1.0, 1.0, 0, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, Ks)
        mat_shininess = shininess
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

        light_ambient = light_intensity
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

        light_diffuse = light_intensity
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

        light_specular = light_intensity
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        light_position = light_pos

        glPushMatrix()
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glPopMatrix()

        glVertexPointer(3, GL_FLOAT, 0, positions)
        glColorPointer(3, GL_FLOAT, 0, colors)
        glNormalPointer(GL_FLOAT, 0, normals)
        glTexCoordPointer(2, GL_FLOAT, 0, uvs)

    else:
        glUseProgram(prog_id)
        glUniform3fv(glGetUniformLocation(prog_id, "AmbientProduct"), 1, Ka)
        glUniform3fv(glGetUniformLocation(prog_id, "DiffuseProduct"), 1, Kd)
        glUniform3fv(glGetUniformLocation(prog_id, "SpecularProduct"), 1, Ks)
        glUniform1f(glGetUniformLocation(prog_id, "Shininess"), shininess)
        glUniform3fv(glGetUniformLocation(prog_id, "light_intensity"), 1, light_intensity)
        glUniform3fv(glGetUniformLocation(prog_id, "LightPosition"), 1, light_pos)
        glUniform3fv(glGetUniformLocation(prog_id, "eye_pos"), 1, eye_pos)
        glUniform1i(glGetUniformLocation(prog_id, "FlatShading"), selection[1])
        glUniform1i(glGetUniformLocation(prog_id, "GouraudShading"), selection[2])
        glUniform1i(glGetUniformLocation(prog_id, "PhongShading"), selection[3])
        glUniform1i(glGetUniformLocation(prog_id, "PhongOn"), phong_on)
        glUniform1i(glGetUniformLocation(prog_id, "SpecularOn"), specular_on)


        modelTransform_location = glGetUniformLocation(prog_id, "modelTransform")
        viewTransform_location = glGetUniformLocation(prog_id, "viewTransform")
        projectionTransform_location = glGetUniformLocation(prog_id, "projectionTransform")

        glUniformMatrix4fv(modelTransform_location, 1, True, model_mat)
        glUniformMatrix4fv(viewTransform_location, 1, True, view_mat)
        glUniformMatrix4fv(projectionTransform_location, 1, True, proj_mat)

        glBindVertexArray(vao)
    
    glDrawArrays(GL_TRIANGLES, 0, n_vertices)
    glBindVertexArray(0)

    draw_gui()
    imgui.render()
    impl.render(imgui.get_draw_data())
    
    glutSwapBuffers()

wireframe = False
def keyboard(key, x, y):
    global wireframe, selection

    key = key.decode("utf-8")
    if key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)        
    elif key == 'q':
        impl.shutdown()
        sys.exit(0)
    elif key == '1':
        selection = [True, False, False, False]
    elif key == '2':
        selection = [False, True, False, False]
    elif key == '3':
        selection = [False, False, True, False]
    elif key == '4':
        selection = [False, False, False, True]
    print(key)



def idle():
    glutPostRedisplay()

def initialize():
    global impl, tex_unit, tex_unit2

    tex_unit = load_texture("../texture_map/bunny_hair.jpg", 1)                     # change 1.1
    tex_unit2 = load_texture("../texture_map/brick_wall_small.jpg", 2)              # change 1.1
    imgui.create_context()
    imgui.style_colors_dark()
    impl = GlutRenderer()
    impl.user_keyboard_func(keyboard)
    impl.user_mouse_func(mouseCB)
    impl.user_motion_func(motionCB)
    impl.user_wheel_func(mouseWheel)
    impl.user_reshape_func(reshape)
    imgui.set_next_window_position(500, 10)
    imgui.set_next_window_collapsed(True)

def print_shader_info_log(shader, prompt=""):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetShaderInfoLog(shader).decode("utf-8")))
        sys.exit()

def print_program_info_log(shader, prompt=""):
    result = glGetProgramiv(shader, GL_LINK_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetProgramInfoLog(shader).decode("utf-8")))
        sys.exit()
        
def create_shaders():
    global prog_id, vao, vbo

    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    vert_code = b'''
#version 130

flat out vec4 my_color_flat;
out vec4 my_color;
uniform vec3 AmbientProduct, DiffuseProduct, SpecularProduct;
uniform vec3 LightPosition;
uniform float Shininess;
uniform mat4 modelTransform;
uniform mat4 viewTransform;
uniform mat4 projectionTransform;
uniform vec3 eye_pos;
uniform vec3 light_intensity;
uniform bool FlatShading;
uniform bool GouraudShading;
uniform bool PhongShading;
uniform bool PhongOn;
uniform bool SpecularOn;

out vec3 fV, fL, fH, fN;

attribute vec3 position, normal, color, uv;
uniform vec3 Kd;

void main()
{
    gl_Position = projectionTransform* viewTransform * modelTransform * vec4(position, 1);

    // Transform vertex position into eye coordinates
    vec3 pos = (modelTransform * vec4(position, 1)).xyz;
    vec3 L = normalize( LightPosition.xyz - pos );
    vec3 V = normalize( eye_pos - pos );
    vec3 H = normalize( L + V );

    // Transform vertex normal into eye coordinates
    vec3 N = normalize( modelTransform*vec4(normal, 0.0) ).xyz;
    vec3 R = normalize( -reflect(L, N) );

    // Compute terms in the illumination equation
    vec3 ambient = AmbientProduct * light_intensity;
    float cos_theta = max( dot(L, N), 0.0 );
    vec3 diffuse = cos_theta * DiffuseProduct * light_intensity;

    float cos_phi = pow( max(dot(V, R), 0.0), Shininess );
    if (!PhongOn) {
        cos_phi = pow( max( dot(N, H), 0.0), Shininess );
    }

    if (FlatShading){
        my_color_flat.rgb = ambient + diffuse;
        my_color_flat.a = 1.0;
    } else if (GouraudShading){
        vec3 specular = cos_phi * SpecularProduct * light_intensity;
        if( dot(L, N) < 0.0 ) specular = vec3(0.0, 0.0, 0.0);

        my_color.rgb = ambient + diffuse + specular;
        my_color.a = 1.0;
    } else if (PhongShading){
        fN = normalize( viewTransform * modelTransform * vec4(normal, 0.0) ).xyz;
        fV = normalize( eye_pos - pos );
        fL = normalize( LightPosition.xyz - pos );
    }
}'''

    frag_code = b'''
#version 130

// in fragment shader
in vec4 my_color;
flat in vec4 my_color_flat;
in vec3 fV, fL, fH, fN;

uniform vec3 AmbientProduct, DiffuseProduct, SpecularProduct;
uniform vec3 LightPosition;
uniform float Shininess;
uniform mat4 modelTransform;
uniform mat4 viewTransform;
uniform mat4 projectionTransform;
uniform vec3 eye_pos;
uniform vec3 light_intensity;
uniform bool FlatShading;
uniform bool GouraudShading;
uniform bool PhongShading;
uniform bool PhongOn;
uniform bool SpecularOn;

void main()
{
    if (FlatShading) {
        gl_FragColor = my_color_flat;
    } else if (GouraudShading){
        gl_FragColor = my_color;                   // Change 1.0
    } else if (PhongShading){
        vec3 V = normalize(fV);
        vec3 N = normalize(fN);
        vec3 L = normalize(fL);
        vec3 H = normalize( L + V);
        vec3 R = normalize( -reflect(L, N) );
        float cos_phi = pow( max( dot(V, R), 0.0), Shininess );

        vec3 ambient = AmbientProduct * light_intensity;
        float cos_theta = max( dot(L, N), 0.0 );
        vec3 diffuse = cos_theta * DiffuseProduct * light_intensity;

        if (!PhongOn) {
            cos_phi = pow( max( dot(N, H), 0.0), Shininess );
        }
        if (SpecularOn) {
            vec3 specular = cos_phi * SpecularProduct * light_intensity;
            if( dot(L, N) < 0.0 ) specular = vec3(0.0, 0.0, 0.0);    
            gl_FragColor.xyz = ambient + diffuse + specular;
        } else {
            gl_FragColor.xyz = ambient + diffuse;
        }
        gl_FragColor.a = 1.0;
    }
}'''
    prog_id = compileProgram(vert_code, frag_code)                  # change 1.0


    global n_vertices, positions, colors, normals, uvs, centroid, bbox
    global light_pos, eye_pos

    df = pd.read_csv("../models/bunny_uv.tri", delim_whitespace=True,
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)
    light_pos = centroid + (0, 0, 5)
    eye_pos = centroid + (0, 0, 3)

    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    n_vertices = len(positions)

    glUseProgram(prog_id)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(4)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)
    position_loc = glGetAttribLocation(prog_id, "position")
    glVertexAttribPointer(position_loc, 3, GL_FLOAT, GL_FALSE, 0, 
        c_void_p(0))
    glEnableVertexAttribArray(position_loc)
    color_loc = glGetAttribLocation(prog_id, "color")
    if color_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
        glBufferData(GL_ARRAY_BUFFER, colors, GL_STATIC_DRAW)
        glVertexAttribPointer(color_loc, 3, GL_FLOAT, GL_FALSE, 0, 
            c_void_p(0))
        glEnableVertexAttribArray(color_loc)
    normal_loc = glGetAttribLocation(prog_id, "normal")
    if normal_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
        glBufferData(GL_ARRAY_BUFFER, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, GL_FALSE, 0, 
            c_void_p(0))
        glEnableVertexAttribArray(normal_loc)
    uv_loc = glGetAttribLocation(prog_id, "uv")
    if uv_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[3])
        glBufferData(GL_ARRAY_BUFFER, uvs, GL_STATIC_DRAW)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(uv_loc)
    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

def gl_init():
    global n_vertices, positions, colors, normals, uvs, centroid, bbox

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

    df = pd.read_csv("../models/teapot.tri", delim_whitespace=True,
                     comment='#', header=None, dtype=np.float32)
    centroid = df.values[:, 0:3].mean(axis=0)
    bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

    n_vertices = len(df.values)
    positions = df.values[:, 0:3]
    colors = df.values[:, 3:6]
    normals = df.values[:, 6:9]
    uvs = df.values[:, 9:11]
    print("no. of vertices: %d, no. of triangles: %d" %
          (n_vertices, n_vertices//3))
    print("Centroid:", centroid)
    print("BBox:", bbox)

def main():
    global impl, clear_color
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowPosition(80, 0)
    glutInitWindowSize(1024, 768)
    glutCreateWindow("Phong Lighting Model Exercise")
    glutDisplayFunc(display)

    glutMouseFunc(mouseCB)
    glutMotionFunc(motionCB)

    glutIdleFunc(idle)
    # gl_init() is a function for setting up OpenGL but we can't do it ;-;
    gl_init()
    glEnable(GL_DEPTH_TEST)
    initialize()
    create_shaders()
    show_versions()

    glutMainLoop()

def show_versions():
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
            ['OpenGL Version', GL_VERSION],
            ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    for x in lists:
        print("%s: %s" % (x[0], glGetString(x[1]).decode("utf-8")))

if __name__ == "__main__":
    main()