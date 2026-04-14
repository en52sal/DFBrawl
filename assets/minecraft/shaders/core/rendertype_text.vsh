#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>

uniform sampler2D Sampler0;

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;

uniform sampler2D Sampler2;

out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;

out float isTransition;

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1);

    int id = gl_VertexID%4;

    // Transition Code ////////////////////////////////////////
    vec4 color = texture(Sampler0, UV0);
    isTransition = 0;
    if(color.rgb == vec3(250,250,255)/255) {
        isTransition = 1;
        switch(id)  {
            case 0: gl_Position.xy = vec2(-1,1); break;
            case 1: gl_Position.xy = vec2(-1,-1); break;
            case 2: gl_Position.xy = vec2(1,-1); break;
            case 3: gl_Position.xy = vec2(1,1); break;
        }
    }
    ///////////////////////////////////////////////////////////



    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    vertexColor = Color * texelFetch(Sampler2, UV2 / 16, 0);
    texCoord0 = UV0;
}