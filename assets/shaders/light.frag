#version 120

uniform float i_hue;
uniform vec3 i_end;
uniform vec3 i_origin;
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
    float l = length(i_end - i_origin);
    float f = pow(clamp(length(v_pos.xyz - i_end) / l, 0.4, 0.9), 2.2);
    vec4 color = vec4(hue_shift(v_color.rgb, i_hue), v_color.a * i_alpha_f * f);
    gl_FragColor = color;
}
