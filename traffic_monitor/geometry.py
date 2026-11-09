import math
def ccw(a,b,c):
    return ((c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0]))
def segment_intersect(a,b,c,d):
    return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)
def center(box):
    x1,y1,x2,y2=box
    return ((x1+x2)/2,(y1+y2)/2)
def box_iou(a,b):
    ax1,ay1,ax2,ay2=a; bx1,by1,bx2,by2=b
    ix1,iy1=max(ax1,bx1),max(ay1,by1); ix2,iy2=min(ax2,bx2),min(ay2,by2)
    inter=max(0,ix2-ix1)*max(0,iy2-iy1)
    aa=max(0,ax2-ax1)*max(0,ay2-ay1); ab=max(0,bx2-bx1)*max(0,by2-by1)
    return inter/(aa+ab-inter+1e-9)
def side(p,a,b):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def dist(a,b): return math.hypot(b[0]-a[0],b[1]-a[1])
