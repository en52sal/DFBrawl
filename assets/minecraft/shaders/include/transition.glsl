#version 330

const vec2 hexSide = vec2(1.7320508, 1); // proportion between two sides of 30-60-90 triangle

float hexDistance(in vec2 p)
{    
    p = abs(p);
    
    return max(dot(p, hexSide * .5), p.y)*2;
}

vec4 hexCoords(vec2 p)
{   
    // hexagon centers
    vec4 hc = floor(vec4(p, p - vec2(hexSide.x/2., .5)) / hexSide.xyxy) + .5;
    
    // rectangular grids
    vec4 rg = vec4(p - hc.xy * hexSide, p - (hc.zw + .5) * hexSide);
    
    // hexagonal grid and IDs
    return dot(rg.xy, rg.xy) < dot(rg.zw, rg.zw)
        ? vec4(rg.xy, hc.xy)
        : vec4(rg.zw, hc.zw + .5);
}


float filledPercentage(float p, float t, float angle) {
    return t * (angle+1) - p * angle;
}
float filledPercentage(float p, float t) {
    return filledPercentage(p,t,1);
}

vec4 transition(float time, int id, vec2 pos, vec2 screen, float gameTime) {
    //time = 1;


    vec4 color = vec4(16,20,31,255)/255.;
    float sideLong = max(screen.x, screen.y);
    float sideShort = min(screen.x, screen.y);
    vec2 uv = 2*(pos-0.5*screen)/sideLong;
    bool transitionIn = time < 0.5;
    float actualTime = time;

    time = 1-abs(time*2-1);
    // default color behaviour (because load terrain... is stupid and weird and i dont like it #evil)
    color.rgb = fract(uv.x * 16. - uv.y * 8. + gameTime * 1.5) > 0.5 ? color.rgb : vec3(21,29,40)/255.;

    switch (id) {
        case 0: 
        {
            //uv = floor(uv*128)/128;

            uv *= 16. * (transitionIn ? -1 : -1);
            time = 1-actualTime;

            vec4 hex = hexCoords(uv);
            vec2 id = hex.zw/32.+.5;
            float distance = hexDistance(hex.xy);
            color.a = distance < filledPercentage(id.y, time, 5) ? 1 : 0;
        }
        break;
        case 1:
        {
            actualTime = 1 - actualTime;
            color.a = length(uv) > (actualTime * 1.2 - 0.2) * 2 ? 1 : 0;
        }
        break;
        case 2:
        {

            float size = 40.;
            uv *= size;
            time = 2. * size * (actualTime * -2 + 1);

            uv.y += abs(mod(uv.x,2)-1) -.5 - time;

            //color.rgb = (fract(uv.y * 0.5) > .5 ? vec3(21,29,40) : vec3(16,20,31))/255.;

            color.a = abs(uv.y) < size? 1 : 0;            
        }
        break;
		case 3: 
        {
            //uv = floor(uv*128)/128;

            uv *= 16. * (transitionIn ? 1 : 1);
            time = 1-actualTime;

            vec4 hex = hexCoords(uv);
            vec2 id = hex.zw/32.+.5;
            float distance = hexDistance(hex.xy);
            color.a = distance < filledPercentage(id.y, time, 5) ? 0 : 1;
        }
        break;
    }
    return color;
}