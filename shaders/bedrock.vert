#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_tex_coord_0;

uniform mat4 m_proj;
uniform mat4 m_view;

out vec2 uv;

void main() {
    uv = in_tex_coord_0;
    gl_Position = m_proj * m_view * vec4(in_position, 1.0);
}
