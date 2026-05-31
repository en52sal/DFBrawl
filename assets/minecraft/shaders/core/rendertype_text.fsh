#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:globals.glsl>
#moj_import <minecraft:transition.glsl>


bool is_color(vec4 c, ivec3 target) {
    return int(c.x * 255) == target.x && int(c.y * 255) == target.y && int(c.z * 255) == target.z;
}

int guiScale(mat4 ProjMat, vec2 ScreenSize) {
    return int(round(ScreenSize.x * ProjMat[0][0] / 2));
}

bool flag(int value, int flag) {
    return (value & flag) != 0;
}


const int MONO_ALPHA = 204;

// Mono Red Flags (fragment)
const int BACKGROUND_FLAG = 1;
const int TRANSPARANT_FLAG = 2;

// Mono Green Flags (vertex)
const int CENTER_FLAG = 1;
const int DOWN_5_FLAG = 2;
const int DOWN_10_FLAG = 4;
const int DOWN_20_FLAG = 8;
const int DOWN_40_FLAG = 16;

uniform sampler2D Sampler0;

in float sphericalVertexDistance;
in float cylindricalVertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;

in float isTransition;
in float isMono;

out vec4 fragColor;


void main() {
    vec4 baseColor = texture(Sampler0, texCoord0);
    vec4 color = baseColor * vertexColor * ColorModulator;

    if (isTransition == 1) {
        color = transition(color.a, int(round(vertexColor.r*255)), gl_FragCoord.xy, ScreenSize, GameTime * 1200.);
    } else if (isMono == 1) {
        if (ColorModulator.a < 0.1) discard;

        int redFlag = int(round(baseColor.r * 255));
        if (redFlag == BACKGROUND_FLAG) discard;

        color = vertexColor * ColorModulator;
        if (flag(redFlag, TRANSPARANT_FLAG)) color.a = 0.7;

    } else {
        if (color.a < 0.1) {
            discard;
        }
    }


    fragColor = apply_fog(color, sphericalVertexDistance, cylindricalVertexDistance, FogEnvironmentalStart, FogEnvironmentalEnd, FogRenderDistanceStart, FogRenderDistanceEnd, FogColor);
}