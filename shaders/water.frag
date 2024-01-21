#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1 / gamma;

in vec2 uv;

uniform sampler2D u_texture_2;
uniform vec3 bg_color;

void main() {
    vec3 tex_col = texture(u_texture_2, uv).rgb;
    tex_col = pow(tex_col, gamma);
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    tex_col = mix(tex_col, bg_color, (1.0 - exp2(-0.000015 * fog_dist * fog_dist)));
    tex_col = pow(tex_col, inv_gamma);
    fragColor = vec4(tex_col, 0.5);
}
