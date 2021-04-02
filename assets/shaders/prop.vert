#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;

varying vec4 v_color;
varying vec4 v_pos;

void main() {
    v_color = p3d_Color;
    v_pos = p3d_Vertex;
	gl_Position = p3d_ModelViewProjectionMatrix * v_pos;
}
