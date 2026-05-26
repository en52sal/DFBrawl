#version 330

#moj_import <minecraft:light.glsl>
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:globals.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in vec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler2;

out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
out vec2 texCoord1;
out vec3 vertexPosition;

out vec3 camWorldPos;
out vec4 baseColor;
vec3 viewPos;

bool is_color(vec4 c,int r,int g,int b) {
    return (int(c.x*255.0)==r && int(c.y*255.0)==g && int(c.z*255.0)==b);
}

vec3 rgb(int r, int g, int b) {
    return vec3(r / 255.0, g / 255.0, b / 255.0);
}

const float transition_phase = 0.2;
const float transition_phase_threshold = 1.0-transition_phase;
const float transition_phase_multiplier = 1.0/transition_phase;

void main() {
    vec3 pos = Position;
    gl_Position = ProjMat * ModelViewMat * vec4(pos, 1.0);
    // viewPos = (ModelViewMat * vec4(pos, 1.0)).rgb;
    viewPos = transpose(mat3(ModelViewMat)) * Position;
    
    
    // invProjView = inverse(ProjMat * ModelViewMat);

    camWorldPos = CameraBlockPos - CameraOffset - vec3(6200, 1, 2066.); // ModelViewMat[3].xyz;


    sphericalVertexDistance = fog_spherical_distance(pos);
    cylindricalVertexDistance = fog_cylindrical_distance(pos);
    vertexPosition = Position;
    baseColor = Color;


    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color) * texelFetch(Sampler2, UV2 / 16, 0);
    
    texCoord0 = UV0;
    texCoord1 = UV1;
}
