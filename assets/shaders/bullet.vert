#version 120

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

attribute vec4 p3d_Vertex;
attribute vec2 offset;
attribute vec2 rotation;

varying vec2 i_offset;
varying vec2 i_rotate;

void main() {
	gl_Position = p3d_ProjectionMatrix * (p3d_ModelViewMatrix * p3d_Vertex);
	i_offset = offset;
	i_rotate = rotation;
}
