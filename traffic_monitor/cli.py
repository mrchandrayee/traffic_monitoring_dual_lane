import argparse
from .pipeline import process
def main():
    p=argparse.ArgumentParser(description='YOLO traffic detection, tracking, speed and dual-lane counting')
    p.add_argument('--model',default='yolov8n.pt',help='Ultralytics weights .pt')
    p.add_argument('--source',required=True,help='Video path or webcam index')
    p.add_argument('--output',default='vehicle_results')
    p.add_argument('--output-name',default='traffic_annotated.mp4')
    p.add_argument('--conf',type=float,default=.30);p.add_argument('--iou',type=float,default=.45)
    p.add_argument('--imgsz',type=int,default=640)
    p.add_argument('--classes',default='person,motorcycle,car,bus,truck')
    p.add_argument('--tracker',default='bytetrack.yaml')
    p.add_argument('--no-track',dest='tracking',action='store_false');p.set_defaults(tracking=True)
    p.add_argument('--rider-iou',type=float,default=.02)
    p.add_argument('--meters-per-pixel',type=float,default=0.0)
    p.add_argument('--device',default='');p.add_argument('--show',action='store_true')
    process(p.parse_args())
