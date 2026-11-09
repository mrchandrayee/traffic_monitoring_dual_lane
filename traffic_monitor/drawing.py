import cv2
from . import config
def color(label): return config.CLASS_COLORS.get(label,config.CLASS_COLORS['default'])
def draw_box(frame,box,col,tid,label,conf,speed,counted):
    h,w=frame.shape[:2]; x1,y1,x2,y2=[int(v) for v in box]
    x1=max(0,x1);y1=max(0,y1);x2=min(w-1,x2);y2=min(h-1,y2)
    c=(0,255,190) if counted else col
    ov=frame.copy();cv2.rectangle(ov,(x1,y1),(x2,y2),c,-1);cv2.addWeighted(ov,.10,frame,.90,0,frame)
    cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,255),1)
    L=max(14,min(int(min(x2-x1,y2-y1)*.24),35))
    seg=[((x1,y1),(x1+L,y1)),((x1,y1),(x1,y1+L)),((x2,y1),(x2-L,y1)),((x2,y1),(x2,y1+L)),
         ((x1,y2),(x1+L,y2)),((x1,y2),(x1,y2-L)),((x2,y2),(x2-L,y2)),((x2,y2),(x2,y2-L))]
    for a,b in seg: cv2.line(frame,a,b,c,4,cv2.LINE_AA)
    text=f'{label.upper()} ID:{tid} {conf:.2f}'+(f' {speed:.1f} km/h' if speed is not None else '')
    (tw,th),_=cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,.46,1)
    top=max(0,y1-th-10);cv2.rectangle(frame,(x1,top),(min(w-1,x1+tw+10),y1),c,-1)
    cv2.putText(frame,text,(x1+5,max(th+2,y1-4)),cv2.FONT_HERSHEY_SIMPLEX,.46,(0,0,0),1,cv2.LINE_AA)
def trail(frame,history,col):
    pts=[tuple(map(int,p)) for _,p in history]
    for i in range(1,len(pts)):
        cv2.line(frame,pts[i-1],pts[i],col,max(1,int(1+3*i/max(1,len(pts)-1))),cv2.LINE_AA)
def lane_lines(frame):
    h,w=frame.shape[:2]; c=config
    a=(int(c.COUNT_LINE_START[0]*w),int(c.COUNT_LINE_START[1]*h))
    m=(int(c.COUNT_LINE_SPLIT[0]*w),int(c.COUNT_LINE_SPLIT[1]*h))
    b=(int(c.COUNT_LINE_END[0]*w),int(c.COUNT_LINE_END[1]*h))
    cv2.line(frame,a,m,c.COLOR_LANE1,3,cv2.LINE_AA);cv2.line(frame,m,b,c.COLOR_LANE2,3,cv2.LINE_AA)
    cv2.putText(frame,'LANE 1',(a[0]+8,a[1]-8),0,.5,c.COLOR_LANE1,2)
    cv2.putText(frame,'LANE 2',(m[0]+8,m[1]-8),0,.5,c.COLOR_LANE2,2)
    return {'lane1':(a,m),'lane2':(m,b)}
def hud(frame,tracker,fps,idx,total,tracking):
    h,w=frame.shape[:2];x,y=16,16;cw=min(430,w-32);ch=112
    ov=frame.copy();cv2.rectangle(ov,(x,y),(x+cw,y+ch),(15,18,24),-1)
    cv2.rectangle(ov,(x,y),(x+cw,y+ch),(70,85,105),2);cv2.addWeighted(ov,.86,frame,.14,0,frame)
    cv2.putText(frame,'DUAL-LANE VEHICLE AI COUNTER',(x+12,y+24),0,.54,(255,255,255),2)
    cv2.putText(frame,f"LANE 1: {tracker.lanes['lane1']}",(x+12,y+52),0,.55,(0,230,255),2)
    cv2.putText(frame,f"LANE 2: {tracker.lanes['lane2']}",(x+220,y+52),0,.55,(40,40,255),2)
    mode='TRACKING' if tracking else 'DETECT ONLY'
    cv2.putText(frame,f'TOTAL: {tracker.total} | {mode} | ACTIVE: {len(tracker.tracks)}',(x+12,y+78),0,.43,(255,255,0),1)
    pct=idx/total*100 if total else 0
    cv2.putText(frame,f'FPS {fps:.1f} FRAME {idx}/{total} ({pct:.1f}%)',(x+12,y+101),0,.36,(220,220,220),1)
