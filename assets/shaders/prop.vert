#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;

varying vec4 v_color;

void main() {
    v_color = p3d_Color;
	gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
