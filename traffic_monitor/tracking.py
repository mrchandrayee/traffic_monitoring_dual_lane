from collections import defaultdict,deque
from .geometry import center,dist,side,segment_intersect
class Track:
    def __init__(self,tid,box,label,frame,point):
        self.id=int(tid); self.box=box; self.label=label; self.point=point
        self.prev=point; self.history=deque([(frame,point)],maxlen=30)
        self.counted=set(); self.speeds=deque(maxlen=5); self.speed=None; self.last=frame
class TrafficTracker:
    def __init__(self,fps,mpp=0):
        self.fps=fps or 25; self.mpp=max(0,mpp); self.tracks={}
        self.lanes=defaultdict(int); self.classes=defaultdict(int); self.total=0
    def update(self,tid,box,label,frame):
        p=center(box); tid=int(tid)
        if tid not in self.tracks: self.tracks[tid]=Track(tid,box,label,frame,p)
        t=self.tracks[tid]; t.prev=t.point; t.point=p; t.box=box; t.label=label; t.last=frame
        t.history.append((frame,p))
        if self.mpp>0 and len(t.history)>=2:
            oldf,oldp=t.history[-2]; dt=max(1,frame-oldf)/self.fps
            v=dist(oldp,p)*self.mpp/dt*3.6
            if v<250: t.speeds.append(v); t.speed=sum(t.speeds)/len(t.speeds)
        return t
    def crossing(self,t,lines):
        for lane,(a,b) in lines.items():
            if lane in t.counted: continue
            s0,s1=side(t.prev,a,b),side(t.point,a,b)
            if s0*s1<0 and segment_intersect(t.prev,t.point,a,b):
                t.counted.add(lane); self.lanes[lane]+=1; self.classes[t.label]+=1; self.total+=1
    def cleanup(self,frame,max_age=60):
        for tid in [i for i,t in self.tracks.items() if frame-t.last>max_age]:
            del self.tracks[tid]
