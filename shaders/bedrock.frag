#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1 / gamma;

in vec2 uv;

uniform sampler2DArray u_texture_array_0;
uniform vec3 bg_color;

void main() {
    vec2 face_uv = uv;
    vec4 uv_texture = texture(u_texture_array_0, vec3(face_uv, 1));
    vec3 tex_col = uv_texture.rgb;
//    vec3 tex_col = vec3(0.9, 0.5, 0.5);
    tex_col = pow(tex_col, gamma);
    tex_col *= vec3(0.0, 0.3, 1.0);
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    tex_col = mix(tex_col, bg_color, (1.0 - exp2(-0.000015 * fog_dist * fog_dist)));
    tex_col = pow(tex_col, inv_gamma);
    fragColor = vec4(tex_col, 1.0);
}
