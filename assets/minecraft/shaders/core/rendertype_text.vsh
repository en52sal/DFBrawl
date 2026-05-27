#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:globals.glsl>

#define PI 3.14159265

const vec2[] corners = vec2[](
    vec2(-1, 1),
    vec2(-1, -1),
    vec2(1, -1),
    vec2(1, 1)
);

const vec2[] anchors = vec2[](
    vec2(-1.0, 0.0),   // TOP_LEFT
    vec2(0.0, 0.0),    // TOP_CENTER
    vec2(1.0, 0.0),    // TOP_RIGHT
    vec2(-1.0, -1.0),  // MIDDLE_LEFT
    vec2(0.0, -1.0),   // CENTER
    vec2(1.0, -1.0),   // MIDDLE_RIGHT
    vec2(-1.0, -2.0),  // BOTTOM_LEFT
    vec2(0.0, -2.0),   // BOTTOM_CENTER
    vec2(1.0, -2.0)    // BOTTOM_RIGHT
);

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;

uniform sampler2D Sampler2;
uniform sampler2D Sampler0;

out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;

out float isTransition;

const ivec3 TRANSITION_COLOR = ivec3(250, 250, 255);
const ivec3 CENTER_COLOR = ivec3(250, 245, 255);

bool is_color(vec4 c, ivec3 target) {
    return int(c.x * 255) == target.x && int(c.y * 255) == target.y && int(c.z * 255) == target.z;
}

vec2 guiPixel(mat4 ProjMat) {
	return vec2(ProjMat[0][0], ProjMat[1][1]) / 1.9;
}

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1);

    int id = gl_VertexID%4;
    vec4 color = Color;

    // Transition Code ////////////////////////////////////////
    vec4 sample = texture(Sampler0, UV0);
    isTransition = 0;
    if (is_color(sample, TRANSITION_COLOR)) {
        isTransition = 1;
        gl_Position.xy = corners[id];
    }
    ///////////////////////////////////////////////////////////

    // Center
    if (is_color(color, CENTER_COLOR)) {
        gl_Position.xy += vec2(0.0, -1.0);
        gl_Position.xy += guiPixel(ProjMat) * vec2(1, -70);
        color = vec4(1, 1, 1, 1);
    }

    
    // ANCHOR CODE ////////////////////////////////////////////
//    int anchorCheck = int(Color.b * 255);
//    int anchor = anchorCheck - 16 * 15; // #f1 -> #f9
//
//    if (anchor >= 0 && anchor < 9) {
//        vec2 offset = vec2(Color.r - 0.5, Color.g - 0.5);
//        offset *= guiPixel(ProjMat) * 255.;
//        gl_Position.xy += anchors[anchor-1];
//        gl_Position.xy += offset;
//
//        color = vec4(1, 1, 1, 1);
//    }
//    ///////////////////////////////////////////////////////////


    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    vertexColor = color * texelFetch(Sampler2, UV2 / 16, 0);
    texCoord0 = UV0;
}