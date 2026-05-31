
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