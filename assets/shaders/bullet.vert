#version 120

attribute vec2 offset;
attribute vec2 rotation;

varying vec2 i_offset;
varying vec2 i_rotate;

void main() {
	gl_Position = ftransform();
	i_offset = offset;
	i_rotate = rotation;
}
