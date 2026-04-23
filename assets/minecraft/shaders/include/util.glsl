
int guiScale(mat4 ProjMat, vec2 ScreenSize) {
    return int(round(ScreenSize.x * ProjMat[0][0] / 2));
}