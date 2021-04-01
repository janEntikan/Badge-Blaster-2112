#version 120

uniform sampler2D p3d_Texture0;
uniform float osg_FrameTime;
uniform vec3 sprite_layout;

varying vec2 i_offset;
varying vec2 i_rotate;

void main() {
	vec2 sprite_coords = (gl_PointCoord.xy - vec2(0.5, 0.5)) * mat2(i_rotate[0], -i_rotate[1], i_rotate[1], i_rotate[0]) + vec2(0.5, 0.5);
	float frame = int(osg_FrameTime * 24 - i_offset[0]);
	float sprite = i_offset[1];
	vec2 coords = (clamp(sprite_coords, 0.0, 1.0) + vec2(frame, sprite_layout.y - sprite - 1.0)) * vec2(1.0 / sprite_layout.x, 1.0 / sprite_layout.y);
	gl_FragColor = texture2D(p3d_Texture0, coords);
}
