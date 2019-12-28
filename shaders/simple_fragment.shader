
#version 430 compatibility

in vec2 texCoords;
in vec4 vertexColor;

uniform sampler2D tex;

void main()
{
		vec4 texColor = texture2D(tex, texCoords);
		gl_FragColor = vertexColor * texColor;
}