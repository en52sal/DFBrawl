#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:globals.glsl>
#moj_import <minecraft:transition.glsl>
#moj_import <minecraft:util.glsl>


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
        if (flag(redFlag, TRANSPARANT_MORE_FLAG)) color.a *= 0.4;

    } else {
        if (color.a < 0.1) {
            discard;
        }
    }


    fragColor = apply_fog(color, sphericalVertexDistance, cylindricalVertexDistance, FogEnvironmentalStart, FogEnvironmentalEnd, FogRenderDistanceStart, FogRenderDistanceEnd, FogColor);
}