#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:globals.glsl>

#moj_import <minecraft:transition.glsl>

uniform sampler2D Sampler0;

in float sphericalVertexDistance;
in float cylindricalVertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;

in float isTransition;
in float isMono;

out vec4 fragColor;

const ivec3 MONO_BACKGROUND = ivec3(101, 35, 78);
const ivec3 AMMO_COLOR = ivec3(255, 200, 255);

bool is_color(vec4 c, ivec3 target) {
    return int(c.x * 255) == target.x && int(c.y * 255) == target.y && int(c.z * 255) == target.z;
}


void main() {
    vec4 baseColor = texture(Sampler0, texCoord0);
    vec4 color = baseColor * vertexColor * ColorModulator;

    if (isTransition == 1) {
        color = transition(color.a, int(round(vertexColor.r*255)), gl_FragCoord.xy, ScreenSize, GameTime * 1200.);
    } else if (isMono == 1) {
        if (is_color(baseColor, MONO_BACKGROUND)) discard;
        if (ColorModulator.a < 0.1) discard;
        color.a = vertexColor.a;

        if (is_color(baseColor, AMMO_COLOR)) {
            
        }
        

    } else {
        if (color.a < 0.1) {
            discard;
        }
    }


    fragColor = apply_fog(color, sphericalVertexDistance, cylindricalVertexDistance, FogEnvironmentalStart, FogEnvironmentalEnd, FogRenderDistanceStart, FogRenderDistanceEnd, FogColor);
}