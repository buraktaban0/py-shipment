#version 430 compatibility

layout (location = 0) in vec3 position;
layout (location = 3) in vec3 color;
layout (location = 4) in vec2 uv;


out vec2 texCoords;
out vec4 vertexColor;

void main()
{
		gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1.0);
		
		vertexColor = vec4(color, 1.0);
		texCoords = uv;
}