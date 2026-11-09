from pathlib import Path
import cv2
from ultralytics import YOLO
from .fusion import merge_rider_and_motorcycle
from .tracking import TrafficTracker
from .drawing import color,draw_box,trail,lane_lines,hud
def source_value(s): return int(s) if s.isdigit() else s
def process(args):
    model=YOLO(args.model); names=model.names
    wanted=[s.strip().lower() for s in args.classes.split(',')]
    ids=[int(i) for i,n in names.items() if str(n).lower() in wanted]
    if not ids: raise RuntimeError(f'No requested classes {wanted} in model labels {names}')
    cap=cv2.VideoCapture(source_value(args.source))
    if not cap.isOpened(): raise RuntimeError(f'Cannot open source {args.source}')
    w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    fps=cap.get(cv2.CAP_PROP_FPS) or 25.0
    if fps<=0 or fps>240: fps=25.0
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    outdir=Path(args.output);outdir.mkdir(parents=True,exist_ok=True)
    outpath=outdir/args.output_name
    writer=cv2.VideoWriter(str(outpath),cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h))
    if not writer.isOpened(): raise RuntimeError(f'Cannot create {outpath}')
    tracker=TrafficTracker(fps,args.meters_per_pixel);idx=0;det_total=0
    try:
        while True:
            ok,frame=cap.read()
            if not ok: break
            idx+=1
            kw=dict(source=frame,conf=args.conf,iou=args.iou,imgsz=args.imgsz,classes=ids,verbose=False)
            if args.device: kw['device']=args.device
            result=(model.track(**kw,tracker=args.tracker,persist=True)[0] if args.tracking else model.predict(**kw)[0])
            boxes=[];confs=[];clses=[];tids=[]
            if result.boxes is not None and len(result.boxes):
                boxes=result.boxes.xyxy.cpu().numpy().tolist()
                confs=result.boxes.conf.cpu().numpy().tolist()
                clses=result.boxes.cls.cpu().numpy().astype(int).tolist()
                tids=(result.boxes.id.cpu().numpy().astype(int).tolist()
                      if args.tracking and result.boxes.id is not None else [None]*len(boxes))
            fused=merge_rider_and_motorcycle(boxes,confs,clses,tids,names,args.rider_iou)
            lines=lane_lines(frame)
            for j,item in enumerate(fused):
                tid=item['track_id'];label=item['class_name'];box=item['box']
                if tid is not None and args.tracking:
                    t=tracker.update(tid,box,label,idx);tracker.crossing(t,lines)
                    pts=[tuple(map(int,p)) for _,p in t.history]
                    for k in range(1,len(pts)): cv2.line(frame,pts[k-1],pts[k],color(label),2,cv2.LINE_AA)
                    speed=t.speed;counted=bool(t.counted)
                else:
                    tid=None;speed=None;counted=False
                draw_box(frame,box,color(label),tid,label,item['conf'],speed,counted)
                det_total+=1
            tracker.cleanup(idx)
            hud(frame,tracker,fps,idx,total,args.tracking);writer.write(frame)
            if args.show:
                cv2.imshow('AI Dual-Lane Traffic Monitoring',frame)
                key=cv2.waitKey(1)&0xff
                if key==ord('q'): break
                if key==ord('p'): cv2.waitKey(0)
            if idx%50==0:
                print(f'Frame {idx}/{total} | L1={tracker.lanes["lane1"]} L2={tracker.lanes["lane2"]} total={tracker.total}')
    finally:
        cap.release();writer.release();cv2.destroyAllWindows()
    print('TRAFFIC MONITORING SUMMARY')
    print(f'Frames: {idx} | Detection instances: {det_total}')
    print(f'Lane 1: {tracker.lanes["lane1"]} | Lane 2: {tracker.lanes["lane2"]} | Total: {tracker.total}')
    print(f'Output: {outpath.resolve()}')
