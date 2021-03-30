#version 120

uniform sampler2D p3d_Texture0;
uniform float osg_FrameTime;

varying vec2 i_offset;
varying vec2 i_rotate;

void main() {
	vec2 sprite_coords = (gl_PointCoord.xy - vec2(0.5, 0.5)) * mat2(i_rotate[0], -i_rotate[1], i_rotate[1], i_rotate[0]) + vec2(0.5, 0.5);
	float frame = int(osg_FrameTime * 24 + i_offset[0]);
	float sprite = i_offset[1];
	vec2 coords = (sprite_coords + vec2(frame, 7 - sprite)) / 8;
	gl_FragColor = texture2D(p3d_Texture0, coords);
}
