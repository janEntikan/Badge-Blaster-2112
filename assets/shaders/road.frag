#version 120

uniform float i_hue;

varying vec4 v_color;

vec3 hue_shift(vec3 color, float hue) {
    const vec3 k = vec3(0.57735, 0.57735, 0.57735);
    float cos_rad = cos(hue);
    return vec3(color * cos_rad + cross(k, color) * sin(hue) + k * dot(k, color) * (1.0 - cos_rad));
}


void main() {
	gl_FragColor = vec4(hue_shift(v_color.rgb, i_hue), 1.0f);
}
