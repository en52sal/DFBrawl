#version 330

#moj_import <minecraft:light.glsl>
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:globals.glsl>

uniform sampler2D Sampler0;

in float sphericalVertexDistance;
in float cylindricalVertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord1;
in vec3 vertexPosition;
in vec3 camWorldPos;
in vec4 baseColor;
in vec3 viewPos;

out vec4 fragColor;


mat4 ditherMat = mat4(
    0.0, 8.0, 2.0, 10.0,
    12.0, 4.0, 14.0, 6.0,
    3.0, 11.0, 1.0, 9.0,
    15.0, 7.0, 13.0, 5.0
) / 16.0;


void main() {
    vec3 tex = texture(Sampler0, texCoord0).rgb;

    if (tex.r >= 1. && tex.g >= 1. && tex.b >= 1.) {
        vec2 ditherInput = gl_FragCoord.xy / 2.0;

        int x = int(mod(ditherInput.x, 4.0));
        int y = int(mod(ditherInput.y, 4.0));
        float threshold = ditherMat[y][x];

        float a = length(vertexPosition) - 0.5;
        if (a < threshold) discard;

        fragColor = vec4(baseColor.rgb, 1.);
        return;
    }

    vec4 color = texture(Sampler0, texCoord0) * vertexColor * ColorModulator;
    if (color.a < 0.1) {
        discard;
    }
    
    fragColor = apply_fog(color, sphericalVertexDistance, cylindricalVertexDistance, FogEnvironmentalStart, FogEnvironmentalEnd, FogRenderDistanceStart, FogRenderDistanceEnd, FogColor);
}