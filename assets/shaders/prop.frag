#version 120

uniform float i_hue;
uniform float i_zmax;
uniform float i_height;
uniform vec3 i_shade;
uniform float i_shade_exp;
uniform float i_alpha_f;

varying vec4 v_color;
varying vec4 v_pos;

vec3 hue_shift(vec3 color, float hue) {
    const vec3 k = vec3(0.57735, 0.57735, 0.57735);
    float cos_rad = cos(hue);
    return vec3(color * cos_rad + cross(k, color) * sin(hue) + k * dot(k, color) * (1.0 - cos_rad));
}


void main() {
  float f = clamp((i_zmax - v_pos.z) / i_height, 0.1, 0.8);
  vec4 color = vec4(hue_shift(v_color.rgb, i_hue), v_color.a * i_alpha_f);
  color.rgb = mix(i_shade, color.rgb, pow(f, i_shade_exp));
	gl_FragColor = color;
}
