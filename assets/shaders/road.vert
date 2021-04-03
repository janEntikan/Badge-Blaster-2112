#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float i_hskew;
uniform float i_ymax;
uniform vec2 i_scale;
uniform float i_len;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;

varying vec4 v_color;
varying vec4 v_pos;

void main() {
    v_color = p3d_Color;
    float f = (i_len - (i_ymax - p3d_Vertex.y)) / i_len;
    float s = (f - 0.5f) * (i_hskew * 2.0f);
    v_pos = p3d_Vertex;
    v_pos.x *= (i_scale.y - i_scale.x) * f + i_scale.x;
    v_pos.x += s;
	gl_Position = p3d_ModelViewProjectionMatrix * v_pos;
}
